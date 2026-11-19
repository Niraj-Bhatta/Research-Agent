"""FastAPI application – REST API + SSE for real-time progress + static UI."""

import os
import uuid
from threading import Thread

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .graph import graph

app = FastAPI(
    title="AI Research Assistant",
    description="Multi-agent research assistant with live progress streaming.",
    version="2.0.0",
)

# ---------------------------------------------------------------------------
# In-memory job store (swap for Redis / DB in production)
# ---------------------------------------------------------------------------
JOBS: dict[str, dict] = {}

# Stage descriptions shown in the UI
STAGE_LABELS = {
    "planning":       "Planning research tasks…",
    "searching":      "Searching the web…",
    "deduplicating":  "Removing duplicates…",
    "summarising":    "Summarising findings…",
    "writing":        "Writing the report…",
    "reviewing":      "Reviewing the draft…",
    "completed":      "Report generated ✓",
    "failed":         "Something went wrong ✗",
}


class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, examples=["Impact of AI on healthcare"])


# ---------------------------------------------------------------------------
# Background runner
# ---------------------------------------------------------------------------
def _run_job(job_id: str, topic: str) -> None:
    job = JOBS[job_id]
    job["status"] = "running"
    try:
        state: dict = {"job_id": job_id, "topic": topic}
        for update in graph.stream(state, stream_mode="updates"):
            for node, delta in update.items():
                stage = delta.get("stage", node)
                job["stage"] = stage
                job["stage_label"] = STAGE_LABELS.get(stage, stage)
                job["agent"] = node
                state.update(delta)
        job.update(
            status="completed",
            stage="completed",
            stage_label=STAGE_LABELS["completed"],
            title=state.get("title"),
            plan=state.get("plan"),
            sources_used=len(state.get("sources", [])),
            duplicates_removed=state.get("duplicates_removed", 0),
            revisions=state.get("revisions", 0),
            review=state.get("review"),
            report=state.get("report"),
            md_path=state.get("md_path"),
            pdf_path=state.get("pdf_path"),
        )
    except Exception as exc:
        job.update(
            status="failed",
            stage="failed",
            stage_label=STAGE_LABELS["failed"],
            error=str(exc),
        )


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/research", status_code=202)
@app.post("/research", status_code=202)
def create_research(req: ResearchRequest):
    job_id = uuid.uuid4().hex[:12]
    JOBS[job_id] = {
        "job_id": job_id,
        "topic": req.topic,
        "status": "queued",
        "stage": "queued",
        "stage_label": "Queued – starting soon…",
    }
    thread = Thread(target=_run_job, args=(job_id, req.topic), daemon=True)
    thread.start()
    return {
        "job_id": job_id,
        "status": "queued",
        "status_url": f"/api/research/{job_id}",
    }


@app.get("/api/research/{job_id}")
@app.get("/research/{job_id}")
def get_research(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@app.get("/api/research/{job_id}/download/{fmt}")
@app.get("/research/{job_id}/download/{fmt}")
def download(job_id: str, fmt: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "completed":
        raise HTTPException(409, f"Job is {job['status']}")
    if fmt not in ("md", "pdf"):
        raise HTTPException(400, "fmt must be 'md' or 'pdf'")
    path = job["md_path"] if fmt == "md" else job["pdf_path"]
    if not path or not os.path.exists(path):
        raise HTTPException(404, "File missing")
    return FileResponse(path, filename=f"report.{fmt}")


# ---------------------------------------------------------------------------
# Serve the frontend
# ---------------------------------------------------------------------------
_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/", response_class=HTMLResponse)
def index():
    index_path = os.path.join(_STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as fh:
        return HTMLResponse(content=fh.read())


# Mount static assets AFTER the root route so /style.css etc. work
if os.path.isdir(_STATIC_DIR):
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
