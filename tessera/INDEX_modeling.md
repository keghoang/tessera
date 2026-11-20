# BUCK modeling skills

Start at `tessera:modeling`: it works out where the asset stands and picks from these.

Task definitions ordered from broad deliverables to focused operations. Size describes scope, not difficulty. Each task has a distinct result and acceptance criteria; these skills are not yet production-tested.

## What modeling should deliver

A model should satisfy the design, work at the intended camera distance, and support its downstream use. Judge form, construction, and usability rather than detail count. Acceptable means ready for the intended review or handoff, not automatically artist-approved.

## Large — complete asset deliverables

| Task | Acceptable | Failure |
|---|---|---|
| [Build a first model](skills/modeling-first-pass/SKILL.md) | Editable major forms match intended silhouette, proportions, and scale; inferred details are identified. | Fine detail disguises incorrect primary forms or unsupported design assumptions. |
| [Develop an approved model for production](skills/modeling-production/SKILL.md) | Approved forms gain purposeful construction/detail and meet agreed rigging, shading, and rendering needs. | Added complexity changes the design or leaves downstream departments unable to use the asset. |
| [Build a modular asset kit](skills/modeling-modular/SKILL.md) | Parts share compatible dimensions, interfaces, and placement conventions; representative combinations work. | Pieces look correct individually but cannot assemble without manual repair. |
| [Prepare a modeling handoff](skills/modeling-handoff/SKILL.md) | The delivered version opens correctly and includes the structure, dependencies, and known limits needed by the next artist. | The recipient must reconstruct intent, locate missing files, or discover unusable geometry. |

## Medium — targeted revisions and preparation

| Task | Acceptable | Failure |
|---|---|---|
| [Address modeling notes](skills/modeling-notes/SKILL.md) | Requested shape or construction changes are visible; approved proportions and unrelated parts remain intact. | Solving one note breaks an accepted feature or changes unrelated geometry. |
| [Develop shape variations](skills/modeling-variations/SKILL.md) | Alternatives explore a specific design question with consistent review views. | Variants change unrelated properties or differ only in insignificant detail. |
| [Write the design document](skills/modeling-design-doc/SKILL.md) | A short document fixes the target, real dimensions, parts, comparison cameras, budgets and acceptance checklist before anything is built, with at most three open questions. | Building starts from memory of the brief, or the work waits on questions that had a sensible default. |
| [Inspect a model](skills/modeling-inspect/SKILL.md) | A read-only inspection gives every checklist item pass, fail or not confirmed, with measured checks by script before any image. | The builder passes its own work, or an item nobody could see is counted as a pass. |
| [Move a Blender model to Maya](skills/modeling-to-maya/SKILL.md) | The Maya file matches the Blender model in scale, axes, names, hierarchy, pivots, normals and UVs, and is the reviewed deliverable. | A model that looked right in Blender arrives scaled, rotated, renamed or re-normalled, or the Blender file is treated as the deliverable. |
| [Prepare geometry for rigging](skills/modeling-rigging/SKILL.md) | Moving/deforming regions, hierarchy, and pivots support the stated motion. | Pieces cannot perform the intended action, or controls are built when only model preparation was requested. |
| [Prepare UVs for lookdev](skills/modeling-uvs/SKILL.md) | Layout, distortion, density, seams, and overlaps suit the agreed texture workflow. | A UV layout exists but stretches visible textures or breaks required assignments. |
| [Retopologize for intended use](skills/modeling-retopology/SKILL.md) | Edge flow and mesh structure support the required deformation or editing while retaining intended surface form. | A visually similar mesh has unsuitable edge flow, deforms poorly, or invalidates surface data without a transfer plan. |
| [Optimize a heavy asset](skills/modeling-optimize/SKILL.md) | Measured complexity or memory improves within agreed visual and downstream tolerances. | A smaller file loses needed detail, editability, or reference compatibility. |
| [Revise a referenced asset safely](skills/modeling-reference-update/SKILL.md) | The new version works in a representative consuming scene and preserves required identities and behavior. | A correct-looking model breaks assignments, rig connections, or existing animation downstream. |

## Small — focused construction and checks

| Task | Acceptable | Failure |
|---|---|---|
| [Split or combine specified parts](skills/modeling-split-combine/SKILL.md) | Resulting pieces have correct boundaries, membership, and retained surface data. | Wrong cuts, lost UVs, or broken component assignments create downstream repair work. |
| [Set pivots and placement groups](skills/modeling-pivots/SKILL.md) | Simple transform tests demonstrate the intended rotation and assembly behavior. | Pivots are conveniently centered but mechanically wrong, or placement shifts unexpectedly. |
| [Refine bevels and edge treatment](skills/modeling-bevels/SKILL.md) | Edges produce the intended highlight and silhouette at delivery scale. | Bevels alter proportions, intersect, or add invisible complexity. |
| [Repair mesh defects](skills/modeling-repair/SKILL.md) | Identified normal, topology, or surface problems are corrected without collateral changes. | Blanket cleanup changes intentional construction or hides the underlying issue. |
| [Check model against reference](skills/modeling-reference-check/SKILL.md) | Consistent views reveal specific proportion, silhouette, and construction differences. | A flattering angle or persuasive shading hides inaccuracies. |
| [Check asset readiness](skills/modeling-readiness/SKILL.md) | Scale, hierarchy, naming, geometry, UVs, and intended downstream use are verified to agreed requirements. | Generic cleanup passes despite failure in the actual consuming workflow. |

