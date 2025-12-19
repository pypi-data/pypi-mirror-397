"""Modal orchestration helpers for the Pulka TUI."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import suppress
from dataclasses import dataclass
from typing import Any

from prompt_toolkit.layout.containers import Float, FloatContainer


@dataclass(slots=True)
class ModalState:
    modal: Float | None = None
    context: dict[str, object] | None = None


class ModalManager:
    """Owns modal display/removal and context bookkeeping."""

    def __init__(self, *, window: FloatContainer, table_window: Any) -> None:
        self._window = window
        self._table_window = table_window
        self._state = ModalState()

    @property
    def active(self) -> bool:
        return self._state.modal is not None

    @property
    def context(self) -> dict[str, object] | None:
        return self._state.context

    @staticmethod
    def calculate_dimensions_for_size(
        *,
        target_width: int,
        target_height: int,
        columns: int | None,
        rows: int | None,
        chrome_height: int,
    ) -> tuple[int, int]:
        width = max(1, target_width)
        height = max(1, target_height)

        if columns is not None and rows is not None:
            columns = max(1, columns)
            rows = max(1, rows)

            if columns < target_width:
                width = max(10, int(columns * 0.8))
            else:
                width = min(target_width, columns)

            height = max(5, int(rows * 0.8)) if rows < target_height else min(target_height, rows)

            width = max(10, min(width, columns))
            height = max(5, min(height, rows))

        height = max(height, 3 + chrome_height)
        return width, height

    def calculate_dimensions(
        self,
        app: Any,
        *,
        target_width: int,
        target_height: int,
        chrome_height: int,
    ) -> tuple[int, int]:
        size = None
        try:
            size = app.output.get_size()
        except Exception:
            size = None
        columns = getattr(size, "columns", None) if size is not None else None
        rows = getattr(size, "rows", None) if size is not None else None
        return self.calculate_dimensions_for_size(
            target_width=target_width,
            target_height=target_height,
            columns=columns,
            rows=rows,
            chrome_height=chrome_height,
        )

    def display(
        self,
        app: Any,
        container: Any,
        *,
        focus: Any | None = None,
        context_type: str | None = None,
        payload: Mapping[str, object] | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        if self._state.modal is not None:
            self.remove(app, restore_focus=False)

        float_kwargs: dict[str, object] = {"z_index": 10}
        size = None
        try:
            size = app.output.get_size()
        except Exception:
            size = None

        base_container = getattr(container, "container", container)
        measured_width: int | None = None
        measured_height: int | None = None
        if hasattr(base_container, "preferred_width"):
            try:
                dim_w = base_container.preferred_width(size.columns if size else 80)
                measured_width = dim_w.preferred or dim_w.max or dim_w.min
            except Exception:
                measured_width = None
        if hasattr(base_container, "preferred_height"):
            try:
                dim_h = base_container.preferred_height(
                    size.columns if size else 80,
                    size.rows if size else 24,
                )
                measured_height = dim_h.preferred or dim_h.max or dim_h.min
            except Exception:
                measured_height = None

        actual_width = width if width is not None else measured_width
        if actual_width is not None:
            float_kwargs["width"] = actual_width
        if height is not None:
            float_kwargs["height"] = height

        if size is not None and actual_width is not None:
            float_kwargs["left"] = max(0, (size.columns - actual_width) // 2)
        if size is not None:
            target_height = height if height is not None else measured_height
            if target_height is not None:
                float_kwargs["top"] = max(0, (size.rows - target_height) // 3)

        modal = Float(content=container, **float_kwargs)
        self._window.floats.append(modal)
        self._state.modal = modal

        ctx: dict[str, object] = {}
        if payload:
            ctx.update(dict(payload))
        if context_type is not None:
            ctx.setdefault("type", context_type)
        self._state.context = ctx or None

        if focus is not None:
            app.layout.focus(focus)
        app.invalidate()

    def remove(self, app: Any, *, restore_focus: bool = True) -> None:
        if self._state.modal is None:
            return
        with suppress(ValueError):
            self._window.floats.remove(self._state.modal)
        self._state.modal = None
        self._state.context = None

        if restore_focus:
            try:
                windows = list(app.layout.find_all_windows())
            except Exception:
                windows = []
            if self._table_window in windows:
                with suppress(Exception):
                    app.layout.focus(self._table_window)

        app.invalidate()
