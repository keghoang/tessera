---
name: modeling
description: Model an asset, from first blockout to final.
when_to_use: Models an asset on a job from first blockout to final - the one entry point for any modeling request. Works out where the asset stands and what the request needs, then follows the matching procedure. Use for any request to model, block out, detail, revise, fix, UV, optimize, check or hand off an asset, at any stage. Not for lighting or material work (tessera:lighting).
---

# Modeling an asset

This is the front door for modeling. The artist names an asset and what they need; you work out the stage and read the procedure for it. The work isn't done at the first blockout: carry the asset through review, production detail and the checks the next department needs, as the artist asks for each.

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_modeling.md` (shared conventions, the polygon budget and handoff rules). This skill grants no permissions.

## The bar

Production quality: the standard of a delivered asset. A blockout is the first step toward it, not a lower standard: its forms, proportions and scale must already be right. Stay at a blockout only when the artist asks for one.

## Where to build: Blender, delivered as Maya

- **New models are built in Blender**, in a live Blender session of your own, so you can look at the result after every change.
- **One Blender per agent session.** The Blender connection's scene tools (`mcp__Blender__*`) all reach the one Blender on port 9876, whichever session calls them, so two sessions using them work in each other's scene. If `SHOW.md` gives a way to start your own Blender instance, use it: start yours, note its port, do everything through that port, and stop it when the task is done. Use the `mcp__Blender__*` scene tools only when `SHOW.md` gives no other way and no other session on this computer is using Blender. The documentation tools (`search_api_docs`, `get_python_api_docs`, `search_manual_docs`) are fine either way.
- **Models are delivered as Maya files.** When a Blender-built model is ready to show or hand on, move it with `tessera:modeling-to-maya`. The artist reviews captures of the Maya file.
- **The Blender file stays local**, in the scratch folder as `<asset>_mdl_v###.blend`, numbered like the Maya version it produces. It never goes on the server.
- **An asset that already exists in Maya stays in Maya**: one that has a Maya work file, or that shots, a rig or a lookdev file reference. Don't round-trip it through Blender.

If you can reach no Blender at all (no instance of your own and no connection), say so in one line and tell the artist what is needed (`tessera:start` checks it). Build in Maya instead only if the artist says to.

## Working copy and versions

The Blender file and the Maya scene it is moved into are local working files. Save locally as you see fit: working copies in the scratch folder need no permission. The server gets a version only when the artist says "save" or "version up", or asks for something that needs one. Never bring up saving to the server: don't ask, offer, suggest or remind, and don't list it as a next step. The artist raises it first. Show the result and carry on.

## 0. Report what you're on, first

Before anything else on the asset, run `status.py set` (`tessera:pipeline-status`) with the asset, the task and one line on what you are about to do. Do it again at the start of every new request, even on the same asset. Then proceed. If it can't report, carry on.

## 1. Find where the asset stands

Before asking anything, look:

- the newest file in the asset's `Modeling/maya/work/` folder and its `.trail`, and the Blender file it names as its source, if any
- the design reference for it
- whether shots, a rig or a lookdev file already reference it

Tell the artist in one or two lines what you found.

## 2. Design before you build

A new model, or a change that alters an existing model's forms, starts with a design document: `tessera:modeling-design-doc`. It needs a reference to work from, fixes the real dimensions, the parts in build order, the comparison cameras, the budgets and the acceptance checklist, and it is short. It decides instead of asking: at most three open questions, each with a default you carry on with.

The document is the source of truth. Build what it says. If it lacks something, fix the document first, then build. Small review notes don't need one.

## 3. Build from a script, in stages

For a model built in Blender:

- **The build script is the model.** Keep the build as Python in the asset's scratch folder (`build/<asset>_build.py`), run it to make the base, and adjust in the live session while looking. Every value you settle on by hand goes back into the script. Running the script on an empty file must give the current model; if it wouldn't, the script is behind and gets fixed before you go on.
- **Cameras and light first.** Before any detail, set up the comparison cameras and the review lighting from the design document. Everything after is judged against them.
- **Boxes first, then one part at a time.** Block out every part as simple volumes at the right size and place, check that against the reference, then replace volumes with real parts in the document's build order. Small steps; one large script that does everything fails in ways that are hard to see.
- **A comparison sheet after every stage.** From each comparison camera: the reference, the capture, the two overlaid, and the model's outline over the reference. Don't start the next stage until this one holds up.
- **Stay inside the budgets** in the document, and say so when a part can't.