## Build a first model

**Definition:** Create an editable first model that establishes the asset's silhouette, proportions, scale, and construction for design review. Detail should be sufficient to judge the design; production finish is a separate task unless included.

**Ingredients**

- **Design:** Reference views or approved concept; identify which qualities must match and which require interpretation.
- **Intent:** What the asset is, how it is seen, and what it must do.
- **Scale and context:** Dimensions or scale anchor, shot camera/viewing distance, and surrounding assets where relevant.
- **Downstream needs:** Static, rigid assembly, or deforming use; expected moving pieces and texture requirements.
- **Project setup:** Buck5 environment, approved application/version, asset folder, and an existing project modeling example for naming and hierarchy.

Inspect available references and project assets before asking the artist for missing facts. Explicitly identify inferred dimensions and hidden construction; do not present interpretation as an exact match.

**Execution**

1. **Establish the design:** Identify defining forms, scale anchors, intended use, and properties to preserve.
2. **Build primary forms:** Resolve silhouette and proportions in matched views before adding secondary geometry.
3. **Establish construction:** Separate meaningful pieces and position pivots according to required motion or assembly.
4. **Add review-relevant detail:** Include features necessary to judge identity and construction at the intended viewing distance.
5. **Save and verify:** Save the next free work version, reopen in the project environment, and capture review views from the saved model.

**Expected outcome**

- An editable model saved as the next free `<Asset>_mdl_vNNN.mb` in the asset's `Modeling/maya/work/` folder for Maya tasks.
- Clear primary forms and logical pieces, following the project's modeling conventions.
- Neutral review views against the reference, plus intended camera views when available.
- A short list of inferred design choices and unresolved construction questions.

**Verification**

| Check | Acceptable | Failure |
|---|---|---|
| **Design fidelity** | Matched views show the intended silhouette, proportions, and defining features. | Detail or presentation hides incorrect major forms. |
| **Construction** | Piece boundaries, thickness, gaps, and intersections suit the intended use. | Geometry looks plausible from one view but cannot support the intended assembly. |
| **Motion readiness** | Required rigid pieces pass simple rotation/separation tests; deforming regions have a clear downstream plan. | Arbitrary pivots prevent movement, or a static inspection is claimed as proof of deformation quality. |
| **Review clarity** | Neutral views and relevant shot views expose the actual geometry at useful scales. | Lighting, perspective, or selective framing conceals defects. |
| **Saved delivery** | The reopened file retains correct scale, structure, assignments, and dependencies. | Only the working session is valid or the next artist needs undocumented repairs. |

**Completion:** A reviewable first model and a clear list of unresolved design decisions. UV preparation, finished lookdev, controls, and publishing are separate unless requested.

## Revision rules

- Validate primary forms before increasing detail.
- Judge visible quality at the intended viewing distance; use close-ups to diagnose defects.
- Derive cuts and pivots from actual construction and movement, not convenience.
- Preserve meaningful UVs, material assignments, naming, and reference identities when revising an asset.
- Validate downstream compatibility in a consuming scene when the change could affect it.
- Keep modeling, rigging, and lookdev ownership explicit; do not silently turn one assignment into all three.
- Retain an accepted baseline and check each revision against it before returning work.
- Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass.

## Geometry and memory budget

- **Warn above 500,000 polygons** for the complete modeled asset or assembled kit. Count evaluated faces, including subdivision and repeated geometry; report base faces and triangles separately.
- Check at the start, before predictable high-cost operations, and after major additions. If already over the threshold, warn before further substantial additions. State estimated counts when exact evaluation is unavailable.
- Explain the main contributors and offer a reduction option. Do not silently remove approved detail; the warning is advisory, not an automatic approval gate.
- Track available RAM and application memory where accessible before heavy operations. Polygon count is not a memory measurement; no fixed RAM threshold has been specified.
- Under actual memory pressure, preserve a recoverable version and avoid launching additional heavy operations. Include final counts and memory observations in the handoff.

## BUCK pipeline and handoff

Environment, permissions and what goes on the server come from `BUCK_AGENT_STARTER.md`; software versions and conventions come from the show's `SHOW.md`. For Maya, save new model versions under `Production/Assets/<Category>/<Asset>/Modeling/maya/work/` using `<Asset>_mdl_vNNN.mb`. Recheck the destination before saving and preserve existing versions. Publishing is done by the artist through Buck5. Scripts and working files stay local.

Establish modeling roots, naming suffixes, pivot groups, and placement conventions from the project's actual assets. Lighting hierarchy rules do not automatically define a modeling asset's structure.

Scale validation to the receiving workflow:

- **Static assets:** Check silhouette, visible surfaces, shading, and placement.
- **Mechanical assemblies:** Also check separation, pivots, clearance, and representative movement.
- **Deforming assets:** Also check suitable topology and representative deformation when a test rig is available; otherwise state the validation limit.
- **Referenced revisions:** Test in a consuming scene before claiming compatibility with existing rigging, animation, or lookdev.

Every saved version gets a `.trail` identifying the workfile, source version, changes, checks performed, and unresolved issues. Preserve the agreed ownership of model, rig, and lookdev changes.
- A version goes on the server only when the artist says "save" or "version up" (the starter's versioning rule). Where a skill says "save the next version", that is when it happens; until then save locally as you see fit, and never ask, offer or suggest a server save.
