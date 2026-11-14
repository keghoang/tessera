#!/usr/bin/env python
"""Read one job's shots, latest versions, trails and live agent sessions into the JSON the dashboard draws.

    collect.py --job-root <path to the job folder> --out data/<name>.json [--activity <folder>]

It only reads the job: folder listings under Production/shots and Production/Assets,
the newest versioned work file per shot and task, and the .trail next to it.
Live sessions come from the files status.py (skill pipeline-status) writes into the job's
Production/Common/Agents/Activity folder, or --activity. The output
goes to a local file; open the dashboard at index.html#<name>.
Python 3.7+, standard library only.
"""
from __future__ import print_function

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

TASK_OF = {"animation": "anim", "layout": "lyt", "lighting": "lgt", "comp": "comp", "fx": "fx", "previs": "prev",
           "modeling": "mdl", "rigging": "rig", "lookdev": "lkdv", "styleframe": "style"}
ORDER = ["style", "prev", "lyt", "anim", "fx", "lgt", "comp", "mdl", "rig", "lkdv"]
WORK_EXT = (".mb", ".ma", ".nk", ".hip", ".hiplc", ".c4d", ".blend", ".aep")
NAME_RE = re.compile(r"^(?P<name>.+)_(?P<task>[A-Za-z]+)_v(?P<ver>\d{3})(?:_(?P<suffix>[A-Za-z0-9]+))?$")


def subdirs(path):
    try:
        return sorted(e.name for e in os.scandir(path) if e.is_dir() and not e.name.startswith((".", "_")))
    except OSError:
        return []


def stamp(ts):
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def latest_work_file(dept_dir):
    """Newest versioned work file under <dept>/<app>/work plus up to five earlier ones, or None."""
    best, every = None, []
    for app in subdirs(dept_dir):
        work = os.path.join(dept_dir, app, "work")
        try:
            entries = list(os.scandir(work))
        except OSError:
            continue
        for e in entries:
            stem, ext = os.path.splitext(e.name)
            if ext.lower() not in WORK_EXT or not e.is_file():
                continue
            m = NAME_RE.match(stem)
            if not m:
                continue
            key = (int(m.group("ver")), e.stat().st_mtime)
            every.append((key, e.path, m))
            if best is None or key > best[0]:
                best = (key, e.path, m)
    if best is None:
        return None
    earlier = sorted((x for x in every if x[1] != best[1]), reverse=True)[:5]
    return best + (earlier,)


def read_trail(scene_path):
    """Header fields and the Changes bullets of the .trail next to a scene, or None."""
    path = os.path.splitext(scene_path)[0] + ".trail"
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return None
    head = {}
    m = re.match(r"---\n(.*?)\n---\n(.*)\Z", text, re.S)
    body = text
    if m:
        body = m.group(2)
        for line in m.group(1).splitlines():
            if re.match(r"^[a-z_]+:", line):
                k, v = line.split(":", 1)
                head[k.strip()] = v.split("  #")[0].strip()

    def section(title):
        s = re.search(r"## %s\n(.*?)(?=\n## |\Z)" % re.escape(title), body, re.S)
        return s.group(1).strip() if s else ""

    changes = [l[2:].strip() for l in section("Changes").splitlines() if l.startswith("- ") and "TODO" not in l]
    request = " ".join(l.strip() for l in section("Request").splitlines() if l.strip() and "TODO" not in l)
    return {"head": head, "changes": [c for c in changes if c], "request": request}


def history_entry(key, path, m):
    """An earlier version, for the detail panel: who made it comes from its trail or its name suffix only."""
    trail = read_trail(path)
    head = trail["head"] if trail else {}
    made_by = head.get("made_by", "human") if trail else "human"
    return {"version": key[0], "date": stamp(key[1]), "made_by": made_by,
            "agent": head.get("agent", "") if made_by == "agent" else "",
            "artist": head.get("artist", "") or m.group("suffix") or ""}


def owners(paths):
    """Windows file owners for many paths in one PowerShell call. {} elsewhere or on failure."""
    if os.name != "nt" or not paths:
        return {}
    script = ("$input | ForEach-Object { try { $o = (Get-Acl -LiteralPath $_).Owner } catch { $o = '' }; "
              "\"$_`t$o\" }")
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", script], input="\n".join(paths),
                             capture_output=True, text=True, timeout=300).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    res = {}
    for line in out.splitlines():
        if "\t" in line:
            p, o = line.split("\t", 1)
            res[p.strip()] = o.strip().split("\\")[-1].lower()
    return res


