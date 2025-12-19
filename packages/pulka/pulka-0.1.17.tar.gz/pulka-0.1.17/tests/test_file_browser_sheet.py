from __future__ import annotations

from pathlib import Path

import polars as pl

from pulka.api.session import Session
from pulka.core.viewer import Viewer
from pulka.data.scanners import ScannerRegistry
from pulka.render.viewport_plan import compute_viewport_plan
from pulka.sheets.data_sheet import DataSheet
from pulka.sheets.file_browser_sheet import FileBrowserSheet
from pulka.tui.screen import Screen


def _create_sheet(path: Path) -> FileBrowserSheet:
    return FileBrowserSheet(path, scanners=ScannerRegistry())


def test_file_browser_layout_hints(tmp_path: Path):
    sheet = _create_sheet(tmp_path)

    assert sheet.compact_width_layout is False
    assert sheet.preferred_fill_column == "name"


def test_file_browser_lists_supported_entries(tmp_path: Path) -> None:
    (tmp_path / "subdir").mkdir()
    (tmp_path / "data.csv").write_text("a,b\n1,2\n")
    (tmp_path / "workbook.xlsx").write_text("noop")
    (tmp_path / "ignore.txt").write_text("noop")

    sheet = _create_sheet(tmp_path)
    names = [sheet.value_at(idx, "name") for idx in range(sheet.row_count() or 0)]

    assert "subdir/" in names
    assert "data.csv" in names
    assert "workbook.xlsx" in names
    assert "ignore.txt" not in names
    if tmp_path.parent != tmp_path:
        assert names[0] == ".."


