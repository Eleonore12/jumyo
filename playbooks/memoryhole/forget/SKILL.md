---
name: forget
description: Use as Memory Hole when jūmyō relays the user's request to delete everything recorded about one person (the user or someone they added) for good.
---

# jūmyō forget

Follow persona.md norms and `shared/team`. Owner: **Memory Hole**. Reply only in handoffs to jūmyō; never message the user.

## When to use

- A `request` with skill `memoryhole/forget` naming one `instance`: the user wants that person's data gone.
- Withdrawing single items is Data Processor's (`processor/intake`, correct or retract), via jūmyō; never delete
  for a correction.

## Steps

1. Check the instance exists and size what will go: the counts of observations, states, inbox files and work folders
   (from the request). Then look for copies outside `<JUMYO_HOME>`: search the work areas (`/tmp` and the working directory; never the plugin
   folder or another instance) for files that hold its subject id (`s_…`; the label too when it is not a common word
   such as `me`), or are byte copies of its inbox files, and count them by folder. Send ONE `question` to jūmyō with the instance, its relation, the counts, the offer of an export, and the exact choice ("Delete everything recorded
   about <instance> for good? It cannot be undone." Export, then delete / Delete / Cancel). Skip this question when
   the request's `answers` already hold a jūmyō card's delete question with the user's selection naming this
   instance (setup step 6, or a forget card): that selection is the user's explicit confirmation; go to step 2.

   ```bash
   jumyo instances list
   ```

2. If the `answer` asks for an export, export first, outside the instance folder (deletion removes that folder), and
   put the path in `files` of the `result`.

   ```bash
   jumyo export --instance <instance> --out <JUMYO_HOME>/exports/<instance>
   ```

3. Delete only on the user's explicit words relayed unchanged in `answers`, from the user's answer to jūmyō's card
   in the chat; never under a standing approval, never on jūmyō's own judgment: otherwise reply with a `question` that jūmyō shows as the card. The command refuses unless `--confirm` repeats the instance name. If the command is
   missing or fails, delete nothing by hand (`shared/team` rule 12): reply with a failed `result`.

   ```bash
   jumyo instances delete --instance <instance> --confirm <instance>
   ```

4. Then delete only the inbox files, `work/<thread>/` folders, the copies outside `<JUMYO_HOME>` found in step 1.
   Never touch anything inside another instance. Send one `result`: files and events removed, the export path if any, and that the
   deletion is final; never delete the export folder.

## Rules

- The confirmation reaches the user only as one jūmyō question card: never ask, confirm or show a card in your own
  chat, also not "to be safe"; a doubt goes to jūmyō as a `question` handoff.
- One instance per request.
- There is no backup and no undo; say so in the question.
- Only this skill runs `jumyo instances delete`.
- Other agents hold only hashes and summaries; jūmyō drops the instance from its own memory and tells the agents on the
  team to do the same. Afterwards no agent quotes a value or summary from before the deletion: a summary of a new
  instance comes only from that instance's records.
