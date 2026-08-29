"""
Phase 2 - Step 3: RAG-grounded investigator agent.

Takes one flagged conjunction event, retrieves relevant guidance from the
knowledge base, and produces a structured risk assessment. This is the only
LLM call in Phase 2 — detection and screening upstream are deterministic math.
"""

import json

from json_utils import extract_json
from llm_client import call_llm
from rag import KnowledgeBase

SYSTEM_PROMPT = """You are a spacecraft conjunction risk investigator. You are \
given a real flagged close-approach (conjunction) event between two tracked \
objects, plus retrieved reference guidance. Produce a structured risk \
assessment. Be precise, cite which retrieved guidance you relied on by source \
filename, and do not invent numbers not present in the event data. \
Respond ONLY in valid JSON matching this schema, with no other text:

{
  "severity": "low" | "medium" | "high",
  "rationale": "2-4 sentences explaining the severity call, referencing the \
actual miss distance and relative velocity given",
  "guidance_used": ["list of source filenames actually relied on"],
  "recommended_urgency": "monitor" | "plan_maneuver_review" | "immediate_review"
}
"""


def build_query(event: dict) -> str:
    return (
        f"conjunction event miss distance {event['miss_distance_km']} km "
        f"relative velocity {event['relative_velocity_km_s']} km/s "
        f"collision avoidance decision criteria"
    )


def investigate_event(event: dict, kb: KnowledgeBase) -> dict:
    query = build_query(event)
    retrieved = kb.retrieve(query, top_k=3)

    retrieved_text = "\n\n".join(
        f"[Source: {r['source']}]\n{r['text']}" for r in retrieved
    )

    user_prompt = f"""FLAGGED EVENT:
Object A: {event['object_a']}
Object B: {event['object_b']}
Miss distance: {event['miss_distance_km']} km
Relative velocity: {event['relative_velocity_km_s']} km/s
Time of closest approach (UTC): {event['time_of_closest_approach_utc']}

RETRIEVED GUIDANCE:
{retrieved_text}

Produce the risk assessment JSON now."""

    raw_response = call_llm(SYSTEM_PROMPT, user_prompt)

    try:
        assessment = extract_json(raw_response)
    except json.JSONDecodeError:
        # Keep the raw text so nothing is silently lost if the model still
        # doesn't return parseable JSON — check _raw_response in the saved
        # file if you see this happen often, and tighten SYSTEM_PROMPT.
        assessment = {
            "severity": "unknown",
            "rationale": "Could not parse model response as JSON.",
            "guidance_used": [],
            "recommended_urgency": "unknown",
            "_raw_response": raw_response,
        }

    assessment["event"] = event
    assessment["retrieved_sources"] = [r["source"] for r in retrieved]
    return assessment