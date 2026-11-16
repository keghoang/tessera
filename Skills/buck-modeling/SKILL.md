---
name: buck-modeling
description: Models an asset on a Buck job from first blockout to final - the one entry point for any modeling request. Works out where the asset stands and what the request needs, then follows the matching procedure. Use for any request to model, block out, detail, revise, fix, UV, optimize, check or hand off an asset, at any stage. Not for lighting or material work (buck-lighting).
---

# Modeling an asset

This is the front door for modeling. The artist names an asset and what they need; you work out the stage and read the procedure for it. The work isn't done at the first blockout: carry the asset through review, production detail and the checks the next department needs, as the artist asks for each.

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_modeling.md` (shared conventions, the polygon budget and handoff rules). This skill grants no permissions.

## 1. Find where the asset stands

Before asking anything, look:

- the newest file in the asset's `Modeling/maya/work/` folder and its `.trail`
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
| Getting it ready for rigging | `buck-modeling-rigging` |
| Mesh or normal defects | `buck-modeling-repair` |
| Unsuitable topology | `buck-modeling-retopology` |
| Too heavy | `buck-modeling-optimize` |
| Is it ready for the next department? | `buck-modeling-readiness` |
| The asset changes hands | `buck-modeling-handoff` |

If the request fits none of these, do it under the starter's rules and say that no procedure covered it.

## 3. The usual order

First blockout, a check against the reference, then notes until the artist approves the forms. Then production detail, the finishing passes it needs (edges, UVs, pivots), and a readiness check before it goes to rigging, lookdev or lighting.

When a step finishes, name the usual next one in a line and let the artist choose. Don't start it unasked.
