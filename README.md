<div align="center">
  <img src="docs/logo.png" alt="WTI — World Threat Index logo" width="140"/>
  <!-- CODEX: generate a clean corporate product logo for "WTI — World Threat Index": a minimalist globe/grid motif with a single status pip, deep navy (#0b1f3a) on transparent, suitable at 140px. -->

  # World Threat Index
  ### Global geopolitical monitoring for 195 countries &amp; 13 blocs

  ![status](https://img.shields.io/badge/status-active-brightgreen)
  ![division](https://img.shields.io/badge/Geopolitical%20Intelligence-0b1f3a)
  ![Monarch Castle](https://img.shields.io/badge/Monarch%20Castle-Holdings-1f6feb)
  ![license](https://img.shields.io/badge/license-Apache%202.0-lightgrey)
  ![python](https://img.shields.io/badge/Python-3.11%2B-blue)
  ![pages](https://img.shields.io/badge/dashboard-live-success)
</div>

> **Executive summary** — World Threat Index (WTI) is a continuously refreshed geopolitical monitoring platform that scores threat pressure across **195 countries** and **13 major blocs** on a single, comparable 1–10 scale. It ingests multilingual open-source news, attributes each event to a country and threat category, and applies a deterministic, audit-ready scoring model to produce decision-grade situational awareness for analysts, risk officers, and strategy teams. The result is published every few hours to a live public dashboard with full provenance.

## ✨ Highlights
- **Global coverage** — every UN member state plus Taiwan (196 territories) and **13 geopolitical blocs**: OECD, G7, G20, EU, USMCA, NATO, ASEAN, African Union, BRICS, GCC, CIS, MERCOSUR, SCO.
- **Deterministic, reproducible scoring** — a shared BNTI-compatible weighting model maps attributed events to a 1–10 index with three clear status bands: STABLE, ELEVATED, CRITICAL.
- **Tiered, always-on refresh** — countries are graded into tiers A/B/C and refreshed every 2 / 6 / 12 hours via scheduled GitHub Actions.
- **Massively parallel pipeline** — the country universe is split into 10 independent shards that run concurrently, then merged and published atomically.
- **LLM-assisted attribution** — `openrouter/free` assigns each event an ISO-2 country and canonical threat category, with a deterministic heuristic fallback (`--dry-run`) for LLM-free operation.
- **Weighted aggregation** — population-weighted global composite and GDP-weighted bloc indices, so headline numbers reflect real geopolitical weight.
- **Live, zero-backend dashboard** — an interactive D3 world map, bloc grid, and rankings served as a static site on GitHub Pages.

## 🖼️ Preview
<!-- CODEX: drop product screenshots into docs/ -->
![WTI — global dashboard and world threat map](docs/screenshot-1.png)
<!-- CODEX: full-window screenshot of the live dashboard at https://sdcofa.github.io/world-threat-index/ — dark theme, left metric panel (Global Composite + Geopolitical Groups grid + Highest Threat), centre D3 choropleth "World Threat Map". -->

![WTI — bloc indices and country rankings detail](docs/screenshot-2.png)
<!-- CODEX: detail screenshot of the geopolitical-groups grid and country rankings table, showing STABLE/ELEVATED/CRITICAL status pills and per-bloc index values. -->

## 🧭 What it does

WTI turns the daily flood of international news into a single, comparable threat figure per country and per bloc, refreshed around the clock.

**Live dashboard:** **https://sdcofa.github.io/world-threat-index/**

### The pipeline
1. **Ingestion** — Google News RSS mirrors are pulled per country (optional GDELT enrichment via `WTI_INCLUDE_GDELT=true`).
2. **Attribution** — `openrouter/free` assigns each event a canonical ISO-2 country code and a threat category; a deterministic heuristic mode (`--dry-run`) runs the same flow without any LLM.
3. **Scoring** — category weights are applied and volume-normalized into a per-country **1–10 index** (see model below).
4. **Aggregation** — a population-weighted **global composite** plus GDP-weighted **bloc indices** for all 13 groups.
5. **Publication** — results are sharded, merged, gated at the bloc level, committed, and deployed to GitHub Pages.

### Scoring model
Each attributed event carries a category weight; the country's mean weight is mapped through a saturating curve to a bounded 1–10 index.

| Threat category | Weight |
|---|---:|
| Military conflict | 8.0 |
| Terrorism | 7.0 |
| Border security | 5.0 |
| Political instability | 4.0 |
| Humanitarian crisis | 3.0 |
| Diplomatic tensions | 2.5 |
| Trade agreement | −2.0 |
| Neutral | 0.0 |

| Status | Index range |
|---|---|
| 🟢 **STABLE** | 1.0 – 4.0 |
| 🟠 **ELEVATED** | 4.0 – 7.0 |
| 🔴 **CRITICAL** | 7.0 – 10.0 |

The methodology is adapted from the production [Border Neighbor Threat Index (BNTI)](https://github.com/akgularda/border-neighbor-threat-index) and documented in [`docs/wti-methodology.md`](docs/wti-methodology.md).

## 🗂️ Data &amp; provenance

Per Monarch Castle doctrine — *evidence before assertion*. WTI collects only from **open, lawfully accessible sources** (Google News RSS, optional GDELT), and every figure on the dashboard traces back to the events that produced it.

- **Sources:** public news RSS feeds, mirrored per country; optional GDELT event enrichment.
- **Country registry:** `config/countries.json` — 195 states + Taiwan with region, subregion, tier, population, and GDP fields used for weighting.
- **Bloc definitions:** `config/groups.json` — the 13 blocs, their members, and per-bloc weighting strategy (GDP or population).
- **Published dataset:** `wti_data.json` / `wti_data.js` — the latest scored index per country and bloc, regenerated each run.
- **Auditability:** scoring is fully deterministic given the same inputs; the dashboard surfaces the last-update timestamp and live coverage so any published number can be traced to its run.

## 🛠️ Tech stack

- **Data / ETL:** Python 3.11 — `feedparser`, `pandas`, `numpy`, `requests`, `python-dateutil`, `googletrans`.
- **Attribution model:** OpenRouter (`openrouter/free`) with a key + backup-key rotation and a heuristic fallback.
- **Frontend:** vanilla JavaScript with **D3.js v7** (world choropleth) and **Chart.js**; modular CSS (`variables`, `layout`, `components`, `wti`).
- **Automation:** GitHub Actions — a 10-way sharded matrix on a tiered cron schedule, merge-and-publish, then Pages deploy.
- **Hosting:** GitHub Pages (static, no backend).
- **Tests:** `pytest` suite under `tests/`.

## 🚀 Getting started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Dry-run a few countries (no LLM, Google News only)
python worldthreatindex.py --dry-run --countries US,GB,SY,UA

# 3. Run a production shard (as GitHub Actions does)
python worldthreatindex.py --shard 0 --total-shards 10 --output-shard 0 --tier A

# 4. Merge all shards into the published dataset
python scripts/merge_wti_shards.py

# 5. Validate global coverage
python scripts/validate_wti_coverage.py
```

LLM attribution reads `OPENROUTER_API_KEY` (and `OPENROUTER_API_KEY_BACKUP`) from the
environment; never commit keys. Use `--dry-run` for fully local, LLM-free operation.

### Automation &amp; deployment
- **`.github/workflows/wti_update.yml`** — *WTI Intelligence Update*: scheduled tiered refresh (tier A ~2h, B ~6h, C ~12h), 10 parallel shards → merge → commit → Pages deploy.
- **`.github/workflows/pages.yml`** — *Deploy GitHub Pages*: publishes the static dashboard on every push to `main`.

### Repository layout
| Path | Purpose |
|---|---|
| `worldthreatindex.py` | Main analyzer / pipeline entrypoint |
| `wti_core/` | `ingestion`, `feeds`, `llm`, `scoring`, `groups`, `publish` |
| `config/countries.json` | 195-country + Taiwan registry with tiers &amp; weights |
| `config/groups.json` | 13 bloc definitions and weighting strategy |
| `scripts/` | Shard merge, coverage validation, registry build |
| `js/` · `css/` · `index.html` | Static dashboard (map, groups, rankings) |
| `wti_data.json` / `wti_data.js` | Latest published dataset |
| `docs/wti-methodology.md` | Full scoring methodology |

## 🧱 Part of Monarch Castle
> A product of **Geopolitical Intelligence** · **Strategic Data Company of Ankara** — an operating company of **[Monarch Castle Holdings](https://github.com/MonarchCastleHoldings)**.
> Sister companies: [Monarch Castle Technologies](https://github.com/monarchcastletech) · [Strategic Data Company of Ankara](https://github.com/SDCofA)

## 📜 License
Apache License 2.0 — see [`LICENSE`](LICENSE). © 2026 Monarch Castle Holdings · Ankara, Türkiye.

<div align="center"><sub>🏰 Monarch Castle Holdings — turning open-source noise into lawful, verified, decision-grade intelligence.</sub></div>
