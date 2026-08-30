# OrbitGuard AI

Agentic AI collision-avoidance and maneuver-advisor for real, live-tracked satellites and space debris.

**Challenge:** AI Builders Challenge with IBM Bob — August 2026
**Theme:** Advance Space Exploration with AI (space debris tracking & collision avoidance)
**Live demo:** https://aqeelabbas-bsse.github.io/orbitguard-ai/frontend/Landing.dc.html

---

## Problem Statement

Low Earth orbit is increasingly crowded — thousands of active satellites and tracked debris fragments share the same altitude bands, and a single collision can generate thousands of new debris fragments, threatening every other mission in that orbital shell. Operators need to go from raw tracking data to a clear, justified decision fast: is this close approach actually dangerous, and if so, what should be done about it?

Most tools stop at "flagged: possible collision." OrbitGuard AI goes further — it takes real tracked-object data, detects genuine close-approach events, investigates and explains the risk, simulates possible avoidance maneuvers, compares their tradeoffs, and recommends the safest action with a generated incident report — turning data-heavy tracking into an insight-driven decision.

## Solution Overview

OrbitGuard AI is an agentic pipeline built entirely on real orbital data — no synthetic or placeholder inputs anywhere in the system:

```
Live TLE data (CelesTrak)
  → SGP4 orbit propagation (real positions/velocities over a 96-hour window)
  → Conjunction screening (real flagged close-approach events)
  → AI agent: risk investigation, grounded in a retrieved knowledge base (RAG)
  → Deterministic maneuver simulation (real two-body orbital mechanics)
  → Deterministic risk/cost scoring of each candidate maneuver
  → AI agent: final recommendation + auto-generated incident report
  → Dashboard: live event list, risk write-up, maneuver comparison, recommendation
```

Only the two steps that require judgment and synthesis — risk interpretation and the final recommendation — go through an LLM agent. Orbital mechanics, conjunction detection, and maneuver scoring are deterministic math. This keeps the system explainable and reliable rather than a black box, and means every number a user sees traces back to real physics or a real retrieved source, not a model's guess.

## What Makes This Different

The final recommendation agent doesn't simply pick the highest-scoring maneuver. A candidate maneuver can score very highly and still be correctly rejected if the event's severity doesn't justify spending fuel — the agent weighs severity, urgency, and retrieved decision-criteria guidance to make that call, and explains why. Low-severity events are recommended for continued monitoring even when a maneuver would technically improve the miss distance; higher-severity events are recommended for action. This distinction — real judgment, not just detection — is demonstrated live across the 5 investigated events in the dashboard.

## Architecture

| Stage | What it does | Key files |
|---|---|---|
| Live Orbital Data Ingestion | Fetches real TLE sets from CelesTrak, propagates every object 96 hours ahead using SGP4 | `tle_fetch.py`, `propagate.py` |
| Conjunction Detection | Screens every tracked object pair for real close-approach events | `conjunction.py` |
| Risk Investigation | RAG-grounded agent produces a structured severity assessment per event | `rag.py`, `investigator_agent.py`, `knowledge_base/` |
| Maneuver Simulation & Scoring | Simulates candidate avoidance burns with real two-body physics, scores them deterministically | `maneuver.py`, `scoring.py` |
| Recommendation Engine | Second agent weighs scored candidates against retrieved guidance and selects a final action | `recommendation_agent.py` |
| Incident Report Generation | Composes every stage's output into a readable report per event | `report_generator.py` |
| Orchestration | Runs all four phases end-to-end in one command | `main_pipeline.py` |
| Frontend | Dashboard bound directly to real pipeline output on disk | `frontend/` |

Full stage-by-stage detail is also presented on the live site's Architecture page.

## Tech Stack

- **Data & physics:** Python, Skyfield/SGP4 (real orbit propagation), NumPy (two-body RK4 integration for maneuver simulation)
- **Agents & RAG:** watsonx.ai (Llama 3.3 70B Instruct), scikit-learn TF-IDF retrieval over a 6-document knowledge base
- **Frontend:** React (CDN-loaded), custom Liquid Glass design system, day/night theme, live-data-bound dashboard

## Real Data Sources

- **CelesTrak** — live TLE sets for an active Starlink constellation sample and the real Cosmos 1408 debris field (from the 2021 anti-satellite test)
- No synthetic telemetry anywhere in the pipeline — every number in the dashboard traces back to a real propagated orbit or a real agent call against that data

## Running the Pipeline

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file with your watsonx.ai credentials (see `BUILD_GUIDE.md` for full setup steps):
```
WATSONX_API_KEY=your_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=meta-llama/llama-3-3-70b-instruct
```

Run the full pipeline end-to-end:
```bash
python main_pipeline.py
```

This fetches live data, detects real conjunctions, runs both agents, and generates incident reports — fully reproducible from a clean checkout.

## Running the Frontend

```bash
python build_frontend_data.py   # regenerates frontend/data.js from real pipeline output
cd frontend
python -m http.server 8000
```

Open `http://localhost:8000/Landing.dc.html`.

## Project Structure

```
orbitguard-ai/
├── frontend/                   # Dashboard (Landing, Dashboard, Event Detail, Architecture)
├── knowledge_base/             # RAG source documents
├── data/                       # Pipeline output (generated, not committed data itself is real)
├── config.py                   # Tracked object groups, propagation window
├── tle_fetch.py                # Live TLE ingestion (CelesTrak)
├── propagate.py                # SGP4 orbit propagation
├── conjunction.py              # Close-approach screening
├── rag.py                      # Knowledge base retrieval
├── llm_client.py               # watsonx.ai client
├── investigator_agent.py       # Risk investigation agent
├── maneuver.py                 # Two-body maneuver simulation
├── scoring.py                  # Deterministic risk/cost scoring
├── recommendation_agent.py     # Final recommendation agent
├── report_generator.py         # Incident report generation
├── main_phase1-4.py             # Per-phase entry points
├── main_pipeline.py            # Full end-to-end orchestration
├── build_frontend_data.py      # Regenerates frontend data from real pipeline output
├── BUILD_GUIDE.md              # Step-by-step build instructions
└── requirements.txt
```

## How IBM Bob Was Used

IBM Bob was used as the primary development environment throughout the build: scaffolding and debugging pipeline modules across all four phases (including resolving a CelesTrak rate-limiting issue via a caching fallback, and fixing LLM JSON-response parsing for the investigator and recommendation agents), and assisting with the watsonx.ai integration used by both agentic stages of the pipeline.

## License

Built for the IBM AI Builders Challenge — August 2026, "Advance Space Exploration with AI."
