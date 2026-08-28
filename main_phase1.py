"""
Phase 1 entry point — OrbitGuard AI
"""

from tle_fetch import fetch_all_groups
from propagate import propagate_group, save_propagated, sanity_check


def main():
    print("=" * 60)
    print("OrbitGuard AI — Phase 1: Live Data + Orbit Propagation")
    print("=" * 60)

    grouped_objects = fetch_all_groups()

    for group_name, objects in grouped_objects.items():
        if not objects:
            print(f"[skip] No objects parsed for group '{group_name}'")
            continue

        print(f"\n[propagate] Propagating {len(objects)} objects in '{group_name}'...")
        results = propagate_group(group_name, objects)

        out_path = save_propagated(group_name, results)
        print(f"[save] Wrote {out_path}")

        sanity_check(group_name, results)

    print("\n" + "=" * 60)
    print("Phase 1 complete. Data is in data/raw_tle/ and data/propagated/")
    print("=" * 60)


if __name__ == "__main__":
    main()