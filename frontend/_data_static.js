// Static (non-generated) sections of data.js — edited by hand, spliced in
// by build_frontend_data.py. Pipeline-derived STATS and EVENTS are
// generated around this content and must NOT be added here.

export const PIPELINE_STAGES = [
  { id: "detect", label: "Detect", detail: "SGP4 screening \u2264100 km", file: "conjunction.py" },
  { id: "investigate", label: "Investigate", detail: "RAG agent \u00b7 granite-3-8b", file: "investigator_agent.py" },
  { id: "simulate", label: "Simulate", detail: "Two-body RK4 + scoring", file: "maneuver.py" },
  { id: "recommend", label: "Recommend", detail: "Decision agent + report", file: "recommendation_agent.py" },
];

export const ARCHITECTURE_STAGES = [
  { id: "ingest", title: "Live Orbital Data Ingestion", subtitle: "TLE fetch + SGP4 propagation", detail: "Live orbital element sets are pulled for two tracked populations and propagated 96 hours ahead in 5-minute steps, producing real position and velocity timelines for every object." },
  { id: "detect", title: "Conjunction Detection", subtitle: "Close-approach screening", detail: "Every unique pair of propagated timelines is screened for closest approach; pairs under 100 km are flagged. 280 events were flagged from this run." },
  { id: "investigate", title: "Risk Investigation", subtitle: "RAG-grounded agent analysis", detail: "The closest flagged events are handed to an agent grounded by retrieval over a knowledge base of conjunction-assessment guidance, producing a structured severity assessment for each." },
  { id: "simulate", title: "Maneuver Simulation & Scoring", subtitle: "Two-body physics + deterministic scoring", detail: "Two candidate avoidance burns are simulated with real two-body orbital mechanics, then scored on risk reduction, fuel cost, and schedule impact." },
  { id: "recommend", title: "Recommendation Engine", subtitle: "Final agentic decision", detail: "A second agent weighs the scored candidates against retrieved decision-criteria guidance and selects a final action \u2014 not simply the highest score." },
  { id: "report", title: "Incident Report Generation", subtitle: "Exportable record", detail: "Every field above is composed into a full incident report per event \u2014 the artifact an operator reads and exports." },
];

const GUIDANCE_LABELS = {
  "conjunction_assessment_basics.txt": "Conjunction Assessment Guidelines",
  "debris_mitigation_principles.txt": "Debris Mitigation Principles",
  "maneuver_decision_criteria.txt": "Maneuver Decision Criteria",
  "relative_velocity_and_severity.txt": "Relative Velocity Risk Model",
  "fuel_and_schedule_tradeoffs.txt": "Fuel & Schedule Tradeoffs",
  "cosmos_1408_background.txt": "Cosmos 1408 Debris Field Background",
};
export function guidanceLabel(filename) { return GUIDANCE_LABELS[filename] || filename; }

export const KNOWLEDGE_BASE = [
  { file: "conjunction_assessment_basics.txt", summary: "Miss distance and relative velocity together define severity; neither alone is a complete picture." },
  { file: "relative_velocity_and_severity.txt", summary: "Impact energy scales with the square of relative velocity \u2014 it also widens tracking uncertainty at the predicted miss point." },
  { file: "maneuver_decision_criteria.txt", summary: "Weighs collision risk, consequence, fuel cost and lead time into a monitor / plan-review / immediate-review pattern." },
  { file: "fuel_and_schedule_tradeoffs.txt", summary: "Fuel is a fixed, non-renewable budget \u2014 the smallest maneuver that achieves adequate risk reduction is preferred." },
  { file: "debris_mitigation_principles.txt", summary: "A collision endangers the whole orbital environment, not just the two objects involved." },
  { file: "cosmos_1408_background.txt", summary: "Background on the 2021 ASAT test that created the Cosmos 1408 debris field now crossing active LEO constellations." },
];

export function getEvent(id) {
  const n = parseInt(id, 10);
  return EVENTS.find((e) => e.id === n) || EVENTS[0];
}

const SEVERITY_META = {
  low: { label: "Nominal", color: "#3DDC97" },
  medium: { label: "Caution", color: "#FFB020" },
  high: { label: "Critical", color: "#FF4B5C" },
};
export function severityMeta(sev) { return SEVERITY_META[sev] || SEVERITY_META.low; }

const URGENCY_LABELS = {
  monitor: "Monitor",
  plan_maneuver_review: "Plan Maneuver Review",
  immediate_review: "Immediate Review",
};
export function urgencyLabel(u) { return URGENCY_LABELS[u] || u; }

const ACTION_LABELS = {
  no_maneuver: "No Maneuver \u2014 Continue Monitoring",
  prograde_burn: "Execute Prograde Burn",
  radial_burn: "Execute Radial Burn",
};
export function actionLabel(a) { return ACTION_LABELS[a] || a; }

// Overall mission status derived from the live set of investigated events.
export function missionStatus() {
  if (EVENTS.some((e) => e.urgency === "immediate_review")) return { label: "Action Required", color: "#FF4B5C" };
  if (EVENTS.some((e) => e.urgency === "plan_maneuver_review")) return { label: "Monitoring", color: "#FFB020" };
  return { label: "Nominal", color: "#3DDC97" };
}

export function formatUtcClock(d) {
  const p = (n) => String(n).padStart(2, "0");
  return `${p(d.getUTCHours())}:${p(d.getUTCMinutes())}:${p(d.getUTCSeconds())}`;
}
export function formatUtcDate(d) {
  const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
  return `${d.getUTCDate().toString().padStart(2,"0")} ${months[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

// Live countdown to a UTC ISO timestamp, computed from the real clock (not the static
// t_minutes_from_now snapshot), so it counts down accurately whenever this is viewed.
export function formatCountdown(iso) {
  const p = (n) => String(n).padStart(2, "0");
  const ms = new Date(iso).getTime() - Date.now();
  if (ms <= 0) {
    const past = Math.abs(ms);
    const h = Math.floor(past / 3600000);
    return { text: `T+${h}h past`, prefix: "T+", main: `${h}h past`, past: true };
  }
  const totalSec = Math.floor(ms / 1000);
  const d = Math.floor(totalSec / 86400);
  const h = Math.floor((totalSec % 86400) / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  const s = totalSec % 60;
  const main = `${p(h)}:${p(m)}:${p(s)}`;
  const prefix = d > 0 ? `${d}d` : "";
  return { text: prefix ? `${prefix} ${main}` : main, prefix, main, past: false };
}

export function formatKm(km, decimals = 3) {
  return Number(km).toFixed(decimals);
}