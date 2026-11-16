# Buck: working notes for AI agents

Version: 2026-11-15.2

You are an AI agent helping a Buck artist on their workstation. Buck is a motion design and animation studio. This file holds what is true on every job: where work lives, what you may do without asking, and what record to leave. Procedures live in skills, listed at the end; read a skill when its task comes up. Follow this file over your own defaults.

Lines marked `TODO(Workflow)` are not confirmed yet. When you reach one, tell the artist and ask before acting on it.

## For artists

Keep Buck5 running and start your agent.

- **Claude, with the plugin installed:** just say what you need. The first time on a machine it runs a two-minute setup (`buck-start`); after that it picks up your job by itself.
- **Codex, or no plugin:** paste this as your first message:

```
Read \\buck\work\current\<JOB>\Production\Common\Agents\BUCK_AGENT_STARTER.md and follow it. I'm <username>. Today: <shot or asset>, <task>.
```

The agent saves new versions next to yours, never overwrites a file, leaves a `.trail` note beside each version, tells you before a full-range farm submit, and asks before deleting or publishing.

## The files

`Agents/` is `\\buck\work\current\<JOB>\Production\Common\Agents\`.

| File | Holds |
| --- | --- |
| `Agents/BUCK_AGENT_STARTER.md` (this file) | Rules for every job. |
| `Agents/SHOW.md` | This job's facts: software versions, colour, shots and task ids, and what the team has learned. |
| `Agents/Artists/<username>/ARTIST.md` | One artist's name, version suffix and preferences. |
| `Agents/Skills/buck-<group>-<task>/SKILL.md` | How to do one kind of task. Listed at the end of this file and in `INDEX_lighting.md` and `INDEX_modeling.md`. |

The show and artist files add facts and preferences. On permissions they can only make a rule stricter, never looser. Skills describe a task; they never grant permission. If the job has no `Agents` folder or no `SHOW.md`, say so and use `buck-pipeline-setup`.

Keeping these files short: a line goes in this file only if an agent got something wrong without it and it is true on every job. A job's facts go in `SHOW.md`, a procedure goes in a skill, and a line that no longer changes what an agent does comes out. Change the version at the top with every edit: the date, plus `.2`, `.3` for further edits the same day.

## Start of every session

Work these out yourself before asking the artist anything:

| Item | Where to read it |
| --- | --- |
| Username, machine, site | The operating system and host name. |
| Job, software versions, colour | `SHOW.md`; Aquarium if `SHOW.md` lacks it (`buck-pipeline-aquarium`). |
| Shots, tasks and task ids | `SHOW.md`, then Aquarium. |
| Shot sources (animation, layout, camera, lookdev) | The latest files in the shot's and assets' department folders. Tell the artist which versions you picked. |
| Frame range, resolution, shot camera | The source animation or layout file, and the deliverables in `SHOW.md`. |
| Styleframes | `Production/Design/Styleframe/` in the job. If it is empty, ask. |
| Where the shot stands | The newest file in the work folder and its `.trail`. |
| Suffix, preferences | The artist's `ARTIST.md`. If there is none, run `buck-start`, which creates it. |
| Local scratch folder | `D:\Agents\<agent>\<job folder name>\`, where `<agent>` is your name without spaces (`ClaudeCode`, `Codex`). Create it if missing. Use another folder only if `ARTIST.md` names one; if there is no `D:` drive, ask. |
| What the task should deliver | The skills for the task. Read every one the request needs. |

Ask the artist only for what is still missing, in one message. Then restate the task in one or two sentences, name the files you expect to write, and start.

## Where work lives

| What | Path (Windows) |
| --- | --- |
| Active jobs | `\\buck\work\current\<JOB>\` |
| A job's production tree | `\\buck\work\current\<JOB>\Production\` |
| Studio OCIO configs | `\\buck\globalprefs\SHARED\OCIO\<config>\config.ocio` |

```
Production/shots/<Sequence>/<Shot>/
    Animation/maya/{work,publish,render/playblasts}
    Layout/maya/{work,publish}
    Lighting/maya/work/                   <Shot>_lgt_vNNN.mb  (+ .trail)
    Lighting/maya/render/<Scene>/<Layer>/<Layer>.####.exr
    Comp/nuke/work/                       <Shot>_comp_vNNN.nk  (+ .trail)
Production/Assets/<Category>/<asset>/
    Modeling/maya/{work,publish}          <asset>_mdl_vNNN.mb
    Rigging/maya/{work,publish,data}      <asset>_rig_vNNN.mb
    Lookdev/maya/work                     <asset>_lkdv_vNNN.mb
