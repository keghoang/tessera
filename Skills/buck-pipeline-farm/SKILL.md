---
name: buck-pipeline-farm
description: Submits Maya V-Ray render jobs to the Buck Deadline farm from the command line and checks the result - test frames or a full range, written as job files with no earlier job to copy. Use when job files need writing or submitting, when a farm job failed, errored or rendered in the wrong environment, or when requeueing frames. An artist's request for test frames starts at buck-lighting-previews and for a final render at buck-lighting-render; they call this skill. Not for running Maya locally (buck-pipeline-launch) or for a render that finished but looks wrong (buck-lighting-diagnose).
---

# Submit to the farm (Deadline)

Renders go to the farm, not the artist's workstation. Only files saved on the server can be submitted.

## Before you submit

- **Test renders are free; a full range is "tell, then submit".** For a full range, state the scene, layers, frame range and machines (pool and group, or a machine list). Tell the artist before releasing the first farm job on a show.
- **Tests use the scene's own resolution and quality.** If render time is too high, offer the artist a choice: 25%, 50% or 75% resolution, or reduced sampling. None of these is the default.
- **Reduced settings go on the farm job, never in the saved scene.** Resolution is `ImageWidth` and `ImageHeight` in the plugin file. Reduced sampling has no confirmed job-level method yet (`TODO(Workflow)`); ask the artist how they want it done.
- **Test frames go to the same render folder as the finals.** The full-range render overwrites them.
- **Render settings and AOVs come from the show's lighting template** (render settings and AOV reference): the scene named in `SHOW.md` that every shot copies them from. If `SHOW.md` names none, ask the artist which scene to use, then record it in `SHOW.md`. Default V-Ray sampling when the template doesn't set it: min subdivs 1, max subdivs 24, noise threshold 0.06.
- Use the machine list and priority from `SHOW.md` or the artist's `ARTIST.md` if either gives one.

## Submit with the script

`scripts/farm_submit.py`, next to this file, writes the job files and submits them the way the steps below describe. Run it with any Python 3.7 or newer (`c:\opt\rez\Scripts\python.exe` is on every Buck workstation).

```
farm_submit.py --scene <server scene> --layer <layer> --frames <range> --camera <shot camera>
               --width <px> --height <px> --maya <year> --ocio <config.ocio> --kind test|full
               --agent "<agent>" --task-id <id> --rxt <.rxt> --env <.env> --scratch <scratch>
```

1. Get `--task-id` from `aquarium.py resolve` (`buck-pipeline-aquarium`) and `--rxt` and `--env` from `buck5_context.py find` (`buck-pipeline-launch`). Read the camera, size and layers from the scene with `maya_scene_info.py` (`buck-pipeline-launch`). Repeat `--layer` for several layers. The script fills in the artist's user name and machine from the workstation.
2. Run it as above. This is a dry run: it writes the job files to `<scratch>/farm_jobs/`, prints them and submits nothing. Read them.
3. Add `--submit`. Each job goes to the farm suspended, from inside the Buck5 environment, and the script checks that the farm recorded the show's software packages. A job that fails that check stays suspended.
4. Add `--release` to the same command to resume the jobs as they are submitted, or release them yourself with `deadlinecommand -ResumeJob <id>`. For a full range, tell the artist before this step.
5. Record each job id with `trail.py job` (`buck-pipeline-trail`).

`--pool`, `--group`, `--priority` and `--allowlist` override the studio defaults. `--scale 0.5` renders a test at half size; use it only when the artist chose it.

Dry run, suspended submit, package check and job tags ran on 2026-11-13 against a Maya 2022 show. The script has not released a job or submitted a Maya 2026 scene yet.

## Submit by hand

The script does what follows. Use these steps when it cannot, or to understand a job.

A farm job is two text files plus the Buck5 `.env` file, sent with `deadlinecommand`. One job per render layer.

1. Get the task id: send the scene path to `/templates/resolve` (`buck-pipeline-aquarium`). If the task has no id, stop and ask the artist to create the task in Buck5.
2. Write `job.job` and `plugin.job` as below, in local scratch, with forward-slash paths and no byte-order mark.
3. Submit from inside the job's Buck5 environment (`buck-pipeline-launch`), not from a plain shell:

