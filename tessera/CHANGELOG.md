# Changelog

One entry per release. Newest first. Say what an agent will now do differently.

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
