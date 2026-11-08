---
name: digest
description: Use as Explorer when jūmyō's digest routine or the user asks for a research scan - the longevity digest for the user and new insights for the plan (findings that bear on active plans, open gaps or goals).
---

# jūmyō digest and insights

Follow persona.md norms and `shared/team`. Owner: **Explorer**. Reply only in handoffs to jūmyō; never message the user.

## When to use

- A digest run sends a `request` (thread `digest-<date>`, the start date in `summary`).
- jūmyō asks for an ad-hoc scan on a topic.
- Never create a scheduled task yourself.

## Steps

1. Read the sources and what the user is working on (no records, only published states and plans):

   ```bash
   jumyo refs list
   jumyo status --instance <instance>
   jumyo maps select --instance <instance>
   jumyo state show --instance <instance> --map personal_context
   ```

2. Pick 3-7 topics, in this order: what active plans target, open gaps and out-of-range coordinates, goals, the
   selected maps; a topic named in the request comes first. Search the `digest` and `journal` sources and PubMed for
   items on them published since the date in the request, and drop items an earlier digest already listed (the
   `digest_*.md` files in `<JUMYO_HOME>/work/digest-*/`). Queries use topics only, never personal data:

   ```bash
   jumyo evidence search --source pubmed --query "<topic>"
   ```

3. Verify every paper before listing it; drop what does not verify:

   ```bash
   jumyo evidence verify --kind <pmid|doi> --id <id>
   ```

4. Write the digest items with their identifiers to `<JUMYO_HOME>/work/<thread>/digest_<YYYYMMDD>.md` (today's date,
   `shared/team` rule 3) and send one `result` to jūmyō on the request's thread, with that file in `files` and two
   parts in `summary`:
   - **Digest** for the user: at most 5 items, each with title, link, one line on why it matters to this user, and its
     kind (research, event, industry report). Industry reports and events are news, not clinical evidence.
   - **Insights for the plan**: verified findings that bear on an active plan (a prediction's basis, a new risk, a
     stronger or contradicting trial) or on a gap or goal, each with the plan id or coordinate and the identifier.

   Nothing new: a `result` saying "Nothing new" (jūmyō stays quiet with the user).

## Rules

- Never message the user or another agent directly; jūmyō shows the digest and forwards the insights to Reviewer
  (`reviewer/review`) for active plans and to Nostradamus (`nostradamus/plan`) for a new option.
- Never change plans or record anything.
