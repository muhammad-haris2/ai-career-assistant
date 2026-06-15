"""
cover_letter.py — Agent 5: Cover Letter Writer
"""
from utils.groq_client import call_groq
from datetime import date

def write_cover_letter(cv_analysis: str, jd_analysis: str, gap_analysis: str) -> str:
    prompt = f"""You are an expert career coach and professional cover letter writer.
Write a compelling, tailored cover letter based on the information below.

CV ANALYSIS:
{cv_analysis}

JOB DESCRIPTION ANALYSIS:
{jd_analysis}

GAP ANALYSIS:
{gap_analysis}

INSTRUCTIONS:
1. Write in standard business letter format
2. Address to "Hiring Manager" 
3. Reference the EXACT job title from the JD
4. Mention 2-3 SPECIFIC projects from the CV most relevant to this role
5. Highlight matched skills naturally — do not list them
6. Briefly address 1 gap by showing eagerness to learn
7. Keep to 4 paragraphs maximum
8. End with a clear call to action
9. Sound human and genuine — not generic
10. Do NOT use "I am writing to express my interest" or "I am passionate about"

FORMAT:
[Name] | [Email] | [Phone] | [GitHub]
{date.today().strftime("%B %d, %Y")}

Dear Hiring Manager,

[Paragraph 1 — Who you are + role + one strong hook]
[Paragraph 2 — Most relevant projects with specific numbers]
[Paragraph 3 — Matching skills + address one gap confidently]
[Paragraph 4 — Closing + call to action]

Sincerely,
[Name]"""

    return call_groq(prompt, temperature=0.7, max_tokens=1500)