def scan(root, kind, tree):
    """One block per sequence or asset category under root."""
    blocks, versions = [], []
    for group in subdirs(root):
        items, tasks = [], set()
        for item in subdirs(os.path.join(root, group)):
            depts = subdirs(os.path.join(root, group, item))
            # a shot or asset has at least one department folder holding <app>/work
            if not any(os.path.isdir(os.path.join(root, group, item, d, a, "work"))
                       for d in depts for a in subdirs(os.path.join(root, group, item, d))):
                continue
            items.append(item)
            for dept in depts:
                found = latest_work_file(os.path.join(root, group, item, dept))
                if not found:
                    continue
                (ver, mtime), path, m, earlier = found
                task = TASK_OF.get(dept.lower(), m.group("task").lower())
                tasks.add(task)
                versions.append({"file": os.path.basename(path), "path": path, "shot": item, "task": task, "version": ver,
                                 "suffix": m.group("suffix") or "", "date": stamp(mtime),
                                 "history": [history_entry(k, p, hm) for k, p, hm in earlier]})
        if items:
            blocks.append({"kind": kind, "name": group, "items": items, "tasks": tasks})
    all_tasks = set().union(*[b["tasks"] for b in blocks]) if blocks else set()
    cols = [t for t in ORDER if t in all_tasks] + sorted(all_tasks - set(ORDER))
    for b in blocks:
        b["tasks"] = cols
    tree.extend(blocks)
    return versions


def live_sessions(folder, job, stale_idle, stale_active):
    out = []
    if not folder or not os.path.isdir(folder):
        return out
    now = datetime.datetime.now()
    for e in os.scandir(folder):
        if not e.name.endswith(".json"):
            continue
        try:
            with open(e.path, "r", encoding="utf-8") as fh:
                s = json.load(fh)
            seen = datetime.datetime.strptime(s["updated"], "%Y-%m-%d %H:%M")
        except (OSError, ValueError, KeyError):
            continue
        # an idle session leaves the page soon; a working or waiting one stays until it is cleared,
        # and the long limit only catches sessions that died without clearing
        limit = stale_idle if s.get("state") == "idle" else stale_active
        if s.get("job") != job or (now - seen).total_seconds() > limit * 60:
            continue
        out.append({k: s.get(k, "") for k in ("person", "agent", "shot", "task", "doing", "state", "since", "updated")})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--job-root", required=True, help=r"the job folder, for example \\server\work\current\<JOB>")
    ap.add_argument("--out", required=True, help="local JSON file, for example data/<name>.json")
    ap.add_argument("--activity", help="folder of session files, if not the job's Agents/Activity")
    ap.add_argument("--stale", type=int, default=30, help="minutes an idle session stays on the page")
    ap.add_argument("--stale-active", type=int, default=720, help="minutes a working or waiting session stays without an update")
    ap.add_argument("--label", help="name shown on the page instead of the job folder name")
    args = ap.parse_args()
    if args.out.replace("/", "\\").startswith("\\\\"):
        sys.exit("REFUSED: the dashboard data is written locally, not on the server.")
    prod = os.path.join(args.job_root, "Production")
    if not os.path.isdir(prod):
        sys.exit("NOT ASSESSED: no Production folder under %s" % args.job_root)
    job = os.path.basename(os.path.normpath(args.job_root))

    tree = []
    versions = scan(os.path.join(prod, "shots"), "Shots", tree)
    versions += scan(os.path.join(prod, "Assets"), "Assets", tree)

    no_trail = []
    for v in versions:
        trail = read_trail(v["path"])
        head = trail["head"] if trail else {}
        v["made_by"] = head.get("made_by", "human") if trail else "human"
        v["agent"] = head.get("agent", "") if v["made_by"] == "agent" else ""
        v["artist"] = head.get("artist", "") or v["suffix"]
        v["changes"] = trail["changes"] if trail else []
        v["request"] = trail["request"] if trail else ""
        v["has_trail"] = bool(trail)
        if not v["artist"]:
            no_trail.append(v["path"])
    own = owners(no_trail)
    for v in versions:
        if not v["artist"]:
            v["artist"] = own.get(v["path"], "") or "unknown"
        del v["path"], v["suffix"]

    activity = args.activity or os.path.join(prod, "Common", "Agents", "Activity")
    live = live_sessions(activity, job, args.stale, args.stale_active)
    people = sorted({v["artist"] for v in versions} | {s["person"] for s in live})
    now = stamp(datetime.datetime.now().timestamp())
    data = {"sample": False, "job": args.label or job, "collected": now, "now": now, "structure": tree,
            "versions": versions, "live": live, "people": people}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1)
    shots = sum(len(b["items"]) for b in tree)
    with_trail = sum(1 for v in versions if v["has_trail"])
    print("%s: %d blocks, %d shots and assets, %d latest versions (%d with a trail), %d live sessions, %d people -> %s"
          % (job, len(tree), shots, len(versions), with_trail, len(live), len(people), args.out))
    if not versions:
        print("NOT ASSESSED: no versioned work files found; the page will list shots with empty cells.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
