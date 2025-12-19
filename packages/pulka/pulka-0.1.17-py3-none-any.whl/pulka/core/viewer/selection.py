from __future__ import annotations

import contextlib
import math
import re
from collections.abc import Callable, Hashable, Sequence, Sized
from typing import Any, Protocol, cast, runtime_checkable

from ..errors import PlanError
from ..plan import QueryPlan
from ..plan_ops import set_filter as plan_set_filter
from ..row_provider import RowProvider
from .row_count_tracker import RowCountTracker
from .transformation_manager import ViewerTransformationManager

SELECTION_IDS_LITERAL_CAP = 5000


@runtime_checkable
class SelectionNavigation(Protocol):
    """Minimal surface that :class:`SelectionController` needs from ``Viewer``."""

    @property
    def columns(self) -> list[str]: ...

    @property
    def visible_cols(self) -> list[str]: ...

    @property
    def visible_row_positions(self) -> list[int]: ...

    cur_row: int
    cur_col: int
    row0: int

    @property
    def sheet(self) -> Any: ...

    @property
    def status_message(self) -> str | None: ...

    @status_message.setter
    def status_message(self, message: str | None) -> None: ...

    def clamp(self) -> None: ...

    def _current_plan(self) -> QueryPlan | None: ...

    def _row_identifier_for_slice(
        self,
        table_slice: Any,
        row_index: int,
        *,
        row_positions: Sequence[int] | None = None,
        absolute_row: int | None = None,
    ) -> Hashable | None: ...

    def _count_plan_rows(self, plan: QueryPlan) -> int | None: ...

    def get_visible_table_slice(self, columns: Sequence[str]) -> Any: ...

    @property
    def ui_hooks(self) -> Any: ...

    def _selection_matches_for_slice(
        self, table_slice: Any, row_positions: Sequence[int] | None, expr_text: str | None
    ) -> set[Hashable] | None: ...


