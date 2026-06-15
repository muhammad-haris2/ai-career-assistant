"""
streamlit_app.py
================
AI Career Assistant — Streamlit Frontend

Run with:
    streamlit run app/streamlit_app.py

Make sure FastAPI backend is running first:
    python -m api.main
"""

import os
import sys
import time
import requests
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Config ────────────────────────────────────────────────
try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    
st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🤖",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a1628 0%, #0d1f3c 50%, #0a1628 100%);
    color: #e8f4f8;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1f3c 0%, #0a1628 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}
.block-container { padding-top: 1.5rem; max-width: 1200px; }

.result-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}
.agent-badge {
    background: linear-gradient(135deg, #1a472a, #40916c);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 12px;
}
.match-score {
    font-size: 48px;
    font-weight: 700;
    color: #40916c;
    text-align: center;
}
.step-active {
    background: rgba(64,145,108,0.2);
    border: 1px solid rgba(64,145,108,0.4);
    border-radius: 8px;
    padding: 8px 16px;
    margin: 4px 0;
    color: #40916c;
}
.step-done {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 8px 16px;
    margin: 4px 0;
    color: rgba(255,255,255,0.4);
}
.step-pending {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 8px 16px;
    margin: 4px 0;
    color: rgba(255,255,255,0.25);
}
textarea {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: #e8f4f8 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #1a472a, #40916c) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    padding: 0.6rem 1rem !important;
    min-height: 3rem !important;
}
hr { border-color: rgba(255,255,255,0.1) !important; }
</style>
""", unsafe_allow_html=True)


# ── Helper functions ──────────────────────────────────────
def check_api() -> bool:
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def submit_job(cv_file, jd_text: str):
    """Submit CV and JD to API. Returns job_id string or None."""
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            files={"cv_file": (cv_file.name, cv_file.getvalue(), "application/pdf")},
            data={"jd_text": jd_text},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json().get("job_id")
        else:
            st.error(f"API Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Could not reach API: {e}")
        return None


def get_status(job_id: str) -> dict:
    try:
        r = requests.get(f"{API_URL}/status/{job_id}", timeout=5)
        return r.json()
    except Exception:
        return {"status": "error", "step_message": "Connection error"}


def get_result(job_id: str) -> dict:
    try:
        r = requests.get(f"{API_URL}/result/{job_id}", timeout=10)
        return r.json()
    except Exception:
        return {"status": "error"}


def extract_match_score(gap_analysis: str) -> str:
    """Extract match score from gap analysis text."""
    for line in gap_analysis.split("\n"):
        if "OVERALL MATCH SCORE" in line or "match score" in line.lower():
            parts = line.split(":")
            if len(parts) > 1:
                score = parts[1].strip().split("/")[0].strip().split()[0]
                try:
                    int(score)
                    return score
                except ValueError:
                    pass
    return "N/A"


# ── Header ────────────────────────────────────────────────
def render_header():
    st.markdown("""
    <div style='text-align:center;padding:28px 20px 20px;margin-bottom:8px;
        border-radius:18px;
        background:linear-gradient(135deg,rgba(26,71,42,0.6),rgba(64,145,108,0.4));
        border:1px solid rgba(144,238,144,0.2);'>
        <h1 style='color:#fff;font-size:2.2rem;margin:0 0 6px;'>
            🤖 AI Career Assistant
        </h1>
        <p style='color:rgba(255,255,255,0.75);font-size:15px;margin:0;'>
            5 specialized AI agents analyze your CV against any job description
            &nbsp;|&nbsp; Powered by Groq + CrewAI
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Progress display ──────────────────────────────────────
def render_progress(current_step: int, step_message: str, progress: int):
    steps = [
        "Agent 1: Parsing your CV",
        "Agent 2: Analyzing job description",
        "Agent 3: Comparing CV vs requirements",
        "Agent 4: Building learning roadmap",
        "Agent 5: Writing cover letter",
    ]

    st.markdown(f"### ⚙️ Processing... {progress}%")
    st.progress(progress / 100)
    st.markdown(f"**Current:** {step_message}")
    st.markdown("---")

    for i, step in enumerate(steps, 1):
        if i < current_step:
            st.markdown(f'<div class="step-done">✅ {step}</div>',
                        unsafe_allow_html=True)
        elif i == current_step:
            st.markdown(f'<div class="step-active">⚡ {step}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="step-pending">⏳ {step}</div>',
                        unsafe_allow_html=True)


# ── Results display ───────────────────────────────────────
def render_results(results: dict):
    st.markdown("## ✅ Analysis Complete!")
    st.divider()

    # ── Match Score ───────────────────────────────────────
    score = extract_match_score(results.get("gap_analysis", ""))
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(f"""
        <div class="result-card" style="text-align:center;">
            <div class="agent-badge">Agent 3 — Gap Analyzer</div>
            <div class="match-score">{score}/100</div>
            <div style="color:rgba(255,255,255,0.6);font-size:14px;">
                Overall Match Score
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Four tabs for results ─────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Gap Analysis",
        "📚 Learning Roadmap",
        "✉️ Cover Letter",
        "📄 Full CV & JD Analysis",
    ])

    with tab1:
        st.markdown('<div class="agent-badge">Agent 3 — Gap Analyzer</div>',
                    unsafe_allow_html=True)
        st.markdown(results.get("gap_analysis", "No data"), unsafe_allow_html=False)

    with tab2:
        st.markdown('<div class="agent-badge">Agent 4 — Learning Path Builder</div>',
                    unsafe_allow_html=True)
        st.markdown(results.get("learning_path", "No data"), unsafe_allow_html=False)

    with tab3:
        st.markdown('<div class="agent-badge">Agent 5 — Cover Letter Writer</div>',
                    unsafe_allow_html=True)
        cover_letter = results.get("cover_letter", "")
        st.text_area(
            "Your tailored cover letter (copy from here):",
            value=cover_letter,
            height=500,
            key="cover_letter_box",
        )

    with tab4:
        col_cv, col_jd = st.columns(2)
        with col_cv:
            st.markdown('<div class="agent-badge">Agent 1 — CV Parser</div>',
                        unsafe_allow_html=True)
            st.text_area(
                "CV Analysis",
                results.get("cv_analysis", ""),
                height=400,
                key="cv_analysis_box",
            )
        with col_jd:
            st.markdown('<div class="agent-badge">Agent 2 — JD Analyzer</div>',
                        unsafe_allow_html=True)
            st.text_area(
                "JD Analysis",
                results.get("jd_analysis", ""),
                height=400,
                key="jd_analysis_box",
            )


# ── Main app ──────────────────────────────────────────────
def main():
    render_header()

    # ── API health check ──────────────────────────────────
    if not check_api():
        st.error(
            "⚠️ Cannot connect to the FastAPI backend. "
            "Make sure it is running:\n\n"
            "```\npython -m api.main\n```"
        )
        st.stop()

    # ── Session state init ────────────────────────────────
    if "job_id" not in st.session_state:
        st.session_state.job_id = None
    if "results" not in st.session_state:
        st.session_state.results = None
    if "running" not in st.session_state:
        st.session_state.running = False

    # ── Show results if complete ──────────────────────────
    if st.session_state.results:
        render_results(st.session_state.results)
        st.divider()
        if st.button("🔄 Analyze Another Job"):
            st.session_state.job_id = None
            st.session_state.results = None
            st.session_state.running = False
            st.rerun()
        return

    # ── Polling loop if job is running ────────────────────
    if st.session_state.running and st.session_state.job_id:
        status = get_status(st.session_state.job_id)

        if status["status"] == "complete":
            results = get_result(st.session_state.job_id)
            st.session_state.results = results
            st.session_state.running = False
            st.rerun()

        elif status["status"] == "error":
            st.error(f"Analysis failed: {status.get('step_message', 'Unknown error')}")
            st.session_state.running = False

        else:
            render_progress(
                current_step=status.get("current_step", 0),
                step_message=status.get("step_message", "Starting..."),
                progress=status.get("progress", 0),
            )
            time.sleep(3)
            st.rerun()
        return

    # ── Input form ────────────────────────────────────────
    st.markdown("### 📋 Enter Your Details")
    st.markdown("Upload your CV and paste the job description below.")
    st.divider()

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("#### 📄 Your CV")
        cv_file = st.file_uploader(
            "Upload CV (PDF only)",
            type=["pdf"],
            help="Upload your CV in PDF format",
        )
        if cv_file:
            st.success(
                f"✅ {cv_file.name} uploaded "
                f"({round(len(cv_file.getvalue()) / 1024, 1)} KB)"
            )

    with col_right:
        st.markdown("#### 💼 Job Description")
        jd_text = st.text_area(
            "Paste the full job description here",
            height=300,
            placeholder="Paste the job description you want to apply for...",
            help="Copy and paste the complete job description",
        )
        if jd_text:
            word_count = len(jd_text.split())
            st.caption(f"{word_count} words")

    st.divider()

    # ── Submit button ─────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Analyze My Application", use_container_width=True):
            if not cv_file:
                st.error("Please upload your CV (PDF)")
            elif not jd_text or len(jd_text.strip()) < 50:
                st.error("Please paste a job description (minimum 50 characters)")
            else:
                with st.spinner("Submitting to AI agents..."):
                    job_id = submit_job(cv_file, jd_text)
                    if job_id:
                        st.session_state.job_id = job_id
                        st.session_state.running = True
                        st.rerun()

    # ── Footer ────────────────────────────────────────────
    st.divider()
    st.markdown("""
    <div style='text-align:center;color:rgba(255,255,255,0.3);font-size:12px;'>
        🤖 AI Career Assistant &nbsp;|&nbsp;
        5 Agents: CV Parser → JD Analyzer → Gap Analyzer →
        Learning Path → Cover Letter Writer &nbsp;|&nbsp;
        Powered by Groq + CrewAI
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()