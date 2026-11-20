---
name: buck-pipeline-trail
description: Writes and updates the .trail record that sits next to every versioned Buck work file (.mb, .ma, .nk) - what the version is, what changed, each check and its result, farm jobs and review outcome. Use whenever saving a new version, submitting it to the farm, recording a review result, or reading what a coworker's version contains. Not for the farm submission itself (buck-pipeline-farm).
---

# Write a version's `.trail`

Every version you save gets a trail file next to it with the same name:

```
SH010_lgt_v010.mb
SH010_lgt_v010.trail
```

A `.trail` is a text file: a short YAML header, then markdown notes. It is how the next artist or agent learns what this version is without reading a chat history.

## Scripts in this skill

Use these to save a version and start its trail. They are in the `scripts` folder next to this file; run them with any Python 3.7 or newer (`c:\opt\rez\Scripts\python.exe` is on every Buck workstation).

| Script | Does |
| --- | --- |
| `save_version.py --next <work folder> <Shot>_<task> <ext>` (for example `... SH010_comp nk`) | Prints the next free version path, counting every existing version and suffix. |
| `save_version.py <local file> <destination path>` | Copies a file built in scratch (a `.nk`, an exported `.ma`) to the server. It cannot overwrite: the copy fails if anything is already at that path. It also refuses a `publish` folder, GlobalPrefs, a missing folder and a name without `_v###`, and verifies the copy by hash. |
| `save_version.save_maya(<destination path>, <scratch>)` | The same for the scene open in mayapy: saves to scratch, copies to the server, verifies, and points the session at the server file. Add the `scripts` folder to `sys.path` and `import save_version`. |
| `trail.py new --file <scene> --agent "<agent>" --app "<app and version>"` | Writes the trail skeleton next to the scene, with the header filled from the file name. Refuses if a trail is already there. Then edit the file: replace every `TODO` line under Request, Changes, Checks and the two lists after them, and fill the header fields the script cannot know (`source`, `upstream`, `checks`, `renders`, and `job` if it came out empty). |
| `trail.py job --file <scene> --id <job id> --kind test\|full --layers <names> --frames <range>` | Appends a farm job to the header and to Events. |
| `trail.py event --file <scene> --text "<what happened>"` | Appends a dated line to Events. |
| `trail.py check --file <scene>` | Fails if a `TODO` placeholder is left, a check has no result, or `job`, `source`, `app` or `scripts` is empty. Run it before reporting to the artist. |

Save a version on the server only when the artist tells you to (the starter's versioning rule); until then save locally as you see fit, and never ask, offer or suggest it. Always save versions through `save_version`; it is the only thing that actually stops an overwrite. All of these ran on 2026-11-13, `save_maya` on Maya 2026.3.

## Rules

- Write the trail when you save the version. It replaces the change list you would otherwise give in chat; still summarise it for the artist.
- Update the current version's trail as things happen to it: farm jobs, review outcome, status.
- On an older version's trail, only append to `farm_jobs` and `## Events`. Its history stays as written.
- Every check gets one of three results: `pass`, `fail` or `not assessed`. A check you could not run, or that ran on nothing (no frames found, an empty selection, a script that exited without output), is `not assessed` with the reason. Never write it as a pass, and never leave a planned check out.
- Record what you did not do or could not verify as plainly as what you did.
- Read versions from the application itself (`cmds.about(version=True)`, the loaded V-Ray plugin's version, `nuke.NUKE_VERSION_STRING`), not from `SHOW.md`. If they differ from `SHOW.md`, say so.
- Scripts used to build the version stay in local scratch, in a folder named after the scene. The trail records that path and the machine, and describes the method well enough to redo it without the scripts.
- `review` changes only when the artist answers. Write their words in `## Events`.
- Older trails say `trail: 1` and lack `app`, `renderer`, `review` and `checks`. Read them as they are; don't rewrite them.
- Human-made versions may have no trail yet. Note that in `source` and carry on. Write a trail for someone else's version only when asked.

## Format

```
---
trail: 2                          # format version
file: <Shot>_<task>_v###.<ext>
job: <JOB>
shot: <Shot or asset>
task: <mdl | rig | lkdv | anim | lgt | comp>
version: <###>
date: <YYYY-MM-DD HH:MM>
artist: <username>
made_by: <agent | human>
agent: <Claude Code | Codex | ...>     # leave empty when made_by is human
app: <application and version it was saved in, for example Maya 2026.3>
renderer: <renderer and version, for example V-Ray 7.40.04>   # leave empty if none
source: <file this version was built from, and who saved it>
status: <wip | for_review | approved | rendered | superseded>
review: <not shown | shown | approved | changes asked | rejected>   # the artist's answer, not your opinion
notes_addressed: []               # note ids or short quotes
upstream:                         # what this file consumes
  - kind: <anim | layout | camera | cache | mdl | rig | lkdv | template | render | other>
    file: <file name with its version>
checks:                           # one line per check, the same list as "## Checks"
  - name: <what was checked>
    result: <pass | fail | not assessed>
farm_jobs:
  - id: <Deadline job id>
    kind: <test | full>
    layers: <layer names>
    frames: <range>
    result: <pending | complete | failed | partial>
renders: <output folder>
scripts: <machine>:<local scratch path>   # working files stay local, never on the server
---

## Request

What the artist asked for, in their words where possible.

## Changes

One line per change: what, where in the scene, and which note it answers.

-

## Checks

One line per check: the result (pass, fail or not assessed), then how it was checked (frames looked at, measurements, comparisons) or why it could not be.

- <pass | fail | not assessed> <check> - <how, or why not>

## Not done / not verified

Anything asked for that isn't in this version, and anything that wasn't checked.

-

## Flagged, not fixed

Problems noticed outside the request.

-

## Events

Appended over the version's life: submissions, review outcomes, status changes. Newest last.

- <YYYY-MM-DD HH:MM> <who> <what happened>
```
