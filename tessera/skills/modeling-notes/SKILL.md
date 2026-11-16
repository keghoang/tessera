---
name: modeling-notes
description: Apply model review notes.
when_to_use: Applies review notes to an existing model, changing only what each note asks and keeping accepted forms, UVs and assignments. Use when the artist passes on feedback about a model's shape, proportion or detail. Not for a new model (tessera:modeling-first-pass), alternatives (tessera:modeling-variations), or an asset that shots already reference (tessera:modeling-reference-update).
user-invocable: false
---

# Address modeling notes — BUCK

## Definition

Apply a bounded modeling revision while preserving accepted qualities.

## Ingredients

Current model; exact reviewed version; marked notes; preservation constraints.

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

1. Map each note to a visible change and inspect newer artist edits.
2. Change only responsible forms or construction; retain the accepted baseline.
3. Compare matching views and review affected surface data and downstream behavior.
4. For edits, save and reopen the intended deliverable in the project environment. Review the saved model rather than relying only on the live session. For inspection-only tasks, keep the source unchanged.

## Expected outcome

New work version, before/after views, note dispositions.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Note fulfillment** | Requested changes read clearly and approved qualities survive. | Fixing one area breaks another or changes unrelated design. |
| **Preservation** | Unrelated approved forms, placement, UVs, assignments, and relevant identities remain intact. | The task silently changes properties outside its scope. |
| **Budget visibility** | Evaluated counts are reported and the user is warned above 500,000 polygons; memory observations are distinguished from geometry counts. | Base-mesh counts hide evaluated complexity, the threshold is crossed silently, or face count is presented as a RAM measurement. |
| **Evidence** | Saved-file checks and useful review views demonstrate the stated outcome; downstream test limits are explicit. | Successful commands or attractive stills are substituted for required functional verification. |

## Completion and boundaries

Complete when the specified outcome is reviewable and its checks pass. Report unresolved items explicitly; readiness is not artist approval. Do not expand into rig controls, lookdev redesign, publishing, or unrelated asset cleanup without scope. Preserve current authorization rather than repeatedly asking for routine steps already requested.
