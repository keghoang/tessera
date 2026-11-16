---
name: buck-lighting
description: Lights a shot on a Buck job from first pass to final - the one entry point for any lighting or lookdev request. Works out where the shot stands and what the request needs, then follows the matching procedure. Use for any request to light, relight, look-develop, render, fix or hand off a shot or its materials, at any stage. Not for modeling work (buck-modeling).
---

# Lighting a shot

This is the front door for lighting and lookdev. The artist names a shot and what they need; you work out the stage and read the procedure for it. The work isn't done at the first pass: carry the shot through review, notes and the full render as the artist asks for each.

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md` (shared conventions). This skill grants no permissions.

## 1. Find where the shot stands

Before asking anything, look:

- the newest file in the shot's `Lighting/maya/work/` folder and its `.trail`
- whether newer animation, layout, camera or asset versions exist than the ones it uses
- whether test frames or a full render exist for that version

Tell the artist in one or two lines what you found.

## 2. Read the procedure the request needs

Each is its own skill. Read every one the request touches, then do the work.

| The situation | Procedure |
| --- | --- |
| No lighting file yet, or "start / set up / block in" | `buck-lighting-first-pass` |
| "Match / copy / carry over" the lighting from another shot | `buck-lighting-transfer` |
| Notes on lights, shadows, exposure, colour or mood | `buck-lighting-notes` |
| Notes on materials, textures or surface detail | `buck-lighting-lookdev` |
| "Options / alternatives / A-B" for one creative question | `buck-lighting-variations` |
| New animation, camera, cache or asset versions | `buck-lighting-sources` |
| A change needs to be seen rendered | `buck-lighting-previews` |
| A render looks wrong and the cause is unknown | `buck-lighting-diagnose` |
| Frames are slow, noisy or out of memory | `buck-lighting-optimize` |
| Comp needs a pass, matte or layer | `buck-lighting-aovs` |
| QA across the whole range and every format | `buck-lighting-coverage` |
| An approved version, full range | `buck-lighting-render` |
| The shot changes hands | `buck-lighting-handoff` |

If the request fits none of these, do it under the starter's rules and say that no procedure covered it.

## 3. The usual order

First pass (or transfer), test frames, then notes and test frames until the artist approves. Then passes for comp, a whole-range check, and the full render. Sources, diagnose and optimize come in whenever they are needed.

When a step finishes, name the usual next one in a line and let the artist choose. Don't start it unasked.
