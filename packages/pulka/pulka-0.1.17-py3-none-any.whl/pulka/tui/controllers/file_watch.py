from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from time import monotonic

from ...testing import is_test_mode


@dataclass(slots=True)
class FileSnapshot:
    """File metadata snapshot used to detect on-disk changes."""

    mtime_ns: int | None
    size: int | None
    inode: int | None
    missing: bool = False
    error: str | None = None


@dataclass(slots=True)
class _DatasetWatchState:
    path: Path | None = None
    snapshot: FileSnapshot | None = None
    last_check: float = 0.0
    prompt_active: bool = False


@dataclass(slots=True)
class _FileBrowserWatchState:
    sheet: object | None = None
    directory: Path | None = None
    last_check: float = 0.0


class FileWatchController:
    """Shared helper for dataset and file browser file watching."""

    def __init__(
        self,
        *,
        dataset_path_getter: Callable[[], Path | str | None],
        viewer_getter: Callable[[], object | None],
        hooks_getter: Callable[[], object | None],
        on_dataset_change: Callable[[Path, FileSnapshot | None], None],
        on_file_browser_refresh: Callable[[object], None],
        on_file_browser_error: Callable[[Exception], None],
        interval: float = 1.0,
    ):
        self._dataset_path_getter = dataset_path_getter
        self._viewer_getter = viewer_getter
        self._hooks_getter = hooks_getter
        self._on_dataset_change = on_dataset_change
        self._on_file_browser_refresh = on_file_browser_refresh
        self._on_file_browser_error = on_file_browser_error
        self._interval = interval
        self._dataset = _DatasetWatchState()
        self._file_browser = _FileBrowserWatchState()
        self._file_watch_thread: threading.Thread | None = None
        self._file_watch_stop_event: threading.Event | None = None

    @property
    def dataset_path(self) -> Path | None:
        return self._dataset.path

    @property
    def dataset_prompt_active(self) -> bool:
        return self._dataset.prompt_active

    def set_dataset_prompt_active(self, active: bool) -> None:
        self._dataset.prompt_active = active

    def clear_dataset_prompt(self) -> None:
        self._dataset.prompt_active = False

    def complete_dataset_prompt(self, *, refresh_snapshot: bool = True) -> None:
        self._dataset.prompt_active = False
        if refresh_snapshot and self._dataset.path is not None:
            self._dataset.snapshot = self._capture_dataset_snapshot(self._dataset.path)
            self._dataset.last_check = monotonic()
        self._ensure_file_watch_loop()

    def sync(self, *, force: bool = False) -> None:
        self.sync_dataset(force=force)
        self.sync_file_browser(force=force)

    def sync_dataset(self, *, force: bool = False) -> None:
        path = self._normalize_path(self._dataset_path_getter())
        if path is None:
            if self._dataset.path is not None or self._dataset.snapshot is not None:
                self._dataset.path = None
                self._dataset.snapshot = None
                self._dataset.prompt_active = False
                self._ensure_file_watch_loop()
            return
        if not force and self._dataset.path == path:
            return
        self._dataset.path = path
        self._dataset.snapshot = self._capture_dataset_snapshot(path)
        self._dataset.last_check = monotonic()
        self._ensure_file_watch_loop()

    def sync_file_browser(self, *, force: bool = False) -> None:
        viewer = self._viewer_getter()
        sheet = getattr(viewer, "sheet", None)
        if sheet is None or not getattr(sheet, "is_file_browser", False):
            if self._file_browser.sheet is not None:
                self._file_browser.sheet = None
                self._file_browser.directory = None
                self._file_browser.last_check = 0.0
                self._ensure_file_watch_loop()
            return
        directory = getattr(sheet, "directory", None)
        if directory is None:
            return
        directory_path = Path(directory)
        if (
            not force
            and self._file_browser.sheet is sheet
            and self._file_browser.directory == directory_path
        ):
            return
        self._file_browser.sheet = sheet
        self._file_browser.directory = directory_path
        self._file_browser.last_check = 0.0
        self._ensure_file_watch_loop()

    def check(self, *, force: bool = False) -> None:
        self._check_dataset_file_changes(force=force)
        self._check_file_browser_changes(force=force)

    def check_dataset(self, *, force: bool = False) -> None:
        self._check_dataset_file_changes(force=force)

    def check_file_browser(self, *, force: bool = False) -> None:
        self._check_file_browser_changes(force=force)

    def stop(self) -> None:
        self._stop_file_watch_loop()

    def _check_dataset_file_changes(self, *, force: bool) -> None:
        if self._dataset.prompt_active:
            return
        path = self._normalize_path(self._dataset_path_getter())
        if path is None:
            if self._dataset.path is not None or self._dataset.snapshot is not None:
                self._dataset.path = None
                self._dataset.snapshot = None
                self._ensure_file_watch_loop()
            return
        if self._dataset.path != path:
            self._dataset.path = path
            self._dataset.snapshot = self._capture_dataset_snapshot(path)
            self._dataset.last_check = monotonic()
            self._ensure_file_watch_loop()
            return
        now = monotonic()
        if not force and now - self._dataset.last_check < self._interval:
            return
        self._dataset.last_check = now
        current_snapshot = self._capture_dataset_snapshot(path)
        previous_snapshot = self._dataset.snapshot
        if previous_snapshot is None:
            self._dataset.snapshot = current_snapshot
            return
        if self._file_snapshot_changed(previous_snapshot, current_snapshot):
            self._dataset.snapshot = current_snapshot
            self._dataset.prompt_active = True
            self._on_dataset_change(path, current_snapshot)

    def _check_file_browser_changes(self, *, force: bool) -> None:
        sheet = self._file_browser.sheet
        directory = self._file_browser.directory
        if sheet is None or directory is None:
            return
        viewer = self._viewer_getter()
        if viewer is None or getattr(viewer, "sheet", None) is not sheet:
            self.sync_file_browser(force=True)
            return
        current_directory = getattr(sheet, "directory", None)
        if current_directory is None or Path(current_directory) != directory:
            self.sync_file_browser(force=True)
            return
        now = monotonic()
        if not force and now - self._file_browser.last_check < self._interval:
            return
        self._file_browser.last_check = now
        refresh = getattr(sheet, "refresh_from_disk", None)
        if not callable(refresh):
            return
        try:
            changed = refresh()
        except Exception as exc:  # pragma: no cover - filesystem specific
            self._on_file_browser_error(exc)
            self._invalidate()
            return
        if not changed:
            return
        self._on_file_browser_refresh(sheet)

    def _capture_dataset_snapshot(self, path: Path) -> FileSnapshot | None:
        try:
            stat_result = path.stat()
        except FileNotFoundError:
            return FileSnapshot(mtime_ns=None, size=None, inode=None, missing=True)
        except OSError as exc:  # pragma: no cover - filesystem specific
            return FileSnapshot(
                mtime_ns=None,
                size=None,
                inode=None,
                missing=True,
                error=str(exc),
            )
        mtime_ns = getattr(stat_result, "st_mtime_ns", None)
        if mtime_ns is None:
            mtime_ns = int(stat_result.st_mtime * 1_000_000_000)
        return FileSnapshot(
            mtime_ns=mtime_ns,
            size=getattr(stat_result, "st_size", None),
            inode=getattr(stat_result, "st_ino", None),
            missing=False,
            error=None,
        )

    @staticmethod
    def _file_snapshot_changed(
        previous: FileSnapshot | None,
        current: FileSnapshot | None,
    ) -> bool:
        if previous is None or current is None:
            return False
        return (
            previous.missing != current.missing
            or previous.mtime_ns != current.mtime_ns
            or previous.size != current.size
            or previous.inode != current.inode
        )

    def _has_file_watch_targets(self) -> bool:
        return self._dataset.path is not None or self._file_browser.sheet is not None

    def _ensure_file_watch_loop(self) -> None:
        if is_test_mode():
            return
        if not self._has_file_watch_targets():
            self._stop_file_watch_loop()
            return
        thread = self._file_watch_thread
        if thread is not None and thread.is_alive():
            return
        self._start_file_watch_loop()

    def _start_file_watch_loop(self) -> None:
        if is_test_mode():
            return
        if not self._has_file_watch_targets():
            return
        if self._file_watch_thread is not None:
            return
        stop_event = threading.Event()
        self._file_watch_stop_event = stop_event

        def _loop() -> None:
            while not stop_event.wait(self._interval):
                hooks = self._hooks_getter()
                if hooks is None:
                    continue

                def _tick() -> None:
                    if self._file_watch_stop_event is not stop_event:
                        return
                    self.check(force=True)

                hooks.call_soon(_tick)

        thread = threading.Thread(target=_loop, name="pulka-file-watch", daemon=True)
        self._file_watch_thread = thread
        thread.start()

    def _stop_file_watch_loop(self) -> None:
        stop_event = self._file_watch_stop_event
        thread = self._file_watch_thread
        if stop_event is not None:
            stop_event.set()
        if thread is not None and thread.is_alive():
            thread.join(timeout=0.5)
        self._file_watch_stop_event = None
        self._file_watch_thread = None

    def _normalize_path(self, path: Path | str | None) -> Path | None:
        if path is None or path == "":
            return None
        try:
            return Path(path)
        except TypeError:
            return None

    def _invalidate(self) -> None:
        hooks = self._hooks_getter()
        if hooks is None:
            return
        invalidate = getattr(hooks, "invalidate", None)
        if callable(invalidate):
            invalidate()
