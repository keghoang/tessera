---
name: lighting-aovs
description: Render layers, AOVs and mattes for comp.
when_to_use: Sets up render layers, render elements (AOVs) and output separation on a shot from the show's lighting template and what comp needs. Use when comp asks for a pass, matte or cryptomatte, an AOV is missing or wrong, or layers need splitting. Not for look changes (tessera:lighting-notes) or for render time and noise problems (tessera:lighting-optimize).
user-invocable: false
---

# Prepare render layers and AOVs — BUCK

## Definition

Provide the render separation and channels required by comp without unintentionally changing the approved beauty.

## Ingredients

- Lighting scene, the show's lighting template, and current layer/override setup.
- Comp requirements, expected channel/layer names, and reconstruction method if applicable.
- Representative frames, project color configuration, and existing shot output structure.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions.

## Execution

1. Map each comp requirement to an existing template element, render layer, matte, or justified additional output; avoid redundant passes.
2. Use the show's established render-layer system and naming. Preserve unrelated visibility, materials, and light behavior.
3. Configure membership, overrides, render elements, and shot/version paths through Buck5's Deadline setup.
4. Render representative outputs from the saved scene; inspect actual channels and pixel content, not only enabled settings.
5. Test intended comp use or reconstruction where specified; document any unsupported requirement.

## Expected outcome

- Versioned lighting scene with configured layers/AOVs and unique output destinations.
- Pass map explaining names, contents, color interpretation, and intended comp use, with sample outputs.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Required coverage** | Each requested comp operation has a usable output. | A listed pass is missing, empty, or lacks the necessary objects/contribution. |
| **Separation** | Membership, mattes, and overrides isolate intended content. | Wrong objects appear, edges contaminate mattes, or layer states leak. |
| **Beauty preservation** | Adding outputs leaves the approved beauty unchanged unless requested. | Separation changes shadows, reflections, or material behavior unexpectedly. |
| **Comp usability** | Channels, alpha, data interpretation, and any specified reconstruction work. | Files exist but cannot support the agreed comp operation. |
| **Output integrity** | Saved-scene outputs match template names and distinct version-derived paths. | Layers overwrite each other or deliver incorrect channel names. |

## Completion and boundaries

Complete when comp requirements are demonstrated using actual outputs. Do not assume every AOV set should reconstruct beauty; verify only the agreed method. Comp authoring and full-range rendering are separate unless requested.
