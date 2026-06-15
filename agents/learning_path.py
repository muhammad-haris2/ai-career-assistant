"""
learning_path.py — Agent 4: Learning Path Builder
"""
import os
from tavily import TavilyClient
from dotenv import load_dotenv
from utils.groq_client import call_groq

load_dotenv()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_resources(skill: str) -> str:
    try:
        results = tavily_client.search(
            query=f"best free course to learn {skill} for beginners 2025",
            max_results=2
        )
        resources = []
        for r in results["results"]:
            resources.append(f"  • {r['title']}: {r['url']}")
        return "\n".join(resources)
    except Exception:
        return f"  • Search '{skill} tutorial' on YouTube or freeCodeCamp"


def build_learning_path(gap_analysis: str, jd_analysis: str) -> str:

    # Step 1: Extract skills to learn
    extract_prompt = f"""Based on this gap analysis, list ONLY the missing and 
critical skills. Priority order (most important first). 
Return ONLY a numbered list, nothing else. Maximum 5 skills.

GAP ANALYSIS:
{gap_analysis}"""

    skills_text = call_groq(extract_prompt, temperature=0.1, max_tokens=200)

    # Step 2: Search for resources
    print("   Searching for learning resources...")
    skill_lines = [
        line.strip() for line in skills_text.split("\n")
        if line.strip() and any(c.isalpha() for c in line)
    ][:4]

    resources_text = ""
    for skill_line in skill_lines:
        skill = skill_line.lstrip("0123456789.-) ").strip()
        if skill:
            print(f"   Finding resources for: {skill}")
            resources = search_resources(skill)
            resources_text += f"\n{skill}:\n{resources}\n"

    # Step 3: Build roadmap
    roadmap_prompt = f"""You are an expert career coach.
Build a realistic week-by-week learning roadmap.

SKILLS TO LEARN (priority order):
{skills_text}

REAL RESOURCES FOUND:
{resources_text}

Create the roadmap in this format:

LEARNING ROADMAP
================
TOTAL ESTIMATED TIME: X weeks

PRIORITY ORDER REASONING: (2 sentences)

---
WEEK 1-2: [Skill] — [Why important]
Goal: What learner can do after 2 weeks
Resources:
[use the real URLs from above]
Daily practice: 30-60 mins activity
Mini project: Small project to build

---
[Continue for each skill]

---
FINAL PROJECT: One capstone combining all skills for GitHub/CV

TIPS FOR SUCCESS: 3 practical tips"""

    return call_groq(roadmap_prompt, temperature=0.4, max_tokens=2000)