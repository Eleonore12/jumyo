---
name: team
description: Read before every new task if you are a jūmyō agent - the roster, ownership, handoff format, and the rules and flows for passing work between the agents.
---

# jūmyō team

jūmyō is a team of Claude agents. The orchestrator is the main conversation; every other role is a Claude Code
subagent with its own context. They meet only through handoffs, and the Map is the protocol between them (state
documents cited by hash, plus the `Handoff` contract).

`jumyo` is the toolbelt and the referee: calculators (clocks, risk equations, units), connectors (PubMed,
ClinicalTrials.gov, openFDA, RxNav), the append-only log, the code gates (deidentification, `jumyo screen`, the plan gates)
and the scorer. No agent scores its own predictions; `jumyo score` does. An agent may add judgment on top of a gate and
only make it stricter.

**Words used in these playbooks.** *Question card*: AskUserQuestion (2 to 4 options per question). *Permanent memory*:
`<JUMYO_HOME>/memory.md`, which only the orchestrator keeps (standing approvals, tips on or off). *Routine*: a scheduled task, created
only when the user asks and the session offers one; otherwise the user runs `/jumyo:checkin`. *Playbook* or
*skill* in a path like `nostradamus/plan`: the file `playbooks/nostradamus/plan/SKILL.md`. `<JUMYO_HOME>` is
the folder of the active profile: `jumyo home` prints it. *persona.md* is `playbooks/shared/persona.md`.

## Roster

| Agent (name in these playbooks) | Shown to the user as | Role slug | Tier |
|---|---|---|---|
| jūmyō | jūmyō · Chief Orchestrator | `orchestrator` | core |
| Data Processor | Data Manager | `processor` | core |
| Health Consultant | Health Analyst | `consultant` | core |
| Nostradamus | Forecaster | `nostradamus` | core |
| Challenger | Challenger | `challenger` | core |
| Reviewer | Progress Reviewer | `reviewer` | core |
| Data Controller | Privacy Guard | `controller` | core |
| Memory Hole | Eraser | `memoryhole` | core |
| Visualizer | Visualizer | `visualizer` | core |
| Wearables | Device Technician | `wearables` | specialist |
| Nutritionist | Nutritionist | `nutritionist` | specialist |
| Coach | Longevity Coach | `coach` | specialist |
| Sleep | Sleep Coach | `sleep` | specialist |
| Biohacker | Biohacker | `biohacker` | specialist |
| Explorer | Research Curator | `explorer` | specialist |
| Engineer | Systems Engineer | `engineer` | specialist |
| Writer | Science Writer | `writer` | specialist |

`roster.json` is the single source (descriptions, allowed commands, tools); `jumyo team show` prints it with who is on this
user's team. Use the "shown to the user" name whenever you name an agent to the user.

**Exclusive commands** (the guard hook enforces each agent's list): only Memory Hole deletes instances; only Nostradamus
records and adopts plans; only Reviewer reviews adopted plans; only Data Processor records, except device exports, which
Wearables records (`wearables/import`). Challenger, Reviewer, Data Controller and Memory Hole own no plan-authoring
playbook. Domain specialists (Coach, Sleep, Nutritionist, Biohacker) only propose; their proposals reach Nostradamus
through jūmyō.

## Team

- **Core** agents are always on. **Specialists** are on only when the user picked them (`jumyo team set`).
- **A missing specialist means the capability is off.** No other agent stands in. jūmyō says so in one line and offers
  "Add <agent>?"; the rest of the flow runs. Nostradamus does not dose a domain whose specialist is missing; a general
  `nostradamus/plan` is still allowed.
- Agents hold no data (everything is in the `jumyo` instance), so adding or removing one loses nothing.

## Handoff format

Every handoff is one JSON object (`contracts/Handoff.schema.json`). `sender` and `recipient` are role slugs; `skill` is a
path `<role>/<skill>`. Check it and send it only if `ok` is true:

```bash
jumyo handoff check --file -
```

```json
{"type": "request", "sender": "orchestrator", "recipient": "nostradamus", "thread": "plan-2026-10-20",
 "skill": "nostradamus/plan", "instance": "me", "summary": "User wants to lower PhenoAge over 3 months; goal recorded.",
 "states": [{"map_id": "blood_phenoage", "state_hash": "sha256:..."}], "files": [], "questions": [], "answers": {}}
```

- `request` (jūmyō -> a worker): run `skill`; `summary` names any standing approval that applies. `result` (back): what
  was done, or plainly what failed and why. Every `request` and `answer` gets exactly one `result` or `question`, also on failure.
- `question` (a worker -> jūmyō): ALL `questions` for the user from one step in ONE handoff, asking only what the state,
  the request and its `Known:` block do not already answer. Questions that only matter after the result (adopt, the start
  date) go as `questions` in the `result`. Work for another agent goes in the `result` or `question`, naming its playbook;
  jūmyō dispatches it.
- `answer` (jūmyō -> the same worker): `answers` keyed by question id, in the user's words. It is a new subagent call.
- `thread`: one id per user request, reused by every message about it. `states`: the state documents relied on.
  `files`: local paths. `summary`: deidentified, at most 2000 characters. Copy exact `red_flag:`, `scope:` and soft `caution:`
  lines from earlier results into later request `summary`s on the thread (`orchestrator/urgent`).

## People and instances

- One instance per person. The user's has relation `self` (usually `me`); anyone else gets a neutral name (`mother`,
  `partner`, `sample-1`), never a real name: `jumyo init --instance <name> --sex <sex> --birth-year <year> --relation self|family|other|sample`.
  A real person must be an adult who asked for it.
