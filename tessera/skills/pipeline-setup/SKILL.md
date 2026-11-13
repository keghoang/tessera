---
name: pipeline-setup
description: Set up a job's Agents folder and install skills.
when_to_use: Sets up or maintains the Agents folder on a job - deploys the starter and skills to a new job, creates or refreshes the job's SHOW.md from Aquarium, and installs or updates the skills on an artist's machine. Use when a job has no Agents folder or no SHOW.md, when the artist asks to refresh SHOW.md, or at session start when the installed skills are missing or older than the server's. Not for looking up one fact (tessera:pipeline-aquarium).
---

# Set up a job's `Agents` folder

`Agents/` is `\\buck\work\current\<JOB>\Production\Common\Agents\`. It holds `BUCK_AGENT_STARTER.md`, `SHOW.md`, `Artists/` and `Skills/`.

## Deploy to a new job

1. Create `<JOB>/Production/Common/Agents/` if it is missing.
2. Copy into it, from the job whose starter has the newest "Version" date: `BUCK_AGENT_STARTER.md`, the whole `Skills/` folder, and `Artists/ARTIST_TEMPLATE.md`. Leave `SHOW.md` and every `ARTIST.md` behind; those belong to their job.
3. Create the new job's `SHOW.md` as below.
4. Tell the artist what was set up and what `SHOW.md` holds.

When you change the starter, update its "Version" date. `TODO(Workflow)` host one studio master copy so jobs don't drift apart.

## Create or refresh `SHOW.md`

Buck5 must be running. Record what Aquarium has and leave the rest out; don't quiz the artist.

1. **Find the project** and pull its facts with `aquarium.py project <JOB> --out <scratch file>` (`tessera:pipeline-aquarium`): the project entry and wiki (deliverables, frame rate, deadline), software (launcher entries, ids, versions, renderer and plugins), colour management, and sequences, shots and tasks with their ids.
2. **Write the file** in the shape below. Leave out a section Aquarium has nothing for, and keep "Learned on the job". If two Aquarium values disagree, write both.
3. **Save** to `Agents/SHOW.md` with the date, and tell the artist in two or three lines what it holds.

Everything else (lighting template, farm rules, approved external tools, conventions) gets added under "Learned on the job" when it comes up in real work, by whoever learns it. On a refresh, update only the Aquarium sections and keep what people added.

```
# Show notes for AI agents: <JOB>

Facts for this job, read from Aquarium through Buck5 on <date>. This file adds to `BUCK_AGENT_STARTER.md` in this folder. On permissions it can only make a rule stricter, never looser. Add to it when you learn something that holds for the whole show.

Last updated: <date>

## Job

| Item | Value |
| --- | --- |
| Job folder | `\\buck\work\current\<JOB>\` |
| Aquarium project id | |
| Deadline | |
| Deliverables | |
| Frame rate | |
| Review tools | |

## Software

Launch from Buck5. One version per application for the life of the show.

| Application | Buck5 launcher entry (and its id) | Renderer / key plugins |
| --- | --- | --- |
| | | |

## Colour

<colour management name and package; rendering space; review view>

## Shots and task ids

| Sequence | Shot | Task | Task id |
| --- | --- | --- | --- |
| | | | |

## Learned on the job

Lighting template, farm rules, approved external tools, conventions and traps go here as they come up. One line each, with who said it and when.

-
```

## Install the skills on an artist's machine

Any agent can read the skills straight from `Agents/Skills/`. Claude Code and Codex can also load them as their own skills once installed. Installing is a "tell, then do" action.

1. Compare the `buck-*` folders in `Agents/Skills/` with the installed ones:
   - Claude Code: `%USERPROFILE%\.claude\skills\`
   - Codex: `%USERPROFILE%\.agents\skills\` (from OpenAI's documentation; not yet tried at Buck)
2. If any are missing there, or the server's `SKILL.md` or anything in its `scripts` folder differs from the installed copy, tell the artist, then copy those `buck-*` folders across. Copy whole folders and leave every other folder there alone.
3. Newly installed skills may only show up in the next session. Until then, read them from `Agents/Skills/`.

The copy on the server is the master. Edit skills there, never in the installed copies, and never copy from the artist's machine back to the server.

## Who edits what

`SHOW.md` and each `ARTIST.md` are edited in place, not versioned. Editing `SHOW.md` is a "tell, then do" action: say what you are changing first, and update "Last updated". Edit only your own artist's `ARTIST.md`. Change the starter and the skills only when the artist asks.
