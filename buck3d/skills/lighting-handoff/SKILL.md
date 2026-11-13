---
name: lighting-handoff
description: Packages an existing Buck lighting scene for another artist - verified dependencies, named controls, render status and open issues. Use when a shot changes hands, or the artist asks to clean up or hand off a lighting file. Not for changing the look (buck3d:lighting-notes) or for QA across the frame range (buck3d:lighting-coverage).
---

# Hand off lighting — BUCK

## Definition

Make the current lighting work easy for another artist to open, understand, and continue.

## Ingredients

- Intended workfile/version and its current approval state.
- Dependency list, review renders, render/submission status, and open notes.
- Recipient needs, intended destination, and any authorized publishing scope.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions.

## Execution

1. Identify the authoritative handoff version; distinguish working, reviewed, approved, submitted, and delivered states.
2. Reopen through the project environment; confirm required dependencies and production paths. Inspect scene organization without rewriting unrelated work.
3. Prepare a concise handoff listing the file, source versions, lighting controls/roles, important overrides, AOV setup, and outstanding issues.
4. Link existing representative review media and exact render locations/status. Describe the method well enough to continue or reproduce the setup; build scripts stay local.
5. Save or transfer only within authorized scope; use the approved Buck5 publishing route if publishing is explicitly included. Verify the delivered location rather than relying on a local working copy.

## Expected outcome

- Usable editable scene at the agreed location with dependencies intact.
- Short artist-facing handoff covering how to continue, what is approved, what has rendered, and what remains, written into the version's `.trail`.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Openability** | The delivered file opens in the intended environment without accidental local dependencies. | The recipient needs undocumented files or a different application context. |
| **Usability** | LGT/GEO/MISC organization and role-based light names make the setup understandable. | Hidden workarounds or unexplained overrides prevent normal editing. |
| **Provenance** | Scene, dependencies, and review media identify exact versions. | The recipient must guess which version or image is current. |
| **Status** | Approval, submission, completion, and known limitations are distinguished. | Workfile save or farm submission is misrepresented as approval or delivery. |
| **Continuity** | The next action and unresolved decisions are clear. | The next artist must search chat history to reconstruct the task. |
| **Delivery integrity** | Agreed destination contains the verified artifact and required supporting files. | Only a local copy was checked or dependencies were lost during transfer. |

## Completion and boundaries

Complete when the receiving artist has a verified editable artifact and concise continuation context. Do not publish merely because a handoff was requested, or clean up files as an implicit part of handoff.
