import polars as pl
import pytest

from pulka.api import Session
from pulka.tui.screen import Screen


@pytest.mark.parametrize("initial_enabled", [True, False])
def test_materialize_carries_insight_state(tmp_path, monkeypatch, initial_enabled):
    monkeypatch.setenv("PULKA_INSIGHT_PANEL", "1" if initial_enabled else "0")
    df = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    path = tmp_path / "data.parquet"
    df.write_parquet(path)

    session = Session(str(path), viewport_rows=8, viewport_cols=4)
    screen = Screen(session.viewer)
    try:
        # Align to the desired initial state explicitly.
        screen.set_insight_panel(initial_enabled)
        base_viewer = screen.viewer
        assert screen._insight_allowed
        assert screen._insight_enabled is initial_enabled

        screen._execute_command("materialize_all")

        assert screen.viewer is not base_viewer
        assert screen.view_stack.parent is base_viewer
        assert screen._insight_allowed
        assert screen._insight_enabled is initial_enabled
    finally:
        unsubscribe = getattr(screen, "_view_stack_unsubscribe", None)
        if callable(unsubscribe):
            unsubscribe()


@pytest.mark.parametrize(
    "command, attr_name",
    [("transpose", "is_transpose_view"), ("summary", "is_summary_view")],
)
def test_special_views_disable_insight_by_default(tmp_path, monkeypatch, command, attr_name):
    monkeypatch.setenv("PULKA_INSIGHT_PANEL", "1")
    df = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    path = tmp_path / "data.parquet"
    df.write_parquet(path)

    session = Session(str(path), viewport_rows=8, viewport_cols=4)
    screen = Screen(session.viewer)
    try:
        screen.set_insight_panel(True)
        assert screen._insight_enabled

        screen._execute_command(command)

        assert getattr(screen.viewer.sheet, attr_name, False)
        assert not screen._insight_enabled

        screen.set_insight_panel(True)
        assert screen._insight_enabled
    finally:
        unsubscribe = getattr(screen, "_view_stack_unsubscribe", None)
        if callable(unsubscribe):
            unsubscribe()
