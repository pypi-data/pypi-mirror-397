"""Prompt-toolkit layout wiring for :class:`pulka.tui.screen.Screen`."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    FloatContainer,
    HSplit,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension

from ..core.viewer import Viewer
from .controls.column_insight_panel import ColumnInsightPanel


@dataclass(slots=True)
class ScreenLayoutParts:
    use_ptk_table: bool
    table_control: Any
    status_control: FormattedTextControl
    table_window: Window
    status_window: Window
    insight_panel: ColumnInsightPanel
    insight_control: FormattedTextControl
    insight_window: Window
    insight_border: ConditionalContainer
    insight_border_padding: ConditionalContainer
    insight_container: ConditionalContainer
    window: FloatContainer


def build_screen_layout(
    *,
    viewer: Viewer,
    use_ptk_table: bool,
    build_ptk_table_control: Callable[[], Any],
    get_table_text: Callable[[], Any],
    get_status_text: Callable[[], StyleAndTextTuples],
    insight_enabled: Callable[[], bool],
    insight_allowed: Callable[[], bool],
) -> ScreenLayoutParts:
    del viewer

    table_control = (
        build_ptk_table_control() if use_ptk_table else FormattedTextControl(get_table_text)
    )
    table_window = Window(
        content=table_control,
        wrap_lines=False,
        always_hide_cursor=not use_ptk_table,
    )

    status_control = FormattedTextControl(get_status_text)
    status_window = Window(
        height=1,
        content=status_control,
        wrap_lines=False,
        always_hide_cursor=True,
    )

    insight_panel = ColumnInsightPanel()
    insight_control = FormattedTextControl(lambda: insight_panel.render_fragments())
    insight_window = Window(
        content=insight_control,
        width=Dimension.exact(insight_panel.width),
        wrap_lines=True,
        always_hide_cursor=True,
    )

    insight_filter = Condition(lambda: insight_enabled() and insight_allowed())
    insight_border = ConditionalContainer(
        content=Window(
            width=Dimension.exact(1),
            char="│",
            style="class:table.separator",
            always_hide_cursor=True,
        ),
        filter=insight_filter,
    )
    insight_border_padding = ConditionalContainer(
        content=Window(
            width=Dimension.exact(1),
            char=" ",
            always_hide_cursor=True,
        ),
        filter=insight_filter,
    )
    insight_container = ConditionalContainer(
        content=insight_window,
        filter=insight_filter,
    )

    table_row = VSplit(
        [
            table_window,
            insight_border,
            insight_border_padding,
            insight_container,
        ],
        padding=0,
    )
    body = HSplit([table_row, status_window])
    window = FloatContainer(content=body, floats=[])

    return ScreenLayoutParts(
        use_ptk_table=use_ptk_table,
        table_control=table_control,
        status_control=status_control,
        table_window=table_window,
        status_window=status_window,
        insight_panel=insight_panel,
        insight_control=insight_control,
        insight_window=insight_window,
        insight_border=insight_border,
        insight_border_padding=insight_border_padding,
        insight_container=insight_container,
        window=window,
    )
