"""
cv_parser.py
============
Agent 1: CV Parser
Uses Groq SDK directly to avoid CrewAI/litellm compatibility issues.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def parse_cv(cv_text: str) -> str:
    """
    Parse CV text and extract structured information.
    Returns structured CV analysis as a string.
    """
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
   - Internships/Jobs: (list each with title, company, duration)

4. EDUCATION:
   - Degree:
   - University:
   - Graduation year:

5. PROJECTS: (for each project)
   - Project name:
   - Technologies used:
   - Key achievements:

6. CERTIFICATIONS:
   (list all)

7. CANDIDATE SUMMARY:
   (2-3 sentences summarizing profile, strengths, experience level)

Be precise. Only include information explicitly stated in the CV."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )

    return response.choices[0].message.content