from __future__ import annotations

from uuid import uuid4

from app.models.schemas import GenerationJob, Report
from app.storage.json_store import JsonStore


GENERATION_JOB_STORE = JsonStore("generation_jobs.json", {"jobs": {}})


def create_generation_job(*, status: str = "queued", message: str = "") -> GenerationJob:
    job = GenerationJob(job_id=uuid4().hex, status=status, message=message)
    _save_job(job)
    return job


def complete_generation_job(job_id: str, *, report: Report, status: str, message: str) -> GenerationJob:
    job = GenerationJob(job_id=job_id, status=status, report=report, message=message)
    _save_job(job)
    return job


def get_generation_job(job_id: str) -> GenerationJob | None:
    payload = GENERATION_JOB_STORE.read()
    raw_job = payload.get("jobs", {}).get(job_id)
    return GenerationJob.model_validate(raw_job) if raw_job else None


def _save_job(job: GenerationJob) -> None:
    def write_job(payload: dict) -> None:
        payload.setdefault("jobs", {})[job.job_id] = job.model_dump(mode="json")

    GENERATION_JOB_STORE.update(write_job)
