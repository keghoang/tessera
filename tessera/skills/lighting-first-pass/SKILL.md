---
name: lighting-first-pass
description: First lighting pass on a shot.
when_to_use: Sets up the first lighting pass on a Maya shot - assembles the scene from animation, layout and lookdev, applies the show's lighting template (render settings and AOV reference), and saves a reviewed, editable first version. Use when a shot has no lighting file yet, or the artist asks to start, set up or block in lighting. Not for copying an approved look from another shot (tessera:lighting-transfer), revising an existing file from notes (tessera:lighting-notes), or full-range rendering (tessera:lighting-render).
user-invocable: false
---

# Set up a first lighting pass — BUCK

## Definition

Create the shot's first lighting workfile in its Buck5 environment, ready for visual review and continued artist work. V01 is a first-pass milestone, not permission to overwrite an existing version.

## Ingredients

- **Shot sources:** Agreed animation/layout, camera, lookdev, and caches on the production server.
- **Look target:** Approved styleframes or lighting reference. Specify which qualities to inherit from a donor scene.
- **Intent:** What the shot is about and what the viewer should notice.
- **Project setup:** Buck5/Rez context, approved Maya/renderer versions, project OCIO, and the show's lighting template (render settings and AOV reference).
- **Shot specifications:** Frame range, resolution, required crops, and existing shot folder. Output destinations derive through Buck5's Deadline setup.

Discover these from supplied files and project instructions before asking the artist. Resolve missing or conflicting sources before dependent work; do not substitute guessed settings or paths.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions. If a styleframe is provided, check the result against it, in the same colour view, before reporting for the artist's review.

## Execution

1. **Establish the source:** Read current project instructions; inspect the agreed scene and its nested references, caches, material assignments, and render-visible content. Preserve intended reference load states. Identify missing upstream work without expanding the assignment.
2. **Use the project environment:** Work through Buck5 or its resolved Rez context. Assert the show's required runtime and plugins; retain its OCIO configuration. Do not substitute another version silently.
3. **Assemble the workfile:** Retain production references, organize the scene as specified below, apply the lighting template, and derive output paths from the existing shot through Buck5's Deadline setup. If the shot structure is missing, resolve that setup first.
4. **Develop the look:** Establish direction, values, and color relationships before fine adjustments. Evaluate rendered material response in context. Treat settings donors and visual references as distinct inputs.
5. **Validate and hand off:** Save the next available version with the intended delivery settings, reopen the actual deliverable, and complete the technical and visual checks below.

## Expected outcome

- **Workfile:** `<Shot>_lgt_v001.mb` in the shot's `Lighting/maya/work/`, or the next available version. Recheck the destination before saving to avoid concurrent version collisions.
- **Hierarchy:** `LGT` contains lights; `GEO` contains geometry and geometry references; `MISC` contains all other assets. Preserve reference integrity when organizing them.
- **Light naming:** `lgt_<description>_<role>`, such as `lgt_sun_key`, `lgt_sky_fill`, or `lgt_edge_rim`.
- **Render setup:** Correct camera, layers, the lighting template's AOVs, and Buck5 Deadline-derived output destinations for the shot/version. Deriving destinations does not require submitting a job.
- **Review package:** Labeled renders through the project's OCIO display/view, plus unresolved issues and exact workfile location. Get the renders with the `tessera:lighting-previews` skill. Keep scratch outputs, scripts and working files local, and dependencies at approved production locations.
- **Record:** A `.trail` next to the workfile covering sources, what was built, checks, and unresolved issues.

## Technical verification

Give every check here and under visual verification one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Reopen in the project environment** | Correct runtime/plugins; references, textures, and caches resolve. | Wrong software context, broken dependencies, or accidental scratch-file dependencies. |
| **Compare with the source** | Camera, animation, and intended content remain intact. | Missing, duplicated, superseded, or unintentionally altered content. |
| **Inspect organization** | Assets are grouped under `LGT`, `GEO`, or `MISC` as specified; light names include their prefix and role. | Misplaced or ungrouped assets, or light names that omit the required prefix or role. |
| **Test the saved file** | Representative renders match specified dimensions, the lighting template's AOVs, and derived output paths. | Checks cover only the unsaved session, preview overrides leak into delivery, or outputs disagree with the setup. |

## Visual verification

Judge the result against the shot's intent and reference. Do not turn a preference from another shot into a universal lighting rule.

| Check | Acceptable | Failure |
|---|---|---|
| **Direction and coverage** | Lit surfaces, shadow direction, softness, and coverage support the intended treatment. | Light placement contradicts the reference or obscures important action or form. |
| **Value hierarchy** | Brightness and contrast guide attention to the intended subject, preserving necessary detail. | Unintended areas dominate, important detail is lost, or contrast weakens the intended depth. |
| **Color relationships** | Illumination and shadow colors preserve the intended relationships and material palette. | Correcting one region introduces an unwanted overall cast or changes accepted colors. |
| **Material response** | Reflection, transmission, roughness, and detail communicate the intended materials at delivery scale. | Materials read incorrectly, or parameter changes produce no relevant visible improvement. |
| **Secondary lighting** | Supporting lights reinforce the intended focus, depth, or mood. | Added lighting creates unintended emphasis or contradicts the established direction. |
| **Shot coverage** | The treatment holds across representative motion/reveal frames and required crops. | A selected still hides distracting changes in shadows, reflections, or subject readability. |

## Iteration rules

- **Keep an accepted baseline:** Record qualities to preserve and remaining differences. New feedback does not erase earlier direction.
- **Make controlled revisions:** Adjust the responsible variable and hold unrelated properties steady. When intent is ambiguous, use a small rendered comparison to resolve it.
- **Compare actual images:** Review reference, baseline, and revision at comparable framing and scale with correct color handling. Inspect both the full image and relevant detail crops.
- **Reject regressions internally:** Check the whole brief before returning a revision. Report visible improvement and unresolved differences; do not use parameter changes or successful execution as proof of visual quality.

## Completion and boundaries

Complete when the editable workfile passes technical checks and the first pass has been visually inspected with usable review evidence. Clearly distinguish readiness for review from artist approval, and representative-frame checks from full-sequence validation.

Server saves and test renders follow the starter's tiers. Repairing upstream assets, publishing through Buck5 and production rendering are separate tasks unless explicitly included.
