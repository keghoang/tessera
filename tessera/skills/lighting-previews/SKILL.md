---
name: lighting-previews
description: Farm test frames of a lighting change.
when_to_use: Checks a saved lighting scene, submits a few chosen test frames to the farm and inspects the images. Use whenever a lighting or lookdev change needs to be seen rendered before review. Not for the full production range (tessera:lighting-render) or for the job-file mechanics (tessera:pipeline-farm).
user-invocable: false
---

# Preflight and render previews — BUCK

## Definition

Produce verified preview images that answer a specific lighting review question.

## Ingredients

- A scene the farm can reach, and the intended camera/layers/AOVs: an existing saved version, or for work not yet saved as a version, a test scene copied to the artist's folder under `Production/Work/` (the starter's "Farm test scenes"). A test is never a reason to save a new version.
- Review question, selected frames, preview quality, and required formats.
- Buck5 Deadline submission context and the show's test-render rules in `SHOW.md`.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions. If a styleframe is provided, check the result against it, in the same colour view, before reporting for the artist's review.

## Execution

1. Reopen in the project environment and check references, caches, textures, camera, range, layers, AOVs, and effective resolution.
2. Choose frames that expose the review question and likely failure cases. Use existing adequate renders where possible.
3. Derive destinations from the shot/version through Buck5's Deadline setup. Preview frames of a saved version go to that version's own render folder, where the full render will overwrite them; never write into another version's folder. Preview frames of a test scene go to the `render` folder beside it. Document preview overrides.
4. Write the job with `tessera:pipeline-farm`, using its comment and farm defaults and the show's rules where `SHOW.md` has them.
5. Submit as a test render with `tessera:pipeline-farm` (free under the starter's tiers); record IDs, exact scene/version, frames, and destinations in the version's `.trail`; for a test scene, keep them in your notes and put them in the trail of the version that results. Follow the jobs in the active task and diagnose failures before any authorized retry.
6. Inspect actual output dimensions, channels, pixel content, and display treatment; present the resulting images with relevant limitations.

## Expected outcome

- Color-managed, labeled preview images at the requested frames/formats.
- Submission/result record and concise visual findings; scene delivery settings remain intentional.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Preflight** | Saved scene dependencies and effective render settings are valid. | A job is submitted despite unresolved blockers. |
| **Submission accuracy** | Scene, frames, layers, environment, and project policies match the request. | Wrong version, missing environment metadata, or unauthorized settings are submitted. |
| **Review usefulness** | Images expose the question the preview was requested to answer. | Frames or quality hide the relevant issue. |
| **Output verification** | Actual files are complete, readable, and correctly interpreted. | A job ID or success status substitutes for inspected images. |
| **Isolation** | Preview outputs/settings do not overwrite approved delivery. | Test rendering contaminates production outputs or saved delivery settings. |

## Completion and boundaries

Complete when previews are inspected and presented, not merely submitted. Test submissions are free under the starter's tiers; use the show's or the artist's machine list and priority when one is given. Do not requeue other artists' work or expand into full-range rendering.
