"""
Phase 4 - Step 2: Incident report generation.

Turns one event's full pipeline output (flagged event + risk assessment +
scored maneuver plan + final recommendation) into a human-readable Markdown
incident report — the last step of the "telemetry in, decision out" story.
"""

import os
from datetime import datetime, timezone

REPORTS_DIR = "data/reports"


def generate_report_markdown(maneuver_plan: dict, decision: dict) -> str:
    event = maneuver_plan["event"]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = []
    lines.append("# Collision Avoidance Incident Report")
    lines.append(f"\n**Generated:** {generated_at}")
    lines.append(f"\n**Objects involved:** {event['object_a']} and {event['object_b']}")
    lines.append(f"\n**Time of closest approach (UTC):** {event['time_of_closest_approach_utc']}")

    lines.append("\n## Flagged Event Summary")
    lines.append(f"- Miss distance (SGP4 screening, Phase 2): {event['miss_distance_km']} km")
    lines.append(f"- Relative velocity: {event['relative_velocity_km_s']} km/s")

    lines.append("\n## Risk Assessment")
    lines.append(f"- **Severity:** {maneuver_plan.get('severity')}")
    lines.append(f"- **Recommended urgency:** {maneuver_plan.get('recommended_urgency')}")
    lines.append(f"- **Rationale:** {maneuver_plan.get('rationale')}")

    lines.append("\n## Maneuver Options Considered")
    lines.append(
        f"- No-maneuver baseline miss distance (two-body simulation, Phase 3): "
        f"{maneuver_plan['baseline_miss_distance_km']} km"
    )
    lines.append(
        "\n| Option | New Miss Distance (km) | Risk Reduction | "
        "Delta-v (m/s) | Schedule Impact | Score |"
    )
    lines.append("|---|---|---|---|---|---|")
    for c in maneuver_plan["scored_candidates"]:
        lines.append(
            f"| {c['maneuver_name']} | {c['new_miss_distance_km']} | "
            f"{c['risk_reduction_pct']:+.1f}% | {c['delta_v_m_s']} | "
            f"{c['schedule_impact']} | {c['score']:+.2f} |"
        )

    lines.append("\n## Final Recommendation")
    lines.append(f"- **Recommended action:** {decision.get('recommended_action')}")
    lines.append(f"- **Confidence:** {decision.get('confidence')}")
    lines.append(f"- **Justification:** {decision.get('justification')}")

    sources = decision.get("retrieved_sources", [])
    if sources:
        lines.append(f"\n*Guidance referenced: {', '.join(sources)}*")

    return "\n".join(lines)


def save_report(event_idx: int, report_text: str) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"incident_report_event_{event_idx}.md")
    with open(path, "w") as f:
        f.write(report_text)
    return path