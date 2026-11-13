---
name: buck-lighting-notes
description: Revises an existing Buck Maya lighting file from review notes, changing only what each note asks and keeping approved qualities and render settings. Use when the artist passes on feedback about lights, shadows, exposure, colour or mood in a shot that already has lighting. Not for a first pass (buck-lighting-v01), material notes (buck-lighting-lookdev), new upstream versions (buck-lighting-sources), or a render that differs for an unknown reason (buck-lighting-diagnose).
---

# Address lighting notes — BUCK

## Definition

Apply specific review notes to an existing lighting shot and return a versioned, visibly improved result without losing previously approved qualities.

## Ingredients

- **Working source:** Current lighting scene and its production dependencies. Identify any newer artist changes before editing.
- **Review baseline:** The exact render/version being reviewed. If it differs from the working source, establish what changed between them.
- **Notes:** Requested changes, their priority, and any marked frames or image regions.
- **Intent and preservation:** What the shot should communicate, plus qualities already approved and properties that must remain unchanged.
- **Project context:** Buck5/Rez environment, project OCIO, lighting template, and existing shot structure.

Retrieve established context before asking the artist. Resolve contradictory notes or ambiguous source versions before making dependent changes.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions. If a styleframe is provided, check the result against it, in the same colour view, before reporting for the artist's review.

## Execution

1. **Interpret each note:** Define the visible result it asks for and identify the responsible lighting variable. Distinguish lighting from material, geometry, camera, and comp issues.
2. **Inspect the current scene:** Use the project Buck5 environment. Check that the reviewed issue still exists and that later artist changes are retained. Reuse valid baseline renders.
3. **Make a controlled revision:** Change the responsible variable while holding unrelated properties steady. Diagnose coupled effects before adding compensating lights. Use a small rendered comparison when the intended treatment is genuinely ambiguous.
4. **Check the whole look:** Verify the requested improvement and previously accepted qualities. Inspect affected motion and crops, not only the annotated frame.
5. **Save and verify:** Save the next free workfile version with the intended delivery settings, reopen, and render from the saved result.

Do not silently expand a lighting note into an upstream asset repair or comp change. Identify the dependency and continue unaffected work within scope.

## Expected outcome

- **Workfile:** Next available `<Shot>_lgt_vNNN.mb` in `Lighting/maya/work/`, preserving existing versions and production references.
- **Scene conventions:** Lights under `LGT`; geometry and geometry references under `GEO`; other assets under `MISC`. New or renamed lights follow `lgt_<description>_<role>`. Report pre-existing organization issues rather than reorganizing unrelated content unasked.
- **Render configuration:** Retain camera, timing, resolution, OCIO, layers, and AOVs unless the note requires a change. Derive the new version's output destinations through Buck5's Deadline setup.
- **Review package:** Labeled baseline/revision comparisons and a short disposition for each note: addressed, unresolved, or outside scope. State any remaining tradeoff. Record the same dispositions in the version's `.trail`.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Note fulfillment** | The requested change is visible in the relevant region or action. | Parameters changed but the intended improvement is absent, or the change overshoots the note. |
| **Approved qualities** | Previously accepted direction, value hierarchy, color relationships, and material response remain intact unless explicitly revised. | Solving the latest note undoes an earlier decision or introduces an unwanted overall change. |
| **Scope and source integrity** | Unrelated scene content and newer artist work are preserved. | The revision starts from an obsolete scene or alters assets, camera, animation, or comp without scope to do so. |
| **Temporal and format coverage** | The fix holds through affected motion, transitions, and required crops. | The annotated frame improves while adjacent action or another format breaks. |
| **Comparison quality** | Baseline and revision use matching frames, framing, scale, and display treatment; whole images and relevant crops are shown. | Review conditions hide regressions or exaggerate improvement. |
| **Saved delivery** | Reopened workfile resolves dependencies and produces the expected AOVs and version-specific outputs. | Only the unsaved session works, preview settings remain, or output paths target an earlier version. |

## Iteration rules

- Maintain a short list of accepted qualities and open notes throughout the task.
- Treat a new note as a refinement unless the artist explicitly changes direction.
- Reject obvious mismatches and regressions before presenting a revision.
- If a correction requires sacrificing an accepted quality, present the tradeoff instead of choosing silently.
- Report rendered evidence, not light counts, parameter changes, or successful script execution as proof of improvement.

## Completion and boundaries

Complete when every in-scope note has a clear disposition, the saved revision passes its checks, and comparison media is ready for review. Do not mark unresolved notes as addressed or equate readiness with artist approval.

Server saves and test renders follow the starter's tiers. Once the revision is saved and a test has been seen, a full-range render follows the starter's "Tell" tier. Publishing and changes outside the lighting assignment require their own scope.
