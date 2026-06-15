"""
career_crew.py
==============
Connects all 5 agents into one single pipeline.
Includes rate limit handling for Groq free tier.
"""

import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from agents.cv_parser import parse_cv
from agents.jd_analyzer import analyze_jd
from agents.gap_analyzer import analyze_gaps
from agents.learning_path import build_learning_path
from agents.cover_letter import write_cover_letter
from utils.pdf_reader import extract_text_from_pdf


def truncate(text: str, max_chars: int = 2000) -> str:
    """Truncate text to avoid hitting token limits."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n[truncated for brevity]"


def run_career_crew(cv_path: str, jd_text: str, progress_callback=None) -> dict:
    """
    Run the complete AI Career Assistant pipeline.
    """

    def update_progress(step: int, message: str):
        if progress_callback:
            progress_callback(step, message)
        print(f"[Step {step}/5] {message}")

    results = {}

    try:
        # ── Step 1: Parse CV ──────────────────────────────
        update_progress(1, "Agent 1: Parsing your CV...")
        cv_text     = extract_text_from_pdf(cv_path)
        cv_analysis = parse_cv(cv_text)
        results["cv_analysis"] = cv_analysis
        time.sleep(20)  # wait 20s between agents

        # ── Step 2: Analyze JD ────────────────────────────
        update_progress(2, "Agent 2: Analyzing job description...")
        jd_analysis = analyze_jd(jd_text)
        results["jd_analysis"] = jd_analysis
        time.sleep(20)

        # ── Step 3: Gap Analysis ──────────────────────────
        update_progress(3, "Agent 3: Comparing CV vs job requirements...")
        gap_analysis = analyze_gaps(
            truncate(cv_analysis),
            truncate(jd_analysis)
        )
        results["gap_analysis"] = gap_analysis
        time.sleep(20)

        # ── Step 4: Learning Path ─────────────────────────
        update_progress(4, "Agent 4: Building your personalized learning roadmap...")
        learning_path = build_learning_path(
            truncate(gap_analysis),
            truncate(jd_analysis)
        )
        results["learning_path"] = learning_path
        time.sleep(20)

        # ── Step 5: Cover Letter ──────────────────────────
        update_progress(5, "Agent 5: Writing your tailored cover letter...")
        cover_letter = write_cover_letter(
            truncate(cv_analysis),
            truncate(jd_analysis),
            truncate(gap_analysis)
        )
        results["cover_letter"] = cover_letter

        results["status"] = "success"

    except Exception as e:
        results["status"] = "error"
        results["error"]  = str(e)
        print(f"Pipeline error: {e}")

    return results