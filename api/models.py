"""
models.py
=========
Pydantic models for request and response validation.
"""

from pydantic import BaseModel
from typing import Optional
from enum import Enum


class JobStatus(str, Enum):
    pending  = "pending"
    running  = "running"
    complete = "complete"
    error    = "error"


class AnalyzeResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str


class StatusResponse(BaseModel):
    job_id:       str
    status:       JobStatus
    current_step: int
    step_message: str
    progress:     int  # 0-100 percentage


class ResultResponse(BaseModel):
    job_id:        str
    status:        JobStatus
    cv_analysis:   Optional[str] = None
    jd_analysis:   Optional[str] = None
    gap_analysis:  Optional[str] = None
    learning_path: Optional[str] = None
    cover_letter:  Optional[str] = None
    error:         Optional[str] = None