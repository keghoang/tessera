#!/usr/bin/env python
"""Find a Buck5 (rez) context for a job and run a command inside it.

    buck5_context.py list
    buck5_context.py find --job <JOB> [--software <id>] --scratch <dir>
    buck5_context.py run  --job <JOB> [--software <id>] --scratch <dir> -- <command> [args...]

"find" copies the newest matching context into <scratch>/buck5_context/ and prints
its paths as JSON. "run" does the same, sets the BUCK_* variables and runs the
command through rez-env, returning the command's exit code.

Only the BUCK_* names in KEEP are read from Buck5's .env file. Nothing else in it
(logins, tokens) is read, copied or printed. Python 3.7+, standard library only.
"""
from __future__ import print_function

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys

REZ_ENV = r"c:\opt\rez\Scripts\rez\rez-env.exe"
KEEP = ("BUCK_PROJECT", "BUCK_PROJECT_ID", "BUCK_SOFTWARE_ID", "BUCK5_DAEMON_HOST")


def rez_dir():
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        sys.exit("NOT ASSESSED: LOCALAPPDATA is not set; this script is Windows only.")
    return os.path.join(base, "buck", "Buck5", "rez")


def read_env(path):
    """Return only the KEEP variables from a Buck5 .env file."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    env = data.get("env", data)
    return {k: str(env[k]) for k in KEEP if k in env}


def contexts():
    """Every context Buck5 currently holds, newest first."""
    out = []
    for env_path in glob.glob(os.path.join(rez_dir(), "buck_*.env")):
        uuid = os.path.basename(env_path)[len("buck_"):-len(".env")]
        rxt = os.path.join(rez_dir(), "b5_rez_%s.rxt" % uuid)
        if not os.path.isfile(rxt):
            continue
        try:
            keep = read_env(env_path)
        except (ValueError, OSError):
            continue
        out.append({"env": env_path, "rxt": rxt, "mtime": os.path.getmtime(env_path), "vars": keep})
    return sorted(out, key=lambda c: c["mtime"], reverse=True)


def find(job, software, scratch):
    """Newest context for the job (and launcher entry), copied into scratch."""
    store = os.path.join(scratch, "buck5_context")
    matches = [c for c in contexts()
               if c["vars"].get("BUCK_PROJECT") == job
               and (not software or c["vars"].get("BUCK_SOFTWARE_ID") == str(software))]
    if matches:
        c = matches[0]
        tag = "%s_%s" % (job, c["vars"].get("BUCK_SOFTWARE_ID", "unknown"))
        os.makedirs(store, exist_ok=True)
        rxt = os.path.join(store, tag + ".rxt").replace("\\", "/")
        env = os.path.join(store, tag + ".env").replace("\\", "/")
        shutil.copy2(c["rxt"], rxt)
        shutil.copy2(c["env"], env)
        return {"rxt": rxt, "env": env, "vars": c["vars"], "from": "Buck5"}
    # fall back to a context copied earlier
    pattern = "%s_%s.env" % (job, software if software else "*")
    saved = sorted(glob.glob(os.path.join(store, pattern)), key=os.path.getmtime, reverse=True)
    for env in saved:
        rxt = env[:-4] + ".rxt"
        if os.path.isfile(rxt):
            return {"rxt": rxt.replace("\\", "/"), "env": env.replace("\\", "/"), "vars": read_env(env),
                    "from": "scratch copy"}
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("list")
    for name in ("find", "run"):
        p = sub.add_parser(name)
        p.add_argument("--job", required=True, help="job folder name, for example GSP_DEUS_MACHINA_GSPSF-L0004")
        p.add_argument("--software", help="launcher entry id from SHOW.md (BUCK_SOFTWARE_ID)")
        p.add_argument("--scratch", required=True, help="local scratch folder")
        if name == "run":
            p.add_argument("command", nargs=argparse.REMAINDER, help="-- command and arguments")
    args = ap.parse_args()

    if args.cmd == "list":
        rows = [{"job": c["vars"].get("BUCK_PROJECT"), "software": c["vars"].get("BUCK_SOFTWARE_ID"),
                 "rxt": c["rxt"]} for c in contexts()]
        print(json.dumps(rows, indent=1))
        if not rows:
            print("NOT ASSESSED: Buck5 holds no contexts. Ask the artist to launch the application once from Buck5.",
                  file=sys.stderr)
            return 3
        return 0
    if args.cmd not in ("find", "run"):
        ap.print_help()
        return 2

    ctx = find(args.job, args.software, args.scratch)
    if not ctx:
        print("NOT ASSESSED: no Buck5 context for job %s%s. Ask the artist to launch that entry once from Buck5."
              % (args.job, " software " + str(args.software) if args.software else ""), file=sys.stderr)
        return 3
    if args.cmd == "find":
        print(json.dumps(ctx, indent=1))
        return 0

    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        print("FAIL: no command given after --", file=sys.stderr)
        return 2
    if any("|" in a for a in command):
        print("FAIL: an argument contains '|'. rez-env runs through cmd and breaks on it; "
              "strip the leading '|' from Maya DAG paths.", file=sys.stderr)
        return 2
    if not os.path.isfile(REZ_ENV):
        print("NOT ASSESSED: %s not found." % REZ_ENV, file=sys.stderr)
        return 3
    env = dict(os.environ)
    for k in ("BUCK_PROJECT", "BUCK_PROJECT_ID", "BUCK_SOFTWARE_ID"):
        if k in ctx["vars"]:
            env[k] = ctx["vars"][k]
    env.setdefault("MAYA_DEBUG_NO_SAVE_ON_CRASH", "1")
    print("[buck5_context] %s software %s (%s)" % (args.job, ctx["vars"].get("BUCK_SOFTWARE_ID"), ctx["from"]),
          file=sys.stderr)
    return subprocess.call([REZ_ENV, "--input", ctx["rxt"], "--"] + command, env=env)


if __name__ == "__main__":
    sys.exit(main())
