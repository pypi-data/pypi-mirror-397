"""
Keymap definitions for the Pulka TUI.

This module centralises prompt_toolkit key bindings so `Screen` stays focused on
orchestration rather than inline binding setup.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings

from pulka_builtin_plugins.freq.plugin import open_frequency_viewer
from pulka_builtin_plugins.transpose.plugin import open_transpose_viewer

if TYPE_CHECKING:
    from ..core.viewer import Viewer
    from .screen import Screen


def _select_source_viewer(viewers: Sequence[Viewer], column: str) -> Viewer | None:
    """Return the most recent non-derived viewer whose sheet exposes ``column``."""

    for viewer in reversed(viewers):
        if getattr(viewer, "is_hist_view", False) or getattr(viewer, "is_freq_view", False):
            continue
        schema = getattr(viewer.sheet, "schema", {}) or {}
        if column in schema:
            return viewer
    return None


def build_key_bindings(screen: Screen) -> KeyBindings:
    """Return key bindings configured for the provided screen instance."""

    kb = KeyBindings()
    modal_inactive = Condition(lambda: not screen._modal_manager.active)
    modal_active = ~modal_inactive

    @kb.add("escape", filter=modal_active, eager=True)
    def _(event):
        screen._record_key_event(event)
        ctx = screen._modal_manager.context
        ctx_type = ctx.get("type") if ctx else None
        if ctx and ctx_type in {"expr_filter", "sql_filter", "transform"}:
            # Check if filter field has text; if so, clear it first
            filter_field = ctx.get("field")
            if filter_field and filter_field.text:
                filter_field.text = ""
                filter_field.buffer.cursor_position = 0
                return
        screen._remove_modal(event.app)
        if ctx:
            if ctx_type == "search":
                screen.viewer.status_message = "search canceled"
            elif ctx_type == "expr_filter":
                screen.viewer.status_message = "filter canceled"
            elif ctx_type == "sql_filter":
                screen.viewer.status_message = "SQL filter canceled"
            elif ctx_type == "transform":
                screen.viewer.status_message = "transform canceled"
            elif ctx_type == "column_search":
                screen.viewer.status_message = "column search canceled"
                screen._clear_column_search()
            elif ctx_type == "command":
                screen.viewer.status_message = "command canceled"
            elif ctx_type == "file_change":
                screen._complete_file_change_prompt(reload_file=False)
        screen.refresh()

    @kb.add("q", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        # Back if on a derived view; quit if at root
        if len(screen.view_stack) > 1:
            screen._pop_viewer()
            screen.refresh()
        else:
            event.app.exit()

    @kb.add("c-r", filter=modal_inactive, eager=True)
    def _(event):
        screen._record_key_event(event)
        screen._reload_dataset()

    # Move
    @kb.add("j", filter=modal_inactive)
    @kb.add("down", filter=modal_inactive)
    def _(event):
        screen._clear_g_buf()
        screen._execute_command("down")
        screen._record_key_event(event)
        screen.refresh()

    @kb.add("k", filter=modal_inactive)
    @kb.add("up", filter=modal_inactive)
    def _(event):
        screen._clear_g_buf()
        screen._execute_command("up")
        screen._record_key_event(event)
        screen.refresh()

    @kb.add("h", filter=modal_inactive)
    @kb.add("left", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("left")
        screen.refresh()

    @kb.add("H", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("slide_left")
        screen.refresh()

    @kb.add("l", filter=modal_inactive)
    @kb.add("right", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("right")
        screen.refresh()

    @kb.add("L", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("slide_right")
        screen.refresh()

    @kb.add("pageup", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("pageup")
        screen.refresh()

    @kb.add("pagedown", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("pagedown")
        screen.refresh()

    @kb.add("y", "y", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("yank_cell")
        screen.refresh()

    @kb.add("y", "p", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("yank_path")
        screen.refresh()

    @kb.add("y", "c", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("yank_column")
        screen.refresh()

    @kb.add("y", "a", "c", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("yank_all_columns")
        screen.refresh()

    @kb.add("y", "s", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("yank_schema")
        screen.refresh()

    @kb.add("g", "g", filter=modal_inactive)  # gg top
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("top")
        screen.refresh(skip_metrics=True)

    @kb.add("g", "h", filter=modal_inactive)  # first column overall
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("first_overall")
        screen.refresh()

    @kb.add("g", "l", filter=modal_inactive)  # last column overall
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("last_overall")
        screen.refresh()

    @kb.add("g", "H", filter=modal_inactive)  # slide current column to first
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("slide_first")
        screen.refresh()

    @kb.add("g", "L", filter=modal_inactive)  # slide current column to last
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("slide_last")
        screen.refresh()

    @kb.add("g", "_", filter=modal_inactive)  # maximize all columns
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("maxall")
        screen.refresh()

    @kb.add("G", filter=modal_inactive)  # bottom (best effort)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("bottom")
        screen.refresh()

    @kb.add("0", filter=modal_inactive)  # first col
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("first")
        screen.refresh()

    @kb.add("$", filter=modal_inactive)  # last col
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("last")
        screen.refresh()

    @kb.add("_", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("maxcol")
        screen.refresh()

    @kb.add("z", "z", filter=modal_inactive)  # center current row
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("center")
        screen.refresh()

    @kb.add("z", "t", filter=modal_inactive)  # first visible row
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("viewport_top")
        screen.refresh()

    @kb.add("z", "m", filter=modal_inactive)  # middle visible row
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("viewport_middle")
        screen.refresh()

    @kb.add("z", "b", filter=modal_inactive)  # last visible row
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("viewport_bottom")
        screen.refresh()

    @kb.add("<", filter=modal_inactive)  # prev different value
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("prev_different")
        screen.refresh()

    @kb.add(">", filter=modal_inactive)  # next different value
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("next_different")
        screen.refresh()

    @kb.add("s", filter=modal_inactive)  # sort toggle by current column
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("sort")
        screen.refresh()

    @kb.add("e", filter=modal_inactive)  # expression filter
    def _(event):
        screen._record_key_event(event)
        screen._open_filter_modal(event)

    @kb.add("E", filter=modal_inactive, eager=True)  # transform modal
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._open_transform_modal(event)

    @kb.add("f", filter=modal_inactive)  # SQL filter
    def _(event):
        screen._record_key_event(event)
        screen._open_sql_filter_modal(event)

    @kb.add("c", filter=modal_inactive)  # column search modal
    def _(event):
        screen._record_key_event(event)
        screen._open_column_search_modal(event)

    @kb.add("|", filter=modal_inactive)  # select rows containing text in current column
    def _(event):
        screen._record_key_event(event)
        screen._open_row_search_modal(event)

    @kb.add("/", filter=modal_inactive)  # search current column
    def _(event):
        screen._record_key_event(event)
        screen._open_search_modal(event)

    @kb.add("*", filter=modal_inactive)  # next match for current cell value
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("search_value_next")
        screen.refresh()

    @kb.add("#", filter=modal_inactive)  # previous match for current cell value
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("search_value_prev")
        screen.refresh()

    @kb.add("n", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        if screen._handle_column_search_navigation(forward=True):
            screen.refresh()
            return
        screen._execute_command("next_diff")
        screen.refresh()

    @kb.add("N", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        if screen._handle_column_search_navigation(forward=False):
            screen.refresh()
            return
        screen._execute_command("prev_diff")
        screen.refresh()

    @kb.add("r", "r", filter=modal_inactive)  # reset filters/sorts/selection
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("reset")
        screen.refresh()

    @kb.add("r", "e", filter=modal_inactive)  # reset expression filters
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("reset_expr_filter")
        screen.refresh()

    @kb.add("r", "f", filter=modal_inactive)  # reset SQL filters
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("reset_sql_filter")
        screen.refresh()

    @kb.add("r", "s", filter=modal_inactive)  # reset sorts
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("reset_sort")
        screen.refresh()

    @kb.add("r", "_", filter=modal_inactive)  # reset maximized widths
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("resetmax")
        screen.refresh()

    @kb.add("r", " ", filter=modal_inactive)  # reset selection (alias to gu)
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("clear_selection")
        screen.refresh()

    @kb.add("@", filter=modal_inactive)  # flight recorder toggle
    def _(event):
        screen._toggle_recorder(event)

    @kb.add(":", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        screen._open_command_modal(event)

    @kb.add("?", filter=modal_inactive)  # schema
    def _(event):
        screen._record_key_event(event)
        # In TUI mode, show schema in a modal rather than using the command
        schema_text = "\n".join(f"{k}: {v}" for k, v in screen.viewer.sheet.schema.items())
        screen._open_text_modal(event, "Schema", schema_text)

    @kb.add("i", filter=modal_inactive)  # toggle insight panel
    def _(event):
        screen._record_key_event(event)
        screen.set_insight_panel()

    @kb.add("C", filter=modal_inactive)  # column summary (Shift+C)
    def _(event):
        screen._record_key_event(event)
        if not screen.viewer.columns:
            return
        screen._execute_command("summary")
        screen.refresh()

    @kb.add("F", filter=modal_inactive)  # frequency table of the current column
    def _(event):
        screen._record_key_event(event)
        if not screen.viewer.columns:
            return
        colname = screen.viewer.columns[screen.viewer.cur_col]
        source_viewer = _select_source_viewer(screen.view_stack.viewers, colname)
        if source_viewer is None:
            screen.viewer.status_message = f"frequency view unavailable for column {colname}"
            screen.refresh()
            return
        try:
            screen.viewer = open_frequency_viewer(
                source_viewer,
                colname,
                session=screen.session,
                view_stack=screen.view_stack,
                screen=screen,
            )
        except Exception as exc:
            screen.viewer.status_message = f"freq error: {exc}"[:120]
        screen.refresh()

    @kb.add("t", filter=modal_inactive)  # transpose current row
    def _(event):
        screen._record_key_event(event)
        if not screen.viewer.columns:
            return
        current_row = max(0, getattr(screen.viewer, "cur_row", 0))
        try:
            screen.viewer = open_transpose_viewer(
                screen.viewer,
                session=screen.session,
                view_stack=screen.view_stack,
                sample_rows=1,
                start_row=current_row,
            )
            screen.viewer.status_message = f"transpose row {current_row + 1}"
        except Exception as exc:
            screen.viewer.status_message = f"transpose error: {exc}"[:120]
        screen.refresh()

    @kb.add("T", filter=modal_inactive)  # transpose view (Shift+T)
    def _(event):
        screen._record_key_event(event)
        if not screen.viewer.columns:
            return
        try:
            screen.viewer = open_transpose_viewer(
                screen.viewer,
                session=screen.session,
                view_stack=screen.view_stack,
            )
        except Exception as exc:
            screen.viewer.status_message = f"transpose error: {exc}"[:120]
        screen.refresh()

    @kb.add("d", filter=modal_inactive)  # hide current column
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("hide")
        screen.refresh()

    @kb.add("g", "v", filter=modal_inactive)  # unhide all columns
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("unhide")
        screen.refresh()

    @kb.add("g", "u", filter=modal_inactive)  # clear selection
    def _(event):
        screen._record_key_event(event)
        screen._clear_g_buf()
        screen._execute_command("clear_selection")
        screen.refresh()

    @kb.add("m", "a", filter=modal_inactive)  # materialize active filters/sorts/projection
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("materialize_all")
        screen.refresh()

    @kb.add("m", "m", filter=modal_inactive)  # materialize active filters/sorts/projection
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("materialize_all")
        screen.refresh()

    @kb.add("m", "s", filter=modal_inactive)  # materialize selection
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("materialize_selection")
        screen.refresh()

    @kb.add(",", filter=modal_inactive)  # select all rows matching current value
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("select_same_value")
        screen.refresh()

    @kb.add("+", filter=modal_inactive)  # append filter for current cell value
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("filter_value")
        screen.refresh()

    @kb.add("-", filter=modal_inactive)  # append negative filter for current cell value
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("filter_value_not")
        screen.refresh()

    @kb.add(" ", filter=modal_inactive)  # toggle row selection
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("select_row")
        screen._execute_command("down")
        screen.refresh()

    @kb.add("~", filter=modal_inactive)  # invert selection for visible rows
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("invert_selection")
        screen.refresh()

    @kb.add("u", filter=modal_inactive)  # undo last operation
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("undo")
        screen.refresh()

    @kb.add("U", filter=modal_inactive)  # redo last operation
    def _(event):
        screen._record_key_event(event)
        screen._execute_command("redo")
        screen.refresh()

    @kb.add("x", filter=modal_inactive)  # delete file(s) in browser
    def _(event):
        screen._record_key_event(event)
        screen._open_file_delete_modal(event)

    # Enter key binding for frequency views and normal views
    @kb.add("enter", filter=modal_inactive)
    def _(event):
        screen._record_key_event(event)
        is_file_browser = getattr(screen.viewer.sheet, "is_file_browser", False)
        if is_file_browser and screen._handle_file_browser_enter():
            return
        # Preserve frequency view interaction semantics
        if (
            len(screen.view_stack) > 1
            and hasattr(screen.viewer, "is_freq_view")
            and getattr(screen.viewer, "is_freq_view", False)
        ):
            screen._filter_by_pick()
            return

        if screen._apply_summary_selection():
            return

        screen._open_cell_value_modal(event)

    return kb
