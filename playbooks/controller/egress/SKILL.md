---
name: egress
description: Use as Data Controller when jūmyō has something about a person that is about to leave the computer (an export the user wants to hand over, a report for someone else) - run the code gate, add judgment that can only reject, and return cleared or rejected.
---

# jūmyō egress check

Follow persona.md norms and `shared/team`. Owner: **Data Controller**. Reply only in handoffs to jūmyō; never message the user.

jūmyō shares nothing by itself: there is no automatic sending of any kind. This check runs only when the
user asks to give a file or text to someone or something outside this computer.

## Steps

1. Run the code gate on the exact file in the request. It shows rules and paths, never the text:

   ```bash
   jumyo egress check --file <file> --instance <instance>
   ```

2. Any violation is `rejected`, listing each `{path, rule}`. The gate only finds patterns, so a clean result is not a clearance.
3. Read the file and add rejections for what patterns miss: names, initials, employers, facility names, addresses,
   rare conditions or details that could identify the person, and anything beyond what the request says the user approved.
4. Send one `result` whose `summary` starts `cleared` or `rejected`, naming the file and each reason.

## Rules

- Judgment only adds rejections; it never overrides the code gate.
- Never edit the payload. A rejected file goes back to jūmyō.
- A file the user explicitly wants sent with its identifying details still comes back `rejected` with the reasons; the decision is the user's, on a card.
- Never send anything yourself.
