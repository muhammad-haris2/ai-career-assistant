"""
gap_analyzer.py — Agent 3: Gap Analyzer
"""
from utils.groq_client import call_groq


def analyze_gaps(cv_analysis: str, jd_analysis: str) -> str:
    prompt = f"""You are a senior career consultant and technical recruiter.
Compare the candidate's CV against the job description and produce a gap analysis.

CV ANALYSIS:
{cv_analysis}

JOB DESCRIPTION ANALYSIS:
{jd_analysis}

Produce your analysis in exactly this format:

1. OVERALL MATCH SCORE: X/100

2. MATCH BREAKDOWN:
   - Technical Skills Match: X/100
   - Experience Match: X/100
   - Education Match: X/100
   - Overall Fit: X/100

3. MATCHED SKILLS: ✅
   - Skill: (brief note)

4. MISSING SKILLS: ❌
   - Skill: (why it matters)

5. PARTIAL MATCHES: ⚠️
   - Skill: (what they have vs what's needed)

6. STRENGTHS FOR THIS ROLE: (3-5 points)

7. CRITICAL GAPS: (top 3 most important missing skills)

8. HIRING RECOMMENDATION:
   - Decision: (Strong Match / Good Match / Partial Match / Weak Match)
   - Reasoning: (2-3 sentences)

9. QUICK SUMMARY: (one paragraph)"""

    return call_groq(prompt, temperature=0.3, max_tokens=2000)