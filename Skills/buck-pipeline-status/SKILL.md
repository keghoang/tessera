---
name: buck-pipeline-status
description: Reports which shot or asset and task this agent session is on, and whether it is working, waiting on the artist, waiting on the farm or idle, so the team's dashboard shows it. Use at the start of work on any shot or asset, when the work moves to a different shot or task, before asking the artist a question, when waiting on a farm job, and when the work is done. Not for the record of a saved version (buck-pipeline-trail).
---

# Report what this session is on

The team's dashboard lists every shot and who is on it. Saved versions show there by themselves. Work in progress shows only if the session says so. This is how it says so.

## Script

`scripts/status.py`, next to this file. Run it with any Python 3.7 or newer (`c:\opt\rez\Scripts\python.exe` is on every Buck workstation).

| Command | When |
| --- | --- |
| `status.py set --job <JOB> --shot <shot or asset> --task <task> --agent "<agent>" --doing "<one line>"` | Starting work on a shot or asset, and again when what you are doing changes in a way a teammate would care about. |
| `status.py state waiting --doing "<what you need from the artist>"` | Before you ask the artist a question or for an approval. |
| `status.py state farm --doing "<what is rendering>"` | You submitted a farm job and are waiting for it. |
| `status.py state working` | You carry on after a wait. |
| `status.py clear` | The task is finished, or the artist moves you off the job. |

- `--task` is the short task name used in file names: `lgt`, `comp`, `anim`, `lyt`, `mdl`, `rig`, `lkdv`, `fx`.
- `--shot` is the shot or asset folder name, spelled as on disk.
- `--doing` is one plain line a teammate can read: "Key light notes on the hero", not a step count and not the prompt.
- A session shows on one shot and task at a time. A new `set` replaces the old one.

## What it writes

One small JSON file per session in `<job>/Production/Common/Agents/Activity/`: person, machine, agent, job, shot, task, the `doing` line, the state and two times. No prompt text, no file contents, no paths.

## Rules

- Never put client-sensitive detail, a name the artist didn't give, or anything from the chat in `--doing` beyond what is being done to the shot.
- If the script says `NOT ASSESSED` (the job has no `Agents` folder, or the server is out of reach), carry on with the task. Reporting never blocks work.
- In Claude Code with the plugin installed, the state moves by itself: a new message from the artist sets `working`, the end of a turn sets `idle`, a permission prompt sets `waiting`, closing the session clears it. You still call `set` once per shot, and `state waiting` or `state farm` when that is the truth at the end of your turn. In any other agent, set every state yourself.
