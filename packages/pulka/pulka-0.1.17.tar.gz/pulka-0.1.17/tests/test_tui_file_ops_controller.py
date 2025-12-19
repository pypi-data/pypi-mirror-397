from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from pulka.data.scanners import ScannerRegistry
from pulka.sheets.file_browser_sheet import FileBrowserSheet
from pulka.tui.controllers.file_browser import FileBrowserController, FileTransferPlan
from pulka.tui.controllers.file_ops import FileOpsController


@dataclass
class _Entry:
    path: Path


class _FakeFileBrowser:
    def __init__(
        self,
        *,
        plan_conflicts: list[Path] | None = None,
        plan_missing_dirs: list[Path] | None = None,
    ) -> None:
        self.transfer_calls: list[tuple[str, list[tuple[Path, Path]]]] = []
        self.plan_conflicts = plan_conflicts if plan_conflicts is not None else [Path("dest/a.txt")]
        self.plan_missing_dirs = plan_missing_dirs or []

    def resolve_entries(self, *, viewer):
        return [_Entry(path=Path("a.txt"))], None

    def plan_transfer(self, operation: str, dest: str, *, entries, sheet):
        del dest, entries, sheet
        return FileTransferPlan(
            targets=[(Path("a.txt"), Path("dest/a.txt"))],
            conflicts=list(self.plan_conflicts),
            missing_directories=list(self.plan_missing_dirs),
            error=None,
        )

    def perform_transfer(self, operation: str, targets, *, allow_overwrite: bool):
        self.transfer_calls.append((operation, list(targets), allow_overwrite))
        return "Copied 1 item", [], 1

    def rename_entry(self, *, sheet, entry, new_name: str):
        del sheet, entry, new_name
        return None, None

    def make_directory(self, *, sheet, dest: str):
        del sheet, dest
        return None, None


class _FakePresenter:
    def __init__(self) -> None:
        self.confirm_calls: list[dict[str, object]] = []
        self.status_calls: list[dict[str, object]] = []

    def open_confirmation_modal(self, **kwargs) -> None:
        self.confirm_calls.append(kwargs)

    def open_status_modal(self, **kwargs) -> None:
        self.status_calls.append(kwargs)


class _FakeSheet:
    is_file_browser = True


class _FakeViewer:
    def __init__(self) -> None:
        self.sheet = _FakeSheet()
        self.status_message: str | None = None
        self.clear_selection_calls = 0

    def _clear_selection_state(self) -> bool:
        self.clear_selection_calls += 1
        return True


def test_file_ops_transfer_conflict_prompts_then_executes() -> None:
    viewer = _FakeViewer()
    refresh_calls: list[object] = []
    invalidate_calls: list[object] = []
    browser = _FakeFileBrowser()
    presenter = _FakePresenter()

    def refresh() -> None:
        refresh_calls.append(object())

    def handle_refresh(sheet) -> None:
        del sheet

    def invalidate() -> None:
        invalidate_calls.append(object())

    ops = FileOpsController(
        file_browser=browser,
        presenter=presenter,  # type: ignore[arg-type]
        get_viewer=lambda: viewer,  # type: ignore[return-value]
        refresh=refresh,
        handle_file_browser_refresh=handle_refresh,
        invalidate=invalidate,
    )

    ops.request_transfer("copy", "dest")
    assert len(presenter.confirm_calls) == 1
    confirm = presenter.confirm_calls[0]
    assert confirm["context_type"] == "file_transfer_overwrite"

    on_confirm = confirm["on_confirm"]
    assert callable(on_confirm)
    on_confirm()

    assert browser.transfer_calls == [("copy", [(Path("a.txt"), Path("dest/a.txt"))], True)]
    assert refresh_calls
    assert invalidate_calls


