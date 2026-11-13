---
name: lighting-sources
description: Updates the animation, camera, caches or asset references in an existing Maya lighting scene, keeping the lighting work and compatible overrides. Use when a new animation, layout, model or lookdev version arrives, or references are missing or out of date. Not for look changes (tessera:lighting-notes) or for lighting a different shot (tessera:lighting-transfer).
---

# Update animation, camera, or assets — BUCK

## Definition

Bring specified upstream changes into an existing lighting scene while preserving its approved look and unaffected shot settings.

## Ingredients

- **Lighting source:** Current lighting workfile and baseline renders.
- **Update sources:** Exact replacement animation, camera, cache, or asset versions on the production server.
- **Expected change:** What the update should change, including any intended timing, framing, topology, or naming differences.
- **Preservation:** Lights, material assignments, render-layer overrides, and other shot-specific work to retain.
- **Project context:** Buck5/Rez environment, project OCIO, lighting template, and existing shot folder.

Inspect available source/version information before asking the artist. Do not assume the highest version number is the requested source.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions.

## Execution

1. **Record the baseline:** Inspect reference paths, namespaces, hierarchy, camera, caches, assignments, and relevant layer overrides. Capture the affected state and reuse valid baseline renders.
2. **Check compatibility:** Compare old and new sources for changed names, topology, transforms, timing, and connections. Identify which shot overrides may no longer apply.
3. **Apply the update:** Use the existing reference/cache structure and preserve namespaces where compatible. Update only the specified dependency; inspect nested references and avoid duplicate old/new content.
4. **Reconcile affected overrides:** Restore compatible assignments and overrides using verified object mappings. Do not guess ambiguous mappings or silently discard failed edits; isolate them for an artist decision.
5. **Save and verify:** Save the next free version with intended delivery settings, reopen through the project environment, and render representative affected frames from the saved file.

For camera updates, verify transform, lens, filmback, timing, and renderability. For animation/cache updates, verify range, time offsets, playback, and relevant subframe evaluation. For asset updates, verify placement, deformation, assignments, and render visibility.

## Expected outcome

- **Workfile:** Next available `<Shot>_lgt_vNNN.mb` in `Lighting/maya/work/`, referencing the requested production versions.
- **Preserved setup:** Existing lighting, compatible materials/overrides, and unaffected render settings remain intact. Maintain `LGT`, `GEO`, and `MISC` organization without breaking references.
- **Output setup:** Version-specific destinations derived through Buck5's Deadline setup; existing AOV configuration retained unless explicitly changed.
- **Review package:** Matching-frame before/after renders, an old-to-new source list, and any unresolved override or visual consequences.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Version accuracy** | The reopened scene resolves the requested sources, including affected nested dependencies. | A top-level path changes but stale nested assets or caches still drive the result. |
| **Expected behavior** | New motion, camera, or asset content matches the supplied update. | Timing, scale, placement, deformation, or framing differs unintentionally. |
| **Override integrity** | Assignments and layer overrides still affect the intended objects; failed edits are explained. | Materials disappear, overrides target the wrong objects, or failed edits are ignored. |
| **Preserved work** | Lights and unrelated shot work remain unchanged. | Updating a dependency removes or rewrites existing lighting work. |
| **Scene composition** | Updated content appears once and superseded content no longer contributes where replaced. | Old and new geometry render together, or required content is missing. |
| **Visual consequence** | Comparisons distinguish intended upstream changes from unintended regressions. | Changed shadows, reflections, or coverage are overlooked, or unauthorized lighting changes hide them. |
| **Saved delivery** | The saved scene renders with intended settings, AOVs, and new version destinations. | Only the live session works or outputs overwrite an earlier version. |

## Decision rules

- Preserve lighting parameters; do not promise identical pixels when geometry, animation, or camera has intentionally changed.
- If an update requires look adjustments, report the consequence and treat those adjustments as a separate lighting revision unless already included.
- If a mapping is ambiguous or incompatible, preserve the original version and report the specific conflict. Continue independent compatible updates within scope.
- Do not force-load intentionally unloaded references or import assets merely to bypass reference problems.

## Completion and boundaries

Complete when requested sources are integrated, compatible shot work is preserved, and the saved result has technical and visual evidence. Clearly identify any update that remains unresolved; do not describe partial integration as complete.

Permissions follow the starter's tiers. Upstream asset edits and publishing are outside this skill. Record the old and new source versions in the `.trail`.
