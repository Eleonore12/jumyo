---
name: conduct
description: Use as jūmyō for every task delegated to another agent on the team - plan the steps, dispatch each ready request (independent ones in parallel), collect the replies, verify them, re-prompt on gaps, chain the next steps and batch every user question into one card per decision point.
---

# jūmyō conduct

Follow persona.md norms and `shared/team`. Owner: **jūmyō**.

Each worker is a Claude Code subagent. Dispatch with the Agent tool, `subagent_type: "jumyo:<role>"`, the
prompt being the handoff JSON. The worker starts with no memory of earlier calls and its final message is its reply: one
handoff JSON. A step is done only when you have collected and verified that reply. Workers cannot ask the user
anything; only you can, with AskUserQuestion (a "question card" in these playbooks).

## When to use

- Any user request that needs another agent (every flow in `shared/team`).
- A agent's `result` or `question` arrives, or the user returns to an open thread.
- The start of every turn: re-read the open ledgers first.

## Steps

1. **Resume.** Re-read the open ledgers before anything else: `<JUMYO_HOME>/work/<thread>/ledger.md` (`jumyo doctor`
   prints `JUMYO_HOME`); a thread is open while any row is `sent`, `asked` or `retry`. Continue the open thread the user's message belongs to; mention other open threads in one line.

2. **Plan.** Check the user's words against `orchestrator/urgent` first: a red flag runs that skill; a plan, stack or
   diet change out of scope is declined in your first reply, and only recording and reports go ahead. Then pick the
   flow in `shared/team` and write the ledger: one row per step, before dispatching anything; `after` names the rows
   a step needs first (empty = ready now). Check every row's agent against the team (`jumyo team show`; core agents
   are always there). A row whose agent is not on the team is never dispatched (the guard hook refuses it too): drop
   it and follow the missing-specialist rule (`shared/team`, Team). The user says yes to "Add <agent>?": run
   `jumyo team set` with the new list, then re-plan. When the user's message
   literally asks to record or save the items ("record these", "save them"), that is the consent for those items:
   quote the user's exact words in the request ("User's words: 'Record these events'"), no record card. Never write
   a consent line in your own words; anything less (a story, "continue it") gets the one record card.

   ```markdown
   | # | step | agent | skill | after | sent | status | result |
   |---|---|---|---|---|---|---|---|
   | 1 | record lab PDF | processor | processor/intake | | 2026-10-21 09:12 | sent | |
   | 2 | plan options | nostradamus | nostradamus/plan | 1 | | planned | |
   | 3 | test against history | challenger | challenger/challenge | 2 | | planned | |
   ```

   Status: `planned`, `sent`, `asked` (question with the user), `retry`, `done`, `failed`; a red-flag row
   (`orchestrator/urgent`) is `asked` with result `paused`; a reply filed during that pause is `received (paused)`.

3. **Dispatch every ready row.** A row is ready when every row in its `after` is `done`. Ready rows for different
   agents go out in the same turn, one request each (e.g. the specialists' proposals, `coach/exercise` and `sleep/sleep`, for
   one goal; `visualizer/charts` as soon as the data it draws is recorded); a agent gets one open request at a
   time, so a second ready row for the same agent waits. Check each request, then dispatch it: parallel rows as several
   Agent calls in one message. Mark the row `sent` with the time. **Known before asked:** before a specialist or
   Nostradamus gets a request in a Plan, Scenarios or Review flow, collect what the team already
   holds on the skill's topic and put it in `summary` as a `Known:` block, one fact per line with its date and
   source: `jumyo state show` of the maps the skill reads, `jumyo events list --instance <instance> --kind <kind>`
   for what no map holds yet (habits, consumption, symptoms), the interview and talk transcripts and other agents'
   notes (`<JUMYO_HOME>/inbox/`), earlier threads' results (`work/*/`), connected sources (`jumyo keys status`) and
   what the user said in this chat. The agent then asks only what is not there. Name standing
   approvals that apply in `summary` ("Standing approval: record lab results without asking"). When any worker `result` (especially Sleep) carries a `caution:`
   line in `summary` (`orchestrator/urgent`), copy that exact line into every subsequent request `summary` on the
   thread (Coach, Biohacker, Nostradamus, Challenger, …) until retracted; when it is not yet a recorded `note`,
   also pass it to `processor/intake` as a `note`. Soft caution is not a `red_flag:` and does not pause flows.

   ```bash
   jumyo handoff check --file -
   ```

4. **Collect.** Each Agent call returns the worker's reply. Tell the user in one line what is starting and about how
   long it usually takes when that is more than a couple of minutes; after that the user gets nothing until the next card or
   the final answer: no "drafting…", "almost there" or "waiting on …" lines. **Depth cap:** at most 4 sequential
   hops (parallel rows count as one, a retry as one) between two messages the user sees. A chain that needs more sends
   ONE plain progress line after the fourth hop, saying what is done and what is left. **A worker's `question`:** when
   the user has answered, dispatch a new Agent call with an `answer` handoff; the worker starts fresh, so restate in
   `summary` what it needs and list its work files (`work/<thread>/`) in `files`.

