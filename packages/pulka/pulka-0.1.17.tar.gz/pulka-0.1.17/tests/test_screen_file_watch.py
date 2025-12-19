"""Tests for dataset file change detection in the TUI screen."""

from __future__ import annotations

import os
from types import SimpleNamespace

import polars as pl

os.environ["PULKA_TEST"] = "1"

from pulka.api.runtime import Runtime
from pulka.api.session import Session
from pulka.data.scanners import ScannerRegistry
from pulka.sheets.file_browser_sheet import FileBrowserSheet
from pulka.tui.screen import Screen


def _make_session(tmp_path):
    runtime = Runtime(load_entry_points=False)
    data_path = tmp_path / "watch.parquet"
    pl.DataFrame({"a": [1, 2, 3]}).write_parquet(data_path)
    session = runtime.open(str(data_path))
    return runtime, session, data_path


def _make_file_browser_session(tmp_path):
    sheet = FileBrowserSheet(tmp_path, scanners=ScannerRegistry())
    session = Session(None, initial_sheet=sheet)
    return session


def test_screen_detects_dataset_modification(monkeypatch, tmp_path) -> None:
    _runtime, session, data_path = _make_session(tmp_path)
    screen = Screen(session.viewer)
    triggered: list[tuple[object, bool | None]] = []

    def fake_schedule(self, path, snapshot):
        missing = None if snapshot is None else snapshot.missing
        triggered.append((path, missing))

    monkeypatch.setattr(Screen, "_schedule_file_change_prompt", fake_schedule, raising=False)

    screen._check_dataset_file_changes(force=True)
    assert not triggered

    pl.DataFrame({"a": [10]}).write_parquet(data_path)
    screen._check_dataset_file_changes(force=True)

    assert triggered
    assert triggered[-1][0] == data_path
    assert triggered[-1][1] is False

    session.close()


def test_screen_detects_dataset_removal(monkeypatch, tmp_path) -> None:
    _runtime, session, data_path = _make_session(tmp_path)
    screen = Screen(session.viewer)
    triggered: list[tuple[object, bool | None]] = []

    def fake_schedule(self, path, snapshot):
        missing = None if snapshot is None else snapshot.missing
        triggered.append((path, missing))

    monkeypatch.setattr(Screen, "_schedule_file_change_prompt", fake_schedule, raising=False)

    screen._check_dataset_file_changes(force=True)
    assert not triggered

    data_path.unlink()
    screen._check_dataset_file_changes(force=True)

    assert triggered
    assert triggered[-1][0] == data_path
    assert triggered[-1][1] is True

    session.close()


def test_screen_skips_insight_refresh_when_file_change_pending(tmp_path, monkeypatch) -> None:
    _runtime, session, _ = _make_session(tmp_path)
    screen = Screen(session.viewer)

    called = {"ran": False}

    def _boom():
        called["ran"] = True
        raise AssertionError("insight refresh should be skipped")

    screen._insight_controller = SimpleNamespace(on_refresh=_boom)
    screen._file_watch_prompt_active = True

    # Avoid touching the real terminal metrics during the test.
    monkeypatch.setattr(screen.viewer, "update_terminal_metrics", lambda: None)

    screen.refresh()

    assert called["ran"] is False
    assert "File changed" in screen._insight_panel._status_message

    session.close()


def test_refresh_forces_file_change_check(tmp_path, monkeypatch) -> None:
    _runtime, session, _ = _make_session(tmp_path)
    screen = Screen(session.viewer)

    force_calls: list[bool] = []

    def fake_check(*, force: bool = False):
        force_calls.append(force)

    monkeypatch.setattr(screen, "_check_dataset_file_changes", fake_check)
    monkeypatch.setattr(screen.viewer, "update_terminal_metrics", lambda: None)

    screen.refresh()

    assert force_calls and force_calls[-1] is True

    session.close()


def test_screen_detects_file_browser_change(tmp_path) -> None:
    session = _make_file_browser_session(tmp_path)
    screen = Screen(session.viewer)

    screen._check_file_browser_changes(force=True)
    new_file = tmp_path / "new.csv"
    new_file.write_text("a\n1\n")

    screen._check_file_browser_changes(force=True)

    sheet = screen.viewer.sheet
    names = [sheet.value_at(idx, "name") for idx in range(sheet.row_count() or 0)]
    assert "new.csv" in names
    assert "entries" in (screen.viewer.status_message or "")

    session.close()


