---
name: modeling-bevels
description: Refine bevels and edges.
when_to_use: Refines bevels and edge treatment on a model so edges and highlights read at the required viewing distance. Use when edges look too sharp, too soft or computer-made, or when highlights break along an edge. Not for general detail work (tessera:modeling-production) or for normal and shading defects (tessera:modeling-repair).
user-invocable: false
---

# Refine bevels and edge treatment — BUCK

## Definition

Improve edge form and highlight behavior at the required viewing distance.

## Ingredients

Approved shape; intended edge treatment; camera distance; shading reference.

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

1. Inspect existing edge scale, normals, and silhouette constraints.
2. Apply controlled bevel widths/segments only where they serve the design.
3. Review neutral shading and relevant lighting; check intersections and evaluated polygon cost.
4. For edits, save and reopen the intended deliverable in the project environment. Review the saved model rather than relying only on the live session. For inspection-only tasks, keep the source unchanged.

## Expected outcome

Versioned model and matched full-frame/detail views.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Edge quality** | Highlights and silhouette improve without changing approved proportions. | Bevels intersect, distort forms, or add invisible complexity. |
| **Preservation** | Unrelated approved forms, placement, UVs, assignments, and relevant identities remain intact. | The task silently changes properties outside its scope. |
| **Budget visibility** | Evaluated counts are reported and the user is warned above 500,000 polygons; memory observations are distinguished from geometry counts. | Base-mesh counts hide evaluated complexity, the threshold is crossed silently, or face count is presented as a RAM measurement. |
| **Evidence** | Saved-file checks and useful review views demonstrate the stated outcome; downstream test limits are explicit. | Successful commands or attractive stills are substituted for required functional verification. |

## Completion and boundaries

Complete when the specified outcome is reviewable and its checks pass. Report unresolved items explicitly; readiness is not artist approval. Do not expand into rig controls, lookdev redesign, publishing, or unrelated asset cleanup without scope. Preserve current authorization rather than repeatedly asking for routine steps already requested.
