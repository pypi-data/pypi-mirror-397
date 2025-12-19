"""Dataset reload orchestration for the Screen."""

from __future__ import annotations

import errno
import traceback
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ...api.session import Session
    from ...core.viewer import Viewer
    from ...logging import Recorder
    from ..controllers.file_watch import FileWatchController


class DatasetReloadController:
    """Keeps dataset reload/missing-file flows out of :class:`Screen`."""

    def __init__(
        self,
        *,
        session: Session,
        get_viewer: Callable[[], Viewer],
        get_file_watch: Callable[[], FileWatchController | None],
        refresh: Callable[[], None],
        recorder_getter: Callable[[], Recorder | None],
        open_reload_error_modal: Callable[[str], None],
    ) -> None:
        self._session = session
        self._get_viewer = get_viewer
        self._get_file_watch = get_file_watch
        self._refresh = refresh
        self._recorder_getter = recorder_getter
        self._open_reload_error_modal = open_reload_error_modal

    def reload_dataset(self) -> None:
        viewer = self._get_viewer()
        dataset_path_raw = getattr(self._session, "dataset_path", None)
        if dataset_path_raw is None:
            viewer.status_message = "reload requires a file-backed dataset"
            self._refresh()
            return
        dataset_path = Path(dataset_path_raw)

        if not dataset_path.exists():
            self.handle_missing_dataset(dataset_path)
            return

        try:
            if len(getattr(self._session, "view_stack", ())) > 1 and getattr(
                viewer, "_pulka_has_real_source_path", False
            ):
                self._session.reload_viewer(viewer)
            else:
                self._session.open(dataset_path)
        except Exception as exc:  # pragma: no cover - heavy IO guard
            self.handle_reload_error(exc, dataset_path)
            return

        viewer.status_message = f"reloaded {dataset_path}"
        file_watch = self._get_file_watch()
        if file_watch is not None:
            file_watch.sync_dataset(force=True)
        self._refresh()

    @staticmethod
    def is_missing_error(exc: Exception) -> bool:
        if isinstance(exc, FileNotFoundError):
            return True
        if isinstance(exc, OSError):
            errno_value = getattr(exc, "errno", None)
            return errno_value == errno.ENOENT
        return False

    def handle_missing_dataset(self, dataset_path: Path) -> None:
        viewer = self._get_viewer()
        target_dir = dataset_path.parent if dataset_path.parent != dataset_path else dataset_path
        if not target_dir.exists():
            with suppress(Exception):
                while not target_dir.exists():
                    parent = target_dir.parent
                    if parent == target_dir:
                        break
                    target_dir = parent
        if not target_dir.exists():
            target_dir = Path.cwd()

        file_watch = self._get_file_watch()
        if file_watch is not None:
            file_watch.clear_dataset_prompt()

        try:
            self._session.open_file_browser(target_dir)
        except Exception as browse_exc:
            viewer.status_message = (
                f"{dataset_path} is missing; failed to open browser: {browse_exc}"
            )
            self._refresh()
            return

        if file_watch is not None:
            file_watch.sync(force=True)

        active_viewer = getattr(self._session, "viewer", None) or viewer
        if active_viewer is not None:
            active_viewer.status_message = (
                f"{dataset_path} is missing; opened file browser at {target_dir}"
            )
        self._refresh()

    def handle_reload_error(self, exc: Exception, dataset_path: Path) -> None:
        if self.is_missing_error(exc):
            self.handle_missing_dataset(dataset_path)
            return

        viewer = self._get_viewer()
        viewer.status_message = "reload failed; see error modal"
        stack = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        recorder = self._recorder_getter()
        if recorder is not None and getattr(recorder, "enabled", False):
            with suppress(Exception):
                recorder.record_exception(message=str(exc), stack=stack)
        file_watch = self._get_file_watch()
        if file_watch is not None:
            with suppress(Exception):
                file_watch.sync_dataset(force=True)
        error_text = f"Failed to reload dataset at {dataset_path}\n\n{stack or repr(exc)}"
        self._open_reload_error_modal(error_text)
