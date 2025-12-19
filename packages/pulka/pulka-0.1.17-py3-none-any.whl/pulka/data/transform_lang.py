"""
Transform language compiler for Pulka.

Parses a user-provided expression that transforms a Polars ``LazyFrame`` and
returns a callable that applies it, with safety checks to block I/O or eager
collection.
"""

from __future__ import annotations

import ast
from collections.abc import Callable, Sequence

import polars as pl

from .filter_lang import ColumnNamespace


class TransformError(ValueError):
    """Raised when a transform expression cannot be parsed or evaluated."""


_ALLOWED_NODE_TYPES = (
    ast.Expression,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.Call,
    ast.Attribute,
    ast.Subscript,
    ast.Slice,
    ast.Name,
    ast.Load,
    ast.Store,
    ast.Constant,
    ast.List,
    ast.Tuple,
    ast.Dict,
    ast.keyword,
    ast.Lambda,
    ast.IfExp,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
    ast.JoinedStr,
    ast.FormattedValue,
)

_FORBIDDEN_ATTR_SUFFIXES = ("collect", "fetch")
_FORBIDDEN_ATTR_PREFIXES = ("sink_", "write_")
_FORBIDDEN_PL_PREFIXES = ("read_", "scan_", "write_", "sink_", "from_")
_FORBIDDEN_PL_NAMES = {"SQLContext", "read_database"}


def _validate_ast(node: ast.AST) -> None:
    allowed_names = {"lf", "pl", "c", "col", "lit", "True", "False", "None", "range"}
    extra_allowed = (ast.operator, ast.unaryop, ast.boolop, ast.cmpop, ast.comprehension)
    local_names = {
        n.id
        for n in ast.walk(node)
        if isinstance(n, ast.Name) and isinstance(getattr(n, "ctx", None), ast.Store)
    }
    for child in ast.walk(node):
        if not isinstance(child, _ALLOWED_NODE_TYPES + extra_allowed):
            raise TransformError("Unsupported syntax in transform expression")
        if isinstance(child, ast.Attribute) and child.attr.startswith("_"):
            raise TransformError("Attribute access starting with '_' is not allowed")
        if isinstance(child, ast.Name):
            if isinstance(getattr(child, "ctx", None), ast.Store):
                continue
            if child.id not in allowed_names and child.id not in local_names:
                raise TransformError(f"Unknown name '{child.id}' in transform expression")


def _is_forbidden_call(node: ast.Call) -> str | None:
    target = node.func
    if isinstance(target, ast.Attribute):
        attr = target.attr
        if attr in _FORBIDDEN_ATTR_SUFFIXES or any(
            attr.startswith(prefix) for prefix in _FORBIDDEN_ATTR_PREFIXES
        ):
            return attr
        if (
            isinstance(target.value, ast.Name)
            and target.value.id == "pl"
            and (
                attr in _FORBIDDEN_PL_NAMES
                or any(attr.startswith(prefix) for prefix in _FORBIDDEN_PL_PREFIXES)
            )
        ):
            return attr
    elif isinstance(target, ast.Name):
        name = target.id
        if name in _FORBIDDEN_ATTR_SUFFIXES or any(
            name.startswith(prefix) for prefix in _FORBIDDEN_ATTR_PREFIXES
        ):
            return name
    return None


def compile_transform(text: str, columns: Sequence[str]) -> Callable[[pl.LazyFrame], pl.LazyFrame]:
    """Return a callable that applies ``text`` to a ``LazyFrame``."""

    normalized = text.strip()
    if not normalized:
        raise TransformError("Transform expression cannot be empty")

    try:
        tree = ast.parse(normalized, mode="eval")
    except SyntaxError as exc:  # pragma: no cover - defensive
        raise TransformError(f"Invalid transform syntax: {exc.msg}") from exc

    _validate_ast(tree)

    for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
        forbidden = _is_forbidden_call(call)
        if forbidden is not None:
            raise TransformError(f"Forbidden call in transform: {forbidden}")

    namespace = ColumnNamespace(columns)
    env = {
        "lf": None,  # placeholder, injected per invocation
        "pl": pl,
        "c": namespace,
        "col": pl.col,
        "lit": pl.lit,
        "range": range,
        "True": True,
        "False": False,
        "None": None,
    }

    compiled = compile(tree, "<transform>", "eval")

    def _apply(lf: pl.LazyFrame) -> pl.LazyFrame:
        env["lf"] = lf
        try:
            result = eval(compiled, {"__builtins__": {}}, env)  # noqa: S307
        except TransformError:
            raise
        except Exception as exc:
            raise TransformError(str(exc)) from exc
        if not isinstance(result, pl.LazyFrame):
            raise TransformError("Transform must return a Polars LazyFrame")
        return result

    return _apply


__all__ = ["TransformError", "compile_transform"]
