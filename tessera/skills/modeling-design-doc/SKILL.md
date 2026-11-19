---
name: modeling-design-doc
description: Write the design document a model is built from.
when_to_use: Writes the short design document a model is built from - target, real dimensions, parts in build order, comparison cameras, budgets and an acceptance checklist. Use before building any new model, and before a change that alters an existing model's forms. Not for small review notes (tessera:modeling-notes) or for checking a finished model (tessera:modeling-inspect).
user-invocable: false
---

# Design document for a model — BUCK

Not yet production-tested: this procedure has not been run end to end on a show. Report anything that doesn't behave as written.

## Definition

A model is built from a written design, not from memory of the brief. The document is short, it is decided before any geometry exists, and the build follows it. It is what the inspection (`tessera:modeling-inspect`) checks the model against.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_modeling.md`. This skill grants no permissions.

The document is a working file: `design.md` in the asset's folder in the local scratch folder. It never goes on the server. When a version is saved, its `.trail` carries the summary: dimensions, budgets, the decisions and what stayed open.

## References first

Nothing is designed without a target.

1. Look for the asset's reference: its folders on the job, `SHOW.md`, what the artist attached.
2. If there are images and a written description and they disagree, the image wins.
3. If there is no image at all, say so in one line and ask the artist for one, or for the go-ahead to work from the description. Ask once. On the go-ahead, write the missing description yourself and mark it `[designed]`.

## What the document contains

In this order, and nothing else:

1. **Target.** What the asset is, the style, which reference each view comes from, where it is seen (shot, viewing distance, whether it moves).
2. **Dimensions.** The main sizes in real units, with the scale anchor they come from (a door, a person, a neighbouring asset). Centimetres as Maya will read them; metres in Blender.
3. **Parts, in build order.** Each part small enough to build and check on its own, named as the project names things. Mark which parts repeat.
4. **Comparison cameras and review light.** One camera per reference image, matching its framing, named `CAM_REF_<view>`, with position and focal length. The review lighting: neutral for a design check; for a photoreal target, light and colour set to the reference. Both are set up before any detail goes on, so every later comparison is made against the same baseline.
5. **Budgets.** Evaluated faces per part and in total (the 500,000 warning in `INDEX_modeling.md` still applies), and the time one review capture may take.
6. **Acceptance checklist.** What "done" means, one line per item. Mark each item **number** (a script can check it: sizes, counts, names, overlaps) or **image** (only a picture answers it: silhouette, read of a form, something missing).
7. **Decisions and open questions.** See below.

## Keep it short

Aim for 150 lines; never more than 250. A long document isn't read and contradicts itself.

- A decision is one sentence, plus one sentence of reason. No derivations, no rejected alternatives.
- Don't repeat the studio's or the show's rules. Point to them.
- Write only what is specific to this asset.

## Decide, don't ask

The document's job is to decide. Mark where each value comes from: `[reference]` (read off the reference), `[estimated]` (worked out from the scale anchor or from the real object) or `[designed]` (your choice, because nothing specified it). Then commit to it.

An open question is allowed only when:

- the work can't physically proceed without the answer, or
- a wrong guess would cost a large rebuild and you can't check it yourself.

At most three per asset. Each one comes with its default: "if I hear nothing, I'll build it as ...". Post them with the first progress and carry on with the defaults. Never hold the work for them.

## The document is the source of truth

- Read it before every stage. Build the sizes, parts and order it gives.
- If it turns out to lack something, fix the document first: decide, mark it, then build. Don't improvise in the scene.
- When the artist's notes change the design, change the document first, then the model.
- Stop and report only for something that meets the open-question bar above.

## Showing it

The artist gets a summary with the first progress, not the document: the dimensions, the part count, the budgets, and the open questions with their defaults. Five lines.

## Completion and boundaries

Complete when the document has all seven parts, is within its length, and every checklist item is marked number or image. This skill builds nothing and never touches a scene.
