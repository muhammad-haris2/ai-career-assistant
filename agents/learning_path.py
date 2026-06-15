"""
learning_path.py
================
Agent 4: Learning Path Builder
Takes gap analysis and builds a personalized week-by-week learning roadmap.
Uses Tavily to find real, current learning resources.
"""

import os
from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_resources(skill: str) -> str:
    """Search Tavily for learning resources for a specific skill."""
    try:
        results = tavily_client.search(
            query=f"best free course tutorial to learn {skill} for beginners 2025",
            max_results=3
        )
        resources = []
        for r in results["results"]:
            resources.append(f"- {r['title']}: {r['url']}")
        return "\n".join(resources)
    except Exception:
        return f"- Search for '{skill} tutorial' on YouTube or freeCodeCamp"


def build_learning_path(gap_analysis: str, jd_analysis: str) -> str:
    """
    Build a personalized learning roadmap based on gap analysis.

    Args:
        gap_analysis: Output from Gap Analyzer agent
        jd_analysis: Output from JD Analyzer agent

    Returns:
        Detailed week-by-week learning roadmap as a string
    """

    # Step 1: Extract critical gaps using Groq
    extract_prompt = f"""Based on this gap analysis, list ONLY the missing and 
critical skills that need to be learned. List them in priority order 
(most important for the job first). Return ONLY a numbered list, nothing else.

GAP ANALYSIS:
{gap_analysis}"""

    extract_response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": extract_prompt}],
        temperature=0.1,
        max_tokens=300
    )

    skills_to_learn = extract_response.choices[0].message.content

    # Step 2: Search for resources for top 4 skills
    print("   Searching for learning resources...")
    skill_lines = [
        line.strip() for line in skills_to_learn.split("\n")
        if line.strip() and any(c.isalpha() for c in line)
    ][:4]

    resource_data = {}
    for skill_line in skill_lines:
        # Clean skill name
        skill = skill_line.lstrip("0123456789.-) ").strip()
        if skill:
            print(f"   Finding resources for: {skill}")
            resource_data[skill] = search_resources(skill)

    # Step 3: Build resources string
    resources_text = ""
    for skill, resources in resource_data.items():
        resources_text += f"\n{skill}:\n{resources}\n"

    # Step 4: Generate full learning roadmap
    roadmap_prompt = f"""You are an expert career coach and technical mentor.
Build a detailed, realistic week-by-week learning roadmap.

SKILLS TO LEARN (in priority order):
{skills_to_learn}

REAL LEARNING RESOURCES FOUND:
{resources_text}

JOB REQUIREMENTS CONTEXT:
{jd_analysis}

Create the roadmap in exactly this format:

LEARNING ROADMAP
================

TOTAL ESTIMATED TIME: X weeks

PRIORITY ORDER:
Explain in 2 sentences why you ordered the skills this way.

---

WEEK 1-2: [Skill Name] — [Why most important]
Goal: What the learner will be able to do after these 2 weeks
Resources:
  • [Resource name and URL from the search results above]
  • [Second resource]
Daily practice: What to practice each day (30-60 mins)
Mini project: A small project to build to solidify learning

---

WEEK 3-4: [Next Skill]
Goal: ...
Resources: ...
Daily practice: ...
Mini project: ...

---

[Continue for all skills]

---

FINAL PROJECT SUGGESTION:
Suggest one capstone project that combines ALL the learned skills,
which can be added to GitHub and CV.

TIPS FOR SUCCESS:
3-4 practical tips for staying consistent and learning effectively."""

    roadmap_response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": roadmap_prompt}],
        temperature=0.4,
        max_tokens=2500
    )

    return roadmap_response.choices[0].message.content