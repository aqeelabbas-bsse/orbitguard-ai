"""
Phase 5 - Frontend data build step.

Regenerates frontend/data.js from the REAL pipeline output on disk:
  data/events/flagged_conjunctions.json
  data/risk_assessments/event_N.json
  data/maneuver_plans/event_N.json
  data/decisions/event_N.json
  data/reports/incident_report_event_N.md

Run this after main_pipeline.py so the dashboard always reflects the
latest real run instead of a hand-pasted snapshot.

Usage:
    python build_frontend_data.py
"""

import glob
import json
import os
import re
from datetime import datetime, timezone

FRONTEND_DIR = "frontend"
DATA_JS = os.path.join(FRONTEND_DIR, "data.js")
STATIC_SECTIONS = os.path.join(FRONTEND_DIR, "_data_static.js")

EVENTS_FILE = "data/events/flagged_conjunctions.json"
RISK_DIR = "data/risk_assessments"
PLANS_DIR = "data/maneuver_plans"
DECISIONS_DIR = "data/decisions"
REPORTS_DIR = "data/reports"

# Same friendly labels the UI uses — applied to agent prose so the rendered
# text reads cleanly instead of showing raw .txt filenames.
GUIDANCE_LABELS = {
    "conjunction_assessment_basics.txt": "Conjunction Assessment Guidelines",
    "debris_mitigation_principles.txt": "Debris Mitigation Principles",
    "maneuver_decision_criteria.txt": "Maneuver Decision Criteria",
    "relative_velocity_and_severity.txt": "Relative Velocity Risk Model",
    "fuel_and_schedule_tradeoffs.txt": "Fuel & Schedule Tradeoffs",
    "cosmos_1408_background.txt": "Cosmos 1408 Debris Field Background",
}


def friendly(text: str) -> str:
    """Replace raw knowledge-base filenames in agent prose with clean labels."""
    if not text:
        return text
    for fname, label in GUIDANCE_LABELS.items():
        text = text.replace(fname, label)
    return text


def load_json(path):
    with open(path) as f:
        return json.load(f)


def read_indexed(directory, pattern):
    """Load event_N.json files keyed by their N."""
    out = {}
    for path in glob.glob(os.path.join(directory, pattern)):
        m = re.search(r"event_(\d+)", os.path.basename(path))
        if m:
            out[int(m.group(1))] = load_json(path)
    return out


def read_reports():
    out = {}
    for path in glob.glob(os.path.join(REPORTS_DIR, "incident_report_event_*.md")):
        m = re.search(r"event_(\d+)", os.path.basename(path))
        if m:
            with open(path) as f:
                out[int(m.group(1))] = f.read()
    return out


def build_events(risk, plans, decisions, reports):
    events = []
    for idx in sorted(risk.keys()):
        r = risk[idx]
        p = plans.get(idx, {})
        d = decisions.get(idx, {})
        ev = r.get("event", {})

        candidates = []
        for c in p.get("scored_candidates", []):
            candidates.append({
                "name": c.get("maneuver_name"),
                "direction": c.get("direction"),
                "deltaVms": c.get("delta_v_m_s"),
                "newMissDistanceKm": c.get("new_miss_distance_km"),
                "riskReductionPct": c.get("risk_reduction_pct"),
                "scheduleImpact": c.get("schedule_impact"),
                "score": c.get("score"),
            })

        events.append({
            "id": idx,
            "objectA": ev.get("object_a"),
            "objectB": ev.get("object_b"),
            "missDistanceKm": ev.get("miss_distance_km"),
            "relVelocityKmS": ev.get("relative_velocity_km_s"),
            "tcaUtc": ev.get("time_of_closest_approach_utc"),
            "tMinutesAtGen": ev.get("t_minutes_from_now"),
            "severity": r.get("severity"),
            "urgency": r.get("recommended_urgency"),
            "rationale": friendly(r.get("rationale", "")),
            "guidanceUsed": r.get("guidance_used", []),
            "retrievedSources": r.get("retrieved_sources", []),
            "maneuverableObject": p.get("maneuverable_object"),
            "otherObject": p.get("other_object"),
            "decisionTMinutes": p.get("decision_t_minutes_from_now"),
            "originalMissDistanceSgp4": p.get("original_miss_distance_km_sgp4"),
            "baselineMissDistanceKm": p.get("baseline_miss_distance_km"),
            "scoredCandidates": candidates,
            "rankedBestToWorst": p.get("ranked_best_to_worst", []),
            "decision": {
                "action": d.get("recommended_action"),
                "confidence": d.get("confidence"),
                "justification": friendly(d.get("justification", "")),
                "sources": d.get("retrieved_sources", []),
            },
            "reportMarkdown": reports.get(idx, ""),
        })
    return events


