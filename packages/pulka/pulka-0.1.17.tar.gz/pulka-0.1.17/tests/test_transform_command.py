import polars as pl

from pulka.api.runtime import Runtime
from pulka.testing.data import write_df


def _open_session(tmp_path):
    df = pl.DataFrame({"c0": [1, 2, 3, 4], "c1": [10, 20, 30, 40]})
    path = tmp_path / "transform_cmd.parquet"
    write_df(df, path, "parquet")
    runtime = Runtime(load_entry_points=False)
    return runtime.open(str(path), viewport_rows=4)


def test_transform_command_pushes_derived_view(tmp_path):
    session = _open_session(tmp_path)
    runtime = session.command_runtime
    base_viewer = session.viewer

    result = runtime.invoke(
        "transform",
        args=['lf.with_columns((c.c0 * 2).alias("c0_x2"))'],
        source="test",
    )

    assert result.dispatch is not None
    assert result.dispatch.spec.name == "transform"
    assert len(session.view_stack.viewers) == 2
    derived = session.viewer
    assert derived is not base_viewer
    assert "c0_x2" in derived.columns


def test_transform_command_rejects_forbidden_call(tmp_path):
    session = _open_session(tmp_path)
    runtime = session.command_runtime
    base_viewer = session.viewer

    runtime.invoke("transform", args=["lf.collect()"], source="test")

    assert session.viewer is base_viewer
    assert len(session.view_stack.viewers) == 1
    assert "Forbidden call" in (base_viewer.status_message or "")
