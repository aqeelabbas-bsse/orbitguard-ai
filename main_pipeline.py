"""
Full pipeline orchestration — OrbitGuard AI

Runs Phases 1 through 4 back to back in one command: live data fetch +
propagation, conjunction detection + risk assessment, maneuver simulation +
scoring, and final recommendation + report generation.

This is what you run for your demo and video — one command, real live data
in, complete incident reports out the other end.

Usage:
    python main_pipeline.py
"""

import time

import main_phase1
import main_phase2
import main_phase3
import main_phase4


def main():
    start = time.time()
    print("#" * 60)
    print("# OrbitGuard AI — FULL PIPELINE RUN")
    print("#" * 60)

    print("\n" + "#" * 20 + " PHASE 1: Data + Propagation " + "#" * 20)
    main_phase1.main()

    print("\n" + "#" * 20 + " PHASE 2: Conjunctions + Investigation " + "#" * 20)
    main_phase2.main()

    print("\n" + "#" * 20 + " PHASE 3: Maneuver Sim + Scoring " + "#" * 20)
    main_phase3.main()

    print("\n" + "#" * 20 + " PHASE 4: Recommendation + Reports " + "#" * 20)
    main_phase4.main()

    elapsed = time.time() - start
    print("\n" + "#" * 60)
    print(f"# FULL PIPELINE COMPLETE in {elapsed:.1f}s")
    print("# Incident reports: data/reports/")
    print("#" * 60)


if __name__ == "__main__":
    main()