def priority_order(events):
    """Medium/high urgency first, then soonest time to closest approach."""
    rank = {"immediate_review": 0, "plan_maneuver_review": 1, "monitor": 2}
    ordered = sorted(
        events,
        key=lambda e: (rank.get(e["urgency"], 3), e.get("tMinutesAtGen") or 0),
    )
    return [e["id"] for e in ordered]


def main():
    if not os.path.isdir(FRONTEND_DIR):
        print(f"[error] '{FRONTEND_DIR}/' not found. Create it and copy the "
              "design export into it first (see Phase 5 steps).")
        return
    if not os.path.exists(STATIC_SECTIONS):
        print(f"[error] '{STATIC_SECTIONS}' not found. This holds the "
              "non-generated parts of data.js (pipeline stages, architecture "
              "copy, knowledge base, helper functions). See Phase 5 steps.")
        return

    all_events = load_json(EVENTS_FILE) if os.path.exists(EVENTS_FILE) else []
    risk = read_indexed(RISK_DIR, "event_*.json")
    plans = read_indexed(PLANS_DIR, "event_*.json")
    decisions = read_indexed(DECISIONS_DIR, "event_*.json")
    reports = read_reports()

    if not risk:
        print("[error] No risk assessments found. Run the pipeline first.")
        return

    events = build_events(risk, plans, decisions, reports)

    # Count unique objects appearing across all screened conjunctions
    unique_objects = set()
    for e in all_events:
        unique_objects.add(e.get("object_a"))
        unique_objects.add(e.get("object_b"))

    stats = {
        "objectsTracked": 240,  # config.py: 2 groups x MAX_OBJECTS_PER_GROUP
        "tleGroups": [
            {"id": "starlink", "label": "STARLINK",
             "desc": "Active LEO constellation"},
            {"id": "cosmos-1408-debris", "label": "COSMOS 1408 DEB",
             "desc": "2021 ASAT test debris field"},
        ],
        "screenedTotal": len(all_events),
        "uniqueObjectsInConjunctions": len(unique_objects),
        "cosmosPairs": sum(
            1 for e in all_events
            if "DEB" in (e.get("object_a", "") + e.get("object_b", "")).upper()
        ),
        "conjunctionThresholdKm": 100,
        "propagationHours": 96,
        "stepMinutes": 5,
        "maxEventsInvestigated": len(events),
        "generatedAtUtc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    with open(STATIC_SECTIONS) as f:
        static_js = f.read()

    order = priority_order(events)

    out = []
    out.append("// GENERATED by build_frontend_data.py — do not edit by hand.")
    out.append("// Rebuilt from real pipeline output in data/ after each run.")
    out.append(f"// Generated: {stats['generatedAtUtc']}\n")
    out.append(f"export const STATS = {json.dumps(stats, indent=2)};\n")
    out.append(static_js.rstrip() + "\n")
    out.append(f"export const EVENTS = {json.dumps(events, indent=2)};\n")
    out.append(
        f"export const EVENTS_BY_PRIORITY = {json.dumps(order)}"
        ".map((id) => EVENTS.find((e) => e.id === id)).filter(Boolean);\n"
    )

    with open(DATA_JS, "w") as f:
        f.write("\n".join(out))

    print(f"[build] Wrote {DATA_JS}")
    print(f"[build] {len(events)} investigated events, "
          f"{len(all_events)} total screened, "
          f"{len(unique_objects)} unique objects")
    print(f"[build] Priority order: {order}")


if __name__ == "__main__":
    main()