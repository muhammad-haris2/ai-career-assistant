"""
gap_analyzer.py
===============
Agent 3: Gap Analyzer
Compares CV analysis vs JD analysis and produces match score + skill gaps.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_gaps(cv_analysis: str, jd_analysis: str) -> str:
    """
    Compare CV against JD and identify gaps.
    
    Args:
        cv_analysis: Output from CV Parser agent
        jd_analysis: Output from JD Analyzer agent
        
    Returns:
        Detailed gap analysis as a string
    """
    prompt = f"""You are a senior career consultant and technical recruiter with 
15 years of experience matching candidates to job requirements.

Compare the candidate's CV analysis against the job description analysis below 
and produce a detailed gap analysis.

CV ANALYSIS:
{cv_analysis}

JOB DESCRIPTION ANALYSIS:
{jd_analysis}

Produce your analysis in exactly this format:

1. OVERALL MATCH SCORE: X/100
   - Provide a realistic score out of 100
   - Be honest and accurate, not overly generous

2. MATCH BREAKDOWN:
   - Technical Skills Match: X/100
   - Experience Match: X/100
   - Education Match: X/100
   - Overall Fit: X/100

3. MATCHED SKILLS: ✅
   List every skill/requirement from the JD that the candidate already has.
   Format: - Skill name: (brief note on candidate's level/experience with it)

4. MISSING SKILLS: ❌
   List every required skill from the JD that the candidate completely lacks.
   Format: - Skill name: (why it matters for this role)

5. PARTIAL MATCHES: ⚠️
   Skills the candidate has at a basic level but needs to improve.
   Format: - Skill name: (what they have vs what's needed)

6. STRENGTHS FOR THIS ROLE:
   List 3-5 specific strengths from the candidate's profile that make 
   them a good fit for this particular role.

7. CRITICAL GAPS:
   List the 3 most important skills/experiences missing that would 
   most impact their chances of getting this role.

8. HIRING RECOMMENDATION:
   - Decision: (Strong Match / Good Match / Partial Match / Weak Match)
   - Reasoning: 2-3 sentences explaining the recommendation

9. QUICK SUMMARY:
   One paragraph summarizing the overall match, key strengths, 
   and main gaps for this candidate-role combination."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )

    return response.choices[0].message.content