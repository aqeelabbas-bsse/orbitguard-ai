"""
Phase 4 - Step 1: Recommendation agent.

This is the second and final LLM call in the whole OrbitGuard AI pipeline.
It takes an event's Phase 2 risk assessment plus its Phase 3 scored maneuver
plan, retrieves decision-criteria guidance, and decides the final
recommended action — which may or may not be the highest-scored maneuver,
since a low-severity event can reasonably warrant "keep monitoring, don't
spend fuel" even if a burn scores positively on paper. That judgment call is
exactly why this step is an LLM agent and not just "pick argmax(score)".
"""

import json

from json_utils import extract_json
from llm_client import call_llm
from rag import KnowledgeBase

SYSTEM_PROMPT = """You are a spacecraft collision-avoidance recommendation \
agent. You are given a risk assessment for a flagged conjunction event, a \
set of already-scored candidate maneuvers (deterministically computed: new \
miss distance, risk reduction percentage, fuel cost, schedule impact, and a \
numeric score) plus a no-maneuver baseline, and retrieved decision-criteria \
guidance.

Decide the final recommended action. Do not simply default to the \
highest-scored candidate — use judgment grounded in the retrieved guidance \
and the stated severity/urgency. A low-severity event can reasonably \
warrant "no_maneuver" (continue monitoring) even if a burn scores \
positively, since fuel is a scarce resource — in that case, justify it on \
severity and fuel-conservation grounds, not by understating the maneuver's \
actual effectiveness. A high-severity event should generally proceed with \
the best-scoring maneuver unless its fuel cost is clearly disproportionate. \
Do not invent numbers not present in the data provided, and do not \
characterize a number in a way that contradicts its actual value (e.g. \
do not call a large risk_reduction_pct "low" or "small" — describe it \
accurately even when explaining why you're not acting on it).

Respond ONLY in valid JSON matching this schema, with no other text:

{
  "recommended_action": "<a maneuver_name from the candidates, or 'no_maneuver'>",
  "justification": "3-5 sentences referencing actual numbers from the data \
provided and the retrieved guidance by filename",
  "confidence": "low" | "medium" | "high"
}
"""


def build_query(maneuver_plan: dict) -> str:
    return (
        f"severity {maneuver_plan.get('severity')} "
        f"urgency {maneuver_plan.get('recommended_urgency')} "
        f"decide whether to maneuver fuel cost tradeoff"
    )


def recommend_action(maneuver_plan: dict, kb: KnowledgeBase) -> dict:
    query = build_query(maneuver_plan)
    retrieved = kb.retrieve(query, top_k=2)
    retrieved_text = "\n\n".join(
        f"[Source: {r['source']}]\n{r['text']}" for r in retrieved
    )

    candidates_summary = json.dumps(maneuver_plan["scored_candidates"], indent=2)

    user_prompt = f"""EVENT: {maneuver_plan['event']['object_a']} <-> {maneuver_plan['event']['object_b']}

RISK ASSESSMENT (from Phase 2):
Severity: {maneuver_plan.get('severity')}
Rationale: {maneuver_plan.get('rationale')}
Recommended urgency: {maneuver_plan.get('recommended_urgency')}

MANEUVER OPTIONS (from Phase 3, already scored):
No-maneuver baseline miss distance: {maneuver_plan['baseline_miss_distance_km']} km
{candidates_summary}

RETRIEVED GUIDANCE:
{retrieved_text}

Decide and justify the final recommended action now, as JSON."""

    raw_response = call_llm(SYSTEM_PROMPT, user_prompt)

    try:
        decision = extract_json(raw_response)
    except json.JSONDecodeError:
        # Fail safe rather than silent: fall back to the top-scored
        # candidate so the pipeline still produces a usable report.
        decision = {
            "recommended_action": maneuver_plan["ranked_best_to_worst"][0],
            "justification": "Could not parse model response as JSON; "
                              "falling back to the top-scored candidate.",
            "confidence": "low",
            "_raw_response": raw_response,
        }

    decision["retrieved_sources"] = [r["source"] for r in retrieved]
    return decision