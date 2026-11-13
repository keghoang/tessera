---
name: modeling-optimize
description: Reduces the polygon count or resource cost of a heavy asset, keeping agreed visual and downstream requirements. Use when a model is slow in the viewport, heavy to load or render, or over budget, or when a lighter previs or background version is asked for. Not for rebuilding edge flow (tessera:modeling-retopology) or for fixing defects (tessera:modeling-repair).
---

# Optimize a heavy asset — BUCK

## Definition

Reduce geometry or resource cost while preserving agreed visual and downstream requirements.

## Ingredients

Baseline asset; polygon/RAM measurements; target use and viewing distance; allowed tradeoffs.

Discover source details and project conventions before asking the artist. Preserve the current accepted baseline and state genuine unresolved assumptions.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_modeling.md`. This skill grants no permissions.

## Geometry and memory budget

- Count evaluated polygon faces for the complete modeled asset, including subdivision, procedural duplication, and repeated placements in an assembly. Report base faces and evaluated faces separately; triangles are a separate metric. State estimation limits where exact evaluation is unavailable.
- **Warn the user when the evaluated total exceeds 500,000 polygons.** Include the current/estimated count, dominant contributors, and a practical way to reduce complexity. Check at baseline, before predictable high-cost operations, and after major geometry changes. Exactly 500,000 does not cross this threshold.
- If already over budget, warn before further substantial additions. Repeat only for a material increase or changed risk. Do not silently reduce approved detail or treat this advisory warning as an automatic approval gate.
- Polygon count is not RAM usage. Check available system RAM and DCC process memory where accessible before heavy duplication, subdivision, remeshing, or imports; monitor during long work when possible. Report genuine memory pressure or unavailable measurements honestly. Do not invent a fixed RAM threshold.
- If memory pressure makes an operation unsafe, preserve a recoverable version and avoid launching additional heavy operations; offer a lower-cost approach. Include final polygon counts and relevant memory observations in the handoff.

## Execution

1. Measure evaluated geometry and available/system/process memory where accessible.
2. Identify hidden/redundant complexity; test justified simplification, instancing, or detail representation.
3. Compare silhouette, shading, UVs, and consuming-scene behavior under comparable conditions.
4. For edits, save and reopen the intended deliverable in the project environment. Review the saved model rather than relying only on the live session. For inspection-only tasks, keep the source unchanged.

## Expected outcome

Optimized version, before/after counts and memory measurements, quality evidence.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Measured improvement** | Resource cost decreases with accepted quality preserved. | A smaller file conceals loss of detail, editability, or compatibility. |
| **Preservation** | Unrelated approved forms, placement, UVs, assignments, and relevant identities remain intact. | The task silently changes properties outside its scope. |
| **Budget visibility** | Evaluated counts are reported and the user is warned above 500,000 polygons; memory observations are distinguished from geometry counts. | Base-mesh counts hide evaluated complexity, the threshold is crossed silently, or face count is presented as a RAM measurement. |
| **Evidence** | Saved-file checks and useful review views demonstrate the stated outcome; downstream test limits are explicit. | Successful commands or attractive stills are substituted for required functional verification. |

## Completion and boundaries

Complete when the specified outcome is reviewable and its checks pass. Report unresolved items explicitly; readiness is not artist approval. Do not expand into rig controls, lookdev redesign, publishing, or unrelated asset cleanup without scope. Preserve current authorization rather than repeatedly asking for routine steps already requested.