def test_file_ops_transfer_missing_dirs_prompts_then_executes() -> None:
    viewer = _FakeViewer()
    refresh_calls: list[object] = []
    invalidate_calls: list[object] = []
    browser = _FakeFileBrowser(plan_conflicts=[], plan_missing_dirs=[Path("dest")])
    presenter = _FakePresenter()

    def refresh() -> None:
        refresh_calls.append(object())

    def handle_refresh(sheet) -> None:
        del sheet

    def invalidate() -> None:
        invalidate_calls.append(object())

    ops = FileOpsController(
        file_browser=browser,
        presenter=presenter,  # type: ignore[arg-type]
        get_viewer=lambda: viewer,  # type: ignore[return-value]
        refresh=refresh,
        handle_file_browser_refresh=handle_refresh,
        invalidate=invalidate,
    )

    ops.request_transfer("copy", "dest")
    assert len(presenter.confirm_calls) == 1
    confirm = presenter.confirm_calls[0]
    assert confirm["context_type"] == "file_transfer_mkdir"

    on_confirm = confirm["on_confirm"]
    assert callable(on_confirm)
    on_confirm()

    assert browser.transfer_calls == [("copy", [(Path("a.txt"), Path("dest/a.txt"))], False)]
    assert refresh_calls
    assert invalidate_calls


def test_file_ops_transfer_conflict_detected_from_real_plan(tmp_path) -> None:
    src = tmp_path / "test.csv"
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    src.write_text("data")
    (dest_dir / "test.csv").write_text("old")

    sheet = FileBrowserSheet(tmp_path, scanners=ScannerRegistry())
    viewer = _FakeViewer()
    viewer.sheet = sheet
    selected_entry = next(e for e in sheet._entries if e.path == src)
    viewer._selected_row_ids = {sheet._entries.index(selected_entry)}
    viewer.cur_row = next(idx for idx, e in enumerate(sheet._entries) if e.path == src)

    refresh_calls: list[object] = []
    browser = FileBrowserController(session=SimpleNamespace(), get_viewer=lambda: viewer)
    presenter = _FakePresenter()

    def refresh() -> None:
        refresh_calls.append(object())

    ops = FileOpsController(
        file_browser=browser,
        presenter=presenter,  # type: ignore[arg-type]
        get_viewer=lambda: viewer,  # type: ignore[return-value]
        refresh=refresh,
        handle_file_browser_refresh=lambda sheet: None,
        invalidate=lambda: None,
    )

    ops.request_transfer("copy", str(dest_dir))

    assert presenter.confirm_calls
    assert presenter.confirm_calls[0]["context_type"] == "file_transfer_overwrite"
    assert (dest_dir / "test.csv").read_text() == "old"


def test_file_ops_transfer_conflict_with_relative_dest(tmp_path) -> None:
    src = tmp_path / "test.csv"
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    src.write_text("data")
    (dest_dir / "test.csv").write_text("old")

    sheet = FileBrowserSheet(tmp_path, scanners=ScannerRegistry())
    viewer = _FakeViewer()
    viewer.sheet = sheet
    selected_entry = next(e for e in sheet._entries if e.path == src)
    viewer._selected_row_ids = {sheet._entries.index(selected_entry)}
    viewer.cur_row = next(idx for idx, e in enumerate(sheet._entries) if e.path == src)

    browser = FileBrowserController(session=SimpleNamespace(), get_viewer=lambda: viewer)
    presenter = _FakePresenter()

    ops = FileOpsController(
        file_browser=browser,
        presenter=presenter,  # type: ignore[arg-type]
        get_viewer=lambda: viewer,  # type: ignore[return-value]
        refresh=lambda: None,
        handle_file_browser_refresh=lambda sheet: None,
        invalidate=lambda: None,
    )

    ops.request_transfer("copy", "./dest")

    assert presenter.confirm_calls
    assert presenter.confirm_calls[0]["context_type"] == "file_transfer_overwrite"
    assert (dest_dir / "test.csv").read_text() == "old"


