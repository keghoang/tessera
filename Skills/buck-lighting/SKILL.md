---
name: buck-lighting
description: Lights a shot on a Buck job from first pass to final - the one entry point for any lighting or lookdev request. Works out where the shot stands and what the request needs, then follows the matching procedure. Use for any request to light, relight, look-develop, render, fix or hand off a shot or its materials, at any stage. Not for modeling work (buck-modeling).
---

# Lighting a shot

This is the front door for lighting and lookdev. The artist names a shot and what they need; you work out the stage and read the procedure for it. The work isn't done at the first pass: carry the shot through review, notes and the full render as the artist asks for each.

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md` (shared conventions). This skill grants no permissions.

## The bar

Production quality: the standard of a delivered shot, at every stage. A first pass is the first version, not a rougher one. Go below that only when the artist asks for a rough, a blocking pass or a quick look.

## Working copy and versions

Save locally as you see fit: working copies in the scratch folder need no permission. The server gets a version only when the artist says "save" or "version up", or asks for something that needs one. Never bring up saving to the server: don't ask, offer, suggest or remind, and don't list it as a next step. The artist raises it first. Show the result and carry on. Refinement rounds and test renders never make a version; farm tests run from a test scene in the artist's own folder (the starter's "Farm test scenes").

## 0. Report what you're on, first

Before anything else on the shot, run `status.py set` (`buck-pipeline-status`) with the shot, the task and one line on what you are about to do. Do it again at the start of every new request, even on the same shot. Then proceed. If it can't report, carry on.

## 1. Find where the shot stands

Before asking anything, look:

- the newest file in the shot's `Lighting/maya/work/` folder and its `.trail`
- whether newer animation, layout, camera or asset versions exist than the ones it uses
- whether test frames or a full render exist for that version

Tell the artist in one or two lines what you found.

## 2. Read the procedure the request needs

Each is its own skill. Read every one the request touches, then do the work.

| The situation | Procedure |
| --- | --- |
| No lighting file yet, or "start / set up / block in" | `buck-lighting-first-pass` |
| "Match / copy / carry over" the lighting from another shot | `buck-lighting-transfer` |
| Notes on lights, shadows, exposure, colour or mood | `buck-lighting-notes` |
| Notes on materials, textures or surface detail | `buck-lighting-lookdev` |
| "Options / alternatives / A-B" for one creative question | `buck-lighting-variations` |
| New animation, camera, cache or asset versions | `buck-lighting-sources` |
| A change needs to be seen rendered | `buck-lighting-previews` |
| A render looks wrong and the cause is unknown | `buck-lighting-diagnose` |
| Frames are slow, noisy or out of memory | `buck-lighting-optimize` |
| Comp needs a pass, matte or layer | `buck-lighting-aovs` |
| QA across the whole range and every format | `buck-lighting-coverage` |
| An approved version, full range | `buck-lighting-render` |
| The shot changes hands | `buck-lighting-handoff` |

If the request fits none of these, do it under the starter's rules and say that no procedure covered it.

## 3. Refine your own work before showing it

Never show the first thing you made. Every time you build or change something, run this loop before the artist sees it:

1. **Look.** Get test frames with `buck-lighting-previews` on frames that represent the shot, from a test scene and not a new version, and open them. Judge images, never parameters or a clean log.
2. **Compare.** Put it beside the target (the styleframe, the approved shot it should match, or the previous approved version) in the same view and the same colour view.
3. **List the gaps.** Write down every visible difference from the target and everything that falls short of the bar above, most visible first.
4. **Fix** the gaps that matter, then go back to step 1.

Stop when a round finds nothing worth fixing, or after three rounds. Then show the artist the result with what you fixed on your own and what still falls short. A gap you saw and left is listed, never hidden. A request for a rough or a quick look skips the loop; say that it was skipped.

## 4. The usual order

First pass (or transfer), test frames, then notes and test frames until the artist approves. Then passes for comp, a whole-range check, and the full render. Sources, diagnose and optimize come in whenever they are needed.

Reaching the bar is part of the step you were asked for, so do it without being asked. A separate deliverable is different: a full-range render, a transfer to another shot or a handoff is named in a line when the step before it finishes, and started only when the artist asks.
