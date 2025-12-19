from __future__ import annotations

from pathlib import Path

from pulka.tui.controllers.file_browser import FileBrowserController


class _DummySession:
    pass


class _Sheet:
    def __init__(self, directory: Path):
        self.directory = directory


def _controller() -> FileBrowserController:
    return FileBrowserController(session=_DummySession(), get_viewer=lambda: None)


def test_make_directory_allows_absolute_path(tmp_path: Path) -> None:
    controller = _controller()
    sheet = _Sheet(directory=tmp_path / "base")
    target = tmp_path / "outside" / "nested"

    message, error = controller.make_directory(sheet=sheet, dest=str(target))

    assert error is None
    assert target.exists()
    assert message == f"created directory {target.resolve()}"


def test_make_directory_allows_parent_relative_path(tmp_path: Path) -> None:
    base_dir = tmp_path / "root" / "child"
    base_dir.mkdir(parents=True)
    controller = _controller()
    sheet = _Sheet(directory=base_dir)
    target = base_dir.parent / "sibling" / "new_folder"

    message, error = controller.make_directory(sheet=sheet, dest="../sibling/new_folder")

    assert error is None
    assert target.exists()
    assert message == f"created directory {target.resolve()}"
