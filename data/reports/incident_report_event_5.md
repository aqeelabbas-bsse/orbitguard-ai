# Collision Avoidance Incident Report

**Generated:** 2026-08-29 12:00 UTC

**Objects involved:** STARLINK-1199 and STARLINK-1260

**Time of closest approach (UTC):** 2026-08-30T11:01:31Z

## Flagged Event Summary
- Miss distance (SGP4 screening, Phase 2): 14.774 km
- Relative velocity: 9.535 km/s

## Risk Assessment
- **Severity:** medium
- **Recommended urgency:** plan_maneuver_review
- **Rationale:** The miss distance of 14.774 km is within the tens of kilometers range, which, according to conjunction_assessment_basics.txt, should be monitored and re-assessed as tracking data updates. However, the relative velocity of 9.535 km/s is considered high, especially in the context of low Earth orbit, as noted in relative_velocity_and_severity.txt. This high relative velocity increases the chance of an actual intersection given tracking uncertainty and the severity of a collision if one occurs. Therefore, the combination of a moderate miss distance and a high relative velocity warrants a medium severity call.

## Maneuver Options Considered
- No-maneuver baseline miss distance (two-body simulation, Phase 3): 41.513 km

| Option | New Miss Distance (km) | Risk Reduction | Delta-v (m/s) | Schedule Impact | Score |
|---|---|---|---|---|---|
| prograde_burn | 84.22 | +102.9% | 10.0 | 1.0 | +100.38 |
| radial_burn | 41.816 | +0.7% | 10.0 | 1.5 | -2.77 |

## Final Recommendation
- **Recommended action:** prograde_burn
- **Confidence:** high
- **Justification:** Given the medium severity of the event due to a moderate miss distance of 14.774 km and a high relative velocity of 9.535 km/s, a maneuver review is warranted as per maneuver_decision_criteria.txt. The prograde_burn maneuver offers a significant risk reduction of 102.88%, increasing the miss distance to 84.22 km, which substantially mitigates the collision risk. Although it spends a small amount of fuel (delta_v_km_s of 0.01), the risk reduction achieved per unit of fuel spent is considerable, making it a preferable choice. The guidance from fuel_and_schedule_tradeoffs.txt emphasizes the importance of conserving fuel, but in this case, the fuel cost is not prohibitively high, especially considering the medium severity of the event and the substantial risk reduction achieved.

*Guidance referenced: maneuver_decision_criteria.txt, fuel_and_schedule_tradeoffs.txt*