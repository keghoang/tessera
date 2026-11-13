"""Build the prompt files for one test round. Usage: make_prompts.py <scenarios.json> <Agents mirror> <out dir> [runs=3] [per_agent=5]

Each prompt holds a few scenarios and no expected answers. Groups are rotated per
run so a scenario meets different neighbours each time.
"""
import json
import os
import sys

src, mirror, out = sys.argv[1], sys.argv[2].replace("\\", "/"), sys.argv[3].replace("\\", "/")
runs = int(sys.argv[4]) if len(sys.argv) > 4 else 3
per = int(sys.argv[5]) if len(sys.argv) > 5 else 5
scen = json.load(open(src, encoding="utf-8"))["scenarios"]
os.makedirs(out + "/prompts", exist_ok=True)
os.makedirs(out + "/answers", exist_ok=True)

HEAD = """You are an AI agent starting work for an artist at a studio. You have never seen this studio's files before.

The job's `Agents` folder (normally on the studio server) is mirrored at `{mirror}/Agents`. Read `{mirror}/Agents/BUCK_AGENT_STARTER.md` first and follow it. The job's facts are in `SHOW.md` there, the artist is `sam` (`Artists/sam/ARTIST.md`), and skills are in `Skills/<name>/SKILL.md`; read the skills a question needs. Use only what those files say. Do not run any program, submit anything or write any file except the answer file named below: this is a paper exercise.

For each situation below, say what you would do. Format, one block per situation:

    <number>: <what you do, in at most three sentences>
    Basis: <the file and section, or the skill, that tells you so; write "not covered" if nothing does>

Situations:

"""
TAIL = """
Write your answers, and nothing else, to `{answer}` (plain text). Then reply with one line: the path you wrote.
"""
for run in range(1, runs + 1):
    order = scen[(run - 1) * 7:] + scen[:(run - 1) * 7]          # rotate
    if run % 2 == 0:
        order = order[::2] + order[1::2]                         # and interleave on even runs
    for g in range(0, len(order), per):
        tag = "run%d_g%d" % (run, g // per + 1)
        body = "".join("%d. %s\n\n" % (s["id"], s["situation"]) for s in order[g:g + per])
        text = HEAD.format(mirror=mirror) + body + TAIL.format(answer="%s/answers/%s.txt" % (out, tag))
        open("%s/prompts/%s.txt" % (out, tag), "w", encoding="utf-8", newline="\n").write(text)
print(len(scen), "scenarios ->", runs * ((len(scen) + per - 1) // per), "prompts in", out + "/prompts")
