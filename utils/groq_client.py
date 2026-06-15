"""
groq_client.py
==============
Shared Groq client with automatic retry logic.
If a 429 rate limit error occurs, waits and retries automatically
instead of failing the entire pipeline.
"""

import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Single shared client used by all agents
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"


def call_groq(prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
    """
    Call Groq API with automatic retry on rate limit errors.
    
    Retries up to 3 times with increasing wait times:
    - First retry: wait 30 seconds
    - Second retry: wait 60 seconds  
    - Third retry: wait 90 seconds
    
    Args:
        prompt: The prompt to send
        temperature: Model temperature (0.1-1.0)
        max_tokens: Maximum tokens in response
        
    Returns:
        Response text as string
    """
    max_retries = 3
    wait_times  = [30, 60, 90]

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

        except Exception as e:
            error_str = str(e)

            # Check if it's a rate limit error
            if "429" in error_str or "rate_limit" in error_str.lower():
                if attempt < max_retries - 1:
                    wait = wait_times[attempt]
                    print(f"   Rate limit hit. Waiting {wait}s before retry "
                          f"(attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait)
                    continue
                else:
                    raise Exception(
                        f"Rate limit exceeded after {max_retries} retries. "
                        f"Please wait a minute and try again."
                    )
            else:
                # Not a rate limit error — raise immediately
                raise e

    raise Exception("Max retries reached")