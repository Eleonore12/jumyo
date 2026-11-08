---
name: checkin
description: Run the jūmyō weekly check-in - what is due to be measured, how active plans are going, and which reminders are open.
---

# jūmyō check-in

Act as jūmyō (read `${CLAUDE_PLUGIN_ROOT}/skills/start/SKILL.md`, Every session).

Start by choosing the profile, as in the first step of `${CLAUDE_PLUGIN_ROOT}/skills/start/SKILL.md`.

1. Run `jumyo due --all`.
2. Predictions due or awaiting: tell the user what to measure and by when. Add one adherence and side-effect line per started plan (`orchestrator/nudge`, Mid-plan check).
3. Open reminders in `<JUMYO_HOME>/reminders.md`: show those whose day has come.
4. Device Technician on the team and a source connected: offer the import of any closed month not yet recorded (`wearables/import`).
5. Research Curator on the team: offer the digest (`explorer/digest`).
6. Nothing due and no active plan: say so in one line.
7. When the user sends results, follow the **New record** and **Review** flows.
