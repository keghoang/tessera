#!/usr/bin/env python
"""Report what an agent session is working on, so the dashboard can show it.

    status.py set   --dir <activity folder> --job <JOB> --shot <shot or asset> --task <task>
                    --agent "<agent>" --doing "<one line: what is happening now>"
                    [--step "3 of 6"] [--state working|waiting] [--person <username>]
    status.py clear --dir <activity folder> --job <JOB> --shot <shot or asset> --task <task> --agent "<agent>"

"set" writes one small JSON file per person, agent, shot and task, replacing the
previous one. Call it when work on a shot starts and again at each new step;
call "clear" when the work is done. The dashboard drops a session that has been
silent for 30 minutes. The file holds no prompt text and no file contents: only
the fields above and two times. Python 3.7+, standard library only.
"""
from __future__ import print_function

import argparse
import datetime
import getpass
import json
import os
import re
import socket
import sys


def slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()


def path_for(args, person):
    name = "_".join(slug(x) for x in (person, socket.gethostname(), args.agent, args.job, args.shot, args.task))
    return os.path.join(args.dir, name + ".json")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    for name in ("set", "clear"):
        p = sub.add_parser(name)
        p.add_argument("--dir", required=True)
        p.add_argument("--job", required=True)
        p.add_argument("--shot", required=True)
        p.add_argument("--task", required=True)
        p.add_argument("--agent", required=True)
        p.add_argument("--person", default=getpass.getuser().lower())
        if name == "set":
            p.add_argument("--doing", required=True)
            p.add_argument("--step", default="")
            p.add_argument("--state", default="working", choices=("working", "waiting"))
    args = ap.parse_args()
    if args.cmd not in ("set", "clear"):
        ap.print_help()
        return 2
    if not os.path.isdir(args.dir):
        print("NOT ASSESSED: activity folder not found: %s" % args.dir, file=sys.stderr)
        return 3
    path = path_for(args, args.person)
    if args.cmd == "clear":
        try:
            os.remove(path)
        except OSError:
            pass
        print("cleared")
        return 0
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    since = now
    try:
        with open(path, "r", encoding="utf-8") as fh:
            since = json.load(fh).get("since", now)
    except (OSError, ValueError):
        pass
    data = {"person": args.person, "machine": socket.gethostname(), "agent": args.agent, "job": args.job,
            "shot": args.shot, "task": args.task, "doing": args.doing[:160], "step": args.step,
            "state": args.state, "since": since, "updated": now}
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh)
    os.replace(tmp, path)
    print("reported", os.path.basename(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
