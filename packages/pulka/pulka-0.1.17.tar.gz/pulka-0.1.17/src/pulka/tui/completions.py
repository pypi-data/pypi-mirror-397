"""Prompt-toolkit completions for Pulka TUI."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from prompt_toolkit.completion import (
    Completer,
    Completion,
)
from prompt_toolkit.completion import (
    PathCompleter as PTKPathCompleter,
)
from prompt_toolkit.document import Document


class ColumnNameCompleter(Completer):
    """Prompt-toolkit completer that suggests column names."""

    def __init__(self, columns, *, mode: str = "expr") -> None:
        self._columns = list(columns)
        self._mode = mode
        identifier_columns = [name for name in columns if name.isidentifier()]
        self._sorted_identifier_columns = sorted(
            identifier_columns, key=lambda x: (len(x), x.lower())
        )
        non_identifier_columns = [name for name in columns if not name.isidentifier()]
        self._sorted_non_identifier_columns = sorted(
            non_identifier_columns, key=lambda x: (len(x), x.lower())
        )
        self._sorted_all_columns = sorted(columns, key=lambda x: (len(x), x.lower()))

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        if self._mode == "plain":
            prefix = text
            prefix_lower = prefix.lower()
            start = -len(prefix)

            candidates = self._sorted_all_columns
            matched = False
            for name in candidates:
                if not prefix_lower or prefix_lower in name.lower():
                    matched = True
                    yield Completion(name, start_position=start, display_meta="column")

            if not matched and complete_event.completion_requested:
                for name in candidates:
                    yield Completion(name, start_position=start, display_meta="column")
            return

        if self._mode == "sql":
            yield from self._sql_completions(text, complete_event)
            return

        attr_match = re.search(r"c\.([A-Za-z_]\w*)?$", text)
        if attr_match:
            prefix = attr_match.group(1) or ""
            prefix_lower = prefix.lower()

            for name in self._sorted_identifier_columns:
                if name.lower().startswith(prefix_lower):
                    yield Completion(name, start_position=-len(prefix), display_meta="column")
            return

        bracket_match = re.search(r"c\[(?:\s*['\"])([^'\"]*)$", text)
        if bracket_match:
            prefix = bracket_match.group(1)
            prefix_lower = prefix.lower()

            for name in self._sorted_all_columns:
                if name.lower().startswith(prefix_lower):
                    yield Completion(name, start_position=-len(prefix), display_meta="column")

    def _sql_completions(self, text: str, complete_event):
        dq_match = re.search(r'"([^"\\]*)$', text)
        if dq_match:
            prefix = dq_match.group(1)
            prefix_lower = prefix.lower()
            start = -len(prefix)
            for name in self._sorted_all_columns:
                escaped_name = name.replace('"', '""')
                if escaped_name.lower().startswith(prefix_lower):
                    replacement = escaped_name + '"'
                    yield Completion(replacement, start_position=start, display_meta="column")
            return

        dot_match = re.search(r"\.([A-Za-z_][A-Za-z0-9_]*)?$", text)
        if dot_match:
            prefix = dot_match.group(1) or ""
            prefix_lower = prefix.lower()
            start = -len(prefix)
            for name in self._sorted_identifier_columns:
                if name.lower().startswith(prefix_lower):
                    yield Completion(name, start_position=start, display_meta="column")
            return

        ident_match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)$", text)
        if ident_match:
            prefix = ident_match.group(1)
            prefix_lower = prefix.lower()
            start = -len(prefix)
            for name in self._sorted_identifier_columns:
                if name.lower().startswith(prefix_lower):
                    yield Completion(name, start_position=start, display_meta="column")
            return

        if complete_event.completion_requested:
            for name in self._sorted_identifier_columns:
                yield Completion(name, start_position=0, display_meta="column")
            for name in self._sorted_non_identifier_columns:
                yield Completion(
                    self._quote_identifier(name),
                    start_position=0,
                    display_meta="column",
                )

    @staticmethod
    def _quote_identifier(name: str) -> str:
        escaped = name.replace('"', '""')
        return f'"{escaped}"'


class FilesystemPathCompleter(Completer):
    """Lightweight wrapper to suggest filesystem paths relative to a base dir."""

    def __init__(self, get_base_dir: Callable[[], Path | str | None]) -> None:
        self._get_base_dir = get_base_dir

    def _base_dir(self) -> Path | None:
        raw_base = self._get_base_dir()
        if raw_base is None:
            return None
        try:
            return Path(raw_base)
        except Exception:
            return None

    @staticmethod
    def _should_complete(text: str, *, completion_requested: bool) -> bool:
        if not text:
            return False
        last_token = text.rsplit(" ", 1)[-1]
        stripped = last_token.lstrip("\"' ")
        has_path_hint = "/" in stripped or stripped.startswith(("~", "."))
        if " " in text or has_path_hint:
            return True
        return completion_requested and has_path_hint

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not self._should_complete(
            text, completion_requested=complete_event.completion_requested
        ):
            return

        token = text.rsplit(" ", 1)[-1]
        base_dir = self._base_dir()

        _get_paths: Callable[[], list[Path]] | None = None
        if base_dir is not None:

            def _get_paths() -> list[Path]:
                return [base_dir]

        path_completer = PTKPathCompleter(expanduser=True, get_paths=_get_paths)
        token_doc = Document(token, cursor_position=len(token))

        for completion in path_completer.get_completions(token_doc, complete_event):
            yield Completion(
                completion.text,
                start_position=completion.start_position,
                display=completion.display,
                display_meta=completion.display_meta,
            )
