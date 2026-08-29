"""
Phase 3 entry point — OrbitGuard AI

Run this after Phase 2 to:
  1. Load the risk-assessed events from Phase 2
  2. Simulate 2 candidate avoidance maneuvers per event (real two-body physics)
  3. Score each candidate deterministically on risk reduction vs. fuel/schedule cost
  4. Save ranked maneuver plans to data/maneuver_plans/

No LLM call happens in this phase — it's a fully deterministic simulation and
scoring pipeline that Phase 4's recommendation agent will reason over.

Usage:
    python main_phase3.py
"""

import glob
import json
import os

from conjunction import load_all_propagated
from maneuver import simulate_maneuvers_for_event
from scoring import score_all_candidates

RISK_ASSESSMENTS_DIR = "data/risk_assessments"
MANEUVER_PLANS_DIR = "data/maneuver_plans"


def load_risk_assessments():
    assessments = []
    for path in sorted(glob.glob(os.path.join(RISK_ASSESSMENTS_DIR, "*.json"))):
        with open(path) as f:
            assessments.append(json.load(f))
    return assessments


def main():
    print("=" * 60)
    print("OrbitGuard AI — Phase 3: Maneuver Simulation + Risk/Cost Scoring")
    print("=" * 60)

    assessments = load_risk_assessments()
    if not assessments:
        print("[error] No risk assessments found. Run Phase 2 first.")
        return
    print(f"[load] Loaded {len(assessments)} risk-assessed events from Phase 2")

    all_objects = load_all_propagated()
    print(f"[load] Loaded {len(all_objects)} objects' propagated states from Phase 1")

    os.makedirs(MANEUVER_PLANS_DIR, exist_ok=True)

    for idx, assessment in enumerate(assessments, start=1):
        event = assessment["event"]
        print(f"\n[{idx}/{len(assessments)}] {event['object_a']} <-> {event['object_b']}")

        maneuver_result = simulate_maneuvers_for_event(event, all_objects)
        scored_result = score_all_candidates(maneuver_result)

        # Carry the Phase 2 risk assessment along so Phase 4 has everything
        # it needs in one place, without re-reading multiple files.
        scored_result["severity"] = assessment.get("severity")
        scored_result["rationale"] = assessment.get("rationale")
        scored_result["recommended_urgency"] = assessment.get("recommended_urgency")

        out_path = os.path.join(MANEUVER_PLANS_DIR, f"event_{idx}.json")
        with open(out_path, "w") as f:
            json.dump(scored_result, f, indent=2)

        best = scored_result["ranked_best_to_worst"][0]
        print(f"    baseline (no maneuver) miss distance: "
              f"{scored_result['baseline_miss_distance_km']} km")
        for c in scored_result["scored_candidates"]:
            print(f"    {c['maneuver_name']:15s} -> new miss distance "
                  f"{c['new_miss_distance_km']:8.1f} km  "
                  f"risk_reduction={c['risk_reduction_pct']:+6.1f}%  "
                  f"score={c['score']:+7.2f}")
        print(f"    best candidate: {best}")

    print("\n" + "=" * 60)
    print(f"Phase 3 complete. Maneuver plans saved to {MANEUVER_PLANS_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()