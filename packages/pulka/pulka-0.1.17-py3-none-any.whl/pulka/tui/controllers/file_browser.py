"""Controller for file browser interactions."""

from __future__ import annotations

import shutil
from collections.abc import Callable, Sequence
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ...sheets.file_browser_sheet import FileDeletionResult, file_browser_status_text

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from ...api.session import Session
    from ...core.viewer import Viewer


@dataclass(slots=True)
class FileBrowserTransition:
    """Result of a browser action."""

    status: str | None = None
    sheet_changed: bool = False
    opened_dataset: bool = False


@dataclass(slots=True)
class FileTransferPlan:
    """Planned source/destination pairs for copy/move operations."""

    targets: list[tuple[Path, Path]]
    conflicts: list[Path]
    missing_directories: list[Path] = field(default_factory=list)
    error: str | None = None


class FileBrowserController:
    """Owns non-UI file browser behaviour."""

    def __init__(self, *, session: Session, get_viewer: Callable[[], Viewer | None]) -> None:
        self._session = session
        self._get_viewer = get_viewer

    def on_viewer_changed(self, viewer: Viewer) -> None:
        """Notify the controller when the active viewer switches."""

        del viewer

    # ------------------------------------------------------------------
    # Entry helpers
    # ------------------------------------------------------------------
    def enter_current(self) -> FileBrowserTransition | None:
        viewer = self._get_viewer()
        if viewer is None:
            return None
        sheet = self._browser_sheet(viewer)
        if sheet is None:
            return None
        action_fn = getattr(sheet, "action_for_row", None)
        if not callable(action_fn):
            return None
        try:
            action = action_fn(viewer.cur_row)
        except Exception as exc:
            return FileBrowserTransition(status=f"entry error: {exc}")
        if action is None:
            return FileBrowserTransition(status="entry is not openable")
        target = Path(action.path)
        if action.type == "enter-directory":
            return self._switch_directory(viewer, sheet, target)
        if action.type == "open-file":
            return self._open_file(viewer, target)
        return FileBrowserTransition(status=f"unknown entry action: {action.type}")

    def _switch_directory(self, viewer: Viewer, sheet: Any, target: Path) -> FileBrowserTransition:
        builder = getattr(sheet, "at_path", None)
        if not callable(builder):
            return FileBrowserTransition(status="browser cannot change directory")
        try:
            new_sheet = builder(target)
        except Exception as exc:
            return FileBrowserTransition(status=f"dir open failed: {exc}")

        source_label = getattr(new_sheet, "display_path", None) or str(target)
        viewer.replace_sheet(new_sheet, source_path=source_label)
        with suppress(Exception):
            viewer._clear_selection_state()  # reset selection when changing directories
        with suppress(Exception):
            viewer.row_count_tracker.ensure_total_rows()
        message = getattr(new_sheet, "status_message", None)
        if not message:
            count = new_sheet.row_count() or 0
            message = f"{count} entries"
        return FileBrowserTransition(status=message, sheet_changed=True)

    def _open_file(self, viewer: Viewer, target: Path) -> FileBrowserTransition:
        try:
            self._session.open_dataset_viewer(target, base_viewer=viewer)
        except Exception as exc:
            return FileBrowserTransition(status=f"open failed: {exc}")
        return FileBrowserTransition(status=f"opened {target.name or target}", opened_dataset=True)

    # ------------------------------------------------------------------
    # Selection helpers
    # ------------------------------------------------------------------
    def resolve_entries(
        self,
        *,
        deletable: bool = False,
        viewer: Viewer | None = None,
    ) -> tuple[list[Any], str | None]:
        viewer = viewer or self._get_viewer()
        if viewer is None:
            return [], None
        sheet = self._browser_sheet(viewer)
        if sheet is None:
            return [], None

        target_rows = self._selected_rows(viewer, sheet=sheet)
        entries_fn_name = "deletable_entries_for_rows" if deletable else "entries_for_rows"
        entries_fn = getattr(sheet, entries_fn_name, None)
        if not callable(entries_fn):
            return [], None

        entries = entries_fn(target_rows)
        if entries:
            return entries, None

        selection = getattr(viewer, "_selected_row_ids", set()) or set()
        if deletable:
            status = "select at least one deletable row" if selection else "entry cannot be deleted"
            return [], status

        # Non-deletable entry resolution
        if selection:
            return [], "select at least one item"
        if getattr(viewer, "cur_row", 0) == 0 and len(getattr(sheet, "_entries", [])) > 1:
            extra = entries_fn([1])
            if extra:
                return extra, None
        return [], "entry cannot be used"

    def _selected_rows(self, viewer: Viewer, *, sheet: Any | None = None) -> list[int]:
        def is_selectable(row_id: int) -> bool:
            if sheet is None:
                return True
            entry_at = getattr(sheet, "_entry_at", None)
            if not callable(entry_at):
                return True
            entry = entry_at(row_id)
            if entry is None:
                return False
            name = getattr(entry, "row", {}).get("name", "")
            return name != ".."

        selection = getattr(viewer, "_selected_row_ids", set()) or set()
        rows: list[int] = []
        for row_id in selection:
            if isinstance(row_id, int) and row_id >= 0 and is_selectable(row_id):
                rows.append(row_id)
        if not rows:
            current = getattr(viewer, "cur_row", 0)
            if isinstance(current, int) and current >= 0 and is_selectable(current):
                rows.append(current)
        return rows

    # ------------------------------------------------------------------
    # Transfer operations
    # ------------------------------------------------------------------
    def plan_transfer(
        self,
        operation: str,
        dest: str,
        *,
        entries: Sequence[Any],
        sheet: Any,
    ) -> FileTransferPlan:
        base_dir = getattr(sheet, "directory", Path.cwd())
        dest_text = str(dest)
        dest_has_trailing_sep = dest_text.endswith(("/", "\\"))
        dest_path = Path(dest_text)
        if not dest_path.is_absolute():
            dest_path = base_dir / dest_path
        dest_path = dest_path.expanduser()

        multiple = len(entries) > 1
        dest_exists = dest_path.exists()
        dest_is_dir = dest_exists and dest_path.is_dir()

        treat_dest_as_dir = multiple or dest_is_dir or dest_has_trailing_sep
        if not dest_exists and not treat_dest_as_dir and len(entries) == 1:
            src = Path(entries[0].path)
            # Heuristic: a missing destination without a suffix likely intends a directory.
            if dest_path.suffix == "" and not dest_path.name.startswith("."):
                treat_dest_as_dir = True

        if multiple and dest_exists and not dest_is_dir:
            return FileTransferPlan(
                targets=[],
                conflicts=[],
                error="destination must be an existing directory for multiple items",
            )

        targets: list[tuple[Path, Path]] = []
        conflicts: list[Path] = []
        missing_dirs: set[Path] = set()

        for entry in entries:
            src = Path(entry.path)
            target = dest_path / src.name if treat_dest_as_dir else dest_path

            try:
                src_resolved = src.resolve()
                target_resolved = target.resolve()
            except Exception:
                src_resolved = src
                target_resolved = target

            if operation == "move":
                with suppress(Exception):
                    if target_resolved.is_relative_to(src_resolved):
                        return FileTransferPlan(
                            targets=[], conflicts=[], error="destination cannot be inside source"
                        )

            if target.exists():
                conflicts.append(target)
            parent = target.parent
            if not parent.exists():
                missing_dirs.add(parent)

            targets.append((src, target))

        return FileTransferPlan(
            targets=targets,
            conflicts=conflicts,
            missing_directories=sorted(missing_dirs, key=lambda path: str(path)),
            error=None,
        )

    def perform_transfer(
        self, operation: str, targets: list[tuple[Path, Path]], *, allow_overwrite: bool
    ) -> tuple[str | None, list[tuple[Path, str]], int]:
        errors: list[tuple[Path, str]] = []
        completed = 0

        for src, dest in targets:
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                errors.append((dest, str(exc)))
                continue

            try:
                if dest.exists() and not allow_overwrite:
                    errors.append((dest, "destination exists"))
                    continue

                if operation == "copy":
                    if src.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(src, dest)
                    else:
                        if dest.is_dir():
                            dest = dest / src.name
                        shutil.copy2(src, dest)
                elif operation == "move":
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink(missing_ok=True)
                    shutil.move(src, dest)
                else:
                    errors.append((dest, f"unknown operation {operation}"))
                    continue
            except Exception as exc:  # pragma: no cover - filesystem specific
                errors.append((dest, str(exc)))
                continue
            completed += 1

        message: str | None = None
        if completed:
            suffix = "" if completed == 1 else "s"
            verb = "Copied" if operation == "copy" else "Moved"
            message = f"{verb} {completed} item{suffix}"
        return message, errors, completed

    # ------------------------------------------------------------------
    # Rename and mkdir operations
    # ------------------------------------------------------------------
    def rename_entry(self, sheet: Any, entry: Any, new_name: str) -> tuple[str | None, str | None]:
        if not new_name:
            return None, "rename requires a new name"

        candidate = Path(new_name)
        if candidate.is_absolute():
            return None, "rename target must stay in the current directory"
        if len(candidate.parts) != 1:
            return None, "rename target must not include path separators"
        if candidate.name in ("", ".", ".."):
            return None, "rename target is invalid"

        source_path = Path(getattr(entry, "path", ""))
        if not source_path:
            return None, "invalid source for rename"

        base_dir = getattr(sheet, "directory", source_path.parent)
        try:
            source_dir = source_path.parent.resolve()
            target_dir = Path(base_dir).resolve()
        except Exception:
            source_dir = source_path.parent
            target_dir = Path(base_dir)

        if source_dir != target_dir:
            return None, "rename restricted to current directory"

        target_path = source_path.with_name(candidate.name)
        if target_path.exists():
            return None, f"{target_path.name} already exists"

        try:
            source_path.rename(target_path)
        except Exception as exc:  # pragma: no cover - filesystem specific
            return None, f"rename failed: {exc}"

        return f"renamed {source_path.name} -> {target_path.name}", None

    def make_directory(self, sheet: Any, dest: str) -> tuple[str | None, str | None]:
        if not dest:
            return None, "mkdir requires a destination path"

        path = Path(dest).expanduser()
        base_dir = getattr(sheet, "directory", Path.cwd())
        target = path if path.is_absolute() else Path(base_dir) / path

        try:
            target = target.resolve()
        except Exception:
            target = target.absolute()

        if target.exists():
            if target.is_dir():
                return None, f"{target} already exists"
            return None, f"{target} exists and is not a directory"

        try:
            target.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            return None, f"{target} already exists"
        except Exception as exc:  # pragma: no cover - filesystem specific
            return None, f"mkdir failed: {exc}"

        return f"created directory {target}", None

    # ------------------------------------------------------------------
    # Deletion and refresh helpers
    # ------------------------------------------------------------------
    def delete_entries(self, sheet: Any, entries: Sequence[Any]) -> FileDeletionResult:
        return sheet.delete_entries(entries)

    def refresh_sheet(self, sheet: Any, viewer: Viewer) -> str:
        provider = getattr(viewer, "row_provider", None)
        if provider is not None:
            with suppress(Exception):
                provider.clear()
        with suppress(Exception):
            viewer.invalidate_row_cache()
        with suppress(Exception):
            tracker = viewer.row_count_tracker
            tracker.invalidate()
            tracker.ensure_total_rows()
        message = file_browser_status_text(sheet)
        viewer.status_message = message
        return message

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _browser_sheet(self, viewer: Viewer | None) -> Any | None:
        sheet = getattr(viewer, "sheet", None)
        if sheet is None or not getattr(sheet, "is_file_browser", False):
            return None
        return sheet
