#!/usr/bin/env python
"""Read-only client for Aquarium through Buck5's local API.

    aquarium.py status
    aquarium.py get /projects/<id>/software
    aquarium.py resolve "<file path>"          -> project, shot, task and task id
    aquarium.py project <JOB> [--out <file>]   -> the job's facts as one JSON

It can only read: GET requests, plus POST to /templates/parse and
/templates/resolve (which only read a path). Anything else is refused here.
The API adds the artist's login itself; this script never touches a token.
Python 3.7+, standard library only.
"""
from __future__ import print_function

import argparse
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request

READ_POSTS = ("/templates/parse", "/templates/resolve")
AGENT = os.environ.get("BUCK_AGENT_NAME", "Agent")


def base_url():
    """http://localhost:<port> from the newest 'Proxy listening on' log line."""
    local = os.environ.get("LOCALAPPDATA", "")
    log = os.path.join(local, "buck", "Buck5", "logs", "Buck5.log")
    port = None
    if os.path.isfile(log):
        with open(log, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = re.search(r"Proxy listening on (\d+)", line)
                if m:
                    port = m.group(1)
    if not port:
        envs = sorted(glob.glob(os.path.join(local, "buck", "Buck5", "rez", "buck_*.env")),
                      key=os.path.getmtime, reverse=True)
        for path in envs[:1]:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            host = str(data.get("env", data).get("BUCK5_DAEMON_HOST", ""))
            m = re.search(r"(\d{4,5})\s*$", host)
            if m:
                port = m.group(1)
    if not port:
        sys.exit("NOT ASSESSED: Buck5's local API port not found. Ask the artist to open Buck5.")
    return "http://localhost:" + port


def call(path, body=None, timeout=40):
    if not path.startswith("/"):
        path = "/" + path
    if body is not None and path.split("?")[0] not in READ_POSTS:
        sys.exit("REFUSED: this script only reads. POST is allowed for %s only." % ", ".join(READ_POSTS))
    headers = {"X-BUCK-APP": AGENT, "X-BUCK-OS": "windows" if os.name == "nt" else sys.platform}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base_url() + path, data=data, headers=headers,
                                 method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        sys.exit("FAIL: %s %s -> HTTP %s" % (req.get_method(), path, err.code))
    except (urllib.error.URLError, OSError) as err:
        sys.exit("NOT ASSESSED: Buck5's local API did not answer (%s). Ask the artist to open Buck5." % err)


def rows(payload):
    """The API wraps lists differently per endpoint; return a plain list."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("output", "data", "items", "results"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def name_of(item):
    data = item.get("data") if isinstance(item, dict) else None
    return (data or {}).get("name") if isinstance(data, dict) else None


def resolve(path):
    out = call("/templates/resolve", {"inputPath": path.replace("\\", "/")})
    out = out.get("output", out)
    res = {}
    for key in ("project", "sequence", "shot", "asset", "task"):
        val = out.get(key)
        if isinstance(val, dict):
            res[key] = {"id": val.get("_key"), "name": name_of(val)}
        elif val is not None:
            res[key] = {"id": None, "name": val}
    task = res.get("task")
    res["task_exists"] = bool(task and task["id"])
    return res


def project(job):
    match = [p for p in rows(call("/projects")) if name_of(p) == job]
    if not match:
        sys.exit("NOT ASSESSED: no Aquarium project named %s." % job)
    pid = match[0]["_key"]
    facts = {"job": job, "project_id": pid, "not_assessed": []}

    def take(key, path):
        try:
            facts[key] = call(path)
        except SystemExit as err:
            facts["not_assessed"].append("%s: %s" % (key, err))

    take("software", "/projects/%s/software" % pid)
    take("colormanagement", "/projects/%s/colormanagement" % pid)
    take("wiki", "/projects/%s/wiki" % pid)
    seqs = []
    try:
        for seq in rows(call("/projects/%s/sequences" % pid)):
            shots = []
            for shot in rows(call("/sequences/%s/shots" % seq["_key"])):
                tasks = [{"id": t.get("_key"), "name": name_of(t)}
                         for t in rows(call("/shots/%s/tasks" % shot["_key"]))]
                shots.append({"id": shot["_key"], "name": name_of(shot), "tasks": tasks})
            seqs.append({"id": seq["_key"], "name": name_of(seq), "shots": shots})
    except SystemExit as err:
        facts["not_assessed"].append("sequences: %s" % err)
    facts["sequences"] = seqs
    return facts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status")
    p = sub.add_parser("get")
    p.add_argument("path")
    p = sub.add_parser("resolve")
    p.add_argument("path")
    p = sub.add_parser("project")
    p.add_argument("job")
    p.add_argument("--out", help="write the JSON here (local scratch, never the server)")
    args = ap.parse_args()

    if args.cmd == "status":
        print(json.dumps({"base": base_url(), "status": call("/status")}, indent=1))
    elif args.cmd == "get":
        print(json.dumps(call(args.path), indent=1))
    elif args.cmd == "resolve":
        res = resolve(args.path)
        print(json.dumps(res, indent=1))
        if not res["task_exists"]:
            print("NOT ASSESSED: this path has no task id in Aquarium. Ask the artist to create the task in Buck5.",
                  file=sys.stderr)
            return 3
    elif args.cmd == "project":
        facts = project(args.job)
        text = json.dumps(facts, indent=1)
        if args.out:
            if args.out.replace("/", "\\").startswith("\\\\"):
                sys.exit("REFUSED: pulled data stays in local scratch, not on the server.")
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print("written", args.out, "| not assessed:", facts["not_assessed"] or "nothing")
        else:
            print(text)
    else:
        ap.print_help()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