def test_file_browser_actions(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("a\n1\n")
    sheet = _create_sheet(tmp_path)

    names = [sheet.value_at(idx, "name") for idx in range(sheet.row_count() or 0)]
    dir_row = names.index("nested/")
    file_row = names.index("sample.csv")

    dir_action = sheet.action_for_row(dir_row)
    file_action = sheet.action_for_row(file_row)

    assert dir_action is not None
    assert dir_action.type == "enter-directory"
    assert dir_action.path == nested

    assert file_action is not None
    assert file_action.type == "open-file"
    assert file_action.path == csv_path


def test_file_browser_viewport_navigation_commands(tmp_path: Path) -> None:
    for idx in range(8):
        (tmp_path / f"file-{idx}.csv").write_text("a\n1\n")

    sheet = _create_sheet(tmp_path)
    session = Session(None, initial_sheet=sheet, viewport_rows=5)
    viewer = session.viewer
    assert viewer is not None

    try:
        viewer.configure_terminal(width=80, height=5)
        viewer.get_visible_table_slice(viewer.columns)
        visible_rows = viewer.visible_row_positions
        assert len(visible_rows) >= 2

        runtime = session.command_runtime

        viewer.cur_row = visible_rows[-1]
        runtime.invoke("viewport_top", source="test")
        assert viewer.cur_row == viewer.visible_row_positions[0]

        viewer.get_visible_table_slice(viewer.columns)
        viewer.cur_row = viewer.visible_row_positions[0]
        runtime.invoke("viewport_middle", source="test")
        middle_row = viewer.visible_row_positions[(len(viewer.visible_row_positions) - 1) // 2]
        assert viewer.cur_row == middle_row

        viewer.get_visible_table_slice(viewer.columns)
        viewer.cur_row = viewer.visible_row_positions[0]
        runtime.invoke("viewport_bottom", source="test")
        assert viewer.cur_row == viewer.visible_row_positions[-1]

        viewer.get_visible_table_slice(viewer.columns)
        viewer.cur_row = viewer.visible_row_positions[0]
        runtime.invoke("center", source="test")
        assert viewer.status_message == "centered"
    finally:
        session.close()


def test_file_browser_can_jump_to_new_directory(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    sheet = _create_sheet(tmp_path)

    child_sheet = sheet.at_path(nested)
    assert child_sheet.display_path.endswith("nested")
    if nested.parent != nested:
        assert child_sheet.value_at(0, "name") == ".."


def test_file_browser_len_matches_row_count(tmp_path: Path) -> None:
    (tmp_path / "data.csv").write_text("a\n1\n")
    sheet = _create_sheet(tmp_path)
    assert len(sheet) == sheet.row_count()


def test_file_browser_can_show_unknown_when_configured(tmp_path: Path, monkeypatch) -> None:
    import pulka.data.scan as scan_mod

    (tmp_path / "data").write_text("x")

    monkeypatch.setattr(scan_mod, "_BROWSER_STRICT_EXTENSIONS", False)
    sheet = _create_sheet(tmp_path)
    names = [sheet.value_at(idx, "name") for idx in range(sheet.row_count() or 0)]
    assert "data" in names


def test_insight_panel_allowed_after_browser_open(tmp_path: Path) -> None:
    data_path = tmp_path / "sample.csv"
    data_path.write_text("a\n1\n")

    browser = _create_sheet(tmp_path)
    session = Session(None, initial_sheet=browser)
    screen = Screen(session.viewer)
    try:
        assert not screen._insight_allowed  # browser should disable insight

        screen._open_file_from_browser(data_path)

        assert not getattr(screen.viewer.sheet, "is_file_browser", False)
        assert screen._insight_allowed
    finally:
        unsubscribe = getattr(screen, "_view_stack_unsubscribe", None)
        if callable(unsubscribe):
            unsubscribe()


def test_file_browser_maximizes_name_column(tmp_path: Path, job_runner) -> None:
    (tmp_path / "data.csv").write_text("a\n1\n")
    sheet = _create_sheet(tmp_path)

    viewer = Viewer(sheet, runner=job_runner)

    assert viewer.width_mode_state["mode"] == "default"
    assert viewer.maximized_column_index is None

    plan = compute_viewport_plan(viewer, width=120, height=10)
    name_plan = next(col for col in plan.columns if col.name == "name")
    other_widths = [col.width for col in plan.columns if col.name in {"type", "size", "modified"}]

    assert name_plan.width > max(other_widths)


def test_file_browser_width_resets_after_replacing_sheet(tmp_path: Path, job_runner) -> None:
    (tmp_path / "data.csv").write_text("a\n1\n")
    sheet = _create_sheet(tmp_path)
    viewer = Viewer(sheet, runner=job_runner)

    df = pl.DataFrame({"value": [1, 2]}).lazy()
    data_sheet = DataSheet(df, runner=job_runner)
    viewer.replace_sheet(data_sheet)

    assert viewer.width_mode_state["mode"] == "default"
    assert viewer.maximized_column_index is None


def test_file_browser_refresh_detects_directory_changes(tmp_path: Path) -> None:
    (tmp_path / "alpha.csv").write_text("a\n1\n")
    sheet = _create_sheet(tmp_path)

    # No changes yet
    assert sheet.refresh_from_disk() is False

    beta = tmp_path / "beta.csv"
    beta.write_text("b\n2\n")

    assert sheet.refresh_from_disk() is True
    names = [sheet.value_at(idx, "name") for idx in range(sheet.row_count() or 0)]
    assert "beta.csv" in names

    sizes_snapshot = [sheet.value_at(idx, "size") for idx in range(sheet.row_count() or 0)]

    # Re-running without touching the filesystem should report no change
    assert sheet.refresh_from_disk() is False

    alpha = tmp_path / "alpha.csv"
    alpha.write_text("a\n1\n2\n")

    assert sheet.refresh_from_disk() is True
    sizes = [sheet.value_at(idx, "size") for idx in range(sheet.row_count() or 0)]
    assert sizes != sizes_snapshot


def test_file_browser_delete_entries(tmp_path: Path) -> None:
    remove_me = tmp_path / "remove.csv"
    remove_me.write_text("a\n1\n")
    keep_me = tmp_path / "keep.csv"
    keep_me.write_text("a\n1\n")

    sheet = _create_sheet(tmp_path)
    names = [sheet.value_at(idx, "name") for idx in range(sheet.row_count() or 0)]
    delete_row = names.index("remove.csv")

    targets = sheet.deletable_entries_for_rows([delete_row])
    assert len(targets) == 1

    result = sheet.delete_entries(targets)

    assert not remove_me.exists()
    assert keep_me.exists()
    assert result.deleted == (remove_me,)
    assert not result.errors

    refreshed = [sheet.value_at(idx, "name") for idx in range(sheet.row_count() or 0)]
    assert "remove.csv" not in refreshed
    assert "keep.csv" in refreshed


def test_file_browser_delete_directory_recursive(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "inner.csv").write_text("a\n1\n")
    nested = folder / "nested"
    nested.mkdir()
    (nested / "deep.csv").write_text("a\n2\n")

    sheet = _create_sheet(tmp_path)
    names = [sheet.value_at(idx, "name") for idx in range(sheet.row_count() or 0)]
    folder_row = names.index("folder/")

    targets = sheet.deletable_entries_for_rows([folder_row])
    assert len(targets) == 1

    file_count, count_errors = sheet.deletion_impact(targets)
    assert count_errors == []
    assert file_count == 2

    result = sheet.delete_entries(targets)
    assert not folder.exists()
    assert result.deleted == (folder,)