def test_file_ops_transfer_creates_missing_destination_dir(tmp_path) -> None:
    src = tmp_path / "test.csv"
    src.write_text("data")
    dest_dir = tmp_path / "newdir"

    sheet = FileBrowserSheet(tmp_path, scanners=ScannerRegistry())
    viewer = _FakeViewer()
    viewer.sheet = sheet
    selected_entry = next(e for e in sheet._entries if e.path == src)
    viewer._selected_row_ids = {sheet._entries.index(selected_entry)}
    viewer.cur_row = next(idx for idx, e in enumerate(sheet._entries) if e.path == src)

    browser = FileBrowserController(session=SimpleNamespace(), get_viewer=lambda: viewer)
    presenter = _FakePresenter()

    ops = FileOpsController(
        file_browser=browser,
        presenter=presenter,  # type: ignore[arg-type]
        get_viewer=lambda: viewer,  # type: ignore[return-value]
        refresh=lambda: None,
        handle_file_browser_refresh=lambda sheet: None,
        invalidate=lambda: None,
    )

    ops.request_transfer("copy", "./newdir")

    assert presenter.confirm_calls
    assert presenter.confirm_calls[0]["context_type"] == "file_transfer_mkdir"
    assert not dest_dir.exists()


def test_file_ops_move_clears_selection_on_success() -> None:
    viewer = _FakeViewer()
    refresh_calls: list[object] = []
    invalidate_calls: list[object] = []
    browser = _FakeFileBrowser()
    presenter = _FakePresenter()

    def refresh() -> None:
        refresh_calls.append(object())

    def handle_refresh(sheet) -> None:
        del sheet

    def invalidate() -> None:
        invalidate_calls.append(object())

    ops = FileOpsController(
        file_browser=browser,
        presenter=presenter,  # type: ignore[arg-type]
        get_viewer=lambda: viewer,  # type: ignore[return-value]
        refresh=refresh,
        handle_file_browser_refresh=handle_refresh,
        invalidate=invalidate,
    )

    ops.perform_transfer("move", [(Path("a.txt"), Path("dest/a.txt"))])

    assert browser.transfer_calls == [("move", [(Path("a.txt"), Path("dest/a.txt"))], False)]
    assert viewer.clear_selection_calls == 1
    assert refresh_calls
    assert invalidate_calls


def test_plan_transfer_collects_missing_directories(tmp_path) -> None:
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    file_a = src_dir / "a.txt"
    file_b = src_dir / "b.txt"
    file_a.write_text("a")
    file_b.write_text("b")

    controller = FileBrowserController(session=SimpleNamespace(), get_viewer=lambda: None)
    sheet = SimpleNamespace(directory=src_dir)
    entries = [SimpleNamespace(path=file_a), SimpleNamespace(path=file_b)]

    dest_dir = src_dir / "new" / "dest"
    plan = controller.plan_transfer("copy", str(dest_dir), entries=entries, sheet=sheet)

    assert plan.error is None
    assert plan.missing_directories == [dest_dir]
    assert plan.targets == [(file_a, dest_dir / "a.txt"), (file_b, dest_dir / "b.txt")]


def test_make_directory_reports_files(tmp_path) -> None:
    blocker = tmp_path / "test"
    blocker.write_text("x")

    controller = FileBrowserController(session=SimpleNamespace(), get_viewer=lambda: None)
    sheet = SimpleNamespace(directory=tmp_path)

    message, error = controller.make_directory(sheet=sheet, dest="test")

    assert message is None
    assert "not a directory" in (error or "")


def test_perform_transfer_requires_overwrite_permission(tmp_path) -> None:
    src = tmp_path / "src.txt"
    dest = tmp_path / "dest.txt"
    dest.write_text("old")
    src.write_text("new")

    controller = FileBrowserController(session=SimpleNamespace(), get_viewer=lambda: None)

    message, errors, completed = controller.perform_transfer(
        "copy", [(src, dest)], allow_overwrite=False
    )

    assert completed == 0
    assert message is None
    assert errors and "destination exists" in errors[0][1]
    assert dest.read_text() == "old"

    message, errors, completed = controller.perform_transfer(
        "copy", [(src, dest)], allow_overwrite=True
    )

    assert completed == 1
    assert not errors
    assert "Copied 1 item" in (message or "")
    assert dest.read_text() == "new"
