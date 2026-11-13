---
name: pipeline-aquarium
description: Reads a Buck job's facts from Aquarium (the production tracker) through Buck5's local API - project id, software and launcher entries, colour management, sequences, shots, tasks and task ids, deliverables. Use when SHOW.md lacks a fact, when a farm job needs a task id, or when checking whether a shot or task exists. Read-only. Not for changing anything in Aquarium, and not for writing SHOW.md (buck3d:pipeline-setup).
---

# Look up job facts in Aquarium

Aquarium is the source of truth for a job's software versions, colour management, sequences, shots and tasks. While Buck5 is running it serves a local API that already carries the artist's login.

## Script in this skill

`scripts/aquarium.py`, next to this file, does the connecting and can only read: it refuses any request that would change Aquarium. Run it with any Python 3.7 or newer (`c:\opt\rez\Scripts\python.exe` is on every Buck workstation). Set `BUCK_AGENT_NAME` to your agent's name first.

| Command | Gives |
| --- | --- |
| `aquarium.py status` | Whether Buck5's API answers, and its address. |
| `aquarium.py resolve "<file path>"` | The project, sequence, shot and task a path belongs to, with ids. Exit code 3 if the task has no id yet. |
| `aquarium.py project <JOB> --out <scratch file>` | The job's software, colour management, wiki, sequences, shots and tasks as one JSON, with a `not_assessed` list of anything it could not read. |
| `aquarium.py get <endpoint>` | Any other read, for example `get /projects/<id>/software`. |

Ran against Buck5 on 2026-11-13. The sections below describe the API itself, for anything the script does not cover.

## Connect

- Base address: `BUCK5_DAEMON_HOST` in the newest Buck5 `.env` (`%LOCALAPPDATA%\buck\Buck5\rez\buck_<uuid>.env`), or the latest "Proxy listening on <port>" line in `%LOCALAPPDATA%\buck\Buck5\logs\Buck5.log` (`http://localhost:<port>`). The port changes each time Buck5 starts.
- Send the headers `X-BUCK-APP: <your agent's name>` and `X-BUCK-OS: windows` (or `macos`, `linux`).
- Check `GET /status` answers before anything else. If it doesn't, ask the artist to open Buck5.
- The API adds the artist's login itself. Never read, copy or print the artist's access token.

## Read

`GET /openapi.json` lists every endpoint. The useful ones:

| Call | Gives |
| --- | --- |
| `/projects` | All projects. Match `data.name` to the job folder name; `_key` is the project id. |
| `/projects/<id>/wiki` | Brief, crew, deliverables, resources. |
| `/projects/<id>/software` | Launcher entries, their ids (`_key`), rez package, addon packages (renderer and plugin versions). |
| `/projects/<id>/colormanagement` | Colour management name, package, rendering space, view. |
| `/projects/<id>/sequences`, `/sequences/<id>/shots`, `/shots/<id>/tasks` | Sequences, shots, tasks and their ids. |
| `/projects/<id>/libraries`, `/libraries/<id>/assets` | Asset libraries and assets. |

To learn what a file path belongs to, send `{"inputPath": "<file path>"}` to `POST /templates/resolve`. It returns the project, sequence, shot and task with their ids. A task that comes back as plain text instead of an object with an id does not exist in Aquarium yet: ask the artist to create it in Buck5.

## Limits

- `GET` only, plus `POST /templates/parse` and `POST /templates/resolve`, which only read a path. The same API can create and delete projects, shots and tasks; any write to Aquarium is "Always ask".
- `/projects/<id>/team` and `/projects/<id>/presets` return an error without extra parameters, and `/folder-structure` is missing on new jobs. Skip them.
- The job's `Production/Common/Meta/project.json` on disk can be an untouched studio template. Don't read software versions from it.
- When `SHOW.md` and Aquarium disagree, Aquarium wins. Tell the artist, then correct `SHOW.md`.
- Save pulled data in local scratch, not on the server.

## Where the scripts are

This skill's folder is `${CLAUDE_SKILL_DIR}`; its scripts are in `${CLAUDE_SKILL_DIR}/scripts/`.