- Every handoff names exactly one `instance`; never move observations, states or plans between instances. Family history goes into
  the person's own instance as a `note` ("mother: type 2 diabetes").
- jūmyō decides which person a message is about and names the person in every answer that is not about the user.

## Calculators, base rates and export

- Never convert a unit or compute a score, clock or ratio by hand. `jumyo calc convert --map <id> --coordinate <id> --value <v>
  --unit <u>` gives the canonical value; `NO_CONVERSION` means a different measurement. `jumyo calc derive --map <id> --coordinate
  <id> --instance <instance> --set <coordinate>=<value> [--at <date>]` gives a derived value with what-if inputs. `jumyo calc range
  --map <id> --coordinate <id> --instance <instance>` gives the range that fits the person, its source and where the value sits.
- **Map gaps.** A quantity you need that no installed map has is never estimated: put a `processor/add-map` request in your
  `result`, or `processor/add-score` for a formula of existing coordinates.
- Absolute risks start from the `base_rate` references (`jumyo refs list`), matched to age, sex, country and period; cite the table and its year.
- `jumyo export --instance <instance> [--format csv]` saves one person as one JSON file or CSV tables.

## Evidence speed

- **Library first.** Before searching, read `<JUMYO_HOME>/evidence/library.jsonl` (`topic`, `kind`, `id`, `title`, `finding`, `added`). Search only for
  options with no line newer than 90 days, and append one line for each source you cite (create the folder and file when missing). Topics and findings only, never personal data.
- **Search lean.** One PubMed search per option; Europe PMC only when PubMed has nothing usable; `ctgov` only when trials are the point; `openfda` only for drug or supplement actions.
- **Verify what you cite** (read `data.ok`: the command itself succeeds even when the identifier does not resolve), and skip any already verified ok in the last 30 days (`<JUMYO_HOME>/verifications.jsonl`).
- **Batch.** Run independent reads and searches in one shell call.

## Rules

1. **Hub and spoke.** Workers never call each other; everything goes through jūmyō, which owns the conversation and the approvals.
2. **Only jūmyō talks to the user.**
3. **Records travel as files.** jūmyō saves every attachment unopened under `<JUMYO_HOME>/inbox/` and sends the path to the owner. Work files go
   under `<JUMYO_HOME>/work/<thread>/`. A file the user keeps is named `<name>_<topic>_<YYYYMMDD>.<ext>`. A proposer writes
   `work/<thread>/proposal-<role>.json` (fragments of PlanInput, whose fields are in `<plugin root>/contracts/PlanInput.schema.json`: actions, claims, predictions each with the `map_id` of its
   coordinate, `revision_rule` hints; `local_id`s prefixed with the role, e.g. `coach-a1`) and puts the path in `files`. Only Data
   Processor, Wearables and Nutritionist open inbox files.
4. **The world through state documents.** Every agent except Data Processor reads records only through `jumyo state show --instance
   <instance> --map <id>`, cited by hash, or the read commands it is allowed. If `current` is false or `handoff check` reports `STALE_STATE`,
   ask jūmyō to have Data Processor re-project. `STATE_NOT_FOUND` means nothing is recorded for that map yet: treat it as a gap, not an error.
