"""
TUI screen management for Pulka.

This module manages the sheet stack, viewer state, and dialog handling
within the terminal user interface.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator, Sequence
from contextlib import suppress
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING

import polars as pl
from prompt_toolkit import Application
from prompt_toolkit.formatted_text import ANSI, StyleAndTextTuples
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.widgets import Box, Button, Dialog, TextArea
from rich.console import Console
from rich.pretty import Pretty

from .. import theme
from ..clipboard import copy_to_clipboard
from ..command.parser import CommandDispatchResult
from ..command.registry import CommandContext
from ..command.runtime import CommandRuntimeResult
from ..config import use_prompt_toolkit_table
from ..core.engine.contracts import TableSlice
from ..core.engine.polars_adapter import table_slice_from_dataframe
from ..core.viewer import Viewer, build_filter_expr_for_values, viewer_public_state
from ..core.viewer.ui_hooks import NullViewerUIHooks
from ..core.viewer.ui_state import resolve_insight_state, set_insight_state
from ..data.filter_lang import FilterError
from ..data.transform_lang import TransformError
from ..logging import Recorder, frame_hash, viewer_state_snapshot
from ..sheets.file_browser_sheet import FileDeletionResult

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from ..api.session import Session

from . import modals as tui_modals
from .completions import ColumnNameCompleter, FilesystemPathCompleter
from .controllers.column_insight import ColumnInsightController
from .controllers.dataset_reload import DatasetReloadController
from .controllers.file_browser import (
    FileBrowserController,
    FileBrowserTransition,
)
from .controllers.file_ops import FileOpsController
from .controllers.file_watch import FileSnapshot, FileWatchController
from .job_pump import JobPump
from .keymap import build_key_bindings
from .modal_manager import ModalManager
from .presenters import StatusPresenter
from .screen_layout import build_screen_layout
from .ui_hooks import PromptToolkitViewerUIHooks

# Constants
_STACK_MIN_SIZE = 2  # Minimum stack size for frequency view filters
_HISTORY_MAX_SIZE = 20  # Maximum size for search/filter history
_CELL_MODAL_CHROME_HEIGHT = 8  # Non-text area rows needed by the cell modal
_INSIGHT_MIN_COLS_DEFAULT = 120  # Hide insight by default when terminal narrower than this


def _format_expr_filters_for_modal(filter_clauses: Sequence[object]) -> str:
    """Return a joined expression filter string for the expression modal."""

    expr_texts: list[str] = []
    for clause in filter_clauses:
        kind = getattr(clause, "kind", None)
        text = getattr(clause, "text", None)
        if kind != "expr" or not text:
            continue
        expr_texts.append(text.strip())

    if not expr_texts:
        return ""

    wrapped = [f"({text})" for text in expr_texts]
    return " & ".join(wrapped)


def _ordered_freq_values(freq_viewer: Viewer, selected_ids: set[object]) -> list[object]:
    """Return selected frequency values ordered by current display rows."""

    if not selected_ids:
        return []

    freq_column = getattr(freq_viewer, "freq_source_col", None)
    if not freq_column:
        freq_column = freq_viewer.columns[0] if freq_viewer.columns else None

    ordered: list[object] = []
    display_df = getattr(getattr(freq_viewer, "sheet", None), "_display_df", None)
    if display_df is not None and freq_column in getattr(display_df, "columns", ()):
        with suppress(Exception):
            for value in display_df.get_column(freq_column).to_list():
                if value in selected_ids and value not in ordered:
                    ordered.append(value)

    for value in selected_ids:
        if value not in ordered:
            ordered.append(value)

    return ordered


@dataclass
class _ColumnSearchState:
    """Mutable state tracked while the column search feature is active."""

    query: str | None = None
    matches: list[int] = field(default_factory=list)
    position: int | None = None

    def clear(self) -> None:
        """Reset the stored query and matches."""

        self.query = None
        self.matches.clear()
        self.position = None

    def set(self, query: str, matches: list[int], *, current_col: int) -> None:
        """Store a fresh query and its matches."""

        self.query = query
        self._apply_matches(matches, current_col=current_col, preserve_position=False)

    def recompute(self, matches: list[int], *, current_col: int) -> None:
        """Refresh matches for an existing query while keeping position when possible."""

        self._apply_matches(matches, current_col=current_col, preserve_position=True)

    def _apply_matches(
        self, matches: list[int], *, current_col: int, preserve_position: bool
    ) -> None:
        previous_position = self.position if preserve_position else None
        self.matches = list(matches)
        if not self.matches:
            self.position = None
            return

        if current_col in self.matches:
            self.position = self.matches.index(current_col)
        elif previous_position is not None and previous_position < len(self.matches):
            self.position = previous_position
        else:
            self.position = 0


class Screen:
    def __init__(
        self,
        viewer: Viewer,
        recorder: Recorder | None = None,
        *,
        on_shutdown: Callable[[Session], None] | None = None,
    ):
        self.viewer = viewer
        self.session = viewer.session
        if self.session is None:
            raise RuntimeError("Screen requires a session-bound viewer")
        self._on_shutdown = on_shutdown
        self.commands = self.session.commands
        self._runtime = self.session.command_runtime
        self._recorder = recorder or self.session.recorder
        self._runtime.prepare_viewer(self.viewer)
        self.view_stack = self.session.view_stack
        self._insight_controller: ColumnInsightController | None = None
        self._insight_base_default = self._initial_insight_enabled()
        initial_insight_state = resolve_insight_state(
            self.viewer, fallback_enabled=self._insight_base_default
        )
        self._insight_enabled = initial_insight_state.enabled
        self._insight_user_enabled = initial_insight_state.user_enabled
        self._insight_allowed = initial_insight_state.allowed
        self._jobs: dict[Viewer, object] = {}  # Jobs for background processing
        self._job_pump = JobPump(
            jobs=self._jobs,
            check_dataset_file_changes=self._check_dataset_file_changes,
            check_file_browser_changes=self._check_file_browser_changes,
        )
        self._file_browser_controller = FileBrowserController(
            session=self.session, get_viewer=lambda: self.viewer
        )
        self._file_watch: FileWatchController | None = None
        self._view_stack_unsubscribe = self.view_stack.add_active_viewer_listener(
            self._on_active_viewer_changed
        )
        # Use a getter that applies queued moves per frame (capped)
        self._pending_row_delta = 0
        self._pending_col_delta = 0
        # Allow tuning via env; default to 3 steps/frame
        try:
            from ..utils import _get_int_env

            self._max_steps_per_frame = max(
                1, _get_int_env("PULKA_MAX_STEPS_PER_FRAME", "PD_MAX_STEPS_PER_FRAME", 3)
            )
        except Exception:
            self._max_steps_per_frame = 3
        self._base_max_steps_per_frame = self._max_steps_per_frame
        use_ptk_table = self._should_use_ptk_table()
        self._last_status_fragments: StyleAndTextTuples | None = None
        self._last_status_plain: str | None = None
        layout_parts = build_screen_layout(
            viewer=self.viewer,
            use_ptk_table=use_ptk_table,
            build_ptk_table_control=self._build_table_control,
            get_table_text=self._get_table_text,
            get_status_text=self._get_status_text,
            insight_enabled=lambda: self._insight_enabled,
            insight_allowed=lambda: self._insight_allowed,
        )
        self._use_ptk_table = layout_parts.use_ptk_table
        self._table_control = layout_parts.table_control
        self._status_control = layout_parts.status_control
        self._table_window = layout_parts.table_window
        self._status_window = layout_parts.status_window
        self._insight_panel = layout_parts.insight_panel
        self._insight_control = layout_parts.insight_control
        self._insight_window = layout_parts.insight_window
        self._insight_border = layout_parts.insight_border
        self._insight_border_padding = layout_parts.insight_border_padding
        self._insight_container = layout_parts.insight_container
        self.window = layout_parts.window
        self._modal_manager = ModalManager(window=self.window, table_window=self._table_window)
        self._presenter = StatusPresenter(
            get_viewer=lambda: self.viewer,
            refresh=self.refresh,
            modals=self._modal_manager,
            get_app=lambda: self.app,
        )
        self._file_ops = FileOpsController(
            file_browser=self._file_browser_controller,
            presenter=self._presenter,
            get_viewer=lambda: self.viewer,
            refresh=self.refresh,
            handle_file_browser_refresh=self._handle_file_browser_refresh,
            invalidate=self._invalidate_app,
        )
        self._dataset_reload = DatasetReloadController(
            session=self.session,
            get_viewer=lambda: self.viewer,
            get_file_watch=lambda: self._file_watch,
            refresh=self.refresh,
            recorder_getter=lambda: getattr(self, "_recorder", None),
            open_reload_error_modal=lambda error_text: self._open_reload_error_modal(
                error_text=error_text
            ),
        )
        self._search_history: list[str] = []
        self._row_search_history: list[str] = []
        self._expr_filter_history: list[str] = []
        self._sql_filter_history: list[str] = []
        self._transform_history: list[str] = []
        self._command_history: list[str] = []
        self._command_history.append("write output.parquet")
        self._col_search_history: list[str] = []
        self._col_search_state = _ColumnSearchState()

        kb = build_key_bindings(self)

        self.app = Application(
            layout=Layout(self.window, focused_element=self._table_window),
            key_bindings=kb,
            full_screen=True,
            mouse_support=self._use_ptk_table,
            style=theme.APP_STYLE,
        )

        self._viewer_ui_hooks = PromptToolkitViewerUIHooks(self.app)
        attach_hooks = getattr(self._table_control, "attach_ui_hooks", None)
        if callable(attach_hooks):
            hooks = attach_hooks(self._viewer_ui_hooks)
            if hooks is not None:
                self._viewer_ui_hooks = hooks
        self.session.set_viewer_ui_hooks(self._viewer_ui_hooks)
        self._file_watch = FileWatchController(
            dataset_path_getter=lambda: getattr(self.session, "dataset_path", None),
            viewer_getter=lambda: self.viewer,
            hooks_getter=lambda: getattr(self, "_viewer_ui_hooks", None),
            on_dataset_change=lambda path, snapshot: self._schedule_file_change_prompt(
                path, snapshot
            ),
            on_file_browser_refresh=lambda sheet: self._handle_file_browser_refresh(sheet),
            on_file_browser_error=lambda exc: self._handle_file_browser_error(exc),
        )

        self._insight_controller = ColumnInsightController(
            viewer=self.viewer,
            panel=self._insight_panel,
            recorder=self._recorder,
            invalidate=self.app.invalidate,
            call_soon=self._viewer_ui_hooks.call_soon,
        )
        self._apply_insight_state(refresh=True)
        self._file_watch.sync(force=True)
        self._file_watch.check(force=True)

    def _should_use_ptk_table(self) -> bool:
        return use_prompt_toolkit_table()

    def _initial_insight_enabled(self) -> bool:
        env_value = os.getenv("PULKA_INSIGHT_PANEL")
        if env_value is None:
            try:
                from shutil import get_terminal_size

                cols = get_terminal_size(fallback=(0, 0)).columns
            except Exception:
                cols = 0
            if cols:
                return cols >= _INSIGHT_MIN_COLS_DEFAULT
            return True
        normalized = env_value.strip().lower()
        if normalized in {"0", "false", "off", "no"}:
            return False
        if normalized in {"1", "true", "on", "yes"}:
            return True
        return True

    def _apply_budget_plan(self, plan) -> None:
        multiplier = float(getattr(plan, "coalesce_multiplier", 1.0) or 1.0)
        base = getattr(self, "_base_max_steps_per_frame", self._max_steps_per_frame)
        if multiplier > 1.0:
            boosted = max(base, int(round(base * multiplier)))
            self._max_steps_per_frame = max(base, min(12, boosted))
        else:
            self._max_steps_per_frame = base

    def _build_table_control(self):
        from .controls.table_control import TableControl

        return TableControl(
            self.viewer,
            apply_pending_moves=self._apply_pending_moves,
            poll_background_jobs=self._poll_background_jobs,
            set_status=self._set_status_from_table,
            apply_budget_plan=self._apply_budget_plan,
            recorder=self._recorder,
        )

    def _clear_g_buf(self) -> None:
        """Reset the pending g-command state."""
        if hasattr(self, "_g_buf"):
            self._g_buf = 0

    def _on_active_viewer_changed(self, viewer: Viewer) -> None:
        previous = getattr(self, "viewer", None)
        self.viewer = viewer
        self._runtime.prepare_viewer(viewer)
        controller = getattr(self, "_file_browser_controller", None)
        if controller is not None:
            with suppress(Exception):
                controller.on_viewer_changed(viewer)
        table_control = getattr(self, "_table_control", None)
        update_viewer = getattr(table_control, "update_viewer", None)
        if callable(update_viewer):
            update_viewer(viewer)
        if previous is not None and previous is not viewer:
            self._clear_column_search()
        controller = getattr(self, "_insight_controller", None)
        if controller is not None:
            controller.on_viewer_changed(viewer)
        fallback_enabled = getattr(self, "_insight_enabled", self._insight_base_default)
        insight_state = resolve_insight_state(viewer, fallback_enabled=fallback_enabled)
        allowed_changed = insight_state.allowed != self._insight_allowed
        enabled_changed = insight_state.enabled != self._insight_enabled
        self._insight_enabled = insight_state.enabled
        self._insight_user_enabled = insight_state.user_enabled
        self._insight_allowed = insight_state.allowed
        if allowed_changed or enabled_changed or insight_state.effective:
            self._apply_insight_state(refresh=insight_state.effective)
        self._prune_stale_jobs()
        file_watch = getattr(self, "_file_watch", None)
        if file_watch is not None:
            file_watch.sync(force=True)

    def _prune_stale_jobs(self) -> None:
        active = set(self.view_stack.viewers)
        for stale_viewer, job in list(self._jobs.items()):
            if stale_viewer not in active:
                if job is not None and hasattr(job, "cancel"):
                    with suppress(Exception):
                        job.cancel()
                self._jobs.pop(stale_viewer, None)

    def _mutate_context(self, context: CommandContext) -> None:
        context.screen = self

    def _finalise_runtime_result(
        self, result: CommandRuntimeResult
    ) -> CommandDispatchResult | None:
        if result.message:
            self.viewer.status_message = result.message
        dispatch = result.dispatch
        if dispatch and dispatch.spec.name == "search":
            self._clear_column_search()
        return dispatch

    def _execute_command(
        self, name: str, args: list[str] | None = None, *, repeat: int = 1
    ) -> CommandDispatchResult | None:
        """Execute a command through the session command runtime."""

        invocation_args = list(args or [])
        result = self._runtime.invoke(
            name,
            args=invocation_args,
            repeat=repeat,
            source="tui",
            context_mutator=self._mutate_context,
        )
        self._apply_insight_state(refresh=self._insight_enabled)
        return self._finalise_runtime_result(result)

    def _queue_move(self, dr: int = 0, dc: int = 0) -> None:
        # Accumulate deltas; they'll be applied (capped) during next paint
        if dr != 0:
            self._pending_row_delta += 1 if dr > 0 else -1
            # prevent runaway accumulation
            self._pending_row_delta = max(-100, min(100, self._pending_row_delta))
        if dc != 0:
            self._pending_col_delta += 1 if dc > 0 else -1
            self._pending_col_delta = max(-100, min(100, self._pending_col_delta))

    def _record_key_event(self, event) -> None:
        # Record with structured recorder if available
        if self._recorder and self._recorder.enabled:
            try:
                sequence = [kp.key for kp in event.key_sequence]
                data = [kp.data for kp in event.key_sequence]
            except Exception:
                sequence = []
                data = []
            payload = {"sequence": sequence, "data": data}
            payload["repeat"] = bool(getattr(event, "is_repeat", False))
            self._recorder.record("key", payload)

    def _toggle_recorder(self, event) -> None:
        """Toggle the structured recorder on/off from the TUI."""
        recorder = self._recorder
        if recorder is None:
            self.viewer.status_message = "recorder unavailable"
            self.refresh()
            return

        self._record_key_event(event)

        try:
            user_command = event.key_sequence[0].key if event.key_sequence else "@"
        except Exception:
            user_command = "@"

        if recorder.enabled:
            recorder.record(
                "control", {"action": "record_off", "source": "tui", "key": user_command}
            )
            path = recorder.flush_and_clear(reason="tui-toggle")
            recorder.disable()
            if path is not None:
                copied = self._copy_path_to_clipboard(path)
                if copied:
                    self.viewer.status_message = (
                        f"flight recorder stopped - {path.name} (path copied to clipboard)"
                    )
                else:
                    self.viewer.status_message = f"flight recorder stopped - saved to {path.name}"
            else:
                self.viewer.status_message = "flight recorder disabled"
            self.refresh()
            return

        recorder.enable()
        recorder.ensure_env_recorded()
        source_path = getattr(self.viewer, "_source_path", None)
        schema = getattr(self.viewer.sheet, "schema", {})
        if source_path is not None:
            recorder.record_dataset_open(path=source_path, schema=schema, lazy=True)
        recorder.record("control", {"action": "record_on", "source": "tui", "key": user_command})
        self.viewer.status_message = "flight recorder started"
        self.refresh()

    def _handle_file_browser_enter(self) -> bool:
        sheet = getattr(self.viewer, "sheet", None)
        if not getattr(sheet, "is_file_browser", False):
            return False
        controller = self._file_browser_controller
        result: FileBrowserTransition | None = None
        with suppress(Exception):
            result = controller.enter_current()
        if result is None:
            return False
        if result.status:
            self.viewer.status_message = result.status
        if result.sheet_changed:
            self._after_file_browser_directory_change()
        if result.opened_dataset:
            self._file_watch.sync(force=True)
        self.refresh()
        return True

    def _after_file_browser_directory_change(self) -> None:
        self._file_watch.sync_file_browser(force=True)
        self._apply_insight_state(refresh=True)
        with suppress(Exception):
            self.viewer.row_count_tracker.ensure_total_rows()

    def _path_completion_base_dir(self) -> Path:
        sheet = getattr(self.viewer, "sheet", None)
        directory = getattr(sheet, "directory", None) if sheet is not None else None
        if directory:
            with suppress(Exception):
                return Path(directory)
        command_cwd = getattr(self.session, "command_cwd", None)
        if command_cwd:
            with suppress(Exception):
                return Path(command_cwd)
        dataset_path = getattr(self.session, "dataset_path", None)
        if dataset_path:
            with suppress(Exception):
                ds_path = Path(dataset_path)
                return ds_path if ds_path.is_dir() else ds_path.parent
        return Path.cwd()

    def _open_file_from_browser(self, target: Path) -> None:
        try:
            self.session.open_dataset_viewer(target, base_viewer=self.viewer)
        except Exception as exc:
            self.viewer.status_message = f"open failed: {exc}"
            self.refresh()
            return
        self.viewer.status_message = f"opened {target.name or target}"
        self._file_watch.sync(force=True)
        self.refresh()

    def _file_browser_delete_targets(self, sheet) -> list[object]:
        viewer = getattr(self, "viewer", None)
        if viewer is None:
            return []
        controller = self._file_browser_controller
        targets, status = controller.resolve_entries(deletable=True, viewer=viewer)
        if status:
            viewer.status_message = status
        if targets:
            return targets
        self.refresh()
        return []

    def _file_browser_entries(self, sheet) -> list[object]:
        viewer = getattr(self, "viewer", None)
        if viewer is None:
            return []
        controller = self._file_browser_controller
        targets, status = controller.resolve_entries(viewer=viewer)
        if status:
            viewer.status_message = status
        if targets:
            return targets
        self.refresh()
        return []

    def _open_file_delete_modal(self, event) -> None:
        viewer = getattr(self, "viewer", None)
        sheet = getattr(viewer, "sheet", None)
        if viewer is None or sheet is None or not getattr(sheet, "is_file_browser", False):
            return

        targets = self._file_browser_delete_targets(sheet)
        if not targets:
            return

        count = len(targets)
        title = "Delete item" if count == 1 else "Delete items"
        name = targets[0].path.name if count == 1 else None
        has_dir = any(getattr(entry, "is_dir", False) for entry in targets)

        try:
            file_count, impact_errors = sheet.deletion_impact(targets)
        except Exception:
            file_count, impact_errors = 0, []

        message_lines = []
        if count == 1:
            if has_dir:
                message_lines.append(f"Delete folder {name or 'item'} and its contents?")
            else:
                message_lines.append(f"Delete {name or 'file'}?")
        else:
            kind = "items" if has_dir else "files"
            message_lines.append(f"Delete all {count} selected {kind}?")

        suffix = "" if file_count == 1 else "s"
        recurse_note = " recursively" if has_dir else ""
        message_lines.append(f"This will delete {file_count} file{suffix}{recurse_note}.")
        if impact_errors:
            path, err = impact_errors[0]
            message_lines.append(f"Count may be incomplete ({path}: {err})")

        body = tui_modals.build_lines_body(message_lines)
        app = event.app

        def _resolve(confirmed: bool) -> None:
            self._remove_modal(app)
            if confirmed:
                self._delete_file_browser_entries(sheet, targets)

        yes_button = Button(text="Yes", handler=lambda: _resolve(True))
        cancel_button = Button(text="Cancel", handler=lambda: _resolve(False))

        dialog = Dialog(
            title=title,
            body=body,
            buttons=[yes_button, cancel_button],
        )
        self._display_modal(
            app,
            dialog,
            focus=yes_button,
            context_type="file_delete",
            payload={"count": count},
            width=60,
        )

    def _delete_file_browser_entries(self, sheet, entries: Sequence[object]) -> None:
        viewer = getattr(self, "viewer", None)
        if viewer is None:
            return

        try:
            result: FileDeletionResult = self._file_browser_controller.delete_entries(
                sheet, entries
            )
        except Exception as exc:
            viewer.status_message = f"delete failed: {exc}"
            self.refresh()
            return

        with suppress(Exception):
            viewer.clear_row_selection()

        message = "No items deleted"
        if result.deleted:
            if len(result.deleted) == 1:
                target = result.deleted[0]
                message = f"Deleted {target.name or target}"
            else:
                message = f"Deleted {len(result.deleted)} items"

        if result.errors:
            path, error = result.errors[0]
            prefix = f"{message}; " if result.deleted else "Delete failed: "
            message = f"{prefix}{path.name}: {error}"

        if result.changed or result.errors:
            self._handle_file_browser_refresh(sheet)

        viewer.status_message = message[:120]
        self.refresh()

    def _open_confirmation_modal(
        self,
        *,
        title: str,
        message_lines: Sequence[str],
        on_confirm: Callable[[], None],
        context_type: str | None = None,
        payload: dict[str, object] | None = None,
    ) -> None:
        self._presenter.open_confirmation_modal(
            title=title,
            message_lines=message_lines,
            on_confirm=on_confirm,
            context_type=context_type,
            payload=payload,
        )

    def _open_simple_status_modal(self, title: str, lines: Sequence[str]) -> None:
        self._presenter.open_status_modal(title=title, lines=lines)

    def _request_file_transfer(self, operation: str, dest: str) -> None:
        self._file_ops.request_transfer(operation, dest)

    def _request_file_rename(self, new_name: str) -> None:
        self._file_ops.request_rename(new_name)

    def _request_file_mkdir(self, path: str) -> None:
        self._file_ops.request_mkdir(path)

    def _perform_file_transfer(
        self, operation: str, targets: list[tuple[Path, Path]], *, allow_overwrite: bool = False
    ) -> None:
        self._file_ops.perform_transfer(operation, targets, allow_overwrite=allow_overwrite)

    def _reload_dataset(self) -> None:
        """Reload the currently open dataset if it originated from a path."""

        self._dataset_reload.reload_dataset()

    @staticmethod
    def _is_missing_error(exc: Exception) -> bool:
        return DatasetReloadController.is_missing_error(exc)

    def _handle_missing_dataset(self, dataset_path: Path) -> None:
        """Switch to file browser when the backing file disappears."""

        self._dataset_reload.handle_missing_dataset(dataset_path)

    def _handle_reload_error(self, exc: Exception, dataset_path: Path) -> None:
        self._dataset_reload.handle_reload_error(exc, dataset_path)

    def _apply_insight_state(self, *, refresh: bool = False) -> None:
        controller = getattr(self, "_insight_controller", None)
        viewer = getattr(self, "viewer", None)
        if viewer is not None:
            insight_state = set_insight_state(
                viewer,
                enabled=self._insight_enabled,
                user_enabled=self._insight_user_enabled,
            )
            self._insight_enabled = insight_state.enabled
            self._insight_user_enabled = insight_state.user_enabled
            self._insight_allowed = insight_state.allowed
        effective = self._insight_enabled and self._insight_allowed
        with suppress(Exception):
            self._update_viewer_metrics()
        if controller is not None:
            controller.set_enabled(effective)
            if effective and refresh:
                with suppress(Exception):
                    controller.on_refresh()
        if not effective and not self._insight_allowed:
            self._insight_panel.set_unavailable("Insight unavailable for this view.")
        app = getattr(self, "app", None)
        if app is not None:
            app.invalidate()

    def set_insight_panel(self, enabled: bool | None = None) -> bool:
        """Toggle or explicitly set the insight sidecar visibility."""

        if enabled is None:
            enabled = not self._insight_enabled
        self._insight_enabled = bool(enabled)
        self._insight_user_enabled = True
        self._apply_insight_state(refresh=self._insight_enabled)
        return self._insight_enabled

    @staticmethod
    def _copy_path_to_clipboard(path: Path) -> bool:
        """Attempt to copy the given path to the system clipboard."""
        return copy_to_clipboard(str(path))

    def _apply_pending_moves(self) -> None:
        # Apply up to N moves per axis this frame, for smoother scrolling
        steps = min(self._max_steps_per_frame, abs(self._pending_row_delta))
        if steps:
            if self._pending_row_delta > 0:
                for _ in range(steps):
                    self.viewer.move_down()
                self._pending_row_delta -= steps
            else:
                for _ in range(steps):
                    self.viewer.move_up()
                self._pending_row_delta += steps
        steps = min(self._max_steps_per_frame, abs(self._pending_col_delta))
        if steps:
            if self._pending_col_delta > 0:
                for _ in range(steps):
                    self.viewer.move_right()
                self._pending_col_delta -= steps
            else:
                for _ in range(steps):
                    self.viewer.move_left()
                self._pending_col_delta += steps

    def _get_table_text(self):
        # Coalesce rapid key repeats by applying pending deltas here
        self._apply_pending_moves()
        self._poll_background_jobs()
        # Import the render table function here to avoid circular imports
        from ..render.table import render_table

        recorder = self._recorder if getattr(self, "_recorder", None) else None
        if recorder and recorder.enabled:
            with recorder.perf_timer(
                "render.table",
                payload={"context": "tui", "trigger": "refresh"},
            ):
                body = render_table(self.viewer)
        else:
            body = render_table(self.viewer)

        # Precompute status text so the footer stays in sync with the latest render
        from ..render.status_bar import render_status_line

        status_fragments: StyleAndTextTuples = []
        if recorder and recorder.enabled:
            with recorder.perf_timer(
                "render.status",
                payload={"context": "tui", "trigger": "refresh"},
            ):
                status_fragments = render_status_line(self.viewer)
        else:
            status_fragments = render_status_line(self.viewer)
        self._set_status_from_table(status_fragments)
        self.viewer.acknowledge_status_rendered()
        status_text = self._last_status_plain or ""
        if self._recorder and self._recorder.enabled:
            state_snapshot = viewer_state_snapshot(self.viewer)
            self._recorder.record_state(state_snapshot)
            if status_text:
                self._recorder.record_status(status_text)
            frame_capture = f"{body}\n{status_text}" if status_text else body
            if self._insight_enabled and self._insight_allowed:
                panel_block = self._insight_panel.render_for_recorder()
                if panel_block:
                    frame_capture = f"{frame_capture}\n\n{panel_block}"
            self._recorder.record_frame(
                frame_text=frame_capture,
                frame_hash=frame_hash(frame_capture),
            )
        return ANSI(body).__pt_formatted_text__()

    def _get_status_text(self):
        viewer = self.viewer
        status_dirty = bool(viewer.is_status_dirty())
        if status_dirty:
            # Import lazily to avoid circular dependency at module import time
            from ..render.status_bar import render_status_line

            self._set_status_from_table(render_status_line(viewer))
            viewer.acknowledge_status_rendered()
        elif self._last_status_fragments is None:
            from ..render.status_bar import render_status_line

            self._set_status_from_table(render_status_line(viewer))
            viewer.acknowledge_status_rendered()
        return self._last_status_fragments or [("", "")]

    def _set_status_from_table(self, fragments: StyleAndTextTuples) -> None:
        stored = list(fragments)
        self._last_status_fragments = stored
        self._last_status_plain = "".join(part for _, part in stored)

    def _insight_sidecar_width(self) -> int:
        if not (self._insight_enabled and self._insight_allowed):
            return 0
        # Insight column, plus border and padding containers.
        return self._insight_panel.width + 2

    def _update_viewer_metrics(self) -> None:
        hooks = getattr(self, "_viewer_ui_hooks", None)
        cols, _rows = NullViewerUIHooks().get_terminal_size((100, 30))
        if hooks is not None:
            with suppress(Exception):
                cols, _rows = hooks.get_terminal_size((cols, _rows))
        insight_width = self._insight_sidecar_width()
        if insight_width:
            width_override = max(20, cols - insight_width)
            self.viewer.set_view_width_override(width_override)
        else:
            self.viewer.set_view_width_override(None)
        self.viewer.update_terminal_metrics()

    def _pop_viewer(self) -> None:
        removed = self.view_stack.pop()
        if removed is None:
            return
        job = self._jobs.pop(removed, None)
        if job is not None and hasattr(job, "cancel"):
            with suppress(Exception):
                job.cancel()

    def refresh(self, *, skip_metrics: bool = False):
        if not skip_metrics:
            self._update_viewer_metrics()
        self.viewer.clamp()
        self._check_dataset_file_changes(force=True)
        self._check_file_browser_changes(force=True)
        controller = getattr(self, "_insight_controller", None)
        if controller is not None:
            if self._file_watch.dataset_prompt_active:
                self._insight_panel.set_unavailable("File changed; reload to resume insight.")
            else:
                controller.on_refresh()
        with suppress(Exception):
            self._viewer_ui_hooks.invalidate()

    def _invalidate_app(self) -> None:
        hooks = getattr(self, "_viewer_ui_hooks", None)
        if hooks is not None:
            with suppress(Exception):
                hooks.invalidate()
            return
        with suppress(Exception):
            self.app.invalidate()

    def _poll_background_jobs(self) -> None:
        self._job_pump.poll()

    def _handle_file_browser_refresh(self, sheet) -> None:
        viewer = getattr(self, "viewer", None)
        if viewer is None or viewer.sheet is not sheet:
            return
        self._file_browser_controller.refresh_sheet(sheet, viewer)
        hooks = getattr(self, "_viewer_ui_hooks", None)
        if hooks is not None:
            with suppress(Exception):
                hooks.invalidate()
        else:
            self.app.invalidate()

    def _handle_file_browser_error(self, exc: Exception) -> None:
        viewer = getattr(self, "viewer", None)
        if viewer is not None:
            viewer.status_message = f"dir refresh failed: {exc}"
        hooks = getattr(self, "_viewer_ui_hooks", None)
        if hooks is not None:
            with suppress(Exception):
                hooks.invalidate()
        else:
            self.app.invalidate()

    def _check_dataset_file_changes(self, *, force: bool = False) -> None:
        if self._file_watch is None:
            return
        self._file_watch.check_dataset(force=force)

    def _check_file_browser_changes(self, *, force: bool = False) -> None:
        if self._file_watch is None:
            return
        self._file_watch.check_file_browser(force=force)

    @property
    def _file_watch_prompt_active(self) -> bool:
        return bool(self._file_watch and self._file_watch.dataset_prompt_active)

    @_file_watch_prompt_active.setter
    def _file_watch_prompt_active(self, active: bool) -> None:
        if self._file_watch is None:
            return
        if active:
            self._file_watch.set_dataset_prompt_active(True)
        else:
            self._file_watch.clear_dataset_prompt()

    def _schedule_file_change_prompt(
        self,
        path: Path,
        snapshot: FileSnapshot | None,
    ) -> None:
        def _open_prompt() -> None:
            self._open_dataset_file_change_modal(path=path, snapshot=snapshot)

        hooks = getattr(self, "_viewer_ui_hooks", None)
        if hooks is None:
            _open_prompt()
            return
        hooks.call_soon(_open_prompt)

    def _open_dataset_file_change_modal(
        self,
        *,
        path: Path,
        snapshot: FileSnapshot | None,
    ) -> None:
        if self._file_watch.dataset_path != path:
            self._file_watch.clear_dataset_prompt()
            return
        if snapshot is None:
            snapshot = FileSnapshot(
                mtime_ns=None,
                size=None,
                inode=None,
                missing=True,
                error=None,
            )
        if snapshot.missing:
            self._open_missing_dataset_modal(path=path, snapshot=snapshot)
            return
        message_lines = [
            f"{path} changed on disk while Pulka is running.",
        ]
        if snapshot.missing:
            missing_reason = snapshot.error or "The file may have been deleted or replaced."
            message_lines.append(missing_reason)
        else:
            message_lines.append("Reload to view the latest data or keep the current snapshot.")

        body = tui_modals.build_lines_body(message_lines)
        app = self.app

        def _resolve(reload_file: bool) -> None:
            self._remove_modal(app)
            self._complete_file_change_prompt(reload_file=reload_file)
            if not reload_file:
                self.refresh()

        reload_button = Button(text="Reload file", handler=lambda: _resolve(True))
        keep_button = Button(text="Keep current view", handler=lambda: _resolve(False))

        dialog = Dialog(
            title="File changed",
            body=body,
            buttons=[reload_button, keep_button],
        )
        self._display_modal(
            app,
            dialog,
            focus=reload_button,
            context_type="file_change",
            payload={"path": str(path)},
            width=80,
        )

    def _complete_file_change_prompt(self, *, reload_file: bool) -> None:
        self._file_watch.complete_dataset_prompt(refresh_snapshot=not reload_file)
        if reload_file:
            self._reload_dataset()
            return
        self.viewer.status_message = "file changed on disk (kept current view)"
        self._file_watch.sync_dataset(force=True)

    def run(self):
        try:
            self.app.run()
        finally:
            unsubscribe = getattr(self, "_view_stack_unsubscribe", None)
            if unsubscribe is not None:
                unsubscribe()
            self._file_watch.stop()
            session = self.session
            if session is not None and self._on_shutdown is not None:
                with suppress(Exception):
                    self._on_shutdown(session)
            if session is not None:
                with suppress(Exception):
                    session.close()
                recorder = getattr(session, "recorder", None)
                if recorder is not None and recorder.enabled:
                    with suppress(Exception):
                        recorder.on_process_exit(reason="tui")

    def _display_modal(
        self,
        app,
        container,
        *,
        focus=None,
        context_type: str | None = None,
        payload: dict[str, object] | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        self._modal_manager.display(
            app,
            container,
            focus=focus,
            context_type=context_type,
            payload=payload,
            width=width,
            height=height,
        )

    def _calculate_modal_dimensions(
        self,
        app,
        *,
        target_width: int,
        target_height: int,
    ) -> tuple[int, int]:
        """Determine modal dimensions respecting terminal size constraints."""

        return self._modal_manager.calculate_dimensions(
            app,
            target_width=target_width,
            target_height=target_height,
            chrome_height=_CELL_MODAL_CHROME_HEIGHT,
        )

    def _remove_modal(self, app, *, restore_focus: bool = True) -> None:
        self._modal_manager.remove(app, restore_focus=restore_focus)

    def _build_read_only_modal_dialog(
        self,
        *,
        app,
        title: str,
        text_area: TextArea,
    ) -> tuple[Dialog, Button]:
        """Create a dialog with a read-only text area and shared controls."""

        def _close_modal(target_app) -> None:
            self._remove_modal(target_app)
            self.refresh()

        tui_modals.bind_close_keys(text_area, on_close=_close_modal)

        body = Box(body=HSplit([text_area], padding=1), padding=1)

        ok_button = Button(text="OK", handler=lambda: _close_modal(app))

        dialog = Dialog(title=title, body=body, buttons=[ok_button])
        return dialog, ok_button

    def _open_missing_dataset_modal(
        self,
        *,
        path: Path,
        snapshot: FileSnapshot,
    ) -> None:
        app = self.app
        message_lines = [
            f"{path} is no longer available.",
        ]
        if snapshot.error:
            message_lines.append(snapshot.error)
        message_lines.append("You will be redirected to the file browser sheet.")

        body = tui_modals.build_lines_body(message_lines)

        def _confirm() -> None:
            self._remove_modal(app)
            self._handle_missing_dataset(path)

        ok_button = Button(text="OK", handler=_confirm)

        dialog = Dialog(
            title="File missing",
            body=body,
            buttons=[ok_button],
        )

        self._display_modal(
            app,
            dialog,
            focus=ok_button,
            context_type="missing_dataset",
            payload={"path": str(path)},
            width=80,
        )

    def _open_reload_error_modal(self, *, error_text: str) -> None:
        app = self.app
        target_width = 80
        target_height = 40
        width, height = self._calculate_modal_dimensions(
            app,
            target_width=target_width,
            target_height=target_height,
        )
        text_area_height = max(3, height - _CELL_MODAL_CHROME_HEIGHT)

        text_area = TextArea(
            text=error_text,
            read_only=True,
            scrollbar=True,
            wrap_lines=True,
            height=text_area_height,
        )

        def _close_modal(target_app) -> None:
            self._remove_modal(target_app)
            self.refresh()

        tui_modals.bind_close_keys(text_area, on_close=_close_modal)

        body = Box(body=HSplit([text_area], padding=1), padding=1)

        def _copy_error() -> None:
            copied = copy_to_clipboard(error_text)
            self.viewer.status_message = (
                "copied reload error to clipboard" if copied else "clipboard unavailable"
            )
            app.invalidate()

        copy_button = Button(text="Copy to clipboard", handler=_copy_error)
        close_button = Button(text="Close", handler=lambda: _close_modal(app))

        dialog = Dialog(
            title="Reload failed",
            body=body,
            buttons=[copy_button, close_button],
        )

        self._display_modal(
            app,
            dialog,
            focus=copy_button,
            context_type="reload_error",
            width=width,
            height=height,
        )

    def _open_cell_value_modal(self, event) -> None:
        """Open a modal showing details about the currently focused cell."""

        if not self.viewer.columns:
            return

        column_name = self.viewer.columns[self.viewer.cur_col]
        row_index = self.viewer.cur_row

        value = None
        value_error: str | None = None
        try:
            slice_ = self.viewer.sheet.fetch_slice(row_index, 1, [column_name])
            if isinstance(slice_, TableSlice):
                table_slice = slice_
            elif isinstance(slice_, pl.DataFrame):
                schema = getattr(self.viewer.sheet, "schema", {})
                table_slice = table_slice_from_dataframe(slice_, schema)
            else:
                table_slice = table_slice_from_dataframe(
                    pl.DataFrame(slice_), getattr(self.viewer.sheet, "schema", {})
                )

            if table_slice.height > 0 and column_name in table_slice.column_names:
                value = table_slice.column(column_name).values[0]
        except Exception as exc:  # pragma: no cover - defensive
            value_error = str(exc)

        target_width = 60
        target_height = 40
        width, height = self._calculate_modal_dimensions(
            event.app,
            target_width=target_width,
            target_height=target_height,
        )
        content_width = max(20, width - 6)

        console_buffer = StringIO()
        console = Console(
            record=True,
            width=content_width,
            highlight=False,
            file=console_buffer,
        )
        if value_error is not None:
            console.print(f"Error: {value_error}")
        else:
            console.print(Pretty(value, expand_all=True, overflow="fold"))

        rendered_text = console.export_text(clear=False)

        # Account for dialog chrome (label, padding, frame, and buttons) so the
        # text area fits within the requested height without triggering the
        # "window too small" warning from prompt_toolkit.
        text_area_height = max(3, height - _CELL_MODAL_CHROME_HEIGHT)

        text_area = TextArea(
            text=rendered_text,
            read_only=True,
            scrollbar=True,
            wrap_lines=True,
            height=text_area_height,
        )

        dialog, ok_button = self._build_read_only_modal_dialog(
            app=event.app,
            title=f"Cell {column_name} @ row {row_index + 1}",
            text_area=text_area,
        )

        self._display_modal(
            event.app,
            dialog,
            focus=ok_button,
            context_type="cell_value",
            payload={"column": column_name, "row": row_index},
            width=width,
            height=height,
        )

    def _apply_summary_selection(self) -> bool:
        """Hide non-selected columns on the parent view based on summary picks."""

        if len(self.view_stack) < _STACK_MIN_SIZE:
            return False

        summary_viewer = self.viewer
        source_viewer = self.view_stack.parent
        if source_viewer is None:
            return False

        try:
            from pulka_builtin_plugins.summary.plugin import SummarySheet
        except Exception:
            return False

        if not isinstance(getattr(summary_viewer, "sheet", None), SummarySheet):
            return False

        selected_ids = set(getattr(summary_viewer, "_selected_row_ids", set()))
        selected_names: list[str] = []

        if selected_ids:
            for row_id in selected_ids:
                if isinstance(row_id, str):
                    selected_names.append(row_id)
                    continue
                try:
                    name = summary_viewer.sheet.get_value_at(int(row_id), "column")
                except Exception:
                    continue
                if isinstance(name, str):
                    selected_names.append(name)

        if not selected_names:
            try:
                current = summary_viewer.sheet.get_value_at(summary_viewer.cur_row, "column")
            except Exception:
                current = None
            if isinstance(current, str):
                selected_names.append(current)

        selected_lookup = {name for name in selected_names if isinstance(name, str)}
        if not selected_lookup:
            summary_viewer.status_message = "select at least one column"
            return True

        ordered_columns = [name for name in source_viewer.columns if name in selected_lookup]
        if not ordered_columns:
            summary_viewer.status_message = "no matching columns to keep"
            return True

        try:
            source_viewer.keep_columns(ordered_columns)
        except Exception as exc:  # pragma: no cover - defensive
            summary_viewer.status_message = f"keep columns error: {exc}"[:120]
            return True

        with suppress(Exception):
            summary_viewer.clear_row_selection()
        self._pop_viewer()
        self.refresh()
        return True

    def _filter_by_pick(self) -> None:
        """Apply filter based on the currently selected value in a frequency view."""
        # Get the frequency viewer (current view) and the source viewer (parent)
        if len(self.view_stack) < _STACK_MIN_SIZE:
            return

        freq_viewer = self.viewer
        source_viewer = self.view_stack.parent
        if source_viewer is None:
            return

        # Ensure we're in a frequency view
        if not hasattr(freq_viewer, "is_freq_view") or not getattr(
            freq_viewer, "is_freq_view", False
        ):
            return

        selected_ids = set(getattr(freq_viewer, "_selected_row_ids", set()))
        values: list[object] = []
        if selected_ids:
            values = _ordered_freq_values(freq_viewer, selected_ids)
        if not values:
            try:
                values = [freq_viewer.sheet.get_value_at(freq_viewer.cur_row)]
            except Exception:
                self.viewer.status_message = "unable to pick value"
                return

        # Apply the filter to the source view
        try:
            # Build filter expression for the source column
            source_col = freq_viewer.freq_source_col
            if source_col is None:
                self.viewer.status_message = "unknown frequency source"
                return
            filter_expr = build_filter_expr_for_values(source_col, values)

            result = self._runtime.invoke(
                "filter",
                args=[filter_expr, "append"],
                source="tui",
                viewer=source_viewer,
                context_mutator=self._mutate_context,
            )
        except Exception as exc:
            self.viewer.status_message = f"filter error: {exc}"
        else:
            if result.message:
                self.viewer.status_message = result.message
                return
            self.viewer.status_message = None
            with suppress(Exception):
                freq_viewer.clear_row_selection()
            self._pop_viewer()
            self.refresh()

    def _open_filter_modal(self, event, *, initial_text: str | None = None) -> None:
        # Implementation details omitted for brevity to focus on key logic
        title = "Expression Filter"
        prompt_text = "Polars expression (use c.<column>) - Enter: replace existing"
        current_expr_filter = ""
        with suppress(Exception):
            current_expr_filter = _format_expr_filters_for_modal(
                getattr(self.viewer, "filters", ())
            )
        default_text = initial_text or current_expr_filter or ""
        if not default_text:
            current_col = None
            with suppress(Exception):
                current_col = self.viewer.current_colname()
            if current_col:
                if current_col.isidentifier():
                    default_text = f"c.{current_col}"
                else:
                    safe_name = current_col.replace('"', '\\"')
                    default_text = f'c["{safe_name}"]'

        def accept(buff):
            raw_text = buff.text
            text = raw_text.strip()
            if text.lower() == "cancel":
                self.viewer.status_message = "filter canceled"
                self._remove_modal(event.app)
                self.refresh()
                return True

            try:
                args = [text] if text else []
                result = self._runtime.invoke(
                    "filter",
                    args=args,
                    source="tui",
                    context_mutator=self._mutate_context,
                    propagate=(FilterError,),
                )
            except FilterError as err:
                self._open_error_modal(
                    event,
                    "Filter Error",
                    str(err),
                    retry=lambda ev: self._open_filter_modal(ev, initial_text=raw_text),
                )
            except Exception as exc:
                self._open_error_modal(
                    event,
                    "Unexpected Error",
                    str(exc),
                    retry=lambda ev: self._open_filter_modal(ev, initial_text=raw_text),
                )
            else:
                dispatch = self._finalise_runtime_result(result)
                status_error = self._status_error_message(("filter error",))
                error_message = result.message or status_error
                if error_message:
                    self._open_error_modal(
                        event,
                        "Filter Error",
                        error_message,
                        retry=lambda ev: self._open_filter_modal(ev, initial_text=raw_text),
                    )
                    return True
                if dispatch is not None:
                    self._record_expr_filter(text)
                self.viewer.status_message = None
                self._remove_modal(event.app)
                self.refresh()
            return True

        filter_field = TextArea(
            text=default_text,
            multiline=True,
            height=4,
            accept_handler=accept,
            history=None,
            completer=ColumnNameCompleter(self.viewer.columns),
            complete_while_typing=True,
        )
        filter_field.buffer.cursor_position = len(default_text)

        tui_modals.bind_enter_to_accept(filter_field)
        body = tui_modals.build_prompt_body(prompt_text, filter_field)
        dialog = Dialog(title=title, body=body, buttons=[])
        self._display_modal(
            event.app,
            dialog,
            focus=filter_field,
            context_type="expr_filter",
            payload={"field": filter_field},
            width=80,
        )

    def _open_filter_modal_with_text(self, event, text: str) -> None:
        self._open_filter_modal(event, initial_text=text)

    def _open_transform_modal(self, event, *, initial_text: str | None = None) -> None:
        if self.viewer.plan_controller.current_plan() is None:
            self.viewer.status_message = "transform unsupported for this view"
            self.refresh()
            return
        title = "Transform"
        prompt_text = "Polars LazyFrame transform (lf -> LazyFrame) - Enter: derived view"
        history = InMemoryHistory()
        for item in self._transform_history:
            history.append_string(item)

        default_text = initial_text or "lf"
        if initial_text is None:
            current_col = None
            with suppress(Exception):
                current_col = self.viewer.current_colname()
            if current_col:
                if current_col.isidentifier():
                    default_text = f"lf.with_columns(c.{current_col})"
                else:
                    safe_name = current_col.replace('"', '\\"')
                    default_text = f'lf.with_columns(c["{safe_name}"])'

        def accept(buff):
            raw_text = buff.text
            text = raw_text.strip()
            if text.lower() == "cancel":
                self.viewer.status_message = "transform canceled"
                self._remove_modal(event.app)
                self.refresh()
                return True

            try:
                result = self._runtime.invoke(
                    "transform",
                    args=[text],
                    source="tui",
                    context_mutator=self._mutate_context,
                    propagate=(TransformError,),
                )
            except TransformError as err:
                self._open_error_modal(
                    event,
                    "Transform Error",
                    str(err),
                    retry=lambda ev: self._open_transform_modal(ev, initial_text=raw_text),
                )
            except Exception as exc:
                self._open_error_modal(
                    event,
                    "Unexpected Error",
                    str(exc),
                    retry=lambda ev: self._open_transform_modal(ev, initial_text=raw_text),
                )
            else:
                dispatch = self._finalise_runtime_result(result)
                error_message = result.message or self._status_error_message(("transform error",))
                if error_message:
                    self._open_error_modal(
                        event,
                        "Transform Error",
                        error_message,
                        retry=lambda ev: self._open_transform_modal(ev, initial_text=raw_text),
                    )
                    return True
                if dispatch is not None:
                    self._record_transform(text)
                self.viewer.status_message = None
                self._remove_modal(event.app)
                self.refresh()
            return True

        transform_field = TextArea(
            text=default_text,
            multiline=True,
            height=6,
            accept_handler=accept,
            history=history,
            completer=ColumnNameCompleter(self.viewer.columns),
            complete_while_typing=True,
        )
        transform_field.buffer.cursor_position = len(default_text)

        tui_modals.bind_enter_to_accept(transform_field)
        body = tui_modals.build_prompt_body(prompt_text, transform_field)
        dialog = Dialog(title=title, body=body, buttons=[])
        self._display_modal(
            event.app,
            dialog,
            focus=transform_field,
            context_type="transform",
            payload={"field": transform_field},
            width=90,
        )

    def _open_sql_filter_modal(self, event, *, initial_text: str | None = None) -> None:
        title = "SQL Filter"
        prompt_text = "Polars SQL WHERE clause (omit WHERE) - Enter: replace existing"
        current_sql_filter = ""
        with suppress(Exception):
            current_sql_filter = next(
                (
                    clause.text
                    for clause in getattr(self.viewer, "filters", ())
                    if clause.kind == "sql"
                ),
                "",
            )
        default_text = (
            initial_text or current_sql_filter or getattr(self.viewer, "sql_filter_text", "") or ""
        )
        if not default_text:
            current_col = None
            with suppress(Exception):
                current_col = self.viewer.current_colname()
            if current_col:
                if current_col.isidentifier():
                    default_text = current_col
                else:
                    default_text = ColumnNameCompleter._quote_identifier(current_col)

        def accept(buff):
            raw_text = buff.text
            text = raw_text.strip()
            if text.lower() == "cancel":
                self.viewer.status_message = "SQL filter canceled"
                self._remove_modal(event.app)
                self.refresh()
                return True

            args = [text] if text else []
            try:
                result = self._runtime.invoke(
                    "sql_filter",
                    args=args,
                    source="tui",
                    context_mutator=self._mutate_context,
                    propagate=(FilterError,),
                )
            except Exception as exc:
                self._open_error_modal(
                    event,
                    "SQL Filter Error",
                    str(exc),
                    retry=lambda ev: self._open_sql_filter_modal(ev, initial_text=raw_text),
                )
            else:
                dispatch = self._finalise_runtime_result(result)
                status_error = self._status_error_message(("sql filter error",))
                error_message = result.message or status_error
                if error_message:
                    self._open_error_modal(
                        event,
                        "SQL Filter Error",
                        error_message,
                        retry=lambda ev: self._open_sql_filter_modal(ev, initial_text=raw_text),
                    )
                    return True
                if text and dispatch is not None:
                    self._record_sql_filter(text)
                self.viewer.status_message = None
                self._remove_modal(event.app)
                self.refresh()
            return True

        filter_field = TextArea(
            text=default_text,
            multiline=True,
            height=4,
            accept_handler=accept,
            history=None,
            completer=ColumnNameCompleter(self.viewer.columns, mode="sql"),
            complete_while_typing=True,
        )
        filter_field.buffer.cursor_position = len(default_text)

        tui_modals.bind_enter_to_accept(filter_field)
        body = tui_modals.build_prompt_body(prompt_text, filter_field)
        dialog = Dialog(title=title, body=body, buttons=[])
        self._display_modal(
            event.app,
            dialog,
            focus=filter_field,
            context_type="sql_filter",
            payload={"field": filter_field},
            width=80,
        )

    def _open_sql_filter_modal_with_text(self, event, text: str) -> None:
        self._open_sql_filter_modal(event, initial_text=text)

    def _open_command_modal(self, event) -> None:
        history = InMemoryHistory()
        for item in self._command_history:
            history.append_string(item)

        def accept(buff):
            raw_text = buff.text
            command_text = raw_text.strip()

            if not command_text:
                self._remove_modal(event.app)
                self.refresh()
                return True

            lowered = command_text.split(None, 1)[0].lower()
            if lowered in {"transform", "xf"}:
                self.viewer.status_message = "transform is available via Shift+E modal"
                self._remove_modal(event.app)
                self.refresh()
                return True

            result = self._runtime.dispatch_raw(
                command_text,
                source="tui",
                context_mutator=self._mutate_context,
            )
            dispatch = self._finalise_runtime_result(result)
            if dispatch is not None:
                self._record_command(command_text)
            self._remove_modal(event.app)
            self.refresh()
            return True

        command_field = TextArea(
            text="",
            multiline=False,
            accept_handler=accept,
            history=history,
            completer=FilesystemPathCompleter(self._path_completion_base_dir),
            complete_while_typing=True,
        )
        command_field.buffer.cursor_position = 0

        examples = []
        for spec in self.commands.iter_specs():
            hints = spec.ui_hints or {}
            example = hints.get("example") if isinstance(hints, dict) else hints.get("example")
            if example:
                examples.append(str(example))
        unique_examples: list[str] = []
        for example in examples:
            if example not in unique_examples:
                unique_examples.append(example)
        prompt = (
            "Command:"
            if not unique_examples
            else f"Command (e.g. {', '.join(unique_examples[:3])}):"
        )

        body = tui_modals.build_prompt_body(prompt, command_field)
        dialog = Dialog(title="Command", body=body, buttons=[])
        self._display_modal(
            event.app,
            dialog,
            focus=command_field,
            context_type="command",
            payload={"field": command_field},
            width=60,
        )

    def _open_row_search_modal(self, event) -> None:
        def accept(buff):
            text = buff.text.strip()
            if not text:
                self._remove_modal(event.app)
                self.refresh()
                return True

            if text.lower() == "cancel":
                self.viewer.status_message = "row selection canceled"
                self._remove_modal(event.app)
                self.refresh()
                return True

            try:
                columns = ()
                try:
                    columns = (self.viewer.columns[self.viewer.cur_col],)
                except Exception:
                    columns = self.viewer.columns[:1]
                self.viewer.select_rows_containing(text, columns=columns)
                self._record_row_search(text)
            except Exception as exc:
                self.viewer.status_message = f"Row selection error: {exc}"
            self._remove_modal(event.app)
            self.refresh()
            return True

        history = InMemoryHistory()
        for item in self._row_search_history:
            history.append_string(item)

        search_field = TextArea(
            text="",
            multiline=False,
            accept_handler=accept,
            history=history,
        )
        search_field.buffer.cursor_position = 0

        body = tui_modals.build_prompt_body(
            "Substring (current column, case-insensitive):",
            search_field,
        )
        dialog = Dialog(title="Select Rows (current column)", body=body, buttons=[])
        self._display_modal(
            event.app,
            dialog,
            focus=search_field,
            context_type="row_search",
            payload={"field": search_field},
            width=60,
        )

    def _open_search_modal(self, event) -> None:
        def accept(buff):
            text = buff.text.strip()
            if text.lower() == "cancel":
                self.viewer.status_message = "search canceled"
                self._remove_modal(event.app)
                self.refresh()
                return True

            # Apply search to the viewer
            try:
                self.viewer.set_search(text)
                current = self.viewer.search_text
                self._clear_column_search()
                self._record_search(text)
                if current:
                    self.viewer.search(forward=True, include_current=True)
                self._remove_modal(event.app)
                self.refresh()
            except Exception as exc:
                self.viewer.status_message = f"Search error: {exc}"
            return True

        history = InMemoryHistory()
        for item in self._search_history:
            history.append_string(item)

        search_field = TextArea(
            text="",
            multiline=False,
            accept_handler=accept,
            history=history,
        )
        search_field.buffer.cursor_position = 0

        body = tui_modals.build_prompt_body(
            "Substring (current column, case-insensitive):",
            search_field,
        )
        dialog = Dialog(title="Search", body=body, buttons=[])
        self._display_modal(
            event.app,
            dialog,
            focus=search_field,
            context_type="search",
            payload={"field": search_field},
            width=60,
        )

    def _open_column_search_modal(self, event) -> None:
        """Open the column search modal with history and tab completion."""

        def accept(buff):
            raw_text = buff.text
            query = raw_text.strip()

            if not query or query.lower() == "cancel":
                self.viewer.status_message = "column search canceled"
                self._clear_column_search()
                self._remove_modal(event.app)
                self.refresh()
                return True

            self._remove_modal(event.app)
            success = self._apply_column_search(query)
            self._record_column_search(query)
            if not success:
                self._clear_column_search()
            self.refresh()
            return True

        history = InMemoryHistory()
        for item in self._col_search_history:
            history.append_string(item)

        search_field = TextArea(
            text="",
            multiline=False,
            accept_handler=accept,
            history=history,
            completer=ColumnNameCompleter(self.viewer.columns, mode="plain"),
            complete_while_typing=True,
        )
        search_field.buffer.cursor_position = 0

        body = tui_modals.build_prompt_body("Column name (prefix or substring):", search_field)
        dialog = Dialog(title="Column Search", body=body, buttons=[])
        self._display_modal(
            event.app,
            dialog,
            focus=search_field,
            context_type="column_search",
            payload={"field": search_field},
            width=60,
        )

    def _record_search(self, text: str) -> None:
        text = text.strip()
        if not text:
            return
        with suppress(ValueError):
            self._search_history.remove(text)
        self._search_history.append(text)
        if len(self._search_history) > _HISTORY_MAX_SIZE:
            del self._search_history[0]

    def _record_row_search(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        with suppress(ValueError):
            self._row_search_history.remove(cleaned)
        self._row_search_history.append(cleaned)
        if len(self._row_search_history) > _HISTORY_MAX_SIZE:
            del self._row_search_history[0]

    def _record_command(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        with suppress(ValueError):
            self._command_history.remove(cleaned)
        self._command_history.append(cleaned)
        if len(self._command_history) > _HISTORY_MAX_SIZE:
            del self._command_history[0]

    def _record_column_search(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        with suppress(ValueError):
            self._col_search_history.remove(cleaned)
        self._col_search_history.append(cleaned)
        if len(self._col_search_history) > _HISTORY_MAX_SIZE:
            del self._col_search_history[0]

    def _apply_column_search(self, query: str) -> bool:
        """Compute matches for ``query`` and focus the first result."""

        matches = self._compute_column_search_matches(query)
        state = self._col_search_state
        state.set(query, matches, current_col=self.viewer.cur_col)
        if not matches:
            self.viewer.status_message = f"column search: no match for '{query}'"
            return False

        target = state.position or 0
        if self._focus_column_search_match(target):
            return True

        self.viewer.status_message = f"column search: unable to focus '{query}'"
        return False

    def _iter_column_search_candidates(self) -> Iterator[tuple[int, str]]:
        """Yield candidate column indices and names for column search ranking."""

        state = viewer_public_state(self.viewer)
        columns: list[str]
        hidden: set[str]
        if state is None:  # pragma: no cover - defensive
            columns = list(getattr(self.viewer, "columns", ()))
            hidden = set(getattr(self.viewer, "_hidden_cols", ()))
        else:
            columns = list(state.columns)
            hidden = set(state.hidden_columns)

        for idx, name in enumerate(columns):
            if name in hidden:
                continue
            yield idx, name

    def _compute_column_search_matches(self, query: str) -> list[int]:
        """Rank matching columns by how closely they match ``query``."""

        query_lower = query.lower()
        ranked: list[tuple[tuple[int, int], int]] = []

        for idx, name in self._iter_column_search_candidates():
            lowered = name.lower()
            if query_lower not in lowered:
                continue
            if lowered == query_lower:
                priority = 0
            elif lowered.startswith(query_lower):
                priority = 1
            else:
                priority = 2
            ranked.append(((priority, idx), idx))

        ranked.sort(key=lambda item: item[0])
        return [idx for _, idx in ranked]

    def _focus_column_search_match(self, position: int) -> bool:
        matches = self._col_search_state.matches
        if position < 0 or position >= len(matches):
            return False

        match_idx = matches[position]
        if match_idx >= len(self.viewer.columns):
            self._recompute_column_search_matches()
            matches = self._col_search_state.matches
            if position < 0 or position >= len(matches):
                return False
            match_idx = matches[position]

        col_name = self.viewer.columns[match_idx]
        moved = self.viewer.goto_col(col_name)
        if moved:
            self._col_search_state.position = position
            total = len(matches)
            self.viewer.status_message = f"column search: {col_name} ({position + 1}/{total})"
        return moved

    def _handle_column_search_navigation(self, *, forward: bool) -> bool:
        """Navigate among column search matches in response to ``n``/``N``."""

        state = self._col_search_state
        if not state.query or not state.matches:
            return False

        self._recompute_column_search_matches()
        matches = state.matches
        if not matches:
            self.viewer.status_message = f"column search: no match for '{state.query}'"
            self._clear_column_search()
            return True

        try:
            anchor = matches.index(self.viewer.cur_col)
        except ValueError:
            anchor = -1 if forward else len(matches)

        step = 1 if forward else -1
        target = anchor + step
        if 0 <= target < len(matches):
            if self._focus_column_search_match(target):
                return True
            self.viewer.status_message = "column search: unable to focus match"
            return True

        direction = "next" if forward else "previous"
        self.viewer.status_message = f"column search: no {direction} match"
        return True

    def _clear_column_search(self) -> None:
        """Reset column search bookkeeping so ``n``/``N`` fall back to row search."""

        self._col_search_state.clear()

    def _recompute_column_search_matches(self) -> None:
        """Refresh cached matches for the active column search query."""

        state = self._col_search_state
        if not state.query:
            state.clear()
            return

        matches = self._compute_column_search_matches(state.query)
        state.recompute(matches, current_col=self.viewer.cur_col)

    def _status_error_message(self, prefixes: Sequence[str]) -> str | None:
        """Return the current status message when it matches one of ``prefixes``."""

        message = self.viewer.status_message
        if not message:
            return None
        normalized = message.strip().lower()
        for prefix in prefixes:
            if normalized.startswith(prefix):
                return message
        return None

    def _record_expr_filter(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        with suppress(ValueError):
            self._expr_filter_history.remove(cleaned)
        self._expr_filter_history.append(cleaned)
        if len(self._expr_filter_history) > _HISTORY_MAX_SIZE:
            del self._expr_filter_history[0]

    def _record_sql_filter(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        with suppress(ValueError):
            self._sql_filter_history.remove(cleaned)
        self._sql_filter_history.append(cleaned)
        if len(self._sql_filter_history) > _HISTORY_MAX_SIZE:
            del self._sql_filter_history[0]

    def _record_transform(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        with suppress(ValueError):
            self._transform_history.remove(cleaned)
        self._transform_history.append(cleaned)
        if len(self._transform_history) > _HISTORY_MAX_SIZE:
            del self._transform_history[0]

    def _open_error_modal(self, event, title: str, error_message: str, *, retry=None) -> None:
        """Open a modal dialog to display error messages with proper formatting."""
        text_area = TextArea(
            text=error_message,
            read_only=True,
            scrollbar=True,
            wrap_lines=True,
        )
        msg_kb = KeyBindings()

        def _close(app, event_obj=None) -> None:
            self._remove_modal(app)
            if retry is not None:
                retry_event = event_obj
                if retry_event is None:
                    retry_event = SimpleNamespace(app=app)
                retry(retry_event)
            else:
                self.refresh()

        @msg_kb.add("escape")
        def _close_and_reopen_filter(event) -> None:
            _close(event.app, event)

        @msg_kb.add("enter")
        def _close_enter(event) -> None:
            _close(event.app, event)

        tui_modals.merge_text_area_key_bindings(text_area, msg_kb)

        content = HSplit([text_area], padding=0)
        body = Box(body=content, padding=1)
        go_back_button = Button(text="Go back", handler=lambda: _close(event.app))
        dialog = Dialog(title=f"⚠ Error: {title}", body=body, buttons=[go_back_button])
        self._display_modal(
            event.app,
            dialog,
            focus=go_back_button,
            context_type="error",
            width=80,
        )

    def _open_text_modal(self, event, title: str, text: str) -> None:
        target_width = 60
        target_height = 40
        width, height = self._calculate_modal_dimensions(
            event.app,
            target_width=target_width,
            target_height=target_height,
        )
        text_area_height = max(3, height - _CELL_MODAL_CHROME_HEIGHT)

        text_area = TextArea(
            text=text,
            read_only=True,
            scrollbar=True,
            wrap_lines=True,
            height=text_area_height,
        )

        dialog, ok_button = self._build_read_only_modal_dialog(
            app=event.app,
            title=title,
            text_area=text_area,
        )

        self._display_modal(
            event.app,
            dialog,
            focus=ok_button,
            context_type="message",
            width=width,
            height=height,
        )
