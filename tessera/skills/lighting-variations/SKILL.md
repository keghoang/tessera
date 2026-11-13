---
name: lighting-variations
description: Lighting options for one creative question.
when_to_use: Builds a small set of labelled lighting alternatives for one shot so the artist can settle a specific creative question. Use when the artist asks for options, alternatives, explorations or A/B versions of the lighting. Not for applying a note whose direction is already chosen (tessera:lighting-notes) or for material alternatives (tessera:lighting-lookdev).
---

# Develop lighting variations — BUCK

## Definition

Produce a small set of comparable lighting alternatives that help the artist make one defined choice.

## Ingredients

- Baseline scene/render, shot intent, and the question the options should answer.
- Allowed variables and range of exploration; approved qualities to preserve.
- Review camera, representative frames, formats, and project display treatment.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions. If a styleframe is provided, check the result against it, in the same colour view, before reporting for the artist's review.

## Execution

1. State the decision and identify the variables needed to explore it; discover existing constraints before asking questions.
2. Choose a small useful set of distinct options, normally two or three, rather than an arbitrary parameter sweep.
3. Create recoverable variants with named differences. Keep unrelated scene properties and review conditions fixed.
4. Render and compare internally; discard redundant, broken, or clearly off-brief options.
5. Present the remaining alternatives together with a recommendation tied to shot intent.

## Expected outcome

- Editable variants or a documented reversible option setup.
- Labeled comparison renders, variable differences, and a recommendation; the original baseline remains recoverable.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Decision value** | Each option represents a meaningful answer to the stated question. | Variants are indistinguishable or explore unrelated questions. |
| **Comparability** | Frame, camera, resolution, and color handling remain consistent unless explicitly under study. | Presentation conditions make one option appear artificially better. |
| **Preservation** | Locked qualities and scene content survive in every option. | Exploration silently reopens approved decisions. |
| **Coverage** | Options remain plausible at relevant moments and crops. | An option is selected from a flattering frame that hides a failure. |
| **Reproducibility** | The artist can reopen and continue each presented treatment. | Images have no corresponding recoverable scene state. |

## Completion and boundaries

Complete when the artist has usable alternatives and a clear decision. Do not select and propagate an option as approved without the artist's choice. Production rendering is not part of exploration.
