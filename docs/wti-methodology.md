# World Threat Index (WTI) Methodology

WTI applies the BNTI production pipeline globally:

1. **Ingestion** — [Google News RSS](https://news.google.com/rss) mirrors per country. No registration-only feed is required.
2. **Attribution** — [`openrouter/free`](https://openrouter.ai/docs) assigns ISO2 country + canonical threat category
3. **Scoring** — Deterministic BNTI weights → per-country 1–10 index
4. **Aggregation** — Population-weighted global composite; GDP-weighted group indices
5. **Publication** — Block-level gating; shard merge via GitHub Actions

## Groups

OECD, G7, G20, EU, USMCA, NATO, ASEAN, African Union, BRICS, GCC, CIS, MERCOSUR, SCO.

## Thresholds

| Status | Range |
|--------|-------|
| STABLE | 1.0 – 4.0 |
| ELEVATED | 4.0 – 7.0 |
| CRITICAL | 7.0 – 10.0 |

## Scale

195 configured country and territory rows, including Taiwan (`TW`), with tiered refresh (A: 2h, B: 6h, C: 12h).

## Provenance fields

Each published event retains an evidence URL in `link`, the source publication time in `date`, the ingestion registry in `source_country`, the attributed `country`, the canonical `category`, deterministic `weight`, attribution `confidence`, and `ai_model`. The machine-readable snapshot identifies this path as `countries.*.events[].link` and links back to this methodology.

## Task 3 classification

WTI publishes an **assessment**, not a forecast record. The current snapshot supports a per-country `target`, an assessment `issuedAt` through `meta.issued_at`, a documented `method`, and event-level `provenance`.

WTI values themselves remain assessments and must not be described as forecasts or probabilities. The assessment record has no forecast `dataCutoff`, probability `distribution`, calibrated `uncertainty`, forecast `assumptions`, or `resolutionCriteria`; the separate `horizon` below is a triage window, not a forecast target.

## Early-warning precursor ensemble

The dashboard additionally publishes a separate 0–7 day **triage horizon**. It is an anomaly monitor, not an event-probability model:

| Component | Production weight | Observable inputs |
|---|---:|---|
| Narrative precursor pressure | 40% | Force posture, protective action, coercive pressure, and systems-disruption terms in retained news events; source diversity and cross-source confirmation |
| Cross-market dislocation | 35% | Five-session changes in FRED WTI crude (`DCOILWTICO`), VIX (`VIXCLS`), and US high-yield spread (`BAMLH0A0HYM2`) |
| Synchronized acceleration | 25% | Breadth and magnitude of positive WTI country-index changes versus the prior published snapshot |

Market anomalies use a robust z-score against the historical five-session-change distribution:

`z = (x − median(X)) / (1.4826 × MAD(X))`

WTI crude uses the absolute anomaly because either a sharp rise or fall may indicate dislocation. VIX and high-yield spread use only positive anomalies. The market component combines the two largest available indicator scores (65% / 35%). Cached market observations expire after 72 hours.

The ensemble is an availability-renormalized weighted mean. A missing component contributes neither a zero nor its weight. `confidence` measures market, event, and source coverage; it is not the probability that an event will occur. Component alerts begin at 35/100 and retain a plain-language reason. The public JSON includes the full components, health record, alert record, rolling score history, taxonomy, weights, and source links required to reproduce each issued snapshot from the same inputs.

### Autonomous attribution fallback

OpenRouter is the primary headline-to-country/category attribution path. If it is unavailable (including HTTP 429 exhaustion or missing credentials), the batch is classified by deterministic, versioned keyword rules (`heuristic-v1`). Fallback events carry confidence `0.45` and retain `attribution_method`; model-attributed events carry confidence `1.0` and `attribution_method: openrouter`. This prevents a third-party quota failure from stopping the scheduled pipeline while preserving provenance for reproduction and later audit.
