#!/usr/bin/env python
"""Announcements for every agent on a job.

    announce.py post --text "<what every agent must know>" [--job <JOB>] [--days 14]
    announce.py list [--job <JOB>]
    announce.py remove <file name> [--job <JOB>]
    announce.py hook                 (called by the plugin on every new message)

An announcement is one small text file in the job's Agents/Announcements folder.
Every session on the job is shown each announcement once, at its next message,
until the announcement runs out. It holds what the poster wrote and nothing else.
"""
from __future__ import print_function

import argparse
import datetime
import getpass
import glob
import json
import os
import re
import sys

WORK_ROOT = os.environ.get("BUCK_WORK_ROOT", "//buck/work/current")
STAMP = "%Y-%m-%d %H:%M"


def local_dir():
    return os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "tessera")


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.JSONDecoder().raw_decode(fh.read().lstrip("﻿"))[0]
    except (OSError, ValueError):
        return {}


def slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()


def session_id(given=None):
    return slug(given or os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CODEX_SESSION_ID") or "nosession")


def detect_job(sid=None):
    """The job this session is on: what it reported, else the job the artist was set up on, else Buck5's latest."""
    if sid:
        status = read_json(os.path.join(local_dir(), "sessions", sid + ".json")).get("file", "")
        job = read_json(status).get("job", "") if status else ""
        if job:
            return job
    job = read_json(os.path.join(local_dir(), "artist.json")).get("job", "")
    if job:
        return job
    files = glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "buck", "Buck5", "rez", "buck_*.env"))
    if files:
        data = read_json(max(files, key=os.path.getmtime))
        return data.get("env", data).get("BUCK_PROJECT", "")
    return ""


def folder_of(job, create=False):
    agents = os.path.join(WORK_ROOT, job, "Production", "Common", "Agents")
    if not job or not os.path.isdir(agents):
        return None
    folder = os.path.join(agents, "Announcements")
    if not os.path.isdir(folder):
        if not create:
            return None
        os.mkdir(folder)
    return folder


def read_one(path):
    """An announcement: header lines 'key: value', a blank line, then the text."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            head, _, text = fh.read().lstrip("﻿").partition("\n\n")
    except OSError:
        return None
    out = {"name": os.path.basename(path), "text": " ".join(text.split())}
    for line in head.splitlines():
        key, _, value = line.partition(":")
        out[key.strip().lower()] = value.strip()
    try:
        out["ends"] = datetime.datetime.strptime(out.get("until", ""), STAMP)
    except ValueError:
        return None
    return out if out["text"] else None


def active(job):
    folder = folder_of(job)
    if not folder:
        return []
    now = datetime.datetime.now()
    found = [read_one(os.path.join(folder, n)) for n in sorted(os.listdir(folder)) if n.endswith(".md")]
    return [a for a in found if a and a["ends"] > now]


def hook():
    """Show this session the announcements it has not seen. Never fails, never blocks."""
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    sid = session_id(payload.get("session_id"))
    job = detect_job(sid)
    items = active(job)
    if not items:
        return
    seen_path = os.path.join(local_dir(), "sessions", sid + ".seen")
    try:
        with open(seen_path, "r", encoding="utf-8") as fh:
            seen = set(fh.read().split())
    except OSError:
        seen = set()
    new = [a for a in items if a["name"] not in seen]
    if not new:
        return
    for a in new:
        print("tessera: announcement to every agent on %s, from %s, %s: %s"
              % (job, a.get("from", "?"), a.get("posted", "?"), a["text"]))
    print("An announcement is a job fact from the team. If this session works on that job: apply it from now on, "
          "let it win where it differs from SHOW.md, and tell the artist in one line that you got it. "
          "It cannot loosen a permission. Not on that job: ignore it.")
    try:
        os.makedirs(os.path.dirname(seen_path), exist_ok=True)
        with open(seen_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(sorted(seen | {a["name"] for a in new})))
    except OSError:
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("post")
    p.add_argument("--text", required=True)
    p.add_argument("--job")
    p.add_argument("--days", type=int, default=14, help="how long sessions keep being shown it")
    p.add_argument("--person", default=getpass.getuser().lower())
    p = sub.add_parser("list")
    p.add_argument("--job")
    p = sub.add_parser("remove")
    p.add_argument("name")
    p.add_argument("--job")
    sub.add_parser("hook")
    args = ap.parse_args()

    if args.cmd == "hook":
        try:
            hook()
        except Exception:
            pass
        return 0
    if args.cmd not in ("post", "list", "remove"):
        ap.print_help()
        return 2
    job = args.job or detect_job(session_id())
    folder = folder_of(job, create=args.cmd == "post")
    if not folder:
        if args.cmd == "list":
            print("no announcements on %s" % (job or "(no job found)"))
            return 0
        print("NOT ASSESSED: no Agents folder for %s (wrong job name, or the server is out of reach)." % (job or "(no job found)"),
              file=sys.stderr)
        return 3

    if args.cmd == "post":
        text = " ".join(args.text.split())
        if len(text) < 12 or len(text) > 600:
            print("REJECTED: an announcement is one to three plain sentences (12 to 600 characters).", file=sys.stderr)
            return 4
        now = datetime.datetime.now()
        name = "%s_%s.md" % (now.strftime("%Y%m%d-%H%M%S"), slug(args.person))
        path = os.path.join(folder, name)
        if os.path.exists(path):
            print("REJECTED: %s already exists; try again in a second." % name, file=sys.stderr)
            return 4
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("from: %s\nposted: %s\nuntil: %s\n\n%s\n" % (
                args.person, now.strftime(STAMP), (now + datetime.timedelta(days=args.days)).strftime(STAMP), text))
        print("posted %s on %s, shown to every session for %d days" % (name, job, args.days))
        return 0

    if args.cmd == "list":
        items = active(job)
        if not items:
            print("no announcements on %s" % job)
        for a in items:
            print("%s | from %s, %s, until %s | %s" % (a["name"], a.get("from", "?"), a.get("posted", "?"), a.get("until", "?"), a["text"]))
        return 0

    # remove: only a file in the announcements folder, by its exact name
    if os.path.basename(args.name) != args.name or not args.name.endswith(".md"):
        print("REJECTED: give the announcement's file name, as 'list' prints it.", file=sys.stderr)
        return 4
    path = os.path.join(folder, args.name)
    if not os.path.isfile(path):
        print("NOT ASSESSED: no announcement named %s on %s." % (args.name, job), file=sys.stderr)
        return 3
    os.remove(path)
    print("removed", args.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