Production/MAYA/sourceimages/<username>/<asset name>/     all textures and source images
Production/Work/<artist>/                                 personal working space
In/                                                       client material, read only
```

- `\\buck` is a DFS namespace; the same shares also appear under server names such as `\\hsfs-laxdc\...`. Treat them as one location. Mac mount points: `TODO(Workflow)`.
- Job folders are named `<CLIENT>_<PROJECT>_<CODE>`. If more than one folder matches the name the artist gave, ask.
- The network is slow: every file check takes 20 to 100 ms. List a folder once and work from the listing. Search only inside the job, never from a share root.
- `work` is where artists save iterations. `publish` is what other departments consume; the artist publishes through Buck5.
- All textures and source images go in `Production/MAYA/sourceimages/<username>/<asset name>/`, never in a shot or department folder.
- Other applications follow the same `<Department>/<app>/{work,publish}` pattern: `TODO(Workflow)` confirm per app.

### Naming and versions

- Files are named `<Shot or asset>_<task>_v###.<ext>`: `SH010_lgt_v010.mb`, `prop_tower_rig_v003.mb`. Task codes: `mdl`, `rig`, `lkdv`, `anim`, `lgt`, `comp`. Versions are always three digits; "v01" in a request means `v001`.
- Save to the next free version number, through `save_version.py` in `buck-pipeline-trail`: it cannot overwrite a file. If you must save another way, check that the target doesn't exist immediately before saving.
- Work from the latest version in the work folder, even if someone else saved it; coworkers re-save mid-round. Read its `.trail` and tell the artist who saved it and what changed.
- If someone else is versioning the same file in parallel, add the suffix from `ARTIST.md` (`lgt_v023_<suffix>`).
- Agent-made versions go in the same work folder as everyone else's. The `.trail` says who made them.
- If the task folders for a shot are missing, ask the artist to generate them through Buck5. Don't create them yourself.
- Render output goes to the task's `maya/render/` folder, then `<Scene>/<Layer>/`. To version a render, version the file name.

## What you may do

Hard limits first, then three tiers. An action none of them covers counts as "Always ask". These are instructions, not locks: nothing stops a wrong save except you checking first.

### Never

- Write into `\\buck\GlobalPrefs\`, the package repository, or shared code repos.
- Write passwords, tokens or licence details into any file, script, trail or job comment.
- Open a file in a newer application version than the show uses, or open a Maya file with `ignoreVersion`. If a file was saved in a newer version, stop and tell the artist.

### Always ask: wait for a clear yes

- Deleting anything on the server, including renders that look broken. List the exact files first.
- Overwriting any existing server file. (A farm render replacing that same version's own test frames is not an overwrite.)
- Writing files for a shot or asset the artist did not name.
- Publishing, or writing into a `publish` folder.
- Opening, listing or copying another job.
- Sending files, frames or client material to an external tool that `SHOW.md` does not list as approved. Client work is confidential, and approval on one job does not carry to another.
- Starting a render or a simulation on the artist's workstation.
- Requeueing, resubmitting or changing someone else's farm job.
- Creating, changing or deleting anything in Aquarium.

An ask names the exact action, the exact files or paths, and what cannot be undone, and offers the choices as a multiple-choice question. A yes covers that one action, not the next one like it.

### Tell: say what you are about to do, then do it

- Submit a full-range render or comp to the farm. State the scene, layers, frame range and machines.
- Install or update the `buck-*` skills on the artist's machine.
- Build on a version someone else saved since the artist last looked.
- Change something outside the request because the request cannot work without it.
- Edit `SHOW.md`.

### Free: do it, record it in the trail

- Read anything inside the job.
- Save a new version of the file you were asked to work on, with its `.trail`.
- Write anything in the local scratch folder.
- Run an application headless in the job's Buck5 environment (`buck-pipeline-launch`), after checking free RAM.
- Submit test renders to the farm (`buck-pipeline-farm`). Tell the artist before releasing the first farm job on a show.
- Make preview images, viewport captures and comparisons.

### What goes on the server

One file: the versioned deliverable (`.mb`, `.ma`, `.nk`, ...), plus its `.trail`.

- Build scripts, test scenes, Blender files, logs, scratch renders, review images and other working files stay in the local scratch folder. Models are built in Blender and delivered as Maya files (`buck-modeling`). Never save a working folder next to the deliverable.
- The exceptions are textures in the sourceimages folder above, and render output written by the farm.
- If a task seems to need any other file on the server, ask first.

### Changing files

- Change exactly what the artist asked for. Put any extra idea in a separate, labelled variant and describe it in one line.
- Keep the file's existing settings (frame range, resolution, camera, colour config, render settings) unless the task is to change them.
- Open files the way the artist would, with references loaded or unloaded as saved. Unloaded references are often unloaded on purpose.
- Always use absolute paths when saving or exporting. Relative paths in Maya silently land in `Documents/maya/projects/default/`.
- Fix a problem where it comes from (the texture, the asset, the light), not with a patch further down the pipeline.

### The artist's machine

- Check free disk space and RAM before heavy work. Local C: drives are often near full, and a full drive truncates saves silently.
- The artist may have a large session open. Don't stack a heavy job on top of it.
- Leave the artist's application preferences alone, and close any session you started.

## The version record

Every version you save gets a `.trail` file next to it with the same name (`SH010_lgt_v010.mb`, `SH010_lgt_v010.trail`). It says what the version is, what changed, what was checked and what was not, so the next artist or agent doesn't need the chat history. Every check in it is marked pass, fail or not assessed; a check you could not run is "not assessed", never a pass. Write it when you save the version, using `buck-pipeline-trail` for the format.

## Say what you're on

The team sees who is on which shot on the job's dashboard. When you start work on a shot or asset, report it with `status.py` in `buck-pipeline-status`: the shot, the task and one line on what you are doing. Mark yourself waiting when you need the artist or a farm render, and report the outcome when the task is done. The line has a fixed form per state (`Adjusting ...`, `Need <name>'s input`, `Rendering ...`, `Saved ...`); the script refuses anything else and says why. It writes one small file in the job's `Agents/Activity` folder and nothing from the chat. If it can't report, carry on.

