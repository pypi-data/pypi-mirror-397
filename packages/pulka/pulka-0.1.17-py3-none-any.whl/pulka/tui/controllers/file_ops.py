"""UI-facing orchestration for file browser operations."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from pathlib import Path
from typing import Any

from ...core.viewer import Viewer
from ..presenters import StatusPresenter
from .file_browser import FileBrowserController, FileTransferPlan


class FileOpsController:
    """Coordinates file browser operations with screen presentation hooks."""

    def __init__(
        self,
        *,
        file_browser: FileBrowserController,
        presenter: StatusPresenter,
        get_viewer: Callable[[], Viewer | None],
        refresh: Callable[[], None],
        handle_file_browser_refresh: Callable[[Any], None],
        invalidate: Callable[[], None],
    ) -> None:
        self._file_browser = file_browser
        self._presenter = presenter
        self._get_viewer = get_viewer
        self._refresh = refresh
        self._handle_file_browser_refresh = handle_file_browser_refresh
        self._invalidate = invalidate

    def request_transfer(self, operation: str, dest: str) -> None:
        viewer = self._get_viewer()
        sheet = getattr(viewer, "sheet", None) if viewer is not None else None
        if viewer is None or sheet is None or not getattr(sheet, "is_file_browser", False):
            return

        entries, status = self._file_browser.resolve_entries(viewer=viewer)
        if status:
            viewer.status_message = status
        if not entries:
            self._refresh()
            return

        plan: FileTransferPlan = self._file_browser.plan_transfer(
            operation, dest, entries=entries, sheet=sheet
        )
        if plan.error:
            viewer.status_message = plan.error
            self._refresh()
            return

        if plan.missing_directories:
            count = len(plan.missing_directories)
            noun = "directory" if count == 1 else "directories"
            verb = "does" if count == 1 else "do"
            display_path = plan.missing_directories[0]
            prompt = "Create it?" if count == 1 else "Create them?"
            message_lines = [
                f"{count} destination {noun} {verb} not exist.",
                f"First: {display_path}",
                prompt,
            ]

            def _create_and_execute() -> None:
                self.perform_transfer(operation, plan.targets, allow_overwrite=bool(plan.conflicts))

            self._presenter.open_confirmation_modal(
                title="Create destination directories",
                message_lines=message_lines,
                on_confirm=_create_and_execute,
                context_type="file_transfer_mkdir",
                payload={"count": count, "op": operation},
            )
            self._refresh()
            return

        def _execute() -> None:
            self.perform_transfer(operation, plan.targets, allow_overwrite=bool(plan.conflicts))

        if plan.conflicts:
            title = "Overwrite existing items"
            count = len(plan.conflicts)
            suffix = "" if count == 1 else "s"
            display_path = plan.conflicts[0]
            message_lines = [
                f"{count} destination item{suffix} already exist.",
                f"First: {display_path}",
                "Overwrite them?",
            ]
            self._presenter.open_confirmation_modal(
                title=title,
                message_lines=message_lines,
                on_confirm=_execute,
                context_type="file_transfer_overwrite",
                payload={"count": count, "op": operation},
            )
            self._refresh()
            return

        _execute()

    def request_rename(self, new_name: str) -> None:
        viewer = self._get_viewer()
        sheet = getattr(viewer, "sheet", None) if viewer is not None else None
        if viewer is None or sheet is None or not getattr(sheet, "is_file_browser", False):
            return

        entries, status = self._file_browser.resolve_entries(viewer=viewer)
        if status:
            viewer.status_message = status
        if not entries:
            self._refresh()
            return
        if len(entries) != 1:
            viewer.status_message = "select exactly one item to rename"
            self._refresh()
            return

        message, error = self._file_browser.rename_entry(
            sheet=sheet, entry=entries[0], new_name=new_name
        )
        if error:
            viewer.status_message = error
            self._refresh()
            return

        self._handle_file_browser_refresh(sheet)
        self._refresh()
        if message:
            viewer.status_message = message

    def request_mkdir(self, path: str) -> None:
        viewer = self._get_viewer()
        sheet = getattr(viewer, "sheet", None) if viewer is not None else None
        if viewer is None or sheet is None or not getattr(sheet, "is_file_browser", False):
            return

        message, error = self._file_browser.make_directory(sheet=sheet, dest=path)
        if error:
            viewer.status_message = error
            self._refresh()
            return

        self._handle_file_browser_refresh(sheet)
        self._refresh()
        if message:
            viewer.status_message = message

    def perform_transfer(
        self,
        operation: str,
        targets: list[tuple[Path, Path]],
        *,
        allow_overwrite: bool = False,
    ) -> None:
        viewer = self._get_viewer()
        if viewer is None:
            return

        message, errors, completed = self._file_browser.perform_transfer(
            operation, targets, allow_overwrite=allow_overwrite
        )
        sheet = getattr(viewer, "sheet", None)
        if sheet is not None and getattr(sheet, "is_file_browser", False) and (completed or errors):
            self._handle_file_browser_refresh(sheet)
        if errors:
            path, err = errors[0]
            self._presenter.open_status_modal(
                title="File operation error", lines=[f"{path}: {err}"]
            )
            if not completed:
                message = "operation failed"

        if operation == "move" and completed:
            with suppress(Exception):
                viewer._clear_selection_state()

        self._refresh()
        if message:
            viewer.status_message = message
            with suppress(Exception):
                self._invalidate()