def test_file_browser_refresh_clears_row_provider_cache(tmp_path) -> None:
    session = _make_file_browser_session(tmp_path)
    screen = Screen(session.viewer)
    viewer = screen.viewer

    provider = viewer.row_provider
    plan = viewer._current_plan()  # type: ignore[attr-defined]

    initial_slice, _ = provider.get_slice(plan, viewer.columns, 0, 100)
    initial_names = list(initial_slice.column("name").values)
    assert "cached.csv" not in initial_names

    new_file = tmp_path / "cached.csv"
    new_file.write_text("a\n1\n")

    screen._check_file_browser_changes(force=True)

    updated_slice, _ = provider.get_slice(plan, viewer.columns, 0, 100)
    updated_names = list(updated_slice.column("name").values)
    assert "cached.csv" in updated_names

    session.close()


def test_screen_deletes_selected_files(tmp_path) -> None:
    delete_one = tmp_path / "one.csv"
    delete_one.write_text("a\n1\n")
    delete_two = tmp_path / "two.csv"
    delete_two.write_text("a\n2\n")
    keep_file = tmp_path / "keep.csv"
    keep_file.write_text("a\n3\n")

    session = _make_file_browser_session(tmp_path)
    screen = Screen(session.viewer)
    sheet = screen.viewer.sheet

    names = [sheet.value_at(idx, "name") for idx in range(sheet.row_count() or 0)]
    selection_rows = {names.index("one.csv"), names.index("two.csv")}
    screen.viewer._selected_row_ids = selection_rows  # type: ignore[attr-defined]

    targets = screen._file_browser_delete_targets(sheet)
    screen._delete_file_browser_entries(sheet, targets)

    assert not delete_one.exists()
    assert not delete_two.exists()
    assert keep_file.exists()
    assert "Deleted 2 items" in (screen.viewer.status_message or "")
    assert not getattr(screen.viewer, "_selected_row_ids", None)

    session.close()


def test_screen_deletes_directories_recursive(tmp_path) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "inner.csv").write_text("a\n1\n")
    nested = folder / "nested"
    nested.mkdir()
    (nested / "deep.csv").write_text("a\n2\n")
    solo = tmp_path / "solo.csv"
    solo.write_text("a\n3\n")

    session = _make_file_browser_session(tmp_path)
    screen = Screen(session.viewer)
    sheet = screen.viewer.sheet

    names = [sheet.value_at(idx, "name") for idx in range(sheet.row_count() or 0)]
    selection_rows = {names.index("folder/"), names.index("solo.csv")}
    screen.viewer._selected_row_ids = selection_rows  # type: ignore[attr-defined]

    targets = screen._file_browser_delete_targets(sheet)
    screen._delete_file_browser_entries(sheet, targets)

    assert not folder.exists()
    assert not solo.exists()
    assert "Deleted 2 items" in (screen.viewer.status_message or "")

    session.close()


def test_screen_copies_selection(tmp_path) -> None:
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    src_dir.mkdir()
    dst_dir.mkdir()

    file_a = src_dir / "a.csv"
    file_a.write_text("a\n1\n")
    file_b = src_dir / "b.csv"
    file_b.write_text("b\n2\n")

    session = _make_file_browser_session(src_dir)
    screen = Screen(session.viewer)
    sheet = screen.viewer.sheet

    names = [sheet.value_at(idx, "name") for idx in range(sheet.row_count() or 0)]
    selection_rows = {names.index("a.csv"), names.index("b.csv")}
    screen.viewer._selected_row_ids = selection_rows  # type: ignore[attr-defined]

    screen._request_file_transfer("copy", str(dst_dir))

    assert (dst_dir / "a.csv").exists()
    assert (dst_dir / "b.csv").exists()
    assert "Copied 2 items" in (screen.viewer.status_message or "")

    session.close()


def test_screen_moves_single_file_with_rename(tmp_path) -> None:
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    src_dir.mkdir()
    dst_dir.mkdir()
    file_a = src_dir / "a.csv"
    file_a.write_text("a\n1\n")

    session = _make_file_browser_session(src_dir)
    screen = Screen(session.viewer)

    screen._request_file_transfer("move", str(dst_dir / "renamed.csv"))

    assert not file_a.exists()
    assert (dst_dir / "renamed.csv").exists()
    assert "Moved 1 item" in (screen.viewer.status_message or "")

    session.close()
