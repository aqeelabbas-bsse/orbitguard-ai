"""
Phase 1 - Step 1: Fetch real, live TLE (orbital element) data from CelesTrak.

CelesTrak publishes free, public TLE sets for tracked objects, updated regularly.
No API key required.
"""

import glob
import os
from datetime import datetime, timezone

import requests

from config import TLE_GROUPS, MAX_OBJECTS_PER_GROUP, RAW_TLE_DIR

CELESTRAK_URL = "https://celestrak.org/NORAD/elements/gp.php"
_HEADERS = {"User-Agent": "OrbitGuard-AI/1.0 (educational project)"}


def _latest_cache(group: str) -> str | None:
    """Return the text of the most recent cached .tle file for *group*, or None."""
    pattern = os.path.join(RAW_TLE_DIR, f"{group}_*.tle")
    files = sorted(glob.glob(pattern))
    if not files:
        return None
    with open(files[-1]) as f:
        return f.read()


def fetch_group_tle(group: str) -> str:
    """Fetch raw TLE text for one CelesTrak group.

    CelesTrak returns 403 when the data hasn't changed since the last
    successful download (updated every ~2 hours).  In that case we fall
    back to the most recently cached file so the pipeline keeps running.
    """
    params = {"GROUP": group, "FORMAT": "tle"}
    resp = requests.get(CELESTRAK_URL, params=params, headers=_HEADERS, timeout=20)

    if resp.status_code == 403:
        cached = _latest_cache(group)
        if cached:
            print(f"[fetch] CelesTrak says data unchanged for '{group}'; using cached copy.")
            return cached
        resp.raise_for_status()  # no cache — let it fail with the original error

    resp.raise_for_status()
    if not resp.text.strip():
        raise ValueError(
            f"CelesTrak returned empty data for group '{group}'. "
            "Check the group name is still valid at "
            "https://celestrak.org/NORAD/elements/"
        )
    return resp.text


def parse_tle_text(raw_text: str, limit: int) -> list:
    """
    Parse raw 3-line-per-object TLE text into structured records.
    Each object: {name, line1, line2}
    """
    lines = [l.rstrip("\n") for l in raw_text.strip().splitlines()]
    objects = []
    i = 0
    while i < len(lines) - 2 and len(objects) < limit:
        name = lines[i].strip()
        line1 = lines[i + 1].strip()
        line2 = lines[i + 2].strip()
        if line1.startswith("1 ") and line2.startswith("2 "):
            objects.append({"name": name, "line1": line1, "line2": line2})
            i += 3
        else:
            i += 1  # skip malformed entry, try to resync
    return objects


def save_raw(group: str, raw_text: str) -> str:
    os.makedirs(RAW_TLE_DIR, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = os.path.join(RAW_TLE_DIR, f"{group}_{date_str}.tle")
    with open(path, "w") as f:
        f.write(raw_text)
    return path


def fetch_all_groups() -> dict:
    """Fetch and parse TLEs for every group listed in config.TLE_GROUPS."""
    all_objects = {}
    for group in TLE_GROUPS:
        print(f"[fetch] Pulling TLE group '{group}' from CelesTrak...")
        raw_text = fetch_group_tle(group)
        save_raw(group, raw_text)
        objects = parse_tle_text(raw_text, MAX_OBJECTS_PER_GROUP)
        print(f"[fetch] Parsed {len(objects)} objects from group '{group}'")
        all_objects[group] = objects
    return all_objects


if __name__ == "__main__":
    data = fetch_all_groups()
    total = sum(len(v) for v in data.values())
    print(f"\n[done] Fetched {total} objects total across {len(data)} groups.")