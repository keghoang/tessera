---
name: buck-modeling
description: Models an asset on a Buck job from first blockout to final - the one entry point for any modeling request. Works out where the asset stands and what the request needs, then follows the matching procedure. Use for any request to model, block out, detail, revise, fix, UV, optimize, check or hand off an asset, at any stage. Not for lighting or material work (buck-lighting).
---

# Modeling an asset

This is the front door for modeling. The artist names an asset and what they need; you work out the stage and read the procedure for it. The work isn't done at the first blockout: carry the asset through review, production detail and the checks the next department needs, as the artist asks for each.

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_modeling.md` (shared conventions, the polygon budget and handoff rules). This skill grants no permissions.

## The bar

Production quality: the standard of a delivered asset. A blockout is the first step toward it, not a lower standard: its forms, proportions and scale must already be right. Stay at a blockout only when the artist asks for one.

## Where to build: Blender, delivered as Maya

- **New models are built in Blender**, through the Blender connection (tools named `mcp__Blender__*`), in a live Blender session so you can look at the result after every change.
- **Models are delivered as Maya files.** When a Blender-built model is ready to show or hand on, move it with `buck-modeling-to-maya`. The artist reviews captures of the Maya file.
- **The Blender file stays local**, in the scratch folder as `<asset>_mdl_v###.blend`, numbered like the Maya version it produces. It never goes on the server.
- **An asset that already exists in Maya stays in Maya**: one that has a Maya work file, or that shots, a rig or a lookdev file reference. Don't round-trip it through Blender.

Use the Blender connection whenever it is in the session. If the tools are missing, or Blender isn't open and connected, say so in one line and tell the artist what is needed (`buck-start` checks it). Build in Maya instead only if the artist says to.

## 1. Find where the asset stands

Before asking anything, look:

- the newest file in the asset's `Modeling/maya/work/` folder and its `.trail`, and the Blender file it names as its source, if any
- the design reference for it
- whether shots, a rig or a lookdev file already reference it

Tell the artist in one or two lines what you found.

## 2. Read the procedure the request needs

Each is its own skill. Read every one the request touches, then do the work.

| The situation | Procedure |
| --- | --- |
| No model yet, or "start / block out" | `buck-modeling-first-pass` |
| An approved blockout to finish or detail | `buck-modeling-production` |
| Notes on shape, proportion or detail | `buck-modeling-notes` |
| "Options / alternatives" for one design question | `buck-modeling-variations` |
| A kit of pieces that fit together | `buck-modeling-modular` |
| The asset is already referenced by shots or a rig | `buck-modeling-reference-update` |
| Does it match the design? | `buck-modeling-reference-check` |
| Edges and highlights | `buck-modeling-bevels` |
| UVs for lookdev | `buck-modeling-uvs` |
| Pivots and placement groups | `buck-modeling-pivots` |
| Cutting a mesh into parts, or joining parts | `buck-modeling-split-combine` |
| A Blender-built model has to be shown or delivered | `buck-modeling-to-maya` |
| Getting it ready for rigging | `buck-modeling-rigging` |
| Mesh or normal defects | `buck-modeling-repair` |
| Unsuitable topology | `buck-modeling-retopology` |
| Too heavy | `buck-modeling-optimize` |
| Is it ready for the next department? | `buck-modeling-readiness` |
| The asset changes hands | `buck-modeling-handoff` |

If the request fits none of these, do it under the starter's rules and say that no procedure covered it.

## 3. Refine your own work before showing it

Never show the first thing you made. Every time you build or change something, run this loop before the artist sees it:

1. **Look.** While building in Blender, take a viewport screenshot through the connection after each change. For a Maya file, capture the fixed review views with `maya_review_capture.py` in `buck-pipeline-launch`, from the saved file. Open the images. Judge images, never parameters or a clean log.
2. **Compare.** Put it beside the target (the design reference, matched view for view) in the same view and the same colour view.
3. **List the gaps.** Write down every visible difference from the target and everything that falls short of the bar above, most visible first.
4. **Fix** the gaps that matter, then go back to step 1.

Stop when a round finds nothing worth fixing, or after three rounds. Then show the artist the result with what you fixed on your own and what still falls short. A gap you saw and left is listed, never hidden. A request for a rough or a quick look skips the loop; say that it was skipped.

## 4. The usual order

First blockout, a check against the reference, then notes until the artist approves the forms. Then production detail, the finishing passes it needs (edges, UVs, pivots), and a readiness check before it goes to rigging, lookdev or lighting.

"Model this asset" means a finished model. Block out first, refine the blockout with the loop above, and post it as progress. Then carry on into production detail without waiting, unless the artist asked for a blockout only, or the design leaves a choice about the forms that is theirs to make.

A separate deliverable is different: rigging preparation, a kit, a handoff or a change to an asset that shots already use is named in a line when the step before it finishes, and started only when the artist asks.
