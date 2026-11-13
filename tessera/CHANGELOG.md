# Changelog

One entry per release. Newest first. Say what an agent will now do differently.

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
