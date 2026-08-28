"""
Phase 1 - Step 2: Propagate real orbital elements forward in time using SGP4
(via the Skyfield library) to get real position/velocity timelines.
"""

import json
import os
from datetime import timedelta

import numpy as np

from skyfield.api import EarthSatellite, load

from config import (
    PROPAGATION_HOURS,
    STEP_MINUTES,
    PROPAGATED_DIR,
    EARTH_RADIUS_KM,
)

ts = load.timescale()


def build_satellite(obj: dict) -> EarthSatellite:
    """Turn a parsed TLE record into a Skyfield EarthSatellite object."""
    return EarthSatellite(obj["line1"], obj["line2"], obj["name"], ts)


def propagate_object(sat: EarthSatellite) -> list:
    """
    Propagate one satellite forward from now over PROPAGATION_HOURS,
    sampled every STEP_MINUTES. Returns a list of state records.
    """
    t0 = ts.now()
    n_steps = int((PROPAGATION_HOURS * 60) / STEP_MINUTES)

    timeline = []
    for step in range(n_steps + 1):
        minutes_ahead = step * STEP_MINUTES
        t = ts.from_datetime(t0.utc_datetime() + timedelta(minutes=minutes_ahead))
        geocentric = sat.at(t)
        pos_km: np.ndarray = np.asarray(geocentric.position.km)          # type: ignore[arg-type]  # (x, y, z)
        vel_km_s: np.ndarray = np.asarray(geocentric.velocity.km_per_s)  # type: ignore[arg-type]  # (vx, vy, vz)
        altitude_km: float = float(geocentric.distance().km)  # type: ignore[arg-type]
        altitude_km -= EARTH_RADIUS_KM

        timeline.append({
            "t_minutes_from_now": minutes_ahead,
            "timestamp_utc": t.utc_iso(),
            "position_km": pos_km.tolist(),
            "velocity_km_s": vel_km_s.tolist(),
            "altitude_km": round(altitude_km, 2),
        })
    return timeline


def propagate_group(group_name: str, objects: list) -> dict:
    """Propagate every object in a group, return {name: timeline}."""
    results = {}
    for obj in objects:
        try:
            sat = build_satellite(obj)
            results[obj["name"]] = propagate_object(sat)
        except Exception as e:
            print(f"[warn] Skipping '{obj['name']}' — propagation failed: {e}")
    return results


def save_propagated(group_name: str, results: dict) -> str:
    os.makedirs(PROPAGATED_DIR, exist_ok=True)
    path = os.path.join(PROPAGATED_DIR, f"{group_name}_propagated.json")
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    return path


def sanity_check(group_name: str, results: dict) -> None:
    """Print altitude ranges so you can eyeball that results look physically real."""
    print(f"\n[sanity check] Group: {group_name}")
    sample_items = list(results.items())[:5]
    for name, timeline in sample_items:
        altitudes = [pt["altitude_km"] for pt in timeline]
        print(
            f"  {name:30s}  alt min={min(altitudes):8.1f} km  "
            f"max={max(altitudes):8.1f} km  avg={sum(altitudes)/len(altitudes):8.1f} km"
        )
    if len(results) > 5:
        print(f"  ... and {len(results) - 5} more objects")