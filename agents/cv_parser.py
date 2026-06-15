"""
cv_parser.py — Agent 1: CV Parser
"""
from utils.groq_client import call_groq


def parse_cv(cv_text: str) -> str:
    prompt = f"""You are a senior HR professional with 15 years of experience reading CVs.
Analyze the following CV and extract all information into a structured format.

CV TEXT:
{cv_text}

Extract and organize exactly as follows:

1. PERSONAL INFO:
   - Name:
   - Location:
   - Email:
   - Phone:
   - GitHub:
   - LinkedIn:

2. TECHNICAL SKILLS:
   - Programming Languages:
   - Frameworks & Libraries:
   - Databases:
   - Tools & Platforms:
   - AI/ML Skills:
   - Other Technical Skills:

3. EXPERIENCE:
   - Years of experience:
   - Internships/Jobs:

4. EDUCATION:
   - Degree:
   - University:
   - Graduation year:

5. PROJECTS: (for each project)
   - Project name:
   - Technologies used:
   - Key achievements:

6. CERTIFICATIONS:

7. CANDIDATE SUMMARY:
   (2-3 sentences)

Be precise. Only include information explicitly stated in the CV."""

    return call_groq(prompt, temperature=0.3, max_tokens=2000)