---
name: lighting-diagnose
description: Find why a render looks wrong.
when_to_use: Finds why a render differs from its scene, an earlier version or an approved output, and verifies the smallest fix. Use when a render looks wrong and the cause is unknown - missing objects or lights, shifted colour, black or NaN pixels, farm and local results that disagree, two versions that should match and don't. Not for artistic notes (tessera:lighting-notes) or for renders that are only slow or noisy (tessera:lighting-optimize).
user-invocable: false
---

# Diagnose a render discrepancy — BUCK

## Definition

Identify the cause of an unexpected render and prove a correction without disguising the fault through unrelated look changes.

## Ingredients

- Expected image and actual failing output, including exact frame, version, layer, and render route.
- Saved scene, dependencies, project environment, and available render/farm logs.
- Known recent changes and properties to preserve.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions.

## Execution

1. Verify provenance first: which saved scene, camera, frame, layer, output file, and display transform produced each image.
2. Reproduce the issue on the smallest representative render or crop; reuse useful existing outputs.
3. Isolate scene state, dependencies, overrides, materials/lights, environment, and output/display handling. Compare one suspected cause at a time.
4. Test a minimal correction in a recoverable version. Separate confirmed cause from untested hypotheses.
5. Reopen and render through the failing route where feasible; check adjacent affected conditions for regressions.

## Expected outcome

- Concise cause report with reproduction evidence and the corrective change.
- Verified corrected workfile/output, or a specific blocker and retained diagnostic evidence.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Provenance** | Expected and actual outputs are traced to known conditions. | A stale file or different display treatment is mistaken for a lighting defect. |
| **Causal evidence** | Controlled testing supports the identified cause. | A plausible explanation is presented as proven without reproduction. |
| **Correction scope** | The fix addresses the cause and preserves unrelated qualities. | Extra lights or grading conceal an unresolved dependency/configuration issue. |
| **Route verification** | The corrected result succeeds through the relevant saved-scene/render route. | A local test is claimed to prove farm success without checking route differences. |
| **Regression coverage** | Other affected frames/layers remain valid; test limits are stated. | One repaired frame hides new failures elsewhere. |

## Completion and boundaries

Complete when the discrepancy is explained and the correction verified, or report precisely what evidence is still missing. Do not repeatedly submit an unchanged failing job. Infrastructure or upstream changes outside scope remain separate.
