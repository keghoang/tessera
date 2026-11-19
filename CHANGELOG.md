# Changelog

One entry per release. Newest first. Say what an agent will now do differently.

## 0.16.0 (2026-11-19)

- Modeling now starts from a short design document (new skill `buck-modeling-design-doc`): references first, real dimensions, parts in build order, comparison cameras, budgets and an acceptance checklist. It decides instead of asking: at most three open questions, each with a default the agent carries on with.
- A Blender-built model is built from a script that can rebuild it, boxes first and then one part at a time, with cameras and review light set before any detail and a comparison sheet against the reference after every stage.
- The agent no longer passes its own work. New skill `buck-modeling-inspect` and a read-only `model-inspector` sub-agent check the model against the design document: measured checks by script first (sizes, overlaps, floating parts, counts, names), then the fewest images needed. An item that couldn't be confirmed is never a pass.
- When a correction points at the procedure, the agent proposes the change to the skill instead of only remembering it.

## 0.15.0 (2026-11-15)

- Reporting to the dashboard is now the first step of every task: the agent reports the shot or asset, the task and what it is about to do before it opens a file, launches an application or submits anything, and again at the start of every later request.
- In Claude Code, every message from the artist now carries a note with what the session currently reports and the command to correct it, so a line left over from the last request gets replaced before work starts.
- Starter `2026-11-15.5`.

## 0.14.1 (2026-11-15)

- Versioning without stop-and-go: the agent saves locally as it sees fit, with no permission and no question. A version goes on the server only when the artist says "save" or "version up", or asks for something that needs one (a full-range render, a handoff). The agent no longer proposes a save or waits for one; it adds one line that the work is saved locally and carries on.
- Starter `2026-11-15.4`.

## 0.14.0 (2026-11-15)

- Saving a version on the server now needs the artist's go-ahead. The agent works in a local copy, shows the result, then proposes the version name and what is in it. "Save" or "version up" in the request counts as the go-ahead, for one version. One version per request; refinement rounds and experiments stay local.
- Farm tests no longer need a version: the working scene is copied to the artist's own folder under `Production/Work/.../agent_tests/<Shot>/` and its frames render beside it. `farm_submit.py` accepts such a scene with `--kind test` only.
- Model review captures come from the local working scene; the Maya file goes on the server after the go-ahead.
- Starter `2026-11-15.3`.

## 0.13.0 (2026-11-15)

- Modeling: new models are built in Blender through the Blender connection and delivered as Maya files. The Blender file stays in the local scratch folder. An asset that already lives in Maya stays in Maya.
- New procedure `modeling-to-maya`: moving a Blender model into Maya, with checks for scale, axes, names, hierarchy, transforms, pivots, faces, normals, UVs and materials. Not yet production-tested.
- The first-session check has a required Blender row: the Claude-side connection, Blender itself and Blender's MCP add-on.
- Starter `2026-11-15.2`.

## 0.12.1 (2026-11-15)

- The bar is production quality at every stage. A first pass or a blockout is the first step, not a rougher standard; a rough happens only on request.
- Self-refinement is built in: before showing anything, the agent looks at images of its result, compares them with the target, lists the gaps, fixes them and repeats, up to three rounds. It then reports what it fixed and what still falls short.
- "Model this asset" now means a finished model: blockout, refined and posted as progress, then production detail without waiting, unless a blockout only was asked for or the forms need the artist's decision.

## 0.12.0 (2026-11-15)

- Two front doors: `lighting` and `modeling`. Each takes any request in its discipline, from first pass to final: it finds where the shot or asset stands, reads the procedure the request needs, and names the usual next step when one finishes.
- The 30 detailed lighting and modeling skills are now procedures behind those doors. The agent still loads them; the `/tessera:` menu no longer lists them.
- `lighting-v01` and `modeling-v01` are renamed `lighting-first-pass` and `modeling-first-pass`. A first pass is a step, not the finish.
- The first-session briefing shows `/tessera:lighting` and `/tessera:modeling` as its examples.
- Starter `2026-11-15.1`.

## 0.11.1 (2026-11-15)

- The welcome also shows the artist's site, read from `BUCK_LOCATION` in the environment Buck5 built for its latest launch. The line is left out if it can't be read.

## 0.11.0 (2026-11-14)

- New skill `start`: an artist's first session on a machine. A welcome that confirms the username, machine and job it picked up, a five-row workstation check, and a fixed briefing on the skills and how the assistant works. The words come from `start.py`, so they are the same for everyone. It creates the artist's `ARTIST.md` if there is none and runs once per machine.
- New session-start hook: with no setup on the machine it points the agent at `start`; otherwise it names the artist's last job and its starter, so the paste-this-first message is no longer needed with the plugin.
- Starter `2026-11-14.1`.

## 0.10.3 (2026-11-13)

- A waiting line now reads `Need <name>'s input`, optionally followed by `: <what is needed>`.
- Starter `2026-11-13.7`.

## 0.10.2 (2026-11-13)

- A waiting line now reads `Waiting for <name>'s input`, optionally followed by `: <what is needed>`. It no longer starts with `Needs`.
- A working line can't start with `Waiting`.
- Starter `2026-11-13.6`.

## 0.10.1 (2026-11-13)

- The status line has a fixed form per state: working starts with an -ing verb, waiting with `Needs`, farm with `Rendering`, idle with `Saved` or `Finished`. One line, 72 characters, no paths, no first person, no step counts, no vague verbs. `status.py` refuses a line that breaks it and says which rule.
- `status.py state` now requires `--doing`.
- Starter `2026-11-13.5`.

## 0.10.0 (2026-11-13)

- New skill `pipeline-status`: a session reports which shot and task it is on, and whether it is working, waiting on the artist, waiting on the farm or idle. One small file per session in the job's `Agents/Activity` folder, read by the dashboard.
- The plugin now has hooks: a new message sets the session to working, the end of a turn to idle, a permission prompt to waiting, and closing the session clears it.
- Starter `2026-11-13.4`: tells the agent to report what it is on.

## 0.9.3 (2026-11-13)

- Skill descriptions in the plugin are one short line. The "use when" and "not for" text moved to `when_to_use`, which the agent still reads when choosing a skill.

## 0.9.2 (2026-11-13)

- The plugin goes by the code name `tessera` (marketplace `tessera-hub`). Skills show as `tessera:lighting-notes`.
- The studio name is out of the plugin's name, descriptions, author and every skill description.

## 0.9.1 (2026-11-13)

- Skills in the plugin drop the `buck-` prefix: `buck3d:lighting-notes`, `buck3d:pipeline-farm`. References between skills use the same form.
- First version installed on a workstation.

## 0.9.0 (2026-11-13)

First packaged release. Not yet installed on any workstation as a plugin.

- Starter `2026-11-13.3`: hard limits come first (Never, Always ask, Tell, Free), what an ask must contain, a Traps section, a rule for keeping the file short.
- All 35 skill descriptions rewritten: what the skill does, when to use it, and which neighbouring skill to use instead.
- Every check is now marked pass, fail or not assessed. A check that could not run is never a pass.
- `.trail` format 2: application and renderer versions, typed upstream entries, a checks list, a `review` field.
- Farm jobs carry `BUCK_AGENT`, `BUCK_TRAIL` and `BUCK_JOB_KIND` tags.
- Scripts inside the pipeline skills: `buck5_context.py`, `maya_scene_info.py`, `maya_review_capture.py`, `aquarium.py`, `save_version.py`, `trail.py`, `farm_submit.py`.
- Scenario tests: 30 situations, 3 runs each, in `tests/`.
