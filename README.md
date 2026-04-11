# DomaniDono

DomaniDono is an end-to-end donation intelligence product built to answer one concrete user question:

"Where can I donate to maximize social impact, with confidence?"

Instead of showing isolated nonprofit records, the app harmonizes open data, compares organizations across multiple dimensions, and translates complex signals into actionable donation guidance for real people.

---

## Why this project matters

### User value
- Reduces uncertainty in donation decisions.
- Converts fragmented nonprofit data into decision-ready insights (who to support + why).
- Improves trust by exposing transparent comparisons across impact, maturity, efficiency, and growth.

### Business value
- Demonstrates how to build a data product that combines ingestion, quality, analytics, UX, and AI.
- Can be adapted to philanthropic platforms, CSR teams, foundations, and grant-making workflows.
- Shows a practical foundation for monetizable features: premium analytics, NGO scoring APIs, donor profiling, and white-label dashboards.

---

## What I built

### 1) Nonprofit data pipeline and normalization
- Loads multi-dimension data from Open Cooperazione.
- Cleans and normalizes registry, metrics, and geography datasets.
- Applies typed conversions and text harmonization for robust downstream analytics.
- Produces reusable DataFrames for app-wide visual and analytical components.

### 2) Impact intelligence engine
- Computes KPIs and derived metrics (projects, beneficiaries, workers, donations, revenues, expenses).
- Calculates year-over-year deltas and benchmark deltas vs category peers.
- Builds impact quadrants (`High Impact`, `Efficient Reach`, `Scale to Unlock`, `Under Development`) from projects/beneficiaries behavior.
- Generates a multi-dimension ranking table across: `Impact`, `Maturity`, `Efficiency`, `Globalization`, `Dimension`, `Trust`, `Growth`.

### 3) Interactive Streamlit product
- **Home**: product story, ecosystem spotlight, and source transparency.
- **Impacts**: KPI boxes, map, sankey flows, impact scatter, and ranked summaries.
- **Registry**: searchable organization registry with key profile information and operational indicators.

### 4) AI donation concierge
- Embedded OpenRouter-powered assistant for recommendation generation.
- Structured prompt + deterministic ranking table input for grounded output.
- Retry logic with fallback models and user-friendly transient error handling.

### 5) UX and performance engineering
- Custom layout system with adaptive scaling for different viewport sizes.
- Fragmented Streamlit rendering for smoother interactions.
- Cached data builders (`st.cache_data`) and reusable transformation wrappers.
- Branded loading experience with staged messaging and animated progress UI.

---

## Technical highlights

- **Architecture**: modular Python codebase (`app`, `db`, `configuration`, `files`).
- **Data layer**: normalized in-memory DataFrames from curated open data files.
- **Analytics**: reusable helper functions for deltas, peer benchmarking, scoring, and ranking.
- **Resilience**: defensive parsing, null-safe operations, and fallback-aware orchestrations.
- **Performance**: caching, grouped aggregations, and isolated Streamlit fragments.
- **UX engineering**: custom CSS, adaptive sizing, thematic page system, and visual storytelling.

---

## Roadmap ideas

- Add data refresh automation pipeline (scheduled ingestion and validation).
- Introduce persisted storage for historical snapshots and trend reproducibility.
- Add personalized donor profiles and goal-based recommendation constraints.
- Extend scoring explainability with downloadable audit trails.

---