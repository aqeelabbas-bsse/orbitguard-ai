"""
Phase 4 entry point — OrbitGuard AI

Run this after Phase 3 to:
  1. Load each event's scored maneuver plan
  2. Run the recommendation agent (final LLM call in the pipeline)
  3. Generate a human-readable incident report per event

Usage:
    python main_phase4.py
"""

import glob
import json
import os
import time

from rag import KnowledgeBase
from recommendation_agent import recommend_action
from report_generator import generate_report_markdown, save_report

MANEUVER_PLANS_DIR = "data/maneuver_plans"
DECISIONS_DIR = "data/decisions"

# Same pacing as Phase 2 — stays under the watsonx.ai Lite plan's
# requests-per-minute limit. call_llm() also retries on 429, but pacing
# calls like this means you rely on that less.
SECONDS_BETWEEN_CALLS = 8


def load_maneuver_plans():
    plans = []
    for path in sorted(glob.glob(os.path.join(MANEUVER_PLANS_DIR, "*.json"))):
        with open(path) as f:
            plans.append(json.load(f))
    return plans


def main():
    print("=" * 60)
    print("OrbitGuard AI — Phase 4: Recommendation Agent + Report Generation")
    print("=" * 60)

    plans = load_maneuver_plans()
    if not plans:
        print("[error] No maneuver plans found. Run Phase 3 first.")
        return
    print(f"[load] Loaded {len(plans)} scored maneuver plans from Phase 3")

    kb = KnowledgeBase()
    os.makedirs(DECISIONS_DIR, exist_ok=True)

    for idx, maneuver_plan in enumerate(plans, start=1):
        event = maneuver_plan["event"]
        print(f"\n[{idx}/{len(plans)}] {event['object_a']} <-> {event['object_b']}")

        decision = recommend_action(maneuver_plan, kb)
        print(f"    recommended_action={decision.get('recommended_action')} "
              f"confidence={decision.get('confidence')}")

        decision_path = os.path.join(DECISIONS_DIR, f"event_{idx}.json")
        with open(decision_path, "w") as f:
            json.dump(decision, f, indent=2)

        report_text = generate_report_markdown(maneuver_plan, decision)
        report_path = save_report(idx, report_text)
        print(f"    report saved to {report_path}")

        if idx < len(plans):
            time.sleep(SECONDS_BETWEEN_CALLS)

    print("\n" + "=" * 60)
    print(f"Phase 4 complete. Decisions in {DECISIONS_DIR}/, "
          f"reports in data/reports/")
    print("=" * 60)


if __name__ == "__main__":
    main()