# jūmyō

A personal longevity team of Claude agents, packaged as a Claude Code plugin. It turns your health records into a structured, deidentified log, proposes screened experiments with explicit predictions, and scores those predictions against your next results.

You talk to one agent. A team works behind it, each with its own context, and a deterministic toolbelt does what an AI should not do from memory: arithmetic, safety gates, record keeping and scoring.

> **Not medical care.** jūmyō does not diagnose, treat or prescribe, and it can be wrong. No clinician reviews its output. Read the [Disclaimer](DISCLAIMER.md).

## The three laws

Every agent carries these, in this order. A lower law never overrides a higher one.

1. **Do no harm.** Nothing jūmyō suggests, records or sends may hurt the user or anyone else: screen every action, name the risks, act on red flags first, and when the evidence is unclear, say so and do less.
2. **Extend the user's healthy life,** with measured, predicted and honestly scored steps toward their own goals.
3. **Never stop until aging is under control.** Keep delivering measurable progress on the user's biomarkers, plans and understanding of their own aging, for as long as it takes.

## The team

**Core team, always on**

| Agent | Job |
|---|---|
| Chief Orchestrator | The only agent you talk to. Runs every flow and asks for your approvals |
| Data Manager | Turns records into an organised, coded log |
| Health Analyst | Explains results, changes and missing measurements |
| Forecaster | Merges proposals into one plan, screens it, predicts outcomes with intervals |
| Challenger | Attacks every plan before you see it |
| Progress Reviewer | Compares what happened with what was predicted |
| Privacy Guard | Checks anything about you before it leaves your computer |
| Eraser | Deletes a person's data, on explicit request only |
| Visualizer | Charts and dashboards |

**Specialists, you choose**

| Specialist | Job |
|---|---|
| Device Technician | Connects your health apps and wearables and imports your sleep and activity data. |
| Nutritionist | Reads your food logs and proposes evidence-backed diet options for your goals. |
| Longevity Coach | Proposes exercise with amounts and frequency, and supports changes to smoking and alcohol habits. |
| Sleep Coach | Reviews your sleep and stress concerns and proposes practical options. |
| Biohacker | Compares supplement combinations and the evidence behind them. |
| Research Curator | Finds new longevity studies relevant to your goals and prepares your research digest. |
| Systems Engineer | Builds and tests new importers and calculations, installed only with your approval. |
| Science Writer | Turns your cited health summaries into clear reports, with identifying details removed. |

A specialist you did not pick is off: no other agent stands in for it, and a hook refuses to start it. Change your team any time with `/jumyo:team`.

## Install

You need [Claude Code](https://code.claude.com) and Python 3.11 or later. In Claude Code:

```text
/plugin marketplace add Eleonore12/jumyo
/plugin install jumyo@jumyo
```

Then start it:

```text
/jumyo:start
```

The first run takes about a minute to create a private Python environment in `~/.jumyo`, then about five minutes of setup. No API key or server is needed.

To try a local copy, run `claude --plugin-dir ./jumyo`.

## What you can ask

- "Here are my latest blood test results. What is my blood-test age, and what could I try over the next three months to lower it?"
- "Here is my life story so far. Continue it and show me my life arrow."
- "Is my plan working?"

Run `/jumyo:checkin` weekly to see what is due.

## How it stays honest

**Agents judge, code computes.** The `jumyo` toolbelt holds the calculators, connectors, event log, gates and scorer.

| Guarantee | Enforced by |
|---|---|
| Every action is screened before a plan can be recorded | Plan gates in `jumyo plan check` |
| Every citation resolves to a real identifier | `jumyo evidence verify` |
| Predictions are scored by code, never by the agent that made them | `jumyo score` |
| Corrections never rewrite history | Append-only log, `jumyo retract` |
| Each agent runs only its own commands | `hooks/guard.py` |
| Unchosen specialists cannot run | `hooks/guard.py` |
| Only three agents open raw records | `hooks/guard.py` |

The hook is a guard rail, not a sandbox.

## Your data

Records stay in `~/.jumyo` on your computer. What the agents read is processed by Anthropic under your Claude account's terms. Evidence searches send topics, never personal data, to public services (PubMed, Europe PMC, ClinicalTrials.gov, openFDA, RxNav). There is no server, no telemetry and no data sharing. Delete everything with the Eraser, or remove the folder.

Records must be yours, or those of an adult who asked you to keep them.

## Optional extras

Keys go in `~/.jumyo/.env`, typed by you, never in chat. See [.env.example](.env.example). A missing key only disables its capability.

Methylation clocks need extra packages:

```bash
uv pip install --python ~/.jumyo/.venv/bin/python "biolearn>=0.9,<1" "pandas>=2.1,<3" seaborn
```

## Layout

```text
.claude-plugin/    plugin and marketplace manifests
agents/            one subagent per role (generated)
skills/            /jumyo:start, checkin, team
playbooks/         what each agent follows, one folder per role
hooks/guard.py     role and team enforcement
roster.json        single source for names, tiers and permissions
bin/jumyo      launcher for the toolbelt
src/               the toolbelt: life (records), map (state), policy (gates, scoring)
maps/              State Maps: what is tracked and how
references/        trusted sources and API addresses
contracts/         JSON schemas
```

After changing `roster.json` or the laws, run `python3 scripts/build_agents.py`.

## Develop

```bash
uv run --extra dev --with-editable . pytest -q
```

## License and data

Code: [MIT](LICENSE).

The bundled life tables come from the United Nations, World Population Prospects 2024, licensed under [CC BY 3.0 IGO](https://creativecommons.org/licenses/by/3.0/igo/). Source details are in `src/jumyo/map/data/wpp2024_lx.provenance.json`.
