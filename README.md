# AI Career Assistant

A multi-agent AI system that analyzes your CV against any job description and delivers a match score, skill gap analysis, personalized learning roadmap, and tailored cover letter — in under 5 minutes.

**[Try the live demo →](https://ai-career-assistant-crewai.streamlit.app)**

---

## What it does

Upload your CV (PDF) and paste any job description. The system runs five specialized AI agents in sequence and returns:

| Output | Description |
|--------|-------------|
| Match Score | Overall percentage match between your CV and the role |
| Matched Skills | Skills you already have that the job requires |
| Missing Skills | Skills you need to acquire |
| Partial Matches | Skills you have but need to strengthen |
| Learning Roadmap | Week-by-week plan with real courses and resources |
| Cover Letter | Tailored letter that references your actual projects |

---

## Architecture

```
User (CV PDF + Job Description)
        │
        ▼
FastAPI Backend (Render)
        │
        ▼
┌─────────────────────────────────┐
│      CrewAI Agent Pipeline      │
│                                 │
│  1. CV Parser                   │
│     Extracts skills, projects,  │
│     experience, education       │
│              │                  │
│  2. JD Analyzer                 │
│     Extracts required skills,   │
│     keywords, qualifications    │
│              │                  │
│  3. Gap Analyzer                │
│     Compares CV vs JD →         │
│     match score + skill gaps    │
│           ┌──┴──┐               │
│           ▼     ▼               │
│  4. Learning    5. Cover Letter │
│     Path           Writer       │
│     Builder                     │
└─────────────────────────────────┘
        │
        ▼
Streamlit Frontend (Streamlit Cloud)
Results displayed in 4 tabbed sections
```

---

## Tech stack

| Component | Technology |
|-----------|-----------|
| Agent framework | CrewAI |
| LLM | Groq — Llama 3.3 70B |
| Web search | Tavily API |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| PDF processing | PyMuPDF |
| Backend hosting | Render |
| Frontend hosting | Streamlit Community Cloud |

---

## Running locally

### Prerequisites

- Python 3.10+
- Groq API key — [console.groq.com](https://console.groq.com) (free, no credit card)
- Tavily API key — [tavily.com](https://tavily.com) (free tier available)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/muhammad-haris2/ai-career-assistant.git
cd ai-career-assistant

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```

```bash
# 4. Start the FastAPI backend (Terminal 1)
python -m api.main
# Runs at http://localhost:8000
# API docs at http://localhost:8000/docs

# 5. Start the Streamlit frontend (Terminal 2)
streamlit run app/streamlit_app.py
# Open http://localhost:8501
```

---

## API reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Submit CV + JD. Returns a `job_id` immediately |
| `GET` | `/status/{job_id}` | Returns current step, progress %, and status |
| `GET` | `/result/{job_id}` | Returns full results when the pipeline completes |
| `GET` | `/health` | Confirms API and model are reachable |

### Example

```python
import requests

# Submit a job
response = requests.post(
    "http://localhost:8000/analyze",
    files={"cv_file": ("cv.pdf", open("cv.pdf", "rb"), "application/pdf")},
    data={"jd_text": "Software Engineer Intern..."}
)
job_id = response.json()["job_id"]

# Poll for progress
status = requests.get(f"http://localhost:8000/status/{job_id}").json()
print(status["progress"])  # 0–100

# Fetch results
results = requests.get(f"http://localhost:8000/result/{job_id}").json()
print(results["gap_analysis"])
print(results["cover_letter"])
```

---

## Project structure

```
ai-career-assistant/
├── agents/
│   ├── cv_parser.py        # Agent 1 — extracts and structures the CV
│   ├── jd_analyzer.py      # Agent 2 — extracts and structures the JD
│   ├── gap_analyzer.py     # Agent 3 — compares CV vs JD
│   ├── learning_path.py    # Agent 4 — builds the learning roadmap
│   └── cover_letter.py     # Agent 5 — writes the cover letter
├── crew/
│   └── career_crew.py      # Wires all 5 agents into one pipeline
├── api/
│   ├── main.py             # FastAPI entry point
│   ├── routes.py           # /analyze, /status, /result endpoints
│   └── models.py           # Pydantic request/response models
├── app/
│   └── streamlit_app.py    # Streamlit frontend
├── utils/
│   ├── pdf_reader.py       # PDF text extraction
│   └── groq_client.py      # Shared LLM client with auto-retry
├── data/                   # Temporary storage for uploaded CVs
├── .env                    # API keys — never committed
├── requirements.txt
└── README.md
```

---

## How each agent works

**Agent 1 — CV Parser**
Receives raw text from PyMuPDF and acts as a senior HR professional. Structures the CV into categories: personal info, technical skills, experience, education, projects, and certifications.

**Agent 2 — JD Analyzer**
Acts as a recruitment specialist. Extracts required skills, preferred skills, responsibilities, qualifications, and ATS keywords. Explicitly distinguishes must-haves from nice-to-haves.

**Agent 3 — Gap Analyzer**
Compares the CV summary and JD analysis side by side to produce an overall match score (0–100), categorized skill lists (matched ✅ / missing ❌ / partial ⚠️), and a hiring recommendation.

**Agent 4 — Learning Path Builder**
Receives the gap analysis and uses Tavily to find real, current learning resources. Outputs a prioritized week-by-week roadmap with specific courses, daily practice tasks, mini-projects, and a capstone suggestion.

**Agent 5 — Cover Letter Writer**
Receives the CV summary, JD analysis, and gap analysis. Writes a professional cover letter that references specific projects from the CV, highlights matching skills naturally, and addresses one skill gap with confidence.

---

## Environment variables

| Variable | Required | Where to get |
|----------|----------|--------------|
| `GROQ_API_KEY` | Yes | [console.groq.com](https://console.groq.com) |
| `TAVILY_API_KEY` | Yes | [tavily.com](https://tavily.com) |
| `API_URL` | Deployment only | Set in Streamlit Cloud secrets |

---

## Deployment

The project runs on two free platforms:

**Backend → Render**
Auto-deploys from GitHub on every push. Environment variables are set in the Render dashboard.

**Frontend → Streamlit Community Cloud**
Purpose-built for Streamlit apps, always on, and never sleeps. Secrets are managed through the dashboard.

See [`docs/deployment_guide.md`](docs/deployment_guide.md) for step-by-step instructions.

---

## Design decisions

**Why split frontend and backend across platforms?**
Streamlit Community Cloud never sleeps, so users get an instant-loading UI. The FastAPI backend on Render handles the heavy computation separately. Best user experience at zero cost.

**Why Groq instead of OpenAI?**
Groq is completely free with no credit card required. Llama 3.3 70B handles structured text analysis tasks well, and this keeps the project accessible to anyone who wants to run it locally.

**Why not use CrewAI's built-in LLM wrapper?**
CrewAI 1.14.7 has a compatibility bug with Groq's API that sends unsupported parameters. Using the Groq SDK directly with a custom retry wrapper gives cleaner control over rate limit handling.

**Why background tasks in FastAPI?**
The full pipeline takes 3–5 minutes due to API rate limits. Background tasks let the API return a `job_id` immediately while the frontend polls for progress every few seconds — giving users real-time feedback without request timeouts.

---

## Roadmap

- [x] 5-agent pipeline (CV Parser, JD Analyzer, Gap Analyzer, Learning Path, Cover Letter)
- [x] FastAPI backend with background job processing
- [x] Streamlit frontend with real-time progress tracking
- [x] Auto-retry logic for API rate limits
- [x] Docker containerization
- [ ] RAG-powered job market knowledge base
- [ ] Support for DOCX and TXT CV formats
- [ ] Email delivery of results
- [ ] Interview preparation agent (Agent 6)
- [ ] Comparison mode — analyze multiple jobs simultaneously

---

## Requirements

```
crewai
crewai-tools
langchain-groq
langchain-community
pymupdf
python-dotenv
fastapi
uvicorn
streamlit
requests
tavily-python
groq
```

---

## Author

**Muhammad Haris** — CS Undergraduate @ FAST-NUCES Islamabad (Expected 2027)

[![GitHub](https://img.shields.io/badge/GitHub-muhammad--haris2-black?logo=github)](https://github.com/muhammad-haris2)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Muhammad%20Haris-blue?logo=linkedin)](https://linkedin.com/in/muhammad-haris-455166294)
[![Email](https://img.shields.io/badge/Email-haris101gbb%40gmail.com-red?logo=gmail)](mailto:haris101gbb@gmail.com)

---

## License

MIT — free to use, modify, and distribute.
