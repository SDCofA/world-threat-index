# memory.md — World Threat Index (WTI)

Project-local operational knowledge. Required reading at the **start** of a session,
required writing at the **end**. Complements the user-global doctrine in `~/.claude/CLAUDE.md`.

---

## What this repo is

- **WTI Intelligence Update** pipeline: shards the country universe into 10 parallel
  GitHub Actions jobs (`update-shards (0..9)`), each runs `worldthreatindex.py` for its
  shard, uploads `wti_shard_<n>.json` as an artifact. `merge-and-publish` downloads all
  shards, runs `scripts/merge_wti_shards.py`, commits `wti_data.json` / `wti_data.js` /
  `wti_history.csv`, then `deploy-pages` publishes to GitHub Pages.
- Workflow: `.github/workflows/wti_update.yml`. Cron tiers: hourly-ish (`15 */2`),
  tier B (`15 */6`), tier C (`15 */12`). Tier is derived from the **UTC hour** at run time.
- Attribution uses OpenRouter (`OPENROUTER_API_KEY` / `_BACKUP`, model `openrouter/free`);
  `--dry-run` uses heuristic attribution (no LLM).

## Tool playbook

- **Inspect a failed Actions run** → `gh run list --repo akgularda/world-threat-index
  --workflow "WTI Intelligence Update" --status failure` then
  `gh run view <id> --repo ... --log-failed`. The log step column shows `UNKNOWN STEP`;
  find the real failing step by reading the lines just above `##[error]Process completed
  with exit code 1` (the preceding `##[group]Run ...` block names the step).
- **Read a workflow file without cloning** → `gh api repos/akgularda/world-threat-index/
  contents/.github/workflows/wti_update.yml --jq '.content' | base64 -d`.
- **Verify shell-logic fixes** → simulate the exact bash locally across the full input
  range before pushing (e.g. loop `HOUR` 00..23). YAML-lint with
  `python -c "import yaml; yaml.safe_load(open('.github/workflows/wti_update.yml'))"`.

## Gotchas (hard-won)

- **Leading-zero hours are octal in bash** — fixed 2026-06-29. `HOUR=$(date -u +%H)` gives
  `08`/`09`; `$(( HOUR % 12 ))` parses them as octal → `value too great for base` → exit 1.
  Every shard died at 08:xx/09:xx UTC for days while other hours passed. Fix: force base-10
  with `$((10#$(date -u +%H)))`. Same trap applies to any `date`-derived field with a
  leading zero (minute `%M`, day `%d`). See PR #1.
- **`continue-on-error` masks empty outputs** — if a step that sets a step-output can be
  skipped/failed-soft, the *consumer* must default it (we use `${{ steps.tier.outputs.tier
  || 'A' }}`), or the downstream step runs with an empty arg.
- Most steps in `update-shards` are intentionally soft (`continue-on-error` / `exit 0`) so a
  single shard's data hiccup never blocks the merge. The job only hard-fails on the few
  unguarded steps: `checkout`, `setup-python`, `cache`, `Determine tier`, `upload-artifact`.

## Decisions

- **2026-06-29:** tier-selection logic stays in the workflow (not the Python script) but is
  now hardened (base-10 + soft-fail + consumer default) rather than moved — minimal blast
  radius, keeps the schedule→tier mapping visible in one place.
