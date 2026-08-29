"""
Phase 2 - Step 1: Conjunction screening.

Loads propagated timelines from Phase 1 (data/propagated/*.json) and screens
every pair of objects for close approaches below a configurable distance
threshold.
"""

import glob
import json
import math
import os

from config import PROPAGATED_DIR, DATA_DIR

# Distance threshold in km below which a pair is flagged as a conjunction event.
# Real operational thresholds are often tighter (a few km), but for a
# demo/prototype a looser threshold produces enough real events to show the
# pipeline working end-to-end. Tighten this once you've confirmed events are found.
CONJUNCTION_THRESHOLD_KM = 100.0

EVENTS_DIR = f"{DATA_DIR}/events"


def load_all_propagated() -> dict:
    """Load every propagated group file into one {object_name: timeline} dict."""
    combined = {}
    for path in glob.glob(os.path.join(PROPAGATED_DIR, "*_propagated.json")):
        with open(path) as f:
            group_data = json.load(f)
        combined.update(group_data)
    return combined


def distance_km(pos_a, pos_b) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(pos_a, pos_b)))


def relative_velocity_km_s(vel_a, vel_b) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vel_a, vel_b)))


def screen_pair(name_a, timeline_a, name_b, timeline_b):
    """
    Screen one pair of objects across their shared timeline for the closest
    approach. Returns an event dict if it drops below the threshold, else None.
    Both timelines share the same timestamps since Phase 1 propagates every
    object from the same start time with the same step size.
    """
    closest = None
    for pt_a, pt_b in zip(timeline_a, timeline_b):
        d = distance_km(pt_a["position_km"], pt_b["position_km"])
        if closest is None or d < closest["miss_distance_km"]:
            rel_v = relative_velocity_km_s(pt_a["velocity_km_s"], pt_b["velocity_km_s"])
            closest = {
                "object_a": name_a,
                "object_b": name_b,
                "miss_distance_km": round(d, 3),
                "relative_velocity_km_s": round(rel_v, 3),
                "time_of_closest_approach_utc": pt_a["timestamp_utc"],
                "t_minutes_from_now": pt_a["t_minutes_from_now"],
            }
    if closest and closest["miss_distance_km"] <= CONJUNCTION_THRESHOLD_KM:
        return closest
    return None


def screen_all_pairs(all_objects: dict) -> list:
    """
    Screen every unique pair of objects for conjunctions.
    O(n^2) over object count — fine for the object counts used in Phase 1
    (tens of objects per group). If you scale up object counts a lot later,
    add a coarse pre-filter (e.g. altitude-band bucketing) before this step.
    """
    names = list(all_objects.keys())
    events = []
    total_pairs = len(names) * (len(names) - 1) // 2
    print(f"[conjunction] Screening {total_pairs} object pairs "
          f"(threshold: {CONJUNCTION_THRESHOLD_KM} km)...")

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            name_a, name_b = names[i], names[j]
            event = screen_pair(name_a, all_objects[name_a], name_b, all_objects[name_b])
            if event:
                events.append(event)

    events.sort(key=lambda e: e["miss_distance_km"])
    return events


def save_events(events: list) -> str:
    os.makedirs(EVENTS_DIR, exist_ok=True)
    path = os.path.join(EVENTS_DIR, "flagged_conjunctions.json")
    with open(path, "w") as f:
        json.dump(events, f, indent=2)
    return path


if __name__ == "__main__":
    all_objects = load_all_propagated()
    print(f"[conjunction] Loaded {len(all_objects)} objects from Phase 1 data")
    events = screen_all_pairs(all_objects)
    print(f"[conjunction] Found {len(events)} flagged conjunction events")
    path = save_events(events)
    print(f"[conjunction] Saved to {path}")
    for e in events[:5]:
        print(f"  {e['object_a']} <-> {e['object_b']}: "
              f"{e['miss_distance_km']} km at {e['time_of_closest_approach_utc']}")