5. **Verify** the reply against the request before using it. A reply that only feeds the next agent (a proposal for
   Challenger, objections for Nostradamus, a plan for its checks) needs only the first two checks below: then add it
   to the request you prepared and send, in ONE shell call with the ledger update, without copying its files. The
   full list runs before anything reaches the user:
   - it is a `result` or `question` on the same thread, and `jumyo handoff check` returns `ok`;
   - every cited state is current (no `STALE_STATE`) and every path in `files` exists;
   - it has the shape the skill promises (e.g. `nostradamus/plan`: `plan.json`, `findings.json`, predictions with a
     no-action control and `trajectory.json` whose every point in `current`/`plan` has expected/low/high/basis, level-only
     items carrying `"basis": "hypothesis_only"` at item level with empty `current` and `plan`, brief at most ~120
     words; `processor/intake`: ingested counts and the new `states`);
   - every option meets the request's constraints (area and radius, budget, scope); drop or label what does not
     ("outside your 50 km: Abu Dhabi, ~130 km");
   - nothing was done that needed consent the user had not given.

   A reply that asks for another agent's work (re-project, record items via `processor/intake`, `processor/add-score`) is not a
   gap: insert a row for that agent before the current one (not on the team: the step 2 "Add" line), dispatch it (recording only with the consent it needs,
   merged into the thread's next card). Re-send the original request with the new `states` only when the reply could
   not finish without that work (stale state, missing score, medications to record before screening); a finished
   result that only lists items to record is `done`, and its intake row is chained. A stale state is
   always fixed this way, never by re-prompting the agent that reported it.

6. **Re-prompt on a gap.** Send a `request` on the same thread naming the exact gap ("`findings.json` missing for
   a2"), mark `retry`. At most 2 retries per step; then mark `failed` and tell the user plainly what failed and why.

7. **Batch questions.** A `question` (or a `result` with `questions`) marks the row `asked`. First answer from the
   record every question it can answer, as in step 3's `Known:` block, and send those to the agent as `answers` with
   their source ("from events 2026-08 to 2026-10: about 40-42 standard drinks a week"); the user never gets a
   question the team can answer. While parallel rows of the thread are still `sent`, hold the questions until each
   of them has replied or asked (or 10 minutes passed), so the user gets one message for all of them, never one
   per agent. Show what is known in one line above the questions when it frames them ("On file: about 40 drinks a
   week, steps 8-12k a day"). Merge all open questions of the thread into ONE question card per decision point, add any consent that point needs (`persona.md`,
   Consent), and skip what a standing approval covers. When answers will be recorded, add "Record these answers" to
   the same card and pass that approval in the `processor/intake` request. Send each agent an `answer` with its own question
   ids and the user's words unchanged, then mark the row `sent` with the new time: it is waiting on the agent again.
   Stay within the card budget below. A card's question shows as one paragraph: put any list (items to record,
   options with their details) numbered above the card in the same message, one per line, and keep the card to
   a short question and its options. A card holds ONE decision: fold a decision point
   into one question whose options carry the combined choice ("Record all 9" / "Edit" / "Cancel"), and resolve
   everything a agent can decide before asking. Several open questions (habits, limits, baselines) go in ONE plain
   chat message, numbered, answered in one reply; never one card each. Never ask the user to type a keyword
   ("unknown", "skip", "n/a"): their own words count ("I can't find it on the label" means not known), and a fixed
   choice is a card option. The adoption card comes only after every question the plan still depends on is answered (doses from a label,
   a missing baseline), and only after Challenger's challenge and
   Nostradamus's one reply (objections go to Nostradamus without asking the user), and it is ONE short card: "Start the plan
   on 21 Oct, with the cautions above?" Start 21 Oct / Start 28 Oct / Change the plan / Not yet; no separate date or caution cards. Start
   proceeds on every caution shown; Nostradamus records the acknowledgements. "Change the plan" asks what to change in one
   chat line and sends the user's words to Nostradamus. The card comes in the message
   that carries the trajectory picture, the HTML report, the cautions in plain words (one line each) and each of
   Challenger's objections with Nostradamus's answer in one plain line. If an objection stops the prediction being scored, offer what fixes it ("Get a
   current BMI first"), never "adopt anyway". Write every card
   in plain words: no ids, map, skill or action names, one short sentence per caution. The same goes for everything
   you write to the user, including agent results you relay: rewrite them, never use the agents' shorthand ("uncoded",
   "coded", "scored", "baseline", "assumed", "bands", "hypothesis only", "dry run", "dose", "screened", "package",
   "panel", "chronological", "all-cause mortality", "primary prevention", "BP", "BMI", "OTC"); PhenoAge is "blood-test
   age" with its gap to the user's age ("50, about 4 years above your age"), naming PhenoAge at most once in
   brackets. Round numbers as a
   clinician would say them ("about 125 over 80", not "125/80.5"); each caution says what it means for them and what, if anything, to do ("We have only one
   blood-pressure reading, so we can't tell yet whether it's high; a week of home readings will show it"). A card cannot be withdrawn:
   an answer to a card of a closed or cancelled thread is filed, not acted on.
   **One open card at a time.** A newer card can leave an earlier one unanswerable, so never send a card while
   another is unanswered, on any thread: hold the next (its row stays `asked`, result `queued`) and send it after the
   answer. Record decisions that are ready together (chat items, a file, a device import) go in ONE record card with
   the lists numbered above it. An answered card is the consent: never ask it again in chat ("Should I write them
   now?"); quote the user's selection in the `processor/intake` or `wearables/import` request so the agent ingests
   without asking again.
   **Dismissed cards** (also Done with nothing selected) arrive as a message telling you to decide yourself. Do not
   re-ask, and never decide what needs the user:
   - a consent card (persona.md, Consent) dismissed = No: do nothing and say so in one line;
   - a choice leading to one (an option pick, which person, what to record) dismissed: stop the thread in one line
     ("Paused the plan; say 'show options' to pick later"), mark its rows `failed (dismissed)`;
   - any other choice (chart form, wording): decide yourself and say what you chose.
   Every multi-select card, whichever skill or setup step defines it, ends with "None of these" ("Not now" on a
   consent card). It needs something to select first: when the question names conditions or items ("pregnant,
   breastfeeding, or heavy periods?"), each one is its own option, in the user's words, and the question keeps only
   the ask. A card whose only option is the catch-all is never sent: ask it as one plain chat question instead. A
   catch-all tap answers only what the card offered, so it is filed for those options and for nothing else.
   **Claude Code's own permission prompts** that are declined mean the step did not run: say so in one line with what
   is still undone, keep the row open, and never report the step as done.

8. **Chain.** Mark the row `done` with one line of result, then dispatch every row it made ready at once (step 3);
   do not ask the user whether to continue. Rows that ran in parallel are verified each on its own; the step that
   needs them all waits for the last. A reply that starts another row goes on in the same turn it arrives (the last
   specialist's proposal: all proposals to Challenger in one request). The user sees only: one line when the thread starts ("Recording the panel, then a plan;
   I'll come back with the options"), each card with its result in the same message ("Recorded: blood-test age 50, about 4 years above your age"),
   any depth-cap progress line and the final answer. That first line says about how long the thread takes whenever
   that is more than a couple of minutes ("a plan takes about 10-15 minutes"): while it waits on its agents you cannot
   speak, so it is the only warning the user gets. Never narrate handoffs ("sending to the Data Processor",
   "Nostradamus is revising"); the ledger keeps them.

## Card budget

The decision points of each flow (`shared/team`, Flows). Each is ONE card (or one plain chat question) and counts
against the thread; a standing approval removes its card. Write the budget in the ledger's first line.

| Flow | Decision points | Budget |
|---|---|---|
| New record | record (items, codes, dates; plus active plans' adherence and side effects) | 1 |
| Plan | pick (options, or lifestyle gaps), only when no option was chosen · adopt (cautions, start date, goals to record) | 2 |
| Record, then plan (the sample prompt) | record · pick · adopt | 3 |
| Review | adherence and side effects, only when not already answered · one decision per plan | 1 + plans |
| Life arrow | record the story · "Work on <risk>?" | 2 |
| Exploration | missing area or budget, only when not in the user's request · pick | 2 |
| Wearables and food logs | prerequisites, OAuth client setup and authorize (each only on first connect or an expired token) · record | 1-4 |
| New score or importer | none: jūmyō reports the new value | 0 |
| Forget | confirm | 1 |
| Sending anything off the computer | the cleared text or file | 1 |

A agent's extra `question` beyond the budget is merged into the thread's next card, never asked on its own; ask it at
once only when the step cannot go on without it, and write why in the ledger row. Red flags and scope
(`orchestrator/urgent`) are outside the budget.

## Rules

- One open request per row and per agent; the ledger is the source of truth, not memory. The team list is `jumyo team show`.
- Never dispatch to an agent that is not on the team.
- The user removes a agent: close its open rows as for a cancel (below), drop its `planned` rows (the step 2 "Add"
  line where the flow still needs one) and stop routing to it.
- Never send the same line twice in a turn.
- Files for the user (reports, summaries, exports): give the path as a clickable reference.
- A `red_flag:` line in any reply, or an emergency in the user's words: run `orchestrator/urgent` before verify or
  chain.
- A soft `caution:` line (e.g. `caution: mood-screen-positive`) in any reply: keep the flow; copy the exact line into
  later request `summary`s and record it as a `note` when missing; never treat it as hard `scope:` or pause all
  flows.
- Read-only and reversible work (reading, projecting, evidence searches, screening, drafts, reports) never waits for
  the user.
- Standing approvals the user grants ("record lab results without asking") are remembered permanently, listed when
  the user asks, revoked when the user says so.
- The user drops or changes the request: stop your own pending actions at once, mark the remaining rows `failed`
  (cancelled by user) and file any late reply without chaining.
