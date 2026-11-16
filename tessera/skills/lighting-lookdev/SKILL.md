---
name: lighting-lookdev
description: Material, texture and surface notes.
when_to_use: Refines materials, textures and surface detail on assets or shots toward an agreed visual target, keeping the approved design. Use for shader, texture, bump, displacement or surface notes, and for work in lookdev (lkdv) files. Not for light placement, exposure or mood notes (tessera:lighting-notes) or for changing a model's shape (tessera:modeling-notes).
user-invocable: false
---

# Refine lookdev — BUCK

## Definition

Refine materials, textures, and surface detail to achieve the intended asset or shot look under relevant lighting.

## Ingredients

- Current lookdev or lighting scene, affected materials/objects, and baseline renders.
- Intended material identities, visual references, and palette/design constraints.
- Existing lookdev sources, UVs/textures, and agreed ownership of shot versus shared asset changes.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions. If a styleframe is provided, check the result against it, in the same colour view, before reporting for the artist's review.

## Execution

1. Inspect the surface at delivery scale and in detail; isolate whether the issue comes from shader properties, lighting/reflected content, UVs, normals, or color handling.
2. Identify the smallest change that addresses the cause. Do not repair shared geometry or lighting outside the authorized scope.
3. Adjust relevant reflection, roughness, transmission, relief, or texture scale while preserving unrelated material properties.
4. Compare under unchanged review conditions, including affected poses/view angles; reject imperceptible or exaggerated changes.
5. Save the appropriate new work version, reopen, and confirm assignments and texture dependencies.

## Expected outcome

- Editable lookdev revision at the agreed ownership level, with resolved textures and preserved assignments.
- Full-frame and detail comparisons describing the visible improvement and any remaining upstream issue.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Material identity** | The surface reads as intended at its actual viewing distance. | Values change but the material remains unreadable or becomes a different material. |
| **Design preservation** | Palette, silhouette, and approved stylization remain intact. | An unsolicited color or design change substitutes for better response. |
| **Scale and continuity** | Texture/detail scale is appropriate and holds during motion. | Patterns stretch, swim, alias, or become distracting. |
| **Assignments** | Changes affect only intended objects/faces and survive reopening. | Unrelated surfaces change or assignments disappear. |
| **Ownership** | Shot overrides and shared lookdev changes follow the agreed scope. | A local note modifies every downstream asset user unexpectedly. |

## Completion and boundaries

Complete when the intended improvement is visible and technically reproducible. Flag non-material causes rather than compensating blindly. Publishing shared lookdev requires explicit scope.
