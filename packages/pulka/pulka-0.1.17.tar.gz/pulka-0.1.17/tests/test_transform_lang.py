import polars as pl
import pytest

from pulka.data.transform_lang import TransformError, compile_transform


def _sample_lazyframe() -> pl.LazyFrame:
    frame = pl.DataFrame({"city": ["a", "a", "b"], "price": [1, 3, 2]})
    return frame.lazy()


def _columns(lf: pl.LazyFrame) -> list[str]:
    return lf.collect_schema().names()


def test_transform_adds_column():
    lf = _sample_lazyframe()
    transform = compile_transform(
        'lf.with_columns((c.price * 2).alias("price_x2"))', columns=_columns(lf)
    )
    result = transform(lf).collect()
    assert "price_x2" in result.columns
    assert result["price_x2"].to_list() == [2, 6, 4]


def test_transform_groupby_agg():
    lf = _sample_lazyframe()
    transform = compile_transform(
        'lf.group_by("city").agg(pl.col("price").mean().alias("avg_price"))',
        columns=_columns(lf),
    )
    result = transform(lf).collect().sort("city")
    assert result.to_dict(as_series=False) == {"city": ["a", "b"], "avg_price": [2.0, 2.0]}


@pytest.mark.parametrize(
    "expr",
    [
        "lf.collect()",
        "lf.write_parquet('out.parquet')",
        "pl.read_parquet('x.parquet')",
        "pl.from_dicts([])",
        "pl.read_database('dsn','select 1')",
    ],
)
def test_transform_forbids_io_and_collect(expr):
    lf = _sample_lazyframe()
    with pytest.raises(TransformError):
        compile_transform(expr, columns=_columns(lf))


def test_transform_requires_lazyframe_result():
    lf = _sample_lazyframe()
    transform = compile_transform("pl.DataFrame({'x': [1]}).lazy()", columns=_columns(lf))
    assert isinstance(transform(lf), pl.LazyFrame)

    bad = compile_transform("pl.DataFrame({'x': [1]})", columns=_columns(lf))
    with pytest.raises(TransformError):
        bad(lf)


def test_transform_rejects_unknown_name():
    lf = _sample_lazyframe()
    with pytest.raises(TransformError):
        compile_transform("lf.with_columns(foo.bar())", columns=_columns(lf))


def test_transform_allows_comprehension():
    lf = _sample_lazyframe()
    transform = compile_transform(
        "lf.with_columns([pl.lit(x).alias(f'name_{x}') for x in range(1)])",
        columns=_columns(lf),
    )
    result = transform(lf).collect()
    assert "name_0" in result.columns
