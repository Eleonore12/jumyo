---
name: team
description: Show the jūmyō team and add or remove specialists (Device Technician, Nutritionist, Longevity Coach, Sleep Coach, Biohacker, Research Curator, Systems Engineer, Science Writer).
---

# jūmyō team

1. Run `jumyo team show` and list the team by name: core team first, then the specialists on and off.
2. If the user named a change, apply it. Otherwise ask with one AskUserQuestion holding two multi-select questions, as in Setup step 5 of `${CLAUDE_PLUGIN_ROOT}/skills/start/SKILL.md`.
3. Run `jumyo team set --specialists <comma-separated role slugs, the whole new list, or none>`. Slugs: `wearables`, `nutritionist`, `coach`, `sleep`, `biohacker`, `explorer`, `engineer`, `writer`.
4. Confirm in one line. Removing a specialist loses no data; its capability is simply off.
