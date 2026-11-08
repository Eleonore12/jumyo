---
name: dashboard
description: Use as Visualizer when jūmyō asks for a custom dashboard (trajectory brief, state now, plan review, life arrow) - build a DashboardPayload whose scope the requesting skill defines, render it with jumyo report and return it to jūmyō with a matching chart.
---

# jūmyō dashboard

Follow persona.md norms and `shared/team`. Owner: **Visualizer**. Reply only in handoffs to jūmyō; never message the user.
A dashboard is one self-contained HTML file rendered from a DashboardPayload
(`contracts/DashboardPayload.schema.json`); the scope below decides what goes in, the requesting skill decides which
scope. Rendering is read-only: never ask before building one. Clicks in the HTML never reach jūmyō; every choice the
user makes about a dashboard is the question card jūmyō sends with it.

## When to use

- `nostradamus/trajectory` returned `trajectory.json` (Plan flow, "where am I heading"): scope **trajectory brief**.
- The user asks how they are doing now, how a plan went, or for their life arrow.

## Blocks

`markdown {text}` (no raw HTML) · `kv {items:[{key, value}]}` · `table {columns, rows}` (cell: text, number or
`{text, href}`) · `timeseries {series:[{name, unit, points:[{t, v, ref_low, ref_high}], predictions:[{t, expected, low, high}]}]}` ·
`list {items:[{text, href}]}` · `timeline {now, events:[{t, t_end, label, kind: past|predicted, level, probability,
detail, href}]}`.

## Scope

| Scope | From | Blocks, in order |
|---|---|---|
| trajectory brief | `nostradamus/trajectory` | markdown (the brief, unchanged) · one timeseries block with two series per marker item, "<label>: current course" and "<label>: with plan" (each with the recorded points incl. `now`, so both start at today; `current` / `plan` level points as predictions; same prefix and unit share one axis, the plan dashed) · table "Two courses" (item, now, current course, with plan, basis; risks as `expected (low-high) %` by horizon) · list (sources, linked) |
| scenarios | `nostradamus/trajectory` (Scenarios mode) | markdown (the brief, unchanged) · one timeseries block per measurement item, one series per scenario ("<label>: <scenario>", the baseline solid, the others dashed) · one timeseries block "Chance of being alive" with each scenario's survival curve (age on the axis) · table "Scenarios" (scenario, each item at the horizon as `expected (low-high)`, life expectancy, median age at death, chance of reaching 80 and 90, years vs baseline, basis) · list (sources, linked) |
| state now | `consultant/assess` result | kv (as of, maps, gaps count) · table (coordinate, value, unit, reference range, date) · list (gaps and next measurements) |
| plan review | `reviewer/review` result | kv (plan, review date, decision proposed) · timeseries (observed vs predicted, with interval) · table (prediction, expected, interval, observed, score); with a `modify` proposal append the trajectory brief's markdown, timeseries and Two courses table |
| life arrow | `orchestrator/arrow` | timeline · markdown (the story) |

Order is fixed: the takeaway first, pictures next, tables and sources last. At most 6 blocks.

## Steps

1. **Collect** the requesting agent's file named in jūmyō's request (`work/<thread>/trajectory.json` etc.) and the recorded data:

   ```bash
   jumyo export --instance <instance>
   jumyo due --instance <instance>
   ```

2. **Write** `<JUMYO_HOME>/work/<thread>/dashboard.json`, copying values from those files only:

   ```json
   {"kind": "jumyo_dashboard", "schema_version": 1, "title": "Where you are heading", "subject_id": "<subject_id>",
    "generated_at": "2026-10-21T09:00:00Z", "blocks": [
     {"type": "markdown", "title": "In brief", "data": {"text": "..."}},
     {"type": "timeseries", "title": "Biological age gap", "data": {"series": [
       {"name": "Biological age gap: current course", "unit": "years", "points": [{"t": "2026-09-14", "v": 2.1}],
        "predictions": [{"t": "2027-01-19", "expected": 2.1, "low": 0.6, "high": 3.6}]},
       {"name": "Biological age gap: with plan", "unit": "years", "points": [{"t": "2026-09-14", "v": 2.1}],
        "predictions": [{"t": "2027-01-19", "expected": 1.1, "low": -0.9, "high": 2.6}]}]}}]}
   ```

3. **Render** and keep the `uri`:

   ```bash
   jumyo report --instance <instance> --payload <JUMYO_HOME>/work/<thread>/dashboard.json
   ```

4. **Chart for chat.** Draw the same data as one PNG following `visualizer/charts` (trajectory brief: both courses
   on one axis per item, bands for intervals, the plan course lighter and dashed).

5. **Return** to jūmyō in one `result`: the brief, the PNG path and the HTML report path (`uri`). jūmyō sends them, in
   this order, as one turn: the brief with the PNG, the HTML report as a chat attachment and, last, in the Plan flow,
   the single adoption card (jūmyō's `orchestrator/conduct` step 7). If rendering fails, say so in the `result`; jūmyō
   never sends the adoption card without the PNG and the HTML report.

## Rules

- Never in a dashboard: names, places, employers, raw record text or inbox file contents, numbers not in a agent's file
  or the export, points without their interval, intervention names beyond the plan's action labels (the research
  and target scopes: beyond those in the topic's or the dossier's own file), secrets.
- Level-only items go in the table as "not predicted", never as a drawn line.
- `change_from_baseline` points go in the Two courses table only, never on a level timeseries.
- Target scopes never show a composite score, a probability of success, a rank, a "best" or a total across rows; a
  sample carries its denominator (`n of N`, read of deposited); a source in `unread` is "not read", never 0.
- One dashboard per thread step; regenerate rather than edit an old report.