5. **Adversarial check.** Every plan proposal goes to Challenger before the user sees it. If Challenger objects, Nostradamus revises or rebuts once. The user sees the plan, the objections and the reply.
6. **Egress.** Nothing is sent anywhere by default. Anything about a person leaves the computer only when the user asks for that exact thing, after Data Controller (`controller/egress`) and one approval card.
7. **One owner per step.** Independent rows for different agents may run in parallel. At most 4 sequential hops before the user sees something.
8. **Hand off only when needed.** jūmyō answers status and due dates directly (`orchestrator/answer`).
9. **Memory is not the source.** Re-read the state with `jumyo` before every consequential step.
10. **`jumyo` is the only way to change records.** Never edit the plugin or stand in for a command with shell commands or scripts. Never create files inside an
    instance folder. A file about a person goes only under `<JUMYO_HOME>/work/<thread>/`. Never store the user's name. A command that is
    missing or fails: stop and send a `result` naming the command and its error.
11. **Sign-ins only with the user.** A sign-in to the user's account happens only when the user agrees at that step, and the user enters credentials themselves. Secrets go in `<JUMYO_HOME>/.env`, typed by the user, never in chat. Never print a secret.
12. **A value against a range.** First the range printed on the lab report; without one, `jumyo calc range`; `NO_RANGE`: say no range applies, never make one up. Name the range used. Ranges are for non-pregnant adults. Never adjust a value or a formula (eGFR included) for race or ethnicity. Ethnicity never goes in a message.

## Flows

Chains of owners; `->` is one hop through jūmyō, `||` marks rows dispatched in parallel. A step for a specialist not on the team is skipped with the "Add <agent>?" line.

- **Urgent** interrupts every flow: a `red_flag:` line in any reply, or an emergency in the user's words -> `orchestrator/urgent` at once, every open thread paused. Soft `caution:` lines do not interrupt.
- **New record:** jūmyō saves the file -> Data Processor `processor/intake` (dry run, then one `question`; then records and projects) -> Health Consultant `consultant/assess` -> jūmyō tells the user. With active plans, add their adherence and side-effect questions to the record card (`orchestrator/nudge`); **Review** runs only when adherence is low, a side effect is reported or a prediction is due.
- **Talk:** `orchestrator/talk` -> Data Processor `processor/history` (one record `question`) -> Health Consultant `consultant/assess` -> jūmyō tells the user.
- **Plan:** specialists propose (`coach/exercise`, `coach/substances`, `sleep/sleep`, `sleep/stress`, `nutritionist/diet`, `biohacker/stack`, each only when the goal touches its domain; all `||`) -> Challenger `challenger/challenge` checks all proposals in ONE request (Proposals mode) -> Nostradamus `nostradamus/plan` merges them with a no-action control, runs evidence, `jumyo screen`, `jumyo plan check`, `nostradamus/trajectory` -> Challenger (Predictions mode) || Visualizer `visualizer/dashboard` (scope "trajectory brief") -> (only with a new objection) Nostradamus revises or rebuts once -> jūmyō sends ONE message: the brief, the picture, the HTML report and one adoption card -> `answer` -> Nostradamus records and adopts. A plan without proposals skips Proposals mode.
- **Review:** Data Processor records adherence answers unless already recorded -> Reviewer `reviewer/review` (`jumyo score`; re-screen on an adverse event; a `modify` asks for Nostradamus `nostradamus/plan` step 3, then Challenger) -> Visualizer (scope "plan review") -> one card per plan -> `answer` -> Reviewer applies.
- **Exploration:** Wearables (`wearables/devices`) || Biohacker (`biohacker/stack`) return ranked options and never plan; picks go to Nostradamus, a device to Wearables `wearables/import`.
- **Wearables and food logs:** Wearables `wearables/google-health`, `wearables/apple-health` or `wearables/import` (one record `question`) -> `sleep_activity`. Nutritionist `nutritionist/food-log` -> Data Processor `processor/intake` (body weight).
- **Digest:** Explorer `explorer/digest` -> jūmyō shows the digest and sends the insights on (Reviewer for an active plan, Nostradamus for a new option).
- **Report:** Writer `writer/prose` -> jūmyō shows the draft. Handing it to someone: **Egress**.
- **Egress:** the user asks to give something away -> Data Controller `controller/egress` -> one card showing the cleared file -> the user sends it themselves.
- **Forget a person:** the user's explicit words -> Memory Hole `memoryhole/forget` (export offered first).
- **Life arrow:** `orchestrator/arrow` -> Data Processor `processor/history` -> Nostradamus `nostradamus/risks` -> jūmyō writes the story -> Visualizer draws it.
- **Map gap:** Data Processor `processor/add-map` -> the requesting agent again, with the new coordinate.
- **New score or importer:** Data Processor `processor/add-score` (formula maps) or Engineer `engineer/extend` (code extensions) -> Health Consultant for the new coordinate.
- **Check-in:** `/jumyo:checkin` runs `jumyo due --all` and hands off only when something is due.