```bat
set BUCK_PROJECT=<from .env>
set BUCK_PROJECT_ID=<from .env>
set BUCK_SOFTWARE_ID=<from .env>
c:\opt\rez\Scripts\rez\rez-env.exe --input <copied .rxt> -- deadlinecommand job.job plugin.job <buck_uuid.env>
```

The farm reads the software packages a job needs from the environment the submit runs in. Submitted from a plain shell, the job renders outside the show's environment.

4. Check the suspended job: its extra info must list `DEADLINE_REZ_REQUEST_PACKAGES`. If that is empty, the submit ran outside the Buck5 environment; leave the job suspended and resubmit correctly.
5. Release it with `deadlinecommand -ResumeJob <id>`. Release a job that has dependencies with `-PendJob`: resume ignores the dependencies.
6. Record every job id in the version's `.trail`.

**`job.job`**

```
Name=<scene name> - <layer>
BatchName=<scene name>
UserName=<artist>
MachineName=<artist's workstation>
Comment=Submitted from <agent>
Department=<JOB>
Frames=<frames>
ChunkSize=1
Pool=onprem
Group=core-farm
Priority=50
LimitGroups=rez,vray
Plugin=MayaBatch
OutputDirectory0=<task>/maya/render/<scene name>/<layer>
OutputFilename0=<layer>.####.exr
ExtraInfoKeyValue0=BUCK5_TASK_ID=<task id>
ExtraInfoKeyValue1=BUCK_AGENT=<agent>
ExtraInfoKeyValue2=BUCK_TRAIL=<scene path with the extension changed to .trail>
ExtraInfoKeyValue3=BUCK_JOB_KIND=<test | full>
EnvironmentKeyValue0=USE_BUCK_ENVIRONMENT_FILE=1
EnvironmentKeyValue1=BUCK_ENVIRONMENT_BLACKLIST=
InitialStatus=Suspended
```

**`plugin.job`**

```
Animation=1
Renderer=vray
Version=<Maya year, for example 2026>
Build=64bit
UsingRenderLayers=1
UseLegacyRenderLayers=1
RenderLayer=<layer>
ProjectPath=<JOB path>/Production/MAYA
SceneFile=<scene path>
OutputFilePath=<task>/maya/render/
OutputFilePrefix=<scene name>/<Layer>/<Layer>
ImageWidth=<width>
ImageHeight=<height>
Camera=<shot camera>
EnableOpenColorIO=1
OCIOConfigFile=<the job's config.ocio>
```

- **`<Layer>`** in `OutputFilePrefix` is typed literally: it is a V-Ray token the renderer fills in. Every other `<...>` in these templates is a value you replace.
- **Comment** is exactly `Submitted from <agent>`, naming the agent that submitted it: `Submitted from Claude Code`, `Submitted from Codex`. Nothing else.
- **Tags.** `BatchName` groups a version's layers under the scene name. The three `BUCK_` extra-info keys link the job back to its version, so agent jobs can be found and counted on the farm without reading comments. They are extra to what the Buck5 submit button writes; Deadline accepted them on a suspended test job on 2026-11-13.
- **User and machine** are the artist's. A job copied from someone else keeps their name; check both.
- **Camera** is the shot camera, so no other renderable camera renders.
- **Pool, group and priority** above are the studio defaults; `SHOW.md` overrides them. If the artist has an earlier job of the same kind on the show, its values win: read them with `deadlinecommand -GenerateSubmissionInfoFiles <id> job.job plugin.job`.
- `deadlinecommand` is at `C:\Program Files\Thinkbox\Deadline10\bin\deadlinecommand.exe` outside the Buck5 environment.

This was run end to end on Maya 2022 with V-Ray on 2026-11-12: a job written this way matched a button-submitted one and rendered correctly. It has not been run on Maya 2026.

## After it renders

- A finished job is not a finished render. Check that every expected frame exists, opens, and has the right size and channels, and look at representative frames.
- Count what you checked. "0 frames found, no errors" is not a pass: record it in the `.trail` as `not assessed` and find out why.
- Diagnose a failure before retrying. Don't resubmit an unchanged failing job.
- Before requeueing tasks by index, read the job's real task count and chunk size.
- Requeueing, resubmitting or changing someone else's job is "Always ask".
