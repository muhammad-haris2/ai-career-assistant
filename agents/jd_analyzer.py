"""
jd_analyzer.py — Agent 2: JD Analyzer
"""
from utils.groq_client import call_groq


def analyze_jd(jd_text: str) -> str:
    prompt = f"""You are an expert recruitment specialist with 15 years of experience
analyzing job descriptions. Extract all requirements from the following job description.

JOB DESCRIPTION:
{jd_text}

Extract and organize exactly as follows:

1. ROLE INFO:
   - Job Title:
   - Company:
   - Location:
   - Job Type:
   - Experience Level:

2. REQUIRED SKILLS:
   - Programming Languages:
   - Frameworks & Libraries:
   - Databases:
   - Tools & Platforms:
   - AI/ML Skills:
   - Other Technical Skills:

3. PREFERRED SKILLS:

4. RESPONSIBILITIES: (max 6 bullet points)

5. QUALIFICATIONS:
   - Education required:
   - Years of experience:
   - Other qualifications:

6. KEY KEYWORDS:

7. JD SUMMARY: (2-3 sentences)

Distinguish clearly between required and preferred skills."""

    return call_groq(prompt, temperature=0.3, max_tokens=2000)