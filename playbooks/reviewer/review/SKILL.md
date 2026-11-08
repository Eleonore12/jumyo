---
name: review
description: Use as Reviewer when jūmyō asks for a review - predictions are due (weekly check-in, review date reached) or the user brings follow-up results for an adopted plan; collects adherence and side effects, scores predictions, revises the plan and reports calibration.
---

# jūmyō review

Follow persona.md norms and `shared/team`. Owner: **Reviewer**. Reply only in handoffs to jūmyō; never message the user.

## When to use

- The "jūmyō check-in" routine found due or awaiting predictions.
- The user sends follow-up results, or a plan reached its review date.
- jūmyō's mid-plan check (weekly check-in or a record card) reported low adherence or a side effect: run steps
  2-10 without waiting for the review date.
- An insight jūmyō forwards (the digest): check it against the active plans' predictions and
  actions only (`jumyo plan list`), skip step 2, and return `continue` or a `modify` proposal.

## Steps

1. See what is due and what the user has not told yet; each active plan's `plan.json` is in the request's `files`
   (step 4 screens it; missing: say so in a `result`):

   ```bash
   jumyo due --instance <instance>
   jumyo plan list --instance <instance>
   ```

2. **Adherence and side effects first.** Unless the request already carries them for the whole window, send ONE
   `question` handoff to jūmyō per review with, for each active plan: missing measurements; per action the count of
   doses/sessions done of those planned since adoption and the longest gap; any side effect or adverse event since adoption
   (what, when it started, still present, stopped the action?). Wait for the `answer`. jūmyō passes the relayed answers to
   `processor/intake`; do not list them again in your `result`.

3. The new results reach you through jūmyō after Data Processor recorded them and re-projected every map the plan uses. Check
   that the state of each map its predictions name (`map_id`) is current (otherwise say so in a `result`; jūmyō has
   Data Processor re-project):

   ```bash
   jumyo state show --instance <instance> --map <map_id>
   ```

4. **Adverse event: re-screen before scoring.** Add each reported event as a finding on the action it may belong to
   (`caution`, or `block` when serious or when the action must not continue), then screen the adopted plan again:

   ```bash
   jumyo screen --instance <instance> --file plan.json --findings findings.json
   ```

   A `block` outcome forces the proposal to `stop` (or a `modify` that drops the action); state the event plainly.

5. Score:

   ```bash
   jumyo score --instance <instance>
   ```

6. **Decide with adherence.** Low adherence = clearly fewer doses/sessions done than the prediction assumed (plan
   `method`; about four in five of those planned if none stated); quote the counts ("9 of 12"), not a share.
   - A miss with low adherence is reported as **not tested**, not as a failure; propose `continue` or `modify`
     (simpler schedule, later window), never `stop` for lack of effect.
   - A hit with low adherence is reported with that caveat.
   - A miss with adequate adherence is a failure of the prediction; apply the `revision_rule`.

7. Summarize calibration in bullets: scored and missed counts, observed within-interval fraction vs the nominal level, mean absolute error, beat-persistence rate and direction accuracy, per coordinate and overall; list not-tested predictions separately.

8. **Draft the decision** per plan: Continue / Modify / Stop / Complete against the plan's `revision_rule`, with each
   prediction's expected value, interval and observed value, adherence and side effects. Before proposing `modify`,
   ask jūmyō in a `result` to have Nostradamus draft the replacement PlanInput as its own file, screened and
   checked (`nostradamus/plan` step 3), with `nostradamus/trajectory` on it (current course vs revised plan); you
   author no plan. Use its files for the decision. List every new caution from step 4 (one line each);
   jūmyō shows them above the plan's card, and the user's Continue or Modify proceeds on them. `complete` is allowed
   only after the review date.

9. Send ONE `result`: scores, adherence, side effects, calibration and one decision question per plan (its cautions
   listed above it) and, for `modify`, the replacement's start date; list `trajectory.json` in `files` for a `modify`.
   jūmyō shows it with `visualizer/dashboard` (scope "plan review").

10. After jūmyō's `answer`, write `review.json` (for `modify`, the full replacement under `"replacement"`), apply it and
    send a `result` with the new plan status, the voided predictions and, for `modify`, the `replacement_plan_id` and
    the user's start date (jūmyō has Nostradamus adopt it) with Nostradamus's `trajectory.json` unchanged in `files`, or
    plainly what failed. After `stop`, name `nostradamus/trajectory` as follow-up only if a dashboard needs it:

   ```json
   {"decision": "continue", "rationale": "p1 within interval; 12 of 12 sessions done; no adverse effects reported"}
   ```

   ```bash
   jumyo plan review --instance <instance> --plan <plan_id> --file review.json
   ```

## Rules

- Report misses and wrong predictions as plainly as hits; never reword a miss as a success, and never call an
  untested plan a failure.
- Only measurements taken and recorded after adoption, inside the window, count; do not backdate.
- Any adverse event is reported, re-screened and named in the decision, even when the user wants to continue.
- A scored outcome or reported reaction that is a red flag gets a `red_flag:` line (`orchestrator/urgent`) in your
  step's one `question` or `result`; propose pausing the action as a revision.
- `stop` and `modify` void predictions whose window has not opened; say so.
- Never record a decision without the user's choice relayed in jūmyō's `answer`.
