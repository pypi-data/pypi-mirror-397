"""Background job polling helpers for the TUI screen."""

from __future__ import annotations

from collections.abc import Callable, MutableMapping
from typing import Protocol, runtime_checkable

from ..core.viewer import Viewer


@runtime_checkable
class ScreenJob(Protocol):
    """Protocol for background job handles polled by the screen."""

    def consume_update(self, viewer: Viewer) -> bool: ...


class JobPump:
    """Consumes viewer job updates and triggers follow-up checks."""

    def __init__(
        self,
        *,
        jobs: MutableMapping[Viewer, object],
        check_dataset_file_changes: Callable[[], None],
        check_file_browser_changes: Callable[[], None],
    ) -> None:
        self._jobs = jobs
        self._check_dataset_file_changes = check_dataset_file_changes
        self._check_file_browser_changes = check_file_browser_changes

    def poll(self) -> None:
        jobs = list(self._jobs.items())
        for viewer, job in jobs:
            if isinstance(job, ScreenJob):
                done = job.consume_update(viewer)
                if done:
                    self._jobs.pop(viewer, None)
        self._check_dataset_file_changes()
        self._check_file_browser_changes()
