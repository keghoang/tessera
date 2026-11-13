---
name: buck-lighting-transfer
description: Adapts an approved lighting setup from one Buck shot to another, keeping the destination's own animation, camera and sequence continuity. Use when the artist says to match, copy or carry over the lighting from another shot. Not for a shot with no approved look to copy from (buck-lighting-v01), or for swapping animation or asset versions inside the same shot (buck-lighting-sources).
---

# Carry lighting to another shot — BUCK

## Definition

Carry the approved visual treatment into a destination shot while respecting its camera, action, and intended differences.

## Ingredients

- Donor lighting scene, approved renders, and the qualities to transfer.
- Destination animation/layout, camera, lookdev, caches, and shot specifications.
- Shot intent and sequence context, including deliberate departures from the donor.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions. If a styleframe is provided, check the result against it, in the same colour view, before reporting for the artist's review.

## Execution

1. Inspect both scenes and separate transferable lights/material treatments/settings from shot-specific dependencies.
2. Establish destination sources and preserve its camera, animation, and reference structure.
3. Transfer only agreed components; reconcile namespaces, assignments, overrides, and scale without duplicate rigs or assets.
4. Adapt light placement and intensity where framing or action requires it; retain the intended visual relationships rather than copying values blindly.
5. Save with intended delivery settings, reopen, and render destination frames alongside relevant donor views.

## Expected outcome

- Versioned destination lighting workfile and shot-derived output configuration.
- Rendered sequence comparison plus a short transfer map and intentional differences.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Destination integrity** | Destination camera, motion, assets, and timing are preserved. | Donor content replaces or contaminates the destination. |
| **Continuity** | Value hierarchy, color relationships, and material treatment support sequence intent. | Shots share light values but look inconsistent. |
| **Adaptation** | Shadows, reflections, and coverage suit destination action. | A copied setup only works from the donor camera. |
| **Dependencies** | Transferred components resolve without unintended donor-shot dependencies. | Overrides or textures still target donor objects or temporary files. |
| **Saved result** | Reopened scene produces expected AOVs and version-specific outputs. | Only the working session is correct. |

## Completion and boundaries

Complete when the destination has a verified, reviewable treatment. Do not claim creative approval from donor approval alone. Upstream repairs, publishing, and full-range rendering remain outside scope unless requested.
