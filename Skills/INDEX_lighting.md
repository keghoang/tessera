# BUCK lighting skills

Ordered from broadest deliverable to narrowest operation. Size describes scope, not render time or difficulty. Larger assignments can use smaller skills without expanding their authorization.

## 1. Large — complete shot deliverables

| Task | Use when |
|---|---|
| [Set up v01 lighting](buck-lighting-v01/SKILL.md) | A shot needs its first reviewable lighting pass. |
| [Carry lighting to another shot](buck-lighting-transfer/SKILL.md) | An approved treatment needs adapting to a destination shot. |
| [Submit and verify production renders](buck-lighting-render/SKILL.md) | An approved version is ready for an authorized full render. |
| [Hand off lighting](buck-lighting-handoff/SKILL.md) | Another artist needs a usable scene and continuation context. |

## 2. Medium — targeted creative and scene revisions

| Task | Use when |
|---|---|
| [Develop lighting variations](buck-lighting-variations/SKILL.md) | A creative decision needs controlled alternatives. |
| [Refine lookdev](buck-lighting-lookdev/SKILL.md) | Materials, textures, or surface detail need refinement against the intended asset or shot look. |
| [Address lighting notes](buck-lighting-notes/SKILL.md) | Artist feedback calls for a focused look revision. |
| [Update animation, camera, or assets](buck-lighting-sources/SKILL.md) | Upstream sources change in an existing lighting scene. |

## 3. Small — focused setup, checks, and troubleshooting

| Task | Use when |
|---|---|
| [Prepare render layers and AOVs](buck-lighting-aovs/SKILL.md) | Comp needs specific separation or render elements. |
| [Optimize render performance](buck-lighting-optimize/SKILL.md) | Measured render cost or noise needs improvement. |
| [Check lighting across the shot](buck-lighting-coverage/SKILL.md) | Temporal and format consistency need review. |
| [Diagnose a render discrepancy](buck-lighting-diagnose/SKILL.md) | Output differs unexpectedly from the intended scene or look. |
| [Preflight and render previews](buck-lighting-previews/SKILL.md) | Selected-frame renders are needed for a review question. |

## Shared conventions

- Environment, permissions, farm submission and what goes on the server come from `BUCK_AGENT_STARTER.md`; software versions, render setup and farm rules come from the show's `SHOW.md`. These skills grant no permissions.
- Organize scene assets under `LGT`, `GEO`, and `MISC`; name lights `lgt_<description>_<role>`, unless `SHOW.md` says otherwise.
- Use the show's lighting template (render settings and AOV reference).
- If a styleframe is provided, check the result against it, in the same colour view, before reporting for the artist's review.
- Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass.
- Save new workfile versions with intended delivery settings, verify the saved artifact, and write its `.trail`. Scripts and working files stay local.
