"""
Phase 3 - Step 2: Deterministic risk/cost scoring.

Scores each simulated maneuver candidate on three factors: how much it
reduces collision risk (via increased miss distance vs. the no-maneuver
baseline), how much fuel it costs (delta-v), and a simplified schedule-impact
weight per maneuver type.

This is plain arithmetic — no LLM call. The reasoning/judgment layer comes
later in Phase 4, which takes this scored comparison as input context for
the recommendation agent.
"""

# Weights control how much each factor matters in the combined score.
# These are prototype-level assumptions, not derived from a real mission's
# actual constraints — documented here so they're easy to explain or tune.
RISK_REDUCTION_WEIGHT = 1.0     # per percentage point of miss-distance improvement
FUEL_COST_WEIGHT = 0.05         # per meter/second of delta-v spent
SCHEDULE_WEIGHT = 2.0           # per unit of schedule-impact score

# Simplified relative schedule-impact assumption per maneuver direction.
# A prograde (along-track) burn is generally simpler to plan around than a
# radial burn, which more directly reshapes the orbit geometry.
SCHEDULE_IMPACT_BY_DIRECTION = {
    "prograde": 1.0,
    "radial": 1.5,
}


def score_candidate(candidate: dict, baseline_miss_distance_km: float) -> dict:
    new_d = candidate["new_miss_distance_km"]
    risk_reduction_pct = (
        ((new_d - baseline_miss_distance_km) / baseline_miss_distance_km) * 100
        if baseline_miss_distance_km > 0
        else 0.0
    )

    delta_v_m_s = candidate["delta_v_km_s"] * 1000
    schedule_impact = SCHEDULE_IMPACT_BY_DIRECTION.get(candidate["direction"], 1.0)

    score = (
        RISK_REDUCTION_WEIGHT * risk_reduction_pct
        - FUEL_COST_WEIGHT * delta_v_m_s
        - SCHEDULE_WEIGHT * schedule_impact
    )

    return {
        **candidate,
        "risk_reduction_pct": round(risk_reduction_pct, 2),
        "delta_v_m_s": round(delta_v_m_s, 2),
        "schedule_impact": schedule_impact,
        "score": round(score, 3),
    }


def score_all_candidates(maneuver_result: dict) -> dict:
    baseline_km = maneuver_result["baseline_miss_distance_km"]
    scored = [score_candidate(c, baseline_km) for c in maneuver_result["candidates"]]
    scored.sort(key=lambda c: c["score"], reverse=True)

    maneuver_result["scored_candidates"] = scored
    maneuver_result["ranked_best_to_worst"] = [c["maneuver_name"] for c in scored]
    return maneuver_result