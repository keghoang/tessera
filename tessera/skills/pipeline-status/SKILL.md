---
name: pipeline-status
description: Report what this session is working on.
when_to_use: Reports which shot or asset and task this agent session is on, and whether it is working, waiting on the artist, waiting on the farm or idle, so the team's dashboard shows it. Use at the start of work on any shot or asset, when the work moves to a different shot or task, before asking the artist a question, when waiting on a farm job, and when the work is done. Not for the record of a saved version (tessera:pipeline-trail).
---

# Report what this session is on

The team's dashboard lists every shot and who is on it. Saved versions show there by themselves. Work in progress shows only if the session says so. This is how it says so.

## First step of every task

Report before you work, not after. As soon as you know the shot or asset and the task, run `set` with what you are about to do, and only then open a file, launch an application or submit anything. Every new request in the session starts the same way: `set` if the shot or task changed, `state working` with a new line if only the work changed. A line left over from the last request is wrong the moment a new one arrives.

In Claude Code with the plugin, every message from the artist comes with a note saying what this session currently reports. Read it, and correct it first if it isn't what you are about to do.

## Script

`scripts/status.py`, next to this file. Run it with any Python 3.7 or newer (`c:\opt\rez\Scripts\python.exe` is on every Buck workstation).

| Command | When |
| --- | --- |
| `status.py set --job <JOB> --shot <shot or asset> --task <task> --agent "<agent>" --doing "<one line>"` | Starting work on a shot or asset, and again when what you are doing changes in a way a teammate would care about. |
| `status.py state waiting --doing "Need <name>'s input: <what you need>"` | Before you ask the artist a question or for an approval. |
| `status.py state farm --doing "<what is rendering>"` | You submitted a farm job and are waiting for it. |
| `status.py state working --doing "<what you are doing now>"` | You carry on after a wait. |
| `status.py state idle --doing "<the outcome>"` | The task is finished and the session stays open. |
| `status.py clear` | The artist moves you off the job, or the session is ending. |

- `--task` is the short task name used in file names: `lgt`, `comp`, `anim`, `lyt`, `mdl`, `rig`, `lkdv`, `fx`.
- `--shot` is the shot or asset folder name, spelled as on disk.
- A session shows on one shot and task at a time. A new `set` replaces the old one.

## The `--doing` line

One fixed form per state. The script refuses a line that breaks it, tells you which rule, and you run the command again with a corrected line.

| State | The line starts with | Example |
| --- | --- | --- |
| `working` | an -ing verb | `Adjusting key light ratio on the hero` |
| `waiting` | `Need <name>'s input`, then optionally `: <what is needed>` | `Need Kien's input: rim light option A or B` |
| `farm` | `Rendering` | `Rendering test frames 1010, 1088` |
| `idle` | `Saved` or `Finished` | `Saved v015: key light notes applied` |

For every line:

- English, one line, sentence case, at most 72 characters, no full stop at the end.
- Name the thing in production terms a teammate knows: key light, floor matte, door hinge. No node names, file names or paths.
- Say what is happening to the shot, not what the agent is thinking. No "I", no "Let me".
- Use the verb for the real action. `Working on`, `Processing`, `Handling` and `Continuing` are refused.
- No step counts or percentages.
- The script checks the form. Whether the line is true and specific is on you: `Adjusting things on the shot` passes the check and tells a teammate nothing.
- In a waiting line, `<name>` is the artist's first name as they give it, capitalised.
- Change the line only when what is happening changes.

## What it writes

One small JSON file per session in `<job>/Production/Common/Agents/Activity/`: person, machine, agent, job, shot, task, the `doing` line, the state and two times. No prompt text, no file contents, no paths.

## Rules

- Never put client-sensitive detail, a name the artist didn't give, or anything from the chat in `--doing` beyond what is being done to the shot.
- If the script says `NOT ASSESSED` (the job has no `Agents` folder, or the server is out of reach), carry on with the task. Reporting never blocks work.
- In Claude Code with the plugin installed, the state moves by itself: a new message from the artist sets `working`, the end of a turn sets `idle`, a permission prompt sets `waiting`, closing the session clears it. You still call `set` as the first step of every task, `state working` with a new line as the first step of every later request, `state waiting` or `state farm` when that is the truth at the end of your turn, and `state idle` with the outcome line when the task is finished: the end-of-turn hook changes the state but cannot write the outcome. In any other agent, set every state yourself.

## Where the scripts are

This skill's folder is `${CLAUDE_SKILL_DIR}`; its scripts are in `${CLAUDE_SKILL_DIR}/scripts/`.
