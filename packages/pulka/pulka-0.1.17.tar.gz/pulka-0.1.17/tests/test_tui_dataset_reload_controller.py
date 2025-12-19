from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pulka.tui.controllers.dataset_reload import DatasetReloadController


@dataclass
class _FakeRecorder:
    enabled: bool = True
    calls: list[tuple[str, str]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.calls is None:
            self.calls = []

    def record_exception(self, *, message: str, stack: str | None = None) -> None:
        self.calls.append((message, stack or ""))


class _FakeFileWatch:
    def __init__(self) -> None:
        self.dataset_cleared = 0
        self.dataset_synced = 0
        self.synced = 0

    def clear_dataset_prompt(self) -> None:
        self.dataset_cleared += 1

    def sync_dataset(self, *, force: bool) -> None:
        assert force is True
        self.dataset_synced += 1

    def sync(self, *, force: bool) -> None:
        assert force is True
        self.synced += 1


class _FakeSession:
    def __init__(self, *, dataset_path: str | None, view_stack_len: int = 1) -> None:
        self.dataset_path = dataset_path
        self.view_stack = [object()] * view_stack_len
        self.open_calls: list[Path] = []
        self.reload_calls: list[object] = []
        self.browse_calls: list[Path] = []
        self.viewer = None

    def open(self, path: Path) -> None:
        self.open_calls.append(path)

    def reload_viewer(self, viewer) -> None:
        self.reload_calls.append(viewer)

    def open_file_browser(self, path: Path) -> None:
        self.browse_calls.append(path)


class _FakeViewer:
    def __init__(self) -> None:
        self.status_message: str | None = None
        self._pulka_has_real_source_path = False


def test_reload_dataset_uses_session_open(tmp_path: Path) -> None:
    dataset = tmp_path / "data.parquet"
    dataset.write_bytes(b"x")
    viewer = _FakeViewer()
    session = _FakeSession(dataset_path=str(dataset), view_stack_len=1)
    file_watch = _FakeFileWatch()
    recorder = _FakeRecorder()
    modal_texts: list[str] = []
    refresh_calls: list[object] = []

    controller = DatasetReloadController(
        session=session,  # type: ignore[arg-type]
        get_viewer=lambda: viewer,  # type: ignore[return-value]
        get_file_watch=lambda: file_watch,  # type: ignore[return-value]
        refresh=lambda: refresh_calls.append(object()),
        recorder_getter=lambda: recorder,  # type: ignore[return-value]
        open_reload_error_modal=modal_texts.append,
    )

    controller.reload_dataset()
    assert session.open_calls == [dataset]
    assert not modal_texts
    assert file_watch.dataset_synced == 1
    assert refresh_calls


def test_reload_missing_dataset_opens_file_browser(tmp_path: Path) -> None:
    missing = tmp_path / "missing.parquet"
    viewer = _FakeViewer()
    session = _FakeSession(dataset_path=str(missing))
    file_watch = _FakeFileWatch()
    refresh_calls: list[object] = []

    controller = DatasetReloadController(
        session=session,  # type: ignore[arg-type]
        get_viewer=lambda: viewer,  # type: ignore[return-value]
        get_file_watch=lambda: file_watch,  # type: ignore[return-value]
        refresh=lambda: refresh_calls.append(object()),
        recorder_getter=lambda: None,
        open_reload_error_modal=lambda _text: None,
    )

    controller.reload_dataset()
    assert session.browse_calls == [tmp_path]
    assert file_watch.dataset_cleared == 1
    assert file_watch.synced == 1
    assert refresh_calls
