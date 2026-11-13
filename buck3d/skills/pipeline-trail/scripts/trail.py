#!/usr/bin/env python
"""Create and update a version's .trail file.

    trail.py new   --file <scene path> --agent "<agent>" [--made-by agent|human] [--source ...]
                   [--app "Maya 2026.3"] [--renderer "V-Ray 7.40.04"] [--job <JOB>] [--scripts <path>]
    trail.py job   --file <scene path> --id <Deadline id> --kind test|full --layers <names> --frames <range>
    trail.py event --file <scene path> --text "<what happened>" [--who <name>]
    trail.py check --file <scene path>      -> does the trail exist and is every check marked?

"new" writes the skeleton next to the scene and refuses if a trail is already
there. Fill in Request, Changes and Checks by editing the file afterwards.
"job" and "event" only append. Python 3.7+, standard library only.
"""
from __future__ import print_function

import argparse
import datetime
import getpass
import os
import re
import socket
import sys

NAME_RE = re.compile(r"^(?P<shot>.+)_(?P<task>mdl|rig|lkdv|anim|lyt|lgt|comp|fx|prev)_v(?P<ver>\d{3})(?:_(?P<suffix>[A-Za-z0-9]+))?$")
RESULTS = ("pass", "fail", "not assessed")

SKELETON = """---
trail: 2
file: {file}
job: {job}
shot: {shot}
task: {task}
version: {ver}
date: {date}
artist: {artist}
made_by: {made_by}
agent: {agent}
app: {app}
renderer: {renderer}
source: {source}
status: wip
review: not shown
notes_addressed: []
upstream: []
checks: []
farm_jobs: []
renders:
scripts: {scripts}
---

## Request

TODO: what the artist asked for, in their words where possible.

## Changes

- TODO: one line per change - what, where in the scene, which note it answers.

## Checks

- not assessed TODO: list every planned check as "<pass | fail | not assessed> <check> - <how, or why not>".

## Not done / not verified

- TODO, or "nothing".

## Flagged, not fixed

- TODO, or "nothing".

## Events

- {date} {artist} version saved by {who}
"""


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def trail_path(scene):
    return os.path.splitext(scene)[0] + ".trail"


def job_from_path(scene):
    parts = scene.replace("\\", "/").split("/")
    if "Production" in parts and parts.index("Production") > 0:
        return parts[parts.index("Production") - 1]
    return ""


def new(args):
    path = trail_path(args.file)
    stem = os.path.splitext(os.path.basename(args.file))[0]
    m = NAME_RE.match(stem)
    if not m:
        print("FAIL: %s is not named <shot or asset>_<task>_v###[_suffix]." % stem, file=sys.stderr)
        return 1
    artist = args.artist or getpass.getuser()
    text = SKELETON.format(
        file=os.path.basename(args.file), job=args.job or job_from_path(args.file),
        shot=m.group("shot"), task=m.group("task"), ver=m.group("ver"), date=now(), artist=artist,
        made_by=args.made_by, agent=args.agent if args.made_by == "agent" else "",
        app=args.app or "", renderer=args.renderer or "", source=args.source or "",
        scripts="%s:%s" % (socket.gethostname(), args.scripts) if args.scripts else "",
        who=args.agent if args.made_by == "agent" else artist)
    try:
        with open(path, "x", encoding="utf-8", newline="\n") as fh:   # "x": never overwrite
            fh.write(text)
    except FileExistsError:
        print("REFUSED: %s already exists. Edit it, or use 'job' / 'event' to append." % path, file=sys.stderr)
        return 1
    print("written", path)
    return 0


def read(path):
    if not os.path.isfile(path):
        sys.exit("NOT ASSESSED: no trail at %s. Human-made versions may have none." % path)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def split_header(text):
    m = re.match(r"---\n(.*?\n)---\n(.*)\Z", text, re.S)
    if not m:
        sys.exit("FAIL: the trail has no '---' header block.")
    return m.group(1), m.group(2)


def append_event(body, line):
    if "## Events" not in body:
        body = body.rstrip("\n") + "\n\n## Events\n"
    return body.rstrip("\n") + "\n" + line + "\n"


def add_job(args):
    path = trail_path(args.file)
    header, body = split_header(read(path))
    entry = ("  - id: %s\n    kind: %s\n    layers: %s\n    frames: %s\n    result: pending\n"
             % (args.id, args.kind, args.layers, args.frames))
    lines = header.splitlines(True)
    for i, line in enumerate(lines):
        if line.startswith("farm_jobs:"):
            lines[i] = "farm_jobs:\n"
            j = i + 1
            while j < len(lines) and lines[j].startswith((" ", "\t")):
                j += 1
            lines.insert(j, entry)
            break
    else:
        lines.append("farm_jobs:\n" + entry)
    body = append_event(body, "- %s %s farm job %s submitted (%s, %s, frames %s)"
                        % (now(), args.who or getpass.getuser(), args.id, args.kind, args.layers, args.frames))
    write(path, "---\n" + "".join(lines) + "---\n" + body)
    print("job added to", path)
    return 0


def add_event(args):
    path = trail_path(args.file)
    header, body = split_header(read(path))
    body = append_event(body, "- %s %s %s" % (now(), args.who or getpass.getuser(), args.text))
    write(path, "---\n" + header + "---\n" + body)
    print("event added to", path)
    return 0


def check(args):
    path = trail_path(args.file)
    header, body = split_header(read(path))
    problems = []
    if "TODO" in header + body:
        problems.append("%d TODO placeholder(s) left" % (header + body).count("TODO"))
    for field in ("job", "source", "app", "scripts"):
        if re.search(r"(?m)^%s:[ 	]*$" % field, header):
            problems.append("header field '%s' is empty" % field)
    section = re.search(r"## Checks\n(.*?)(?=\n## |\Z)", body, re.S)
    items = [l[2:].strip() for l in (section.group(1) if section else "").splitlines() if l.startswith("- ")]
    if not items:
        problems.append("no checks listed")
    counts = dict.fromkeys(RESULTS, 0)
    for item in items:
        for res in RESULTS:
            if item.lower().startswith(res):
                counts[res] += 1
                break
        else:
            problems.append("check without a result: %s" % item[:60])
    print("checks:", ", ".join("%d %s" % (counts[r], r) for r in RESULTS))
    for p in problems:
        print("FAIL:", p)
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("new")
    p.add_argument("--file", required=True)
    p.add_argument("--agent", required=True, help='"Claude Code", "Codex", ...')
    p.add_argument("--made-by", default="agent", choices=("agent", "human"))
    for opt in ("--artist", "--job", "--source", "--app", "--renderer", "--scripts"):
        p.add_argument(opt)
    p = sub.add_parser("job")
    p.add_argument("--file", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--kind", required=True, choices=("test", "full"))
    p.add_argument("--layers", required=True)
    p.add_argument("--frames", required=True)
    p.add_argument("--who")
    p = sub.add_parser("event")
    p.add_argument("--file", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--who")
    p = sub.add_parser("check")
    p.add_argument("--file", required=True)
    args = ap.parse_args()
    handler = {"new": new, "job": add_job, "event": add_event, "check": check}.get(args.cmd)
    if not handler:
        ap.print_help()
        return 2
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
