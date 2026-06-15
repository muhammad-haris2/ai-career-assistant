"""
routes.py
=========
FastAPI route definitions for the AI Career Assistant API.
"""

import os
import uuid
import shutil
from typing import Dict, Any

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.concurrency import run_in_threadpool

from api.models import AnalyzeResponse, StatusResponse, ResultResponse, JobStatus

router = APIRouter()

# ── In-memory job store ───────────────────────────────────
# Stores job status and results
# In production this would be Redis or a database
jobs: Dict[str, Dict[str, Any]] = {}


def run_pipeline(job_id: str, cv_path: str, jd_text: str):
    """
    Runs the full pipeline in background.
    Updates the jobs dict with progress and results.
    """
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from crew.career_crew import run_career_crew

    def progress_callback(step: int, message: str):
        jobs[job_id]["current_step"]  = step
        jobs[job_id]["step_message"]  = message
        jobs[job_id]["progress"]      = int((step / 5) * 100)
        jobs[job_id]["status"]        = JobStatus.running

    jobs[job_id]["status"] = JobStatus.running

    results = run_career_crew(
        cv_path=cv_path,
        jd_text=jd_text,
        progress_callback=progress_callback
    )

    if results["status"] == "success":
        jobs[job_id].update({
            "status":        JobStatus.complete,
            "progress":      100,
            "current_step":  5,
            "step_message":  "All agents completed successfully",
            "cv_analysis":   results["cv_analysis"],
            "jd_analysis":   results["jd_analysis"],
            "gap_analysis":  results["gap_analysis"],
            "learning_path": results["learning_path"],
            "cover_letter":  results["cover_letter"],
        })
    else:
        jobs[job_id].update({
            "status":       JobStatus.error,
            "step_message": f"Error: {results['error']}",
            "error":        results["error"],
        })

    # Clean up uploaded file
    if os.path.exists(cv_path):
        os.remove(cv_path)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    cv_file: UploadFile = File(...),
    jd_text: str        = Form(...)
):
    """
    Accept CV file + job description text.
    Start the pipeline in background.
    Return job_id immediately.
    """
    # Validate file type
    if not cv_file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )

    # Save uploaded CV temporarily
    job_id   = str(uuid.uuid4())
    cv_path  = f"data/cv_{job_id}.pdf"

    os.makedirs("data", exist_ok=True)
    with open(cv_path, "wb") as f:
        shutil.copyfileobj(cv_file.file, f)

    # Initialize job record
    jobs[job_id] = {
        "status":       JobStatus.pending,
        "current_step": 0,
        "step_message": "Job queued, starting soon...",
        "progress":     0,
    }

    # Run pipeline in background thread
    # (so API returns immediately without waiting)
    import asyncio
    asyncio.create_task(
        run_in_threadpool(run_pipeline, job_id, cv_path, jd_text)
    )

    return AnalyzeResponse(
        job_id=job_id,
        status=JobStatus.pending,
        message="Analysis started. Poll /status/{job_id} for updates."
    )


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """
    Returns current status and progress of a job.
    Frontend polls this every 3 seconds.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return StatusResponse(
        job_id=job_id,
        status=job["status"],
        current_step=job.get("current_step", 0),
        step_message=job.get("step_message", ""),
        progress=job.get("progress", 0),
    )


@router.get("/result/{job_id}", response_model=ResultResponse)
async def get_result(job_id: str):
    """
    Returns full results when job is complete.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job["status"] == JobStatus.running:
        raise HTTPException(
            status_code=202,
            detail="Job still running. Check /status/{job_id}"
        )

    return ResultResponse(
        job_id=job_id,
        status=job["status"],
        cv_analysis=job.get("cv_analysis"),
        jd_analysis=job.get("jd_analysis"),
        gap_analysis=job.get("gap_analysis"),
        learning_path=job.get("learning_path"),
        cover_letter=job.get("cover_letter"),
        error=job.get("error"),
    )


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "AI Career Assistant API"}