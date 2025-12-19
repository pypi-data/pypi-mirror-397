from __future__ import annotations

from pulka.tui.job_pump import JobPump


class _Job:
    def __init__(self, *, done: bool) -> None:
        self.done = done
        self.calls: list[object] = []

    def consume_update(self, viewer) -> bool:
        self.calls.append(viewer)
        return self.done


def test_job_pump_consumes_and_prunes_jobs() -> None:
    viewer_1 = object()
    viewer_2 = object()
    job_done = _Job(done=True)
    job_pending = _Job(done=False)
    jobs = {viewer_1: job_done, viewer_2: job_pending}

    checks: list[str] = []

    def check_dataset() -> None:
        checks.append("dataset")

    def check_browser() -> None:
        checks.append("browser")

    pump = JobPump(
        jobs=jobs,
        check_dataset_file_changes=check_dataset,
        check_file_browser_changes=check_browser,
    )
    pump.poll()

    assert viewer_1 not in jobs
    assert viewer_2 in jobs
    assert job_done.calls == [viewer_1]
    assert job_pending.calls == [viewer_2]
    assert checks == ["dataset", "browser"]
