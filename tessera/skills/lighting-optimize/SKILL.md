---
name: lighting-optimize
description: Cut render time, noise or memory.
when_to_use: Reduces render time, noise or memory use on a shot against a measured baseline, keeping agreed image quality and required outputs. Use when frames are slow, noisy, running out of memory or failing on the farm for resources. Not for a render that looks wrong for an unknown reason (tessera:lighting-diagnose) or for changing which AOVs render (tessera:lighting-aovs).
user-invocable: false
---

# Optimize render performance — BUCK

## Definition

Improve rendering efficiency without sacrificing the shot's accepted appearance or comp requirements.

## Ingredients

- Saved scene, representative frames/layers, and measured baseline render time, memory, and image quality.
- Optimization objective and acceptable visual tolerance or resource limit.
- Production-equivalent renderer/environment, hardware context, and required AOVs.

## BUCK conventions

Follow `BUCK_AGENT_STARTER.md`, the show's `SHOW.md` and `INDEX_lighting.md`. This skill grants no permissions.

## Execution

1. Measure a baseline under recorded conditions. Separate render time from farm queue time and record hardware differences.
2. Identify the dominant cost or noise source from logs, statistics, and images before changing settings.
3. Test one meaningful adjustment at a time using comparable frames, resolution, hardware, and cache conditions.
4. Inspect full-frame images, critical detail, and relevant AOVs; test difficult motion/lighting moments before accepting gains.
5. Save the candidate with intended delivery settings, reopen, and confirm the result. Retain the original and report actual measured tradeoffs.

## Expected outcome

- Versioned optimized scene and reproducible benchmark conditions.
- Before/after time/resource measurements and visual comparisons, including remaining quality tradeoffs.

## Verification

Give every check one of three results: pass, fail or not assessed. A check you could not run is "not assessed", with the reason; it is never a pass. Record each result in the version's `.trail`.

| Check | Acceptable | Failure |
|---|---|---|
| **Measured benefit** | Recorded tests demonstrate the intended time, noise, or memory improvement. | Lower settings or a faster worker are claimed as scene optimization without comparable evidence. |
| **Image quality** | Relevant details, shadows, reflections, and materials remain within agreed tolerance. | Fine detail disappears, denoising smears, or noise becomes unacceptable. |
| **Temporal behavior** | Optimization does not introduce instability at tested motion/transition points. | A clean still hides flicker or inconsistent detail. |
| **Output contract** | Required resolution, AOVs, color configuration, and comp utility remain intact. | Speed gains come from silently dropping required deliverables. |
| **Reproducibility** | Saved settings reproduce the measured benefit; variability is disclosed. | A single unexplained fast run is treated as a reliable improvement. |

## Completion and boundaries

Complete when measured benefit and quality evidence support the candidate. Do not silently trade quality for speed or run costly broad tests beyond the authorized budget. No benefit is a valid finding; preserve the baseline.
