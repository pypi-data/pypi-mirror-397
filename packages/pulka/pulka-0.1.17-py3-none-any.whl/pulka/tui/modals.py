"""
TUI modal dialogs for Pulka.

This module provides filter prompts, search dialogs, error messages,
and other modal interactions in the terminal user interface.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.widgets import Box, Label, TextArea


def build_lines_body(lines: Sequence[str], *, line_padding: int = 1, padding: int = 1) -> Box:
    labels = [Label(text=line) for line in lines]
    return Box(body=HSplit(labels, padding=line_padding), padding=padding)


def build_prompt_body(prompt: str, field: TextArea, *, padding: int = 1) -> Box:
    content = HSplit([Label(prompt, dont_extend_height=True), field], padding=0)
    return Box(body=content, padding=padding)


def merge_text_area_key_bindings(text_area: TextArea, key_bindings: KeyBindings) -> None:
    existing = text_area.control.key_bindings
    if existing is None:
        text_area.control.key_bindings = key_bindings
        return
    text_area.control.key_bindings = merge_key_bindings([existing, key_bindings])


def bind_enter_to_accept(text_area: TextArea) -> None:
    """Treat Enter as submit for multiline text areas."""

    field_kb = KeyBindings()

    @field_kb.add("enter")
    def _apply_from_enter(event) -> None:
        event.current_buffer.validate_and_handle()

    merge_text_area_key_bindings(text_area, field_kb)


def bind_close_keys(
    text_area: TextArea,
    *,
    on_close: Callable[[object], None],
    keys: Sequence[str] = ("escape", "enter"),
) -> None:
    kb = KeyBindings()

    def _close(event) -> None:
        on_close(event.app)

    for key in keys:
        kb.add(key)(_close)

    merge_text_area_key_bindings(text_area, kb)