## 4. Read the procedure the request needs

Each is its own skill. Read every one the request touches, then do the work.

| The situation | Procedure |
| --- | --- |
| Before building a new model, or changing its forms | `tessera:modeling-design-doc` |
| No model yet, or "start / block out" | `tessera:modeling-first-pass` |
| An approved blockout to finish or detail | `tessera:modeling-production` |
| Notes on shape, proportion or detail | `tessera:modeling-notes` |
| "Options / alternatives" for one design question | `tessera:modeling-variations` |
| A kit of pieces that fit together | `tessera:modeling-modular` |
| The asset is already referenced by shots or a rig | `tessera:modeling-reference-update` |
| Checking your own work after a stage, before showing it | `tessera:modeling-inspect` |
| Does it match the design? | `tessera:modeling-reference-check` |
| Edges and highlights | `tessera:modeling-bevels` |
| UVs for lookdev | `tessera:modeling-uvs` |
| Pivots and placement groups | `tessera:modeling-pivots` |
| Cutting a mesh into parts, or joining parts | `tessera:modeling-split-combine` |
| A Blender-built model has to be shown or delivered | `tessera:modeling-to-maya` |
| Getting it ready for rigging | `tessera:modeling-rigging` |
| Mesh or normal defects | `tessera:modeling-repair` |
| Unsuitable topology | `tessera:modeling-retopology` |
| Too heavy | `tessera:modeling-optimize` |
| Is it ready for the next department? | `tessera:modeling-readiness` |
| The asset changes hands | `tessera:modeling-handoff` |

If the request fits none of these, do it under the starter's rules and say that no procedure covered it.

## 5. Refine your own work before showing it

Never show the first thing you made. Every time you build or change something, run this loop before the artist sees it:

1. **Look.** While building in Blender, capture the viewport of your own Blender after each change. For a Maya file, capture the fixed review views with `maya_review_capture.py` in `tessera:pipeline-launch`, from the local working scene. Open the images. Judge images, never parameters or a clean log.
2. **Compare.** Put it beside the target (the design reference, matched view for view) in the same view and the same colour view. For a model with a design document, that is the comparison sheet from each comparison camera.
3. **Inspect.** Have it inspected with `tessera:modeling-inspect`: measured checks by script first, then the images, by an inspector that cannot change the scene. You don't pass your own work.
4. **List the gaps.** The inspection's failed and not-confirmed items, plus everything that falls short of the bar above, most visible first.
5. **Fix** the gaps that matter, then go back to step 1.

Stop when a round finds nothing worth fixing, or after three rounds. Then show the artist the result with what you fixed on your own and what still falls short. A gap you saw and left is listed, never hidden. A request for a rough or a quick look skips the loop; say that it was skipped.

## 6. The usual order

Design document, first blockout, a check against the reference, then notes until the artist approves the forms. Then production detail, the finishing passes it needs (edges, UVs, pivots), and a readiness check before it goes to rigging, lookdev or lighting.

"Model this asset" means a finished model. Block out first, refine the blockout with the loop above, and post it as progress. Then carry on into production detail without waiting, unless the artist asked for a blockout only, or the design leaves a choice about the forms that is theirs to make.

A separate deliverable is different: rigging preparation, a kit, a handoff or a change to an asset that shots already use is named in a line when the step before it finishes, and started only when the artist asks.

## When a correction points at the procedure

When the artist corrects something, or you catch a mistake of your own, ask first whether the procedure caused it: a step that is missing, a check nobody ran, a rule that says the wrong thing. If so, tell the artist in two lines what you would change in which skill, so the next job doesn't repeat it. The shared skills are not yours to edit; the proposal goes to whoever keeps them. A note in your own memory is for what can't be written as a step.
