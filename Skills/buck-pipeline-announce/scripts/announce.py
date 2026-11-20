#!/usr/bin/env python
"""Announcements for every agent on a job: reading them.

    announce.py list [--job <JOB>]
    announce.py hook                 (called by the plugin on every new message)

An announcement is one small text file in the job's Agents/Announcements folder,
posted and taken down from the team dashboard. Every session on the job is shown
each announcement once, at its next message, until the announcement runs out.
"""
from __future__ import print_function

import argparse
import datetime
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


def folder_of(job):
    folder = os.path.join(WORK_ROOT, job, "Production", "Common", "Agents", "Announcements")
    return folder if job and os.path.isdir(folder) else None


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
    p = sub.add_parser("list")
    p.add_argument("--job")
    sub.add_parser("hook")
    args = ap.parse_args()

    if args.cmd == "hook":
        try:
            hook()
        except Exception:
            pass
        return 0
    if args.cmd != "list":
        ap.print_help()
        return 2
    job = args.job or detect_job(session_id())
    items = active(job)
    if not items:
        print("no announcements on %s" % (job or "(no job found)"))
    for a in items:
        print("%s | from %s, %s, until %s | %s" % (a["name"], a.get("from", "?"), a.get("posted", "?"), a.get("until", "?"), a["text"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
