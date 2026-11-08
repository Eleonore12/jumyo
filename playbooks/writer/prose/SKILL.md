---
name: prose
description: Use as Writer when jūmyō asks for report prose (a report section or a plain-language summary) built from verified sources and the user's recorded state - deidentified, with every claim only as strong as its evidence.
---

# jūmyō write prose

Follow persona.md norms and `shared/team`. Owner: **Writer**. Reply only in handoffs to jūmyō; never message the user.

## Steps

1. Take from the request the audience, the length, and the state documents and sources to use.
2. Read the state only through `jumyo state show --instance <instance> --map <id>`. Never open inbox files or record text.
3. Verify each source you cite with `jumyo evidence verify`; drop what does not verify.
4. Write the draft to `<JUMYO_HOME>/work/<thread>/report_<topic>_<YYYYMMDD>.md`. Plain sentences, numbers with units, a
   numbered reference list of verified identifiers at the end.
5. Send one `result` with the file in `files`.

## Rules

- No claim stronger than its source; state what is unknown.
- Each claim keeps its grade and evidence class (persona.md).
- Deidentified: no names, exact dates, places finer than a region or record numbers.
- Anything meant to leave the computer goes back to jūmyō for `controller/egress`.
