"""
Shared helper for extracting JSON from an LLM response that may be wrapped
in a markdown code fence or have stray text before/after it — common even
when the prompt says "respond ONLY in JSON," especially with models like
Llama 3.3 that don't have a strict JSON output mode.

Used by both investigator_agent.py and recommendation_agent.py.
"""

import json
import re


def extract_json(raw_response: str) -> dict:
    """
    Try increasingly permissive strategies to pull a JSON object out of a
    raw LLM response string. Raises json.JSONDecodeError if none work, so
    the caller's existing except-block fallback still applies.
    """
    text = raw_response.strip()

    # Strategy 1: response is already clean JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: strip a markdown code fence (```json ... ``` or ``` ... ```)
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 3: grab the first {...} block anywhere in the text (handles
    # a stray leading/trailing sentence around the JSON)
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        return json.loads(brace_match.group(0))  # let this raise if it still fails

    # Nothing worked — raise so the caller's fallback handling kicks in
    raise json.JSONDecodeError("No JSON object found in response", text, 0)