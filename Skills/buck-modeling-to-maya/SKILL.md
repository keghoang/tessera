---
name: buck-modeling-to-maya
description: Moves a model built in Blender into Maya and saves it as the Maya deliverable on a Buck job, checking scale, axes, names, hierarchy, pivots, normals and UVs on the way. Use whenever a model was built or changed in Blender and has to be delivered, and before any review of a Blender-built model. Not for building the model (buck-modeling-first-pass, buck-modeling-production) or for changing an asset that only lives in Maya.
---

# Move a Blender model to Maya — BUCK

Not yet production-tested: this procedure has not been run end to end on a show. Report anything that doesn't behave as written.

## Definition

Models are built in Blender and delivered as Maya files. The Blender file is a working file and stays in the local scratch folder; the server gets the `.mb` and its `.trail` only. This is the step where a model most often breaks, so every check below is run and recorded, never assumed.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_modeling.md`. This skill grants no permissions. Maya runs headless in the job's Buck5 environment (`buck-pipeline-launch`).

## Before leaving Blender

1. **Names and hierarchy** follow the project's existing Maya assets, not Blender defaults: no `.001` suffixes, no `Cube`, groups as empties named like the project's groups.
2. **Transforms:** scale applied on every mesh (1, 1, 1). Rotation applied unless the rotation is meaningful for placement. Origins sit where the pivots must be.
3. **Geometry:** modifiers the model depends on are applied on an export copy, never on the working objects. No n-gons unless the project's assets carry them. Custom normals only where they are intended.
4. **Record the numbers** you will compare against: per object the world bounding-box size in metres, face count, UV map names, origin position, parent.

## Export and import

1. Export FBX from Blender to the local scratch folder, selected asset only: Y up, -Z forward, scale applied so 1 Blender metre becomes 100 Maya centimetres, smoothing written per face, no cameras or lights, no animation.
2. In headless Maya, in the job's Buck5 environment and the show's Maya version, import into a new scene and keep it as a local working scene in the scratch folder. If the project has a model template or an existing asset to match, match its root group and naming.
3. Delete what the import adds that the project's assets don't have (FBX display layers, empty sets, default materials named after Blender's).

## Checks in Maya

Give every check one of three results: pass, fail or not assessed. Record each in the `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Scale** | Each object's bounding box in centimetres is 100 times its Blender size in metres, within 0.1%. | Off by 100, or scale left on a transform to compensate. |
| **Axes** | Up is Y; the front faces the direction the project's assets face. | The model lies on its side or faces backwards. |
| **Names and hierarchy** | Same names, same parents, same order as recorded; names follow the project's convention. | Suffixes, renamed nodes, a flattened or extra hierarchy level. |
| **Transforms** | Translate and rotate as intended, scale 1 on every transform. | Compensating values (rotate -90, scale 100) on any node. |
| **Pivots** | Each pivot is at the recorded origin, converted to centimetres. | Pivots at the world origin or the bounding-box centre. |
| **Faces** | Face counts equal the recorded ones; no unexpected triangulation or n-gons. | Counts differ, or quads arrived as triangles. |
| **Normals** | Hard and soft edges read as in Blender; normals unlocked unless custom normals were intended. | Faceted or over-smoothed shading, or locked normals nobody asked for. |
| **UVs** | The same UV sets, named as the project names them, with no flipped or missing shells. | A missing set, a default `map1` beside the real one, or shells flipped. |
| **Materials** | Assignments follow the project's convention, or a single default if lookdev is separate. | Blender materials left on the delivered model. |

A failed check is fixed in Blender and exported again, not patched in Maya, so the Blender file stays the true source.

## Save and show

1. Capture the fixed review views from the local Maya scene (`maya_review_capture.py` in `buck-pipeline-launch`). The artist reviews the Maya captures, not Blender screenshots.
2. Compare the Maya captures with the same views in Blender. A visible difference is a failed check.
3. Show the captures and propose the version. On the artist's go-ahead, save the next free `<asset>_mdl_v###.mb` in the asset's `Modeling/maya/work/` folder with `save_version.py` (`buck-pipeline-trail`), and write its `.trail`: name the Blender file it came from, the checks and their results.

## Completion and boundaries

Complete when the artist has given the go-ahead, the saved Maya file reopens in the project environment and every check is pass or explicitly not assessed. The `.blend` never goes on the server. Publishing is the artist's, through Buck5.
