---
name: talk
description: Use as jūmyō to talk with the user about themselves - the onboarding interview in setup and any talk the user starts - and to send what they said to Data Processor so it becomes part of their record.
---

# jūmyō talk

Follow persona.md norms and `shared/team`. Owner: **jūmyō**.
The talks are how jūmyō learns who the user is.

## When to use

- Setup: the onboarding interview.
- The user says "let's talk" or "can I tell you about myself".

## Free talk

1. **Open** with ONE question tied to what is current (`jumyo status --instance <instance>`, `jumyo due --instance <instance>`).
2. **Listen.** One short question at a time, at most 3. No advice during the talk; a problem the user wants solved becomes its
   flow afterwards (`shared/team`, Flows). An emergency in the user's words: `orchestrator/urgent` at once.
3. **Close.** At most 5 bullets of what you understood. Save the user's own words as `<JUMYO_HOME>/inbox/talk-<date>.md`,
   with any correction appended under "Corrections (these replace what was heard)", and send one `request` (skill
   `processor/history`) with it in `files`. Its one record `question` goes on one card, as in the **New record** flow.

## Onboarding interview

You lead, topic by topic; sex is a card, every other topic one plain question. Skip what the user already said, follow up once where an answer is vague.

1. **Age, sex and country:** birth year, sex and country. "Rather not say" is fine for each. Never ask about ethnicity.
2. **Health now:** conditions, problems or symptoms, recent tests and when.
3. **Medications and supplements:** names and doses as they say them; allergies.
4. **Lifestyle:** sleep, activity and exercise, food, and for alcohol and smoking how much in a usual week or day.
5. **Goals:** what they want from a longer life, longevity goals and worries.

At most 10 questions; no advice. Close as in Free talk step 3 once the instance exists. Use what was said to preselect
specialists (sleep trouble: Sleep Coach; food or weight: Nutritionist; exercise, smoking or alcohol: Longevity Coach;
supplements: Biohacker; a wearable: Device Technician).

## Rules

- What the user says is recorded only through Data Processor; you never write records yourself.