## Showing work to the artist

- Post review images in the chat as you go, not only at the end.
- Make previews through the job's own OCIO config and view (named in `SHOW.md`), never an approximate tonemap. Keep a file's colour config as you found it.
- For animation and model approvals, show viewport captures (`maya_review_capture.py` in `buck-pipeline-launch`: the same fixed views every time). For lighting, show farm test frames.
- Side-by-sides compare the artist's original against your version, labelled, with frame numbers, in the same colour view.
- If a styleframe is provided, check your result against it, in the same colour view, before reporting for the artist's review.
- Test on a frame that represents the shot, and judge small details at final resolution.
- Call something an exact match only if you measured it.
- Report problems you notice but weren't asked to fix in one line, and list them in the trail. Don't fix them unasked.

## Traps

Each of these has cost real work.

- A command that ran without an error proves nothing. Reopen the saved file, or open the rendered frame, and look.
- A check that found nothing to check (no frames, an empty selection) has not passed.
- An animation movie or cache can run past the shot. Take the frame range from the layout or lighting file and `SHOW.md`.
- A farm job copied from someone else keeps their name, machine and output paths.
- Preview settings left in a saved scene render as finals. Put test reductions on the farm job, never in the scene.
- Windows shells mangle `\\buck` paths inside inline scripts. Write the script to a file and pass paths as arguments.

## Who to ask

- The artist first, for anything about their shot, task or preferences. Ask decisions as multiple-choice questions.
- Workflow department for launching, environment, storage, farm and tool problems: `TODO(Workflow)` add channel or ticket route.

## Skills

Each is a folder in `Agents/Skills/` with a `SKILL.md`. Read the ones the task needs. The pipeline skills carry tested scripts in a `scripts` folder; use the script instead of rebuilding its steps by hand.

| Skill | Read it when you need to |
| --- | --- |
| `buck-pipeline-launch` | Run Maya, Nuke or another application, headless or in batch, in the job's Buck5 environment. |
| `buck-pipeline-aquarium` | Look up a job's software, colour, shots, tasks or task ids. |
| `buck-pipeline-farm` | Submit a test or full-range render to the farm and check the result. |
| `buck-pipeline-trail` | Write or update a version's `.trail`. |
| `buck-pipeline-status` | Report which shot and task this session is on, and its state. |
| `buck-pipeline-setup` | Set up the `Agents` folder on a new job, create or refresh `SHOW.md`, or install the skills. |
| `buck-start` | Welcome an artist on their first session: confirm who and which job, check the workstation, brief them. |
| `buck-lighting` | Do any lighting or lookdev task, from first pass to final. It picks the `buck-lighting-*` procedure the request needs. |
| `buck-modeling` | Do any modeling task, from first blockout to final. It picks the `buck-modeling-*` procedure the request needs. |
