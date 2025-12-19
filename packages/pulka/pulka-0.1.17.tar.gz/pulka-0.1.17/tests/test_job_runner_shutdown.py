from __future__ import annotations

import pytest

from pulka.core.errors import CancelledError
from pulka.core.jobs import JobRunner


class _Sheet:
    def __init__(self, sheet_id: str) -> None:
        self.sheet_id = sheet_id

    def job_context(self) -> tuple[str, int, str]:
        return (self.sheet_id, 0, "ctx")


def test_job_runner_close_avoids_scheduling_after_executor_shutdown() -> None:
    def _shutdown_submit(_fn):
        raise RuntimeError("cannot schedule new futures after shutdown")

    runner = JobRunner(submit=_shutdown_submit, max_workers=1)
    sheet = _Sheet("shutdown-sheet")

    def _next(_: int) -> str:
        return "next"

    next_future = runner.submit(sheet, "tag", _next, priority=0)
    with pytest.raises(CancelledError):
        next_future.result(timeout=2)
