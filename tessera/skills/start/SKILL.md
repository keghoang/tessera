---
name: start
description: First-session setup and welcome.
when_to_use: Runs an artist's first-session setup on a job - welcomes them, confirms the username, machine and job it picked up, checks the workstation, and briefs them on what the assistant does and how to use the skills. Use when the session-start note says the artist has not been set up on this machine, or when the artist asks to be set up, onboarded or shown how this works. Not for setting up a job's Agents folder or SHOW.md (tessera:pipeline-setup).
---

# First-session setup

Every artist gets the same words. `scripts/start.py` prints them; pass its output on **word for word**, with no summary, no extra lines and no reformatting. Run it with `c:/opt/rez/Scripts/python.exe`.

If the artist opened with a request, hold it. Do the setup, then go back to it.

## Steps

1. **Welcome.** Run `start.py welcome` and pass the output on. If the artist opened with a request, end the line "so a quick setup first" with ", then <their request in a few words>." Ask "Is that right?" as a multiple-choice question and wait.
   - **Wrong job:** ask which job, then use that name as `--job` from here on.
   - **Wrong username:** ask for it, then pass `--user <name>` from here on.
   - **No job found:** the output asks which job they are on. Use the answer as `--job`.
2. **Check.** Run `start.py check --job <JOB>` and pass the table on.
   - A **fail** row says what the artist should do. Stop there; when they say "retry", run the check again.
   - A **needs a pick** row is a question for the artist. Ask it, create the folder they pick, record it in their `ARTIST.md` after step 3, and carry on.
   - "not assessed" rows don't stop the setup.
3. **Brief.** Run `start.py finish --job <JOB>` and pass the output on, except lines in `[square brackets]`, which are for you. This also creates the artist's `ARTIST.md` on the job if they have none, and marks this machine as set up.
4. **Hand over.** Read the job's `BUCK_AGENT_STARTER.md` and `SHOW.md` now if you haven't. Then go back to the request they opened with, or ask which shot or asset and what they need.

## Rules

- Don't ask for a department, a display name or preferences. Artists here work across tasks, and preferences go into `ARTIST.md` as they come up.
- Don't add a tour, a sample task or advice. The setup is the script's output and nothing else.
- The setup runs once per machine. `start.py reset` forgets it, for running it again.
- The username is the Windows login, which is the Buck5 login; `BUCK_USER` overrides it if set.

## Where the scripts are

This skill's folder is `${CLAUDE_SKILL_DIR}`; its scripts are in `${CLAUDE_SKILL_DIR}/scripts/`.
