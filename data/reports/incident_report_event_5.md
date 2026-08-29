# Collision Avoidance Incident Report

**Generated:** 2026-08-29 12:05 UTC

**Objects involved:** STARLINK-1199 and STARLINK-1260

**Time of closest approach (UTC):** 2026-08-30T11:01:31Z

## Flagged Event Summary
- Miss distance (SGP4 screening, Phase 2): 14.774 km
- Relative velocity: 9.535 km/s

## Risk Assessment
- **Severity:** medium
- **Recommended urgency:** plan_maneuver_review
- **Rationale:** The miss distance of 14.774 km is in the tens of kilometers range, which typically warrants monitoring and re-assessment as tracking data updates. However, the relative velocity of 9.535 km/s is considered high, which increases the chance of an actual intersection given tracking uncertainty and the severity of a collision if one occurs. According to the guidance in conjunction_assessment_basics.txt and relative_velocity_and_severity.txt, a moderate miss distance at very high relative velocity can warrant more urgency than a smaller miss distance at low relative velocity. Therefore, the combination of a moderate miss distance and high relative velocity leads to a medium severity assessment.

## Maneuver Options Considered
- No-maneuver baseline miss distance (two-body simulation, Phase 3): 41.513 km

| Option | New Miss Distance (km) | Risk Reduction | Delta-v (m/s) | Schedule Impact | Score |
|---|---|---|---|---|---|
| prograde_burn | 84.22 | +102.9% | 10.0 | 1.0 | +100.38 |
| radial_burn | 41.816 | +0.7% | 10.0 | 1.5 | -2.77 |

## Final Recommendation
- **Recommended action:** prograde_burn
- **Confidence:** high
- **Justification:** Given the medium severity assessment of the STARLINK-1199 <-> STARLINK-1260 conjunction event, with a moderate miss distance of 14.774 km and a high relative velocity of 9.535 km/s, the guidance in maneuver_decision_criteria.txt suggests a maneuver review is warranted. The prograde_burn maneuver achieves a significant risk reduction of 102.88%, increasing the miss distance to 84.22 km, with a relatively low fuel cost of 0.01 km/s delta-v. Although the fuel cost is a consideration, as emphasized in fuel_and_schedule_tradeoffs.txt, the risk reduction achieved by this maneuver justifies its selection, especially given the high relative velocity and potential consequences of a collision. The prograde_burn maneuver has the highest score of 100.376, further supporting its selection as the recommended action.

*Guidance referenced: maneuver_decision_criteria.txt, fuel_and_schedule_tradeoffs.txt*