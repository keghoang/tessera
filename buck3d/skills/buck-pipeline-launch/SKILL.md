---
name: buck-pipeline-launch
description: Runs Maya, Nuke and other Buck applications headless or in batch inside the job's Buck5 (rez) environment on a Windows workstation. Use whenever a task needs to open, build, save or render a scene from a script, or when an application reports a missing licence, plugin or colour config. Not for farm submission (buck-pipeline-farm).
---

# Launch an application in the Buck5 environment

Buck launches every application through Buck5, which resolves the software versions, plugins and environment for the job using rez. An application started any other way (Start menu, a bare `.exe`) is missing the job's tools, colour config and licences and produces wrong results.

Use the application version in `SHOW.md`. Shows stay on one version for their whole life.

## Default: run it yourself, headless

Run the application without a window inside the job's Buck5 environment. Opening, building and saving a scene this way is normal work. Check free RAM first and don't stack it on a large session the artist has open. Use the artist's own open session only when they ask.

## Scripts in this skill

Use these instead of rebuilding the steps by hand. They are in the `scripts` folder next to this file. Run them with any Python 3.7 or newer; every Buck workstation has one at `c:\opt\rez\Scripts\python.exe`.

A full command looks like:

```
c:\opt\rez\Scripts\python.exe <this skill's folder>\scripts\buck5_context.py run --job <JOB> --software <launcher id> --scratch <scratch> -- mayapy <script.py> <args>
```

| Script | Does |
| --- | --- |
| `buck5_context.py find --job <JOB> --software <launcher id> --scratch <scratch>` | Copies the newest matching Buck5 context into `<scratch>/buck5_context/` and prints its `.rxt` and `.env` paths. |
| `buck5_context.py run --job <JOB> --software <launcher id> --scratch <scratch> -- <command>` | Runs a command inside that context, for example `-- mayapy script.py`. Returns the command's exit code. |
| `mayapy maya_scene_info.py --scene <scene>` | Prints the scene's Maya and renderer versions, frame range, resolution, renderable cameras, render layers, OCIO config and references as JSON, between `SCENE_INFO_BEGIN` and `SCENE_INFO_END`. Use it for a farm job's camera, size and layers and for the trail's `app` and `renderer`. Run it through `buck5_context.py run`. |
| `mayapy maya_review_capture.py --scene <scene> --out <scratch folder>` | Viewport captures from fixed views (three-quarter, front, side, top, and `--camera <shot camera>`), with a `manifest.json` marking each capture pass or not assessed. `--look grey` gives a plain grey model look. Run it through `buck5_context.py run`. |

All four ran on Maya 2026.3 on 2026-11-13, on a small test scene; `maya_scene_info.py` has not been run on a V-Ray scene yet. An exit code of 3 means "not assessed": something needed was missing, and the message says what.

- mayapy in Maya 2026 prints a crash stack trace as it exits, after the script has finished. Judge a run by the script's own printed result and exit code, not by that trace.
- The captures are PNGs with a transparent background. Put them over a flat grey before comparing or posting.
- The address in a copied `.env` (`BUCK5_DAEMON_HOST`) goes stale when Buck5 restarts. For Buck5's API, take the live address from `aquarium.py status` (`buck-pipeline-aquarium`).
- The capture script opens the scene and never saves it. It is a viewport look, not a render.

## Get a Buck5 context by hand

`buck5_context.py` does the steps below. They are here for when it cannot (another operating system, a changed Buck5).

Each Buck5 launch writes two files to `%LOCALAPPDATA%\buck\Buck5\rez\`:

- `b5_rez_<uuid>.rxt`: the resolved rez context;
- `buck_<uuid>.env`: a JSON with `BUCK_PROJECT`, `BUCK_PROJECT_ID`, `BUCK_SOFTWARE_ID` and `BUCK5_DAEMON_HOST`.

1. Look in the scratch folder for a context you already copied for this job and application. Reuse it.
2. If there is none, find the newest `.env` whose `BUCK_PROJECT` matches the job and whose `BUCK_SOFTWARE_ID` is the launcher entry you need (the ids are in `SHOW.md`), and its matching `.rxt`. If none matches, ask the artist to launch that entry once from Buck5.
3. Copy both into the scratch folder, named by job and application. Buck5 cleans up its own copies.
4. Set the three `BUCK_*` variables from the `.env`, then run through `rez-env`:

```bat
set BUCK_PROJECT=<from .env>
set BUCK_PROJECT_ID=<from .env>
set BUCK_SOFTWARE_ID=<from .env>
c:\opt\rez\Scripts\rez\rez-env.exe --input <copied .rxt> -- <command>
```

- `rez-env` on Windows runs through `cmd`. A `|` in an argument breaks it; Maya DAG paths start with one, so strip it.
- One context per application and per job. A Maya context won't run Nuke.

## Maya (verified)

```bat
rez-env.exe --input <maya .rxt> -- mayapy script.py
rez-env.exe --input <maya .rxt> -- Render -r vray -s <start> -e <end> -rd <dir> scene.mb
rez-env.exe --input <maya .rxt> -- maya -script x.mel        (GUI test; set MAYA_APP_DIR to scratch)
```

- Set `MAYA_DEBUG_NO_SAVE_ON_CRASH=1`, or crashed sessions leave `.ma` files in `%TEMP%`.
- Keep whatever the context sets for render layers (`MAYA_ENABLE_LEGACY_RENDER_LAYERS`).
- Don't name a Python script after a standard library module (`inspect.py`, `json.py`). mayapy imports it on startup and crashes.
- Don't save a session you used for heavy API queries on referenced meshes. The queries are written as reference edits and bloat the file.
- For a test session, point `MAYA_APP_DIR` at scratch so the artist's preferences stay untouched.
- A local `Render` is a render on the artist's workstation: "Always ask". Renders normally go to the farm.

## Nuke (verified)

```bat
rez-env.exe --input <nuke .rxt> -- "<Nuke install>/Nuke<version>.exe" -t script.py <args>
```

- Nuke only gets a licence inside the Buck5 environment. "A license for nuke was not found" means it was launched outside it.
- `-t` treats trailing numbers as a frame range. Pass frames as strings (`f1100`, `frames=950_1050`).
- Edit `.nk` scripts as text and splice in new nodes. Saving from terminal Nuke silently drops layout, Buck write-node internals and plugin settings.
- Before editing, check whether the artist saved a newer version from the GUI.
- Use forward slashes in Read and Write node paths.
- After versioning a `.nk` by editing it as text, search it for the old version string: the Buck5 submit can bake literal output paths into it.

## Other applications

`TODO(Workflow)`: none of these is confirmed. Ask the artist before relying on them.

- Houdini: `hython` inside the Buck5 context. Confirm the licence type before batch work.
- Cinema 4D: `Commandline.exe` inside the Buck5 context.
- After Effects: `aerender`.
- Premiere: no headless mode. Work only in a session the artist opened.
- Blender: `blender -b`.

## Windows shell traps

- Create folders on network shares before copying into them. In Git Bash, copying onto a UNC folder that doesn't exist creates a file with the folder's name.
- Bash mangles `\\buck\...` paths. Write paths with forward slashes (`//buck/work/...`), or use PowerShell.
- Write job files and scripts without a byte-order mark.
- PowerShell 5.1 drops empty-string arguments to programs. Pass a placeholder value instead.
- PowerShell variable names are case-insensitive: `$s` and `$S` are the same variable.

## Where the scripts are

This skill's folder is `${CLAUDE_SKILL_DIR}`; its scripts are in `${CLAUDE_SKILL_DIR}/scripts/`.
