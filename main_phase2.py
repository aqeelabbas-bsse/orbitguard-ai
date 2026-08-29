"""
Phase 2 entry point — OrbitGuard AI

Run this after Phase 1 to:
  1. Load propagated orbit data
  2. Screen for real flagged conjunction (close-approach) events
  3. For each flagged event, run the RAG-grounded investigator agent
  4. Save structured risk assessments to data/risk_assessments/

Requires LLM_API_BASE, LLM_API_KEY, LLM_MODEL environment variables set
(see llm_client.py) — or swap call_llm() there for IBM Bob's provided call
pattern before running.

Usage:
    python main_phase2.py
"""

import json
import os
import time

from conjunction import load_all_propagated, screen_all_pairs, save_events
from investigator_agent import investigate_event
from rag import KnowledgeBase

RISK_ASSESSMENTS_DIR = "data/risk_assessments"

# Cap how many flagged events get sent to the agent, to control API cost/time
# during testing. Raise this once you've confirmed it works end-to-end.
MAX_EVENTS_TO_INVESTIGATE = 5

# Small pause between agent calls to stay under the watsonx.ai Lite plan's
# requests-per-minute limit. call_llm() also retries automatically on 429,
# but pacing calls like this means you rely on that less.
SECONDS_BETWEEN_CALLS = 8


def main():
    print("=" * 60)
    print("OrbitGuard AI — Phase 2: Conjunction Detection + Investigator Agent")
    print("=" * 60)

    all_objects = load_all_propagated()
    if not all_objects:
        print("[error] No propagated data found. Run Phase 1 first.")
        return
    print(f"[load] Loaded {len(all_objects)} objects from Phase 1")

    events = screen_all_pairs(all_objects)
    save_events(events)
    print(f"[conjunction] Found {len(events)} flagged conjunction events")

    if not events:
        print("[warn] No conjunctions found at the current threshold. "
              "Try raising CONJUNCTION_THRESHOLD_KM in conjunction.py.")
        return

    print("[rag] Building knowledge base index...")
    kb = KnowledgeBase()

    os.makedirs(RISK_ASSESSMENTS_DIR, exist_ok=True)

    to_process = events[:MAX_EVENTS_TO_INVESTIGATE]
    print(f"[agent] Investigating top {len(to_process)} closest events...")

    for idx, event in enumerate(to_process, start=1):
        print(f"  [{idx}/{len(to_process)}] {event['object_a']} <-> "
              f"{event['object_b']} ({event['miss_distance_km']} km)...")
        assessment = investigate_event(event, kb)

        out_path = os.path.join(RISK_ASSESSMENTS_DIR, f"event_{idx}.json")
        with open(out_path, "w") as f:
            json.dump(assessment, f, indent=2)

        print(f"      severity={assessment.get('severity')} "
              f"urgency={assessment.get('recommended_urgency')}")

        if idx < len(to_process):
            time.sleep(SECONDS_BETWEEN_CALLS)

    print("\n" + "=" * 60)
    print(f"Phase 2 complete. Risk assessments saved to {RISK_ASSESSMENTS_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()