class SelectionController:
    """Own selection state and mutations for the viewer."""

    def __init__(
        self,
        navigation: SelectionNavigation,
        *,
        row_provider: RowProvider,
        row_counts: RowCountTracker,
        transformations: ViewerTransformationManager,
    ) -> None:
        self._nav = navigation
        self._row_provider = row_provider
        self._row_counts = row_counts
        self._transformations = transformations

        self._selected_row_ids: set[Hashable] = set()
        self._selection_filter_expr: str | None = None
        self._value_selection_filter: tuple[str, Any, bool] | None = None
        self._selection_epoch: int = 0
        self._uses_row_ids: bool | None = None

    # ------------------------------------------------------------------
    # State accessors
    # ------------------------------------------------------------------

    @property
    def selected_row_ids(self) -> set[Hashable]:
        return self._selected_row_ids

    @selected_row_ids.setter
    def selected_row_ids(self, value: set[Hashable]) -> None:
        self._selected_row_ids = value

    @property
    def selection_filter_expr(self) -> str | None:
        return self._selection_filter_expr

    @selection_filter_expr.setter
    def selection_filter_expr(self, value: str | None) -> None:
        self._selection_filter_expr = value

    @property
    def value_selection_filter(self) -> tuple[str, Any, bool] | None:
        return self._value_selection_filter

    @value_selection_filter.setter
    def value_selection_filter(self, value: tuple[str, Any, bool] | None) -> None:
        self._value_selection_filter = value

    @property
    def uses_row_ids(self) -> bool | None:
        return self._uses_row_ids

    @uses_row_ids.setter
    def uses_row_ids(self, value: bool | None) -> None:
        self._uses_row_ids = value

    @property
    def selection_epoch(self) -> int:
        return self._selection_epoch

    @selection_epoch.setter
    def selection_epoch(self, value: int) -> None:
        self._selection_epoch = value

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def encode_filter_literal(value: object) -> str | None:
        """Return a safe filter literal or ``None`` when the value is unsupported."""

        if isinstance(value, (str, int, bool)) or value is None:
            return f"lit({value!r})"
        if isinstance(value, float):
            if math.isnan(value):
                return None
            return f"lit({value!r})"
        try:
            representation = repr(value)
        except Exception:
            return None
        return f"lit({representation})"

    @staticmethod
    def toggle_inversion_clause(selection_clause: str) -> str:
        """Return the inverted clause, collapsing nested negations when possible."""

        stripped = selection_clause.strip()
        if stripped.startswith("~(") and stripped.endswith(")"):
            inner = stripped[2:-1].strip()
            if inner:
                return inner
        return f"~({selection_clause})"

    def value_selection_filter_expr(self) -> str | None:
        """Return the filter expression for the active value selection, if any."""

        value_filter = self._value_selection_filter
        if value_filter is None:
            return None

        column_name, target_value, is_target_nan = value_filter
        if is_target_nan:
            return f'c["{column_name}"].is_nan()'

        literal = self.encode_filter_literal(target_value)
        if literal is None:
            return None
        return f'c["{column_name}"] == {literal}'

    def selection_filter_clause(self, plan_columns: Sequence[str]) -> str | None:
        """Return a filter expression representing the current selection."""

        parts: list[str] = []
        if self._selection_filter_expr:
            parts.append(self._selection_filter_expr)
        columns_set = set(plan_columns)
        row_id_column = getattr(self._row_provider, "_row_id_column", None)
        value_filter = self._value_selection_filter

        if value_filter is not None:
            column_name, _target_value, _is_target_nan = value_filter
            if column_name in columns_set:
                value_expr = self.value_selection_filter_expr()
                if value_expr is not None:
                    parts.append(value_expr)

        if (
            self._selected_row_ids
            and row_id_column
            and row_id_column in columns_set
            and len(self._selected_row_ids) <= SELECTION_IDS_LITERAL_CAP
        ):
            ids: list[object] = []
            seen: set[object] = set()
            for row_id in self._selected_row_ids:
                if row_id in seen:
                    continue
                seen.add(row_id)
                ids.append(row_id)
            if ids:
                parts.append(f'c["{row_id_column}"].is_in({ids!r})')

        if not parts:
            return None
        return " | ".join(f"({part})" for part in parts)

    def selection_count(self, plan: QueryPlan) -> int | None:
        """Return the number of rows currently selected using a filter-friendly path."""

        plan_columns: list[str] = list(self._nav.columns)
        row_id_column = getattr(self._row_provider, "_row_id_column", None)
        if row_id_column and row_id_column not in plan_columns:
            plan_columns.append(row_id_column)

        filter_clause = self.selection_filter_clause(plan_columns)
        if filter_clause is None:
            if self._selected_row_ids:
                return len(self._selected_row_ids)
            return None

        try:
            selection_plan = plan_set_filter(plan, filter_clause, mode="append")
        except PlanError:
            return None

        plan_count = self._nav._count_plan_rows(selection_plan)
        if plan_count is not None:
            return plan_count

        try:
            plan_result = self._nav.sheet.with_plan(selection_plan)
            return int(len(cast(Sized, plan_result)))
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Selection mutations
    # ------------------------------------------------------------------

    def select_rows_containing_text(
        self,
        text: str,
        *,
        columns: Sequence[str],
        selection_count_fn: Callable[[QueryPlan], int | None] | None = None,
    ) -> None:
        """Select rows where any provided column contains ``text``."""

        cleaned = text.strip()
        if not cleaned:
            self._nav.status_message = "selection requires text"
            return

        unique_columns: list[str] = []
        seen: set[str] = set()
        for name in columns:
            if not isinstance(name, str):
                continue
            if name in seen:
                continue
            seen.add(name)
            unique_columns.append(name)

        if not unique_columns:
            self._nav.status_message = "no columns to search"
            return

        pattern = re.escape(cleaned)
        pattern_literal = pattern.replace("\\", "\\\\").replace('"', '\\"')
        match_nulls = cleaned.lower() in {"null", "none"}

        def _column_expr(name: str) -> str:
            escaped = name.replace("\\", "\\\\").replace('"', '\\"')
            base = f'c["{escaped}"].cast(pl.Utf8, strict=False).fill_null("")'
            contains = f'{base}.str.contains("(?i){pattern_literal}", literal=False)'
            if match_nulls:
                return f'({contains} | c["{escaped}"].is_null())'
            return contains

        clauses = [_column_expr(name) for name in unique_columns]
        selection_expr = " | ".join(f"({clause})" for clause in clauses if clause)
        if not selection_expr:
            self._nav.status_message = "no searchable columns"
            return

        plan = self._nav._current_plan()

        def mutate() -> bool:
            self._selection_filter_expr = selection_expr
            self._value_selection_filter = None
            self._selected_row_ids.clear()
            self._selection_epoch += 1
            return True

        result = self._transformations.record_change(f"select rows containing {cleaned!r}", mutate)
        if not result.committed:
            return

        selected_count: int | None = None
        if selection_count_fn is not None and plan is not None:
            try:
                selected_count = selection_count_fn(plan)
            except Exception:
                selected_count = None

        if selected_count is None:
            self._nav.status_message = f"Selecting rows containing '{cleaned}'"
            self._record_repeat_action()
            return

        suffix = "" if selected_count == 1 else "s"
        self._nav.status_message = f"Selected {selected_count:,} row{suffix} containing '{cleaned}'"
        self._record_repeat_action()

    def _row_index_for_selection(
        self, *, target_row: int, row_positions: Sequence[int], table_slice: Any
    ) -> int | None:
        """Map an absolute row to the index within ``table_slice`` if visible."""

        if row_positions:
            try:
                return row_positions.index(target_row)
            except ValueError:
                pass

        start_offset = getattr(table_slice, "start_offset", None)
        if start_offset is not None:
            try:
                offset_int = int(start_offset)
            except Exception:
                offset_int = None
            if offset_int is not None:
                candidate = target_row - offset_int
                if 0 <= candidate < getattr(table_slice, "height", 0):
                    return candidate
        return None

    def _row_ids_need_materialization(self) -> bool:
        """Return True when row identifiers are not simple offsets."""

        if self._uses_row_ids is True:
            return True
        table = getattr(getattr(self._nav, "_row_cache", None), "table", None)
        if table is not None and getattr(table, "row_ids", None) is not None:
            self._uses_row_ids = True
            return True
        return any(not isinstance(row_id, int) for row_id in self._selected_row_ids)

    def _detect_row_ids(self) -> bool:
        """Lightweight probe to see if the dataset exposes row ids."""

        columns = self._nav.visible_cols or self._nav.columns
        if not columns:
            return False
        plan = self._nav._current_plan()
        try:
            slice_, _status = self._row_provider.get_slice(plan, columns[:1], 0, 1)
        except Exception:
            return False
        row_ids = getattr(slice_, "row_ids", None)
        if row_ids is None:
            return False
        try:
            candidate = row_ids[0]
        except Exception:
            candidate = None
        return candidate is not None

    def _collect_row_ids(self, total_rows: int) -> set[Hashable]:
        """Collect row identifiers for the full dataset."""

        columns = self._nav.visible_cols or self._nav.columns
        if not columns:
            return set()

        plan = self._nav._current_plan()
        chunk = 2048
        collected: set[Hashable] = set()

        start = 0
        while start < total_rows:
            try:
                slice_, _status = self._row_provider.get_slice(plan, columns[:1], start, chunk)
            except Exception:
                break
            if slice_.height <= 0:
                break
            for offset in range(slice_.height):
                absolute_row = start + offset
                row_id = self._nav._row_identifier_for_slice(
                    slice_, offset, row_positions=None, absolute_row=absolute_row
                )
                if row_id is not None:
                    collected.add(row_id)
            if slice_.height < chunk:
                break
            start += slice_.height
        if collected:
            self._uses_row_ids = True
        return collected

    def toggle_row_selection(self) -> None:
        """Toggle selection for the currently focused row."""

        total_rows_hint = getattr(self._nav, "_total_rows", None)
        if total_rows_hint is not None and total_rows_hint <= 0:
            self._nav.status_message = "no rows to select"
            return

        sheet = getattr(self._nav, "sheet", None)
        if sheet is not None and getattr(sheet, "is_file_browser", False):
            entry_at = getattr(sheet, "_entry_at", None)
            if callable(entry_at):
                entry = entry_at(self._nav.cur_row)
                name = getattr(entry, "row", {}).get("name", "") if entry is not None else ""
                if name == "..":
                    self._nav.status_message = "parent directory is not selectable"
                    return

        columns = self._nav.visible_cols or self._nav.columns
        if not columns:
            self._nav.status_message = "no rows to select"
            return

        table_slice = self._nav.get_visible_table_slice(columns)
        if table_slice.height <= 0:
            self._nav.status_message = "no rows to select"
            return

        row_positions = self._nav.visible_row_positions
        row_index = self._row_index_for_selection(
            target_row=self._nav.cur_row, row_positions=row_positions, table_slice=table_slice
        )
        if row_index is None:
            self._nav.status_message = "row not in view"
            return

        row_id = self._nav._row_identifier_for_slice(
            table_slice,
            row_index,
            row_positions=row_positions,
            absolute_row=self._nav.cur_row,
        )
        if row_id is None:
            self._nav.status_message = "row id unavailable"
            return

        was_selected = row_id in self._selected_row_ids

        def mutate() -> bool:
            if was_selected:
                self._selected_row_ids.discard(row_id)
            else:
                self._selected_row_ids.add(row_id)
            self._selection_epoch += 1
            return True

        description = "unselect row" if was_selected else "select row"
        result = self._transformations.record_change(description, mutate)
        if not result.committed:
            return

        self._nav.status_message = "Unselected row" if was_selected else "Selected row"
        self._record_repeat_action()

    def invert_selection(self) -> None:
        """Invert selection state for all rows."""

        plan = self._nav._current_plan()
        row_id_column = getattr(self._row_provider, "_row_id_column", None)
        plan_columns = list(self._nav.columns)
        if row_id_column and row_id_column not in plan_columns:
            plan_columns.append(row_id_column)
        selection_clause = self.selection_filter_clause(plan_columns)
        value_filter_expr = self.value_selection_filter_expr()
        if selection_clause is None and value_filter_expr is not None:
            selection_clause = value_filter_expr

        if selection_clause is not None:
            target_clause = self.toggle_inversion_clause(selection_clause)

            def mutate_selection_clause() -> bool:
                self._selection_filter_expr = target_clause
                self._value_selection_filter = None
                self._selected_row_ids.clear()
                self._selection_epoch += 1
                return True

            result = self._transformations.record_change(
                "invert selection", mutate_selection_clause
            )
            if not result.committed:
                return

            selected_count = self.selection_count(plan) if plan is not None else None
            if selected_count is None:
                self._nav.status_message = "Selected inverted rows"
                self._record_repeat_action()
                return
            suffix = "" if selected_count == 1 else "s"
            self._nav.status_message = f"Selected {selected_count:,} row{suffix}"
            self._record_repeat_action()
            return

        total_rows = self._row_counts.ensure_total_rows()
        if total_rows is None or total_rows <= 0:
            self._nav.status_message = "no rows to select"
            return

        use_row_ids = self._row_ids_need_materialization()
        if not use_row_ids:
            detected = self._detect_row_ids()
            if detected:
                self._uses_row_ids = True
            use_row_ids = detected or use_row_ids
        if use_row_ids:
            invert_targets = self._collect_row_ids(total_rows)
        else:
            invert_targets = set(range(total_rows))

        if not invert_targets and total_rows > 0:
            invert_targets = set(range(total_rows))

        current_selection = set(self._selected_row_ids)
        toggled_selection = current_selection ^ invert_targets
        if toggled_selection == current_selection:
            self._nav.status_message = "selection unchanged"
            return

        def mutate_toggle() -> bool:
            self._selection_filter_expr = None
            self._value_selection_filter = None
            self._selected_row_ids = toggled_selection
            self._selection_epoch += 1
            return True

        result = self._transformations.record_change("invert selection", mutate_toggle)
        if not result.committed:
            return

        selected_count = len(self._selected_row_ids)
        suffix = "" if selected_count == 1 else "s"
        self._nav.status_message = f"Selected {selected_count} row{suffix}"
        self._record_repeat_action()

    def _clear_selection_state(self) -> bool:
        """Clear any stored selection without recording history."""

        selection_clause = self.selection_filter_clause(self._nav.columns)
        has_ids = bool(self._selected_row_ids)
        if not selection_clause and not has_ids:
            return False

        self._selection_filter_expr = None
        self._value_selection_filter = None
        self._selected_row_ids.clear()
        self._selection_epoch += 1
        return True

    def clear_selection_recorded(self, description: str = "clear selection") -> bool:
        """Clear selection and persist an undo snapshot when changed."""

        result = self._transformations.record_change(description, self._clear_selection_state)
        return result.committed

    def clear_row_selection(self) -> None:
        """Clear any selected rows."""

        selection_clause = self.selection_filter_clause(self._nav.columns)
        has_ids = bool(self._selected_row_ids)
        if not selection_clause and not has_ids:
            self._nav.status_message = "no rows selected"
            return

        cleared = len(self._selected_row_ids) if has_ids else None

        def mutate() -> bool:
            return self._clear_selection_state()

        result = self._transformations.record_change("clear selection", mutate)
        if not result.committed:
            return

        if cleared is None:
            self._nav.status_message = "Cleared selection"
            self._record_repeat_action()
            return

        suffix = "" if cleared == 1 else "s"
        self._nav.status_message = f"Cleared selection ({cleared} row{suffix})"
        self._record_repeat_action()

    def matching_row_ids_for_value(
        self,
        column_name: str,
        target_value: object,
        *,
        is_target_nan: bool,
        plan: Any | None = None,
        total_rows: int | None = None,
    ) -> tuple[set[Hashable], bool]:
        """Return row ids matching ``target_value`` for ``column_name``."""

        def _matches(value: object) -> bool:
            if is_target_nan:
                return isinstance(value, float) and math.isnan(value)
            return value == target_value

        if total_rows is None:
            total_rows = self._row_counts.ensure_total_rows()
        matching_ids: set[Hashable] = set()
        chunk = 2048
        start = 0

        while True:
            if total_rows is not None and start >= total_rows:
                break

            table_slice, _status = self._row_provider.get_slice(plan, (column_name,), start, chunk)
            if table_slice.height <= 0:
                break

            try:
                slice_values = table_slice.column(column_name).values
            except Exception:
                slice_values = ()

            for offset in range(table_slice.height):
                try:
                    value = slice_values[offset]
                except Exception:
                    value = None
                if not _matches(value):
                    continue
                row_id = self._nav._row_identifier_for_slice(
                    table_slice,
                    offset,
                    row_positions=None,
                    absolute_row=start + offset,
                )
                if row_id is not None:
                    matching_ids.add(row_id)

            if table_slice.height < chunk:
                break
            start += table_slice.height

        uses_row_ids = any(not isinstance(row_id, int) for row_id in matching_ids)
        return matching_ids, uses_row_ids

    def select_matching_value_rows(
        self,
        *,
        selection_count_fn: Callable[[QueryPlan], int | None] | None = None,
    ) -> None:
        """Select all rows matching the current cell's value in the active column."""

        if not self._nav.columns:
            self._nav.status_message = "no columns to select"
            return

        try:
            current_column = self._nav.columns[self._nav.cur_col]
        except Exception:
            self._nav.status_message = "no columns to select"
            return

        plan = self._nav._current_plan()
        try:
            current_slice, _ = self._row_provider.get_slice(
                plan, (current_column,), self._nav.cur_row, 1
            )
        except Exception as exc:  # pragma: no cover - defensive
            self._nav.status_message = f"select error: {exc}"
            return

        if current_slice.height <= 0:
            self._nav.status_message = "no rows to select"
            return

        try:
            values = current_slice.column(current_column).values
            target_value = values[0] if values else None
        except Exception:  # pragma: no cover - defensive
            self._nav.status_message = "value unavailable"
            return

        is_target_nan = isinstance(target_value, float) and math.isnan(target_value)
        current_filter = self._value_selection_filter
        matches_existing_filter = False
        if current_filter is not None:
            filter_column, filter_value, filter_is_nan = current_filter
            if filter_column == current_column and filter_is_nan is is_target_nan:
                matches_existing_filter = is_target_nan or filter_value == target_value

        if matches_existing_filter:

            def mutate_clear_value_selection() -> bool:
                if self._value_selection_filter is None:
                    return False
                self._selection_filter_expr = None
                self._value_selection_filter = None
                self._selection_epoch += 1
                return True

            result = self._transformations.record_change(
                "clear value selection", mutate_clear_value_selection
            )
            if not result.committed:
                return

            self._nav.status_message = "Cleared value selection"
            try:
                self._nav.ui_hooks.invalidate()
                self._nav.ui_hooks.call_soon(self._nav.ui_hooks.invalidate)
            except Exception:
                pass
            self._record_repeat_action()
            return

        new_filter = (current_column, target_value, is_target_nan)

        def mutate() -> bool:
            self._selection_filter_expr = None
            self._value_selection_filter = new_filter
            self._selection_epoch += 1
            return True

        result = self._transformations.record_change("select matching rows", mutate)
        if not result.committed:
            return

        total_rows = self._row_counts.ensure_total_rows()
        if total_rows is not None and total_rows > 0:
            formatted_total = f"{total_rows:,}"
            self._nav.status_message = f"Selecting matching rows across ~{formatted_total} rows..."
        else:
            self._nav.status_message = "Selecting matching rows..."
        try:
            self._nav.ui_hooks.invalidate()
            self._nav.ui_hooks.call_soon(self._nav.ui_hooks.invalidate)
        except Exception:
            pass

        selected_count: int | None = None
        if plan is not None:
            if selection_count_fn is not None:
                selected_count = selection_count_fn(plan)
            else:
                selected_count = self.selection_count(plan)
        if selected_count is None:
            self._nav.status_message = "Selected matching rows"
            self._record_repeat_action()
            return

        suffix = "" if selected_count == 1 else "s"
        self._nav.status_message = f"Selected {selected_count:,} matching row{suffix}"
        self._record_repeat_action()

    def _record_repeat_action(self) -> None:
        """Mark selection as the most recent repeatable navigation action."""

        recorder = getattr(self._nav, "_record_repeat_action", None)
        if callable(recorder):
            with contextlib.suppress(Exception):
                recorder("selection")

    def navigate_selected_row(self, *, forward: bool) -> bool:
        """Move to the next/previous selected row without wrapping."""

        selection_lookup = set(self._selected_row_ids)
        value_filter = self._value_selection_filter
        columns = list(self._nav.columns)
        row_id_column = getattr(self._row_provider, "_row_id_column", None)
        if row_id_column and row_id_column not in columns:
            columns.append(row_id_column)
        filter_column: str | None = value_filter[0] if value_filter is not None else None
        if filter_column and filter_column not in columns:
            columns.append(filter_column)

        selection_expr = self.selection_filter_clause(columns)
        if selection_expr is None and value_filter is not None:
            selection_expr = self.value_selection_filter_expr()

        has_selection = bool(selection_lookup or selection_expr or value_filter)
        if not has_selection:
            self._nav.status_message = "no rows selected"
            return False

        total_rows = self._row_counts.ensure_total_rows()
        if total_rows is None or total_rows <= 0:
            self._nav.status_message = "no rows to navigate"
            return False

        plan = self._nav._current_plan()
        if plan is None:
            self._nav.status_message = "selection navigation unavailable"
            return False

        start_row = self._nav.cur_row + 1 if forward else self._nav.cur_row - 1
        if forward and start_row >= total_rows:
            self._nav.status_message = "no more selected rows"
            return False
        if not forward and start_row < 0:
            self._nav.status_message = "no more selected rows"
            return False

        chunk = 512
        row_provider = self._row_provider
        fetch_columns = tuple(columns)
        value_candidates = None

        current = start_row
        while 0 <= current < total_rows:
            if forward:
                fetch_start = current
                fetch_count = min(chunk, total_rows - fetch_start)
            else:
                fetch_start = max(0, current - chunk + 1)
                fetch_count = current - fetch_start + 1

            try:
                table_slice, _ = row_provider.get_slice(
                    plan, fetch_columns, fetch_start, fetch_count
                )
            except Exception as exc:  # pragma: no cover - defensive
                self._nav.status_message = f"selection navigation error: {exc}"[:120]
                return False

            height = table_slice.height
            if height <= 0:
                break

            base_row = (
                table_slice.start_offset if table_slice.start_offset is not None else fetch_start
            )
            matches_from_expr = (
                self._nav._selection_matches_for_slice(table_slice, None, selection_expr)
                if selection_expr
                else None
            )

            if value_filter is not None and selection_expr is None and filter_column:
                try:
                    value_candidates = table_slice.column(filter_column).values
                except Exception:
                    value_candidates = None

            indices: Sequence[int] = range(height) if forward else range(height - 1, -1, -1)

            for idx in indices:
                abs_row = base_row + idx
                if forward and abs_row <= self._nav.cur_row:
                    continue
                if not forward and abs_row >= self._nav.cur_row:
                    continue

                row_id = self._nav._row_identifier_for_slice(
                    table_slice,
                    idx,
                    row_positions=None,
                    absolute_row=abs_row,
                )
                if row_id is None:
                    continue

                if row_id in selection_lookup:
                    return self._apply_selection_navigation(abs_row, forward=forward)

                if matches_from_expr and row_id in matches_from_expr:
                    return self._apply_selection_navigation(abs_row, forward=forward)

                if value_candidates is None or value_filter is None:
                    continue

                try:
                    candidate = value_candidates[idx]
                except Exception:
                    continue

                is_match = False
                if value_filter[2]:
                    try:
                        is_match = bool(math.isnan(candidate))
                    except Exception:
                        is_match = False
                else:
                    try:
                        is_match = candidate == value_filter[1]
                    except Exception:
                        is_match = False

                if is_match:
                    return self._apply_selection_navigation(abs_row, forward=forward)

            current = base_row + height if forward else base_row - 1

        self._nav.status_message = "no more selected rows"
        return False

    def _apply_selection_navigation(self, target_row: int, *, forward: bool) -> bool:
        """Move cursor to ``target_row`` and center it when possible."""

        self._nav.cur_row = target_row
        center = getattr(self._nav, "center_current_row", None)
        if callable(center):
            try:
                center()
            except Exception:
                self._nav.clamp()
        else:
            self._nav.clamp()

        direction = "next" if forward else "previous"
        self._nav.status_message = f"{direction} selected row"
        self._record_repeat_action()
        return True
