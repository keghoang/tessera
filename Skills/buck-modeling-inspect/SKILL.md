---
name: buck-modeling-inspect
description: Inspects a Buck model against its design document without changing it - measured checks by script first, then the fewest images that answer what numbers can't - and returns pass, fail or not confirmed per checklist item. Use after every build stage and before any model is shown to the artist. Not for making the fixes (the builder does) or for a department's delivery requirements (buck-modeling-readiness).
---

# Inspect a model — BUCK

Not yet production-tested: this procedure has not been run end to end on a show. Report anything that doesn't behave as written.

## Definition

Whoever built a thing doesn't pass it. Inspection is a separate read of the model against its design document (`buck-modeling-design-doc`), by something that cannot change the scene. Its verdict is advice to the builder and information for the artist; what is worth fixing at the end is the artist's call.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_modeling.md`. This skill grants no permissions.

## Who inspects

- **In Claude Code with the plugin:** hand the inspection to the `model-inspector` sub-agent. Give it the design document's path, where the model is, the images that already exist, and what changed since the last inspection. "Where the model is" has to be exact, or it inspects the wrong scene: for your own Blender instance, the port and the full command it runs a read-only script with (from `SHOW.md`); for the single shared Blender, say "the shared Blender connection"; for Maya, the file path. Through the shared connection it has only reading and capture tools. Through a port it runs scripts, so reading only is a rule it follows, not a lock.
- **Anywhere else:** run the inspection as its own pass, after the building is finished for the stage. Change nothing while inspecting. Write the verdict down before touching the scene again.

Only one thing changes the scene at a time. Never build and inspect in parallel on the same scene.

## Check scripts

Everything that can be measured is checked by a script, never by eye. The builder writes them from the design document's **number** items, one small script per kind of check, in the asset's scratch folder as `checks/check_<what>.py`. They run in Blender in the background or in headless Maya, change nothing, and print one line per item: the item, the measured value, the expected value, pass or fail.

The usual ones:

| Check | What it measures |
|---|---|
| Dimensions | Each part's bounding box against the document, within the tolerance it gives. |
| Overlaps | Separate parts that sit inside each other beyond the tolerance: a prop sunk into a surface, a part buried in a wall. |
| Floating | Parts that should rest on something and have a gap under them. |
| Counts and budget | Parts present against the parts list; evaluated faces per part and in total against the budget. |
| Names and structure | Names and parents against the project's convention. |
| Transforms | Scale applied, no compensating values. |
| Mesh | Non-manifold edges, flipped normals, n-gons where the project doesn't carry them. |

A picture cannot show a prop buried two centimetres into a shelf. A script finds every one.

## Order of work

1. **Numbers first.** Read the design document. Take everything the scene information and the check scripts can give. Record each result.
2. **List what only an image can answer.** The **image** items on the checklist: silhouette, proportion as it reads, a form that looks wrong, something in the reference that is missing from the model.
3. **Plan the shots.** The fewest images that answer that list. Use the builder's comparison sheets first. One image per judgement. No near-duplicate angles. A close-up only once a suspicion is specific, and then one.
4. **Look.** Open every image. Never judge from a file name or a clean log.
5. **Judge** each checklist item, in the document's order.

## The comparison sheet

For each reference image, the builder makes one sheet after every stage, from that reference's comparison camera (`CAM_REF_<view>`): the reference, the capture, the two overlaid, and the model's outline drawn over the reference. The inspector reads placement, proportion, silhouette and what is missing from these. If the reference image and the written description disagree, the image wins.

## The verdict

- **Per checklist item:** pass, fail or not confirmed. An item you could not see or measure is **not confirmed**, with the reason. It is never a pass.
- **Each finding:** the object, what is wrong, the evidence (the script line or the image), the checklist item it breaks, and the direction of the fix.
- **Overall:** pass, or needs fixing.
- Say how many images were used. More images is not better work.
- Keep it short: the verdict and the findings, not a catalogue of every image.

## What the builder does with it

Takes the findings as fact, fixes them, and has the model inspected again. This is one round of the refinement loop in `buck-modeling`, with that loop's limit. What is still failing or not confirmed when the loop ends goes to the artist as a list, never hidden.

## Completion and boundaries

Complete when every checklist item has one of the three results and the verdict is written. The inspection changes nothing: no geometry, no materials, no saves over the working file. Moving the view and writing capture images is all it does to the session.
