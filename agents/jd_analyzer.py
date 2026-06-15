"""
jd_analyzer.py
==============
Agent 2: Job Description Analyzer
Extracts required skills, qualifications, and expectations from a job description.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_jd(jd_text: str) -> str:
    """
    Analyze a job description and extract structured requirements.
    Returns structured JD analysis as a string.
    """
    prompt = f"""You are an expert recruitment specialist with 15 years of experience 
analyzing job descriptions. Extract all requirements from the following job description.

JOB DESCRIPTION:
{jd_text}

Extract and organize exactly as follows:

1. ROLE INFO:
   - Job Title:
   - Company (if mentioned):
   - Location (if mentioned):
   - Job Type: (internship/full-time/part-time/remote)
   - Experience Level: (entry/junior/mid/senior)

2. REQUIRED SKILLS: (must-have, explicitly stated as required)
   - Programming Languages:
   - Frameworks & Libraries:
   - Databases:
   - Tools & Platforms:
   - AI/ML Skills:
   - Other Technical Skills:

3. PREFERRED SKILLS: (nice-to-have, mentioned as preferred/bonus/plus)
   - List all preferred skills:

4. RESPONSIBILITIES:
   - List the main job responsibilities (max 6 bullet points)

5. QUALIFICATIONS:
   - Education required:
   - Years of experience required:
   - Other qualifications:

6. KEY KEYWORDS:
   - List the most important technical keywords from this JD that an ATS would scan for

7. JD SUMMARY:
   - Write 2-3 sentences summarizing what this role is about and what kind of 
     candidate they are looking for.

Be precise. Distinguish clearly between required and preferred skills."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )

    return response.choices[0].message.content