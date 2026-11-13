# Scenario tests for the Buck agent files

These check that a fresh agent, given only the starter, a `SHOW.md`, an `ARTIST.md` and the skills, decides correctly in situations that went wrong on earlier jobs. They are paper tests: the agent says what it would do and runs nothing.

Run them after any change to the starter's rules or to a pipeline skill.

## Files

| File | Holds |
| --- | --- |
| `scenarios.json` | 30 situations, each with what a correct answer must contain (`expect`) and what makes it wrong (`fail_if`). |
| `make_prompts.py` | Builds the prompt files for a round: five situations per agent, three runs, groups rotated per run. Prompts never contain the expected answers. |

## How to run a round

1. Copy the `Agents` folder to a local mirror (starter, `SHOW.md`, `Artists/`, `Skills/`). Add a made-up artist folder, `Artists/sam/ARTIST.md`, from the template; the scenarios name `sam`.
2. `python make_prompts.py scenarios.json <mirror folder> <output folder>` writes 18 prompts to `<output folder>/prompts/`.
3. Give each prompt to a fresh agent with no other context ("Read the file `<prompt>` and follow it exactly."). Each writes its answers to `<output folder>/answers/`.
4. Grade each answer against `expect` and `fail_if` in `scenarios.json`. A scenario passes only if all three runs pass.
5. For each failure, fix the file the agent should have found the rule in, then re-run that scenario.

## Results

| Date | Starter version | Agent | Result | Notes |
| --- | --- | --- | --- | --- |
| 2026-11-13 | 2026-11-13.3 | Claude Code subagents | 90 of 90 answers passed (30 scenarios, 3 runs each) | Graded by the author of the files, not independently. One gap found: no named tool for making an OCIO preview from an EXR (scenario 25). |

## Limits

- Saying the right thing is not doing it. These tests show the rules can be found and are read the same way each time; they do not show an agent follows them mid-task.
- All runs so far used one agent type. Codex has not been run.
- Every scenario has a rule written for it. A situation the files do not cover is not tested here; add one whenever a real mistake happens.
