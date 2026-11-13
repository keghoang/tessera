---
name: lighting-render
description: Full-range farm render of an approved version.
when_to_use: Submits an approved lighting version for its full production range and verifies the delivered image sequences. Use when the artist approves a version and asks to send, submit or render the whole shot, the final or the full range, or asks whether a finished render is complete. Not for a few test frames (tessera:lighting-previews), slow or noisy renders (tessera:lighting-optimize), or the job-file mechanics (tessera:pipeline-farm).
---

# Submit and verify production renders — BUCK

## Definition

Render the approved shot range and establish that the resulting sequences are usable for downstream work.

## Ingredients

- Approved saved lighting version, production settings, and preview/preflight evidence.
- Authorized frame range, layers/AOVs, output specification, and render scope.
- Buck5 Deadline environment and current project policies for comments, priority, eligible workers, and resource limits.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions.

## Execution

1. Confirm the exact version approved for rendering and detect concurrent changes. Reuse valid preflight evidence; repeat checks when relevant sources or settings changed.
2. Verify unique shot/version-derived destinations and dependency availability from the worker environment; ensure preview overrides are not unintentionally active.
3. Tell the artist the scene, layers, range and machines, then submit with `tessera:pipeline-farm`; record job IDs, scene version, expected files, and dependencies in the version's `.trail`.
4. Follow completion in the active task. Diagnose failures before retrying; constrain retries to authorized outputs and avoid duplicate jobs or overwriting valid approved work.
5. Check every expected file for existence and readability, dimensions, and required channels. Inspect sequence playback and representative full-resolution frames for visible defects.
6. Hand off verified paths, coverage, failed/missing frames if any, and downstream readiness.

## Expected outcome

- Complete render sequences at the specified destinations, or an explicit incomplete status with exact blockers.
- Manifest of expected/delivered frames and channels, job records, and inspection results, recorded in the version's `.trail`.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Submission scope** | Only the approved version, range, and layers are submitted with current project policies. | The latest unapproved scene or unintended render range is used. |
| **Completeness** | Every expected output is accounted for and readable. | Farm success hides missing, corrupt, or truncated files. |
| **Output contract** | Dimensions, channels, naming, and color interpretation meet downstream needs. | A sequence exists but cannot be used as specified. |
| **Visual integrity** | Playback and detailed samples show no unexplained render defects; limits are disclosed. | Black frames, pops, layer failures, or temporal defects are overlooked. |
| **Recovery** | Failures are diagnosed and authorized retries are traceable. | Unchanged failing jobs are repeatedly submitted or unrelated work is disturbed. |
| **Handoff accuracy** | Manifest and status reflect inspected outputs. | Submitted or partially rendered work is described as delivered. |

## Completion and boundaries

Complete only when the intended sequences pass the stated checks. Publishing, comp, and movie encoding are separate tasks unless included. Never claim full visual validation from file checks alone.
