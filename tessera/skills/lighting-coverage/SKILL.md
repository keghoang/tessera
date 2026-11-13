---
name: lighting-coverage
description: QA lighting across the whole shot.
when_to_use: Reviews a shot's lighting across its whole frame range and every delivery format, and reports issues without changing the look. Use for whole-shot QA before a full render or delivery - flicker, pops, frames where the lighting breaks, crops in other aspect ratios. Not for fixing what it finds (tessera:lighting-notes) or for tracing one unexplained difference (tessera:lighting-diagnose).
---

# Check lighting across the shot — BUCK

## Definition

Find lighting problems that isolated stills miss across the shot's action, camera movement, and delivery formats.

## Ingredients

- Current lighting scene or render sequence, frame range, camera, and required crops.
- Approved look, shot intent, important beats, and known intentional lighting changes.
- Existing review media and the show's test-render rules for any additional test renders.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions.

## Execution

1. Map camera moves, reveals, fast action, visibility changes, and other risk moments; inspect existing playback before requesting more renders.
2. Review the full available sequence for discontinuities and missing output. Select additional frames around uncertain transitions rather than only evenly spaced samples.
3. Inspect shadow movement, reflection continuity, exposure/color stability, material readability, and focal hierarchy separately.
4. Review every required crop at important moments; inspect final-resolution detail where reduced previews cannot establish quality.
5. Return timecoded/frame-specific findings, severity, and suggested ownership. Do not modify the look unless revision is included.

## Expected outcome

- Annotated review or issue list identifying frame ranges, visible symptoms, and responsible department.
- Coverage statement distinguishing inspected playback, rendered samples, and untested portions.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Temporal behavior** | Lighting evolves consistently with intended motion and events. | Unintended popping, flicker, reflection loss, or exposure shifts occur. |
| **Readability** | Important subjects and actions remain legible. | Motion moves the subject into an unintended visual failure. |
| **Format coverage** | Required crops preserve intended focus and usable scene coverage. | Alternate formats expose missing content or distracting lighting. |
| **Evidence quality** | Issues have reproducible frames/ranges and clear visual evidence. | Vague notes cannot be located or acted on. |
| **Coverage honesty** | Sampling limits and missing frames are explicit. | A handful of stills is reported as full-sequence verification. |

## Completion and boundaries

Complete with an actionable review and accurate coverage statement, including a clean report if no issues were found. Repairs and additional rendering require existing or explicit scope; review alone is not creative approval.
