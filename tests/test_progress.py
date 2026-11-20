import unittest

import time

from app.main import _job_status, _stage_after_node


class StageAfterNodeTests(unittest.TestCase):
    def test_dedup_completion_reports_summarising_as_next_stage(self) -> None:
        self.assertEqual(
            _stage_after_node("dedup", {"stage": "deduplicating"}),
            "summarising",
        )

    def test_reviewer_retry_reports_writing_as_next_stage(self) -> None:
        state = {"review": {"approved": False}, "revisions": 0}
        self.assertEqual(_stage_after_node("reviewer", state), "writing")

    def test_approved_review_reports_exporting_as_next_stage(self) -> None:
        state = {"review": {"approved": True}, "revisions": 0}
        self.assertEqual(_stage_after_node("reviewer", state), "exporting")

    def test_running_job_status_reports_elapsed_stage_time(self) -> None:
        job = {
            "status": "running",
            "stage": "writing",
            "stage_started_at": time.monotonic() - 65,
        }

        response = _job_status(job)

        self.assertGreaterEqual(response["stage_elapsed_seconds"], 65)
        self.assertNotIn("stage_started_at", response)

    def test_completed_job_status_does_not_report_running_elapsed_time(self) -> None:
        job = {
            "status": "completed",
            "stage": "completed",
            "stage_started_at": time.monotonic() - 65,
        }

        self.assertEqual(_job_status(job)["stage_elapsed_seconds"], 0)


if __name__ == "__main__":
    unittest.main()
