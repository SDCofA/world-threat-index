# World Threat Index (WTI) Methodology

WTI applies the BNTI production pipeline globally:

1. **Ingestion** — [Google News RSS](https://news.google.com/rss) mirrors per country (optional [GDELT](https://www.gdeltproject.org/) via `WTI_INCLUDE_GDELT=true`)
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

It does not currently provide a global `dataCutoff`, forecast `horizon`, probability `distribution`, calibrated `uncertainty`, explicit forecast `assumptions`, or forecast `resolutionCriteria`. Because those required Task 3 fields are absent, WTI values and forward-looking scenarios must not be described as forecasts or predictions.
