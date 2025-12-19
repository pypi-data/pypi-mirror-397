"""Presenters for TUI status + modal output."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping, Sequence
from contextlib import suppress
from typing import Any

from prompt_toolkit.widgets import Button, Dialog

from ..core.viewer import Viewer
from . import modals as tui_modals
from .modal_manager import ModalManager


class StatusPresenter:
    """Centralises status text + modal emission for the screen."""

    def __init__(
        self,
        *,
        get_viewer: Callable[[], Viewer | None],
        refresh: Callable[[], None],
        modals: ModalManager,
        get_app: Callable[[], Any],
    ) -> None:
        self._get_viewer = get_viewer
        self._refresh = refresh
        self._modals = modals
        self._get_app = get_app

    def set_status(self, message: str | None, *, refresh: bool = True) -> None:
        viewer = self._get_viewer()
        if viewer is None:
            return
        viewer.status_message = message
        if refresh:
            self._refresh()

    def open_confirmation_modal(
        self,
        *,
        title: str,
        message_lines: Sequence[str],
        on_confirm: Callable[[], None],
        context_type: str | None = None,
        payload: Mapping[str, object] | None = None,
        width: int = 70,
    ) -> None:
        app = self._get_app()

        def _show() -> None:
            body = tui_modals.build_lines_body(message_lines)

            def _resolve(confirmed: bool) -> None:
                self._modals.remove(app)
                if confirmed:
                    on_confirm()

            yes_button = Button(text="Yes", handler=lambda: _resolve(True))
            cancel_button = Button(text="Cancel", handler=lambda: _resolve(False))
            dialog = Dialog(title=title, body=body, buttons=[yes_button, cancel_button])
            self._modals.display(
                app,
                dialog,
                focus=yes_button,
                context_type=context_type or "confirmation",
                payload=payload,
                width=width,
            )

        if hasattr(app, "create_background_task"):

            async def _defer() -> None:
                await asyncio.sleep(0)
                _show()

            app.create_background_task(_defer())
            return

        _show()

    def open_status_modal(self, *, title: str, lines: Sequence[str], width: int = 80) -> None:
        app = self._get_app()

        def _show() -> None:
            body = tui_modals.build_lines_body(lines)

            def _close() -> None:
                self._modals.remove(app)

            ok_button = Button(text="OK", handler=_close)
            dialog = Dialog(title=title, body=body, buttons=[ok_button])
            self._modals.display(app, dialog, focus=ok_button, context_type="status", width=width)

        if hasattr(app, "create_background_task"):

            async def _defer() -> None:
                await asyncio.sleep(0)
                _show()

            app.create_background_task(_defer())
            return

        _show()

    def close_modal(self, *, restore_focus: bool = True) -> None:
        app = self._get_app()
        self._modals.remove(app, restore_focus=restore_focus)

    def record_exception(self, exc: Exception) -> None:
        viewer = self._get_viewer()
        recorder = getattr(viewer, "recorder", None) if viewer is not None else None
        if recorder is None or not getattr(recorder, "enabled", False):
            return
        with suppress(Exception):
            recorder.record_exception(message=str(exc))
