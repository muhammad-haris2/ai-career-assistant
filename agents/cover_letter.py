"""
cover_letter.py
===============
Agent 5: Cover Letter Writer
Writes a tailored, professional cover letter based on CV and JD analysis.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def write_cover_letter(cv_analysis: str, jd_analysis: str, gap_analysis: str) -> str:
    """
    Write a tailored cover letter based on CV, JD, and gap analysis.

    Args:
        cv_analysis: Output from CV Parser agent
        jd_analysis: Output from JD Analyzer agent
        gap_analysis: Output from Gap Analyzer agent

    Returns:
        Professional cover letter as a string
    """
    prompt = f"""You are an expert career coach and professional cover letter writer
with 15 years of experience helping candidates land jobs at top tech companies.

Write a compelling, tailored cover letter based on the information below.

CV ANALYSIS:
{cv_analysis}

JOB DESCRIPTION ANALYSIS:
{jd_analysis}

GAP ANALYSIS:
{gap_analysis}

INSTRUCTIONS:
1. Write a professional cover letter in standard business format
2. Address it to "Hiring Manager" if no specific name is mentioned
3. Reference the EXACT job title from the JD analysis
4. Mention 2-3 SPECIFIC projects from the CV that are most relevant to this role
5. Highlight matched skills naturally within sentences — do not list them
6. Briefly and confidently address 1 gap by showing eagerness to learn
7. Keep it to 4 paragraphs maximum — recruiters don't read long letters
8. End with a clear call to action
9. Make it sound human, confident, and genuine — not generic or robotic
10. Do NOT use cliche phrases like "I am writing to express my interest" or 
    "I am a quick learner" or "I am passionate about"

FORMAT:
[Candidate Name]
[Email] | [Phone] | [GitHub]
[Date]

[Company Name] (if available, else skip)
Hiring Manager

Dear Hiring Manager,

[Paragraph 1 — Opening: Who you are + what role you're applying for + 
one strong hook about why you specifically are a good fit]

[Paragraph 2 — Your most relevant project(s) and how they directly 
relate to what this role requires. Be specific with numbers and outcomes.]

[Paragraph 3 — Your technical skills that match, address one gap 
confidently, show genuine interest in the company/role specifically]

[Paragraph 4 — Closing: Express enthusiasm, call to action, 
thank them for their time]

Sincerely,
[Candidate Name]

Write the complete cover letter now. Make it specific to THIS candidate 
and THIS job — not a generic template."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,  # slightly higher for more natural writing
        max_tokens=1500
    )

    return response.choices[0].message.content