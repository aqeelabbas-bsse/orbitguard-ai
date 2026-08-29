"""
Phase 1 configuration for OrbitGuard AI.
Edit these values to change which objects are tracked and the propagation window.
"""

# CelesTrak TLE group names to pull.
# Full list of valid group names: https://celestrak.org/NORAD/elements/
# starlink = large real active constellation (LEO)
# cosmos-1408-debris = real debris cloud from the 2021 Cosmos 1408 ASAT test
#   (if this group name ever changes on CelesTrak, check the group list above
#   and update it here — the rest of the code doesn't need to change)
TLE_GROUPS = [
    "starlink",
    "cosmos-1408-debris",
]

# Limit how many objects per group we propagate (keeps compute + API load sane
# for a 5-day prototype — raise this later if you have time to spare)
MAX_OBJECTS_PER_GROUP = 120

# Propagation window
PROPAGATION_HOURS = 96
STEP_MINUTES = 5

# Output paths
DATA_DIR = "data"
RAW_TLE_DIR = f"{DATA_DIR}/raw_tle"
PROPAGATED_DIR = f"{DATA_DIR}/propagated"

EARTH_RADIUS_KM = 6378.137