#!/usr/bin/env python
"""First-session setup for an artist: the same welcome, checks and briefing on every machine.

    start.py welcome [--job <JOB>] [--user <username>]
    start.py check   --job <JOB> [--user <username>] [--agent ClaudeCode]
    start.py finish  --job <JOB> [--user <username>]
    start.py hook                    (called by the plugin when a session starts)
    start.py reset                   (forget this machine's setup, to run it again)

"welcome", "check" and "finish" print text for the agent to pass on word for word.
"check" exits 1 if a check failed or needs a pick. "finish" creates the artist's
ARTIST.md on the job if there is none (it never overwrites one) and writes a small
marker on this machine so the setup runs once.
Python 3.7+, standard library only.
"""
from __future__ import print_function

import argparse
import datetime
import getpass
import glob
import json
import os
import re
import socket
import subprocess
import sys

WORK_ROOT = os.environ.get("BUCK_WORK_ROOT", "//buck/work/current")
HERE = os.path.dirname(os.path.abspath(__file__))

INTRO = ("I'm your 3D assistant on this job, and I already know my way around BUCK: Buck5 and Aquarium, "
         "the job's folders and naming, the show's applications (Maya, V-Ray, Nuke and others) and the farm. "
         "Your files are safe with me: I never overwrite your work, and every version I save comes with a note "
         "of what changed. Brief me like a teammate and I'll find the rest myself.")

BRIEF = """**Skills**
Kien has set up a set of common skills for the team, for example:
- `/tessera:lighting`: light a shot, from first pass to final
- `/tessera:modeling`: model an asset, from first blockout to final

**How to use them**
- Type `/tessera:` and pick from the list, or
- Just say what you need and I'll pick the right one

**Beyond the list**
I'm not limited to these. Ask for anything in 3D, and if it's something you do often, we can turn it into a new skill together.

**How I work**
- **I stay on the brief.** I change what you asked for; extra ideas come as separate options.
- **I show my progress.** Images go in the chat as I go, so you can give notes early.
- **I ask before anything that can't be undone.**
- **I'm straight about results.** I tell you what I checked and what I didn't.
- **The team can see us.** The dashboard shows what you and I are on%s"""


def local_dir():
    return os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "tessera")


def marker_path():
    return os.path.join(local_dir(), "artist.json")


def read_marker():
    try:
        with open(marker_path(), "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def buck5_dir():
    return os.path.join(os.environ.get("LOCALAPPDATA", ""), "buck", "Buck5")


def newest_env():
    """The environment Buck5 wrote for its latest launch: the job, and the local API address."""
    files = glob.glob(os.path.join(buck5_dir(), "rez", "buck_*.env"))
    if not files:
        return {}
    try:
        with open(max(files, key=os.path.getmtime), "r", encoding="utf-8") as fh:
            data = json.load(fh)
        env = data.get("env", data)
        return {k: env.get(k, "") for k in ("BUCK_PROJECT", "BUCK5_DAEMON_HOST")}
    except (OSError, ValueError):
        return {}


def site():
    """BUCK_LOCATION from the environment Buck5 built for its latest launch ("LA"). Empty if it can't be read."""
    if os.environ.get("BUCK_LOCATION"):
        return os.environ["BUCK_LOCATION"]
    files = glob.glob(os.path.join(buck5_dir(), "rez", "*.rxt"))
    rez = "c:/opt/rez/Scripts/rez/rez-env.exe"
    if not files or not os.path.isfile(rez):
        return ""
    try:
        # a command with spaces in it hangs here; "set" with one name does not
        out = subprocess.run([rez, "--input", max(files, key=os.path.getmtime), "--", "cmd", "/c", "set", "BUCK_LOCATION"],
                             capture_output=True, text=True, timeout=20, stdin=subprocess.DEVNULL).stdout
        m = re.search(r"BUCK_LOCATION=(\S+)", out)
        return m.group(1) if m else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def username(given=None):
    return (given or os.environ.get("BUCK_USER") or getpass.getuser()).strip().lower()


def display(user):
    return " ".join(p.capitalize() for p in re.split(r"[._\- ]+", user) if p) or user


def detect_job(given=None):
    return given or read_marker().get("job") or newest_env().get("BUCK_PROJECT") or ""


def agents_dir(job):
    return os.path.join(WORK_ROOT, job, "Production", "Common", "Agents")


def starter_version(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            m = re.search(r"(?m)^Version:\s*(\S+)", fh.read(2000))
        return m.group(1) if m else ""
    except OSError:
        return ""


def plugin_root():
    """<root>/skills/<skill>/scripts/start.py in the plugin; None for a copied-folder install."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
    return root if os.path.isfile(os.path.join(root, ".claude-plugin", "plugin.json")) else None


def version_key(text):
    return [int(n) for n in re.findall(r"\d+", text)]


# ---- the checks: each returns (name, result, line); result is pass, fail or pick ----

def check_buck5():
    port = None
    log = os.path.join(buck5_dir(), "logs", "Buck5.log")
    try:
        with open(log, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = re.search(r"Proxy listening on (\d+)", line)
                if m:
                    port = int(m.group(1))
    except OSError:
        pass
    if not port:
        m = re.search(r"(\d{4,5})\s*$", str(newest_env().get("BUCK5_DAEMON_HOST", "")))
        port = int(m.group(1)) if m else None
    if port:
        try:
            socket.create_connection(("127.0.0.1", port), timeout=3).close()
            return "Buck5", "pass", "running"
        except OSError:
            pass
    return "Buck5", "fail", "open Buck5, then say \"retry\""


def check_job(job):
    if os.path.isdir(os.path.join(WORK_ROOT, job, "Production")):
        return "Job folder", "pass", "I can reach the job on the server"
    return "Job folder", "fail", "I can't reach `%s` on the server; check the network drive, then say \"retry\"" % job


def check_scratch(job, agent):
    for drive in ("D:\\",):
        if os.path.isdir(drive):
            folder = os.path.join(drive, "Agents", agent, job)
            existed = os.path.isdir(folder)
            try:
                os.makedirs(folder, exist_ok=True)
                return "Scratch folder", "pass", "%s `%s\\`" % ("found" if existed else "created", folder)
            except OSError:
                return "Scratch folder", "fail", "I can't create `%s\\`" % folder
    return ("Scratch folder", "pick",
            "no `D:` drive. Use `C:\\Agents\\%s\\%s\\` or name another folder" % (agent, job))


def check_skills(job):
    root = plugin_root()
    mine = starter_version(os.path.join(root, "BUCK_AGENT_STARTER.md")) if root else ""
    theirs = starter_version(os.path.join(agents_dir(job), "BUCK_AGENT_STARTER.md"))
    if not mine:
        return "Skills", "not assessed", "not installed as the plugin, so I read them from the job's folder"
    if theirs and version_key(theirs) > version_key(mine):
        return "Skills", "fail", "the job has a newer set (%s, you have %s); update the plugin, restart, then say \"retry\"" % (theirs, mine)
    return "Skills", "pass", "you have the latest set"


def check_dashboard(job, user):
    folder = os.path.join(agents_dir(job), "Activity")
    probe = os.path.join(folder, "_check_%s_%s.tmp" % (re.sub(r"[^a-z0-9]+", "-", user), os.getpid()))
    try:
        if not os.path.isdir(folder):
            if not os.path.isdir(agents_dir(job)):
                raise OSError("no Agents folder")
            os.mkdir(folder)
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write("check")
        os.remove(probe)
        return "Team dashboard", "pass", "the team can see what you and I are working on"
    except OSError:
        return "Team dashboard", "not assessed", "this job isn't set up for it yet; your work is unaffected"


def dashboard_link(job):
    """A line 'Dashboard: <address>' in the job's SHOW.md, if someone has added one."""
    try:
        with open(os.path.join(agents_dir(job), "SHOW.md"), "r", encoding="utf-8") as fh:
            m = re.search(r"(?mi)^\W*Dashboard\W*[:|]\s*`?(\S+?)`?\s*\|?\s*$", fh.read())
        return m.group(1) if m else ""
    except OSError:
        return ""


# ---- commands ----

def welcome(args):
    user, job = username(args.user), detect_job(args.job)
    out = ["Welcome, %s." % display(user), "", INTRO, "",
           "This is your first session here, so a quick setup first.", "", "I picked up:",
           "- **Your Buck5 username:** %s" % user,
           "- **Machine:** `%s`" % socket.gethostname()]
    where = site()
    if where:
        out.append("- **Site:** %s" % where)
    if job:
        out += ["- **Job:** %s" % job, "", "Is that right?", "- a. Yes", "- b. Wrong job", "- c. Wrong username"]
    else:
        out += ["- **Job:** not found; Buck5 hasn't launched one on this machine yet", "",
                "Which job are you on?"]
    print("\n".join(out))
    return 0


def check(args):
    user = username(args.user)
    job = check_job(args.job)
    # no folder is made for a job that isn't there
    scratch = check_scratch(args.job, args.agent) if job[1] == "pass" else ("Scratch folder", "not assessed", "waiting on the job folder")
    results = [check_buck5(), job, scratch, check_skills(args.job), check_dashboard(args.job, user)]
    out = ["Checking this workstation.", "", "| Check | Result |", "|---|---|"]
    bad = 0
    for name, result, line in results:
        if result in ("fail", "pick"):
            bad += 1
            out.append("| %s | **%s**: %s |" % (name, "fail" if result == "fail" else "needs a pick", line))
        else:
            out.append("| %s | %s, %s |" % (name, result, line))
    out += ["", "The scratch folder is on this machine. My test scenes, scripts and review images go there; "
                "only finished versions go on the server."]
    print("\n".join(out))
    return 1 if bad else 0


def finish(args):
    user = username(args.user)
    notes = []
    folder = os.path.join(agents_dir(args.job), "Artists", user)
    target = os.path.join(folder, "ARTIST.md")
    if os.path.isdir(agents_dir(args.job)) and not os.path.exists(target):
        template = ""
        root = plugin_root()
        for path in (os.path.join(agents_dir(args.job), "Artists", "ARTIST_TEMPLATE.md"),
                     os.path.join(root, "ARTIST_TEMPLATE.md") if root else ""):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    template = fh.read()
                break
            except OSError:
                continue
        if template:
            text = template.replace("| Name | |", "| Name | %s |" % display(user), 1)
            text = re.sub(r"(?m)^\| Version suffix \| .*$", "| Version suffix | %s |" % user, text, count=1)
            try:
                os.makedirs(folder, exist_ok=True)
                with open(target, "x", encoding="utf-8", newline="\n") as fh:   # "x": never overwrites
                    fh.write(text)
                notes.append("created " + target)
            except OSError as err:
                notes.append("ARTIST.md not created (%s)" % err)
    os.makedirs(local_dir(), exist_ok=True)
    with open(marker_path(), "w", encoding="utf-8") as fh:
        json.dump({"username": user, "job": args.job, "machine": socket.gethostname(),
                   "set_up": datetime.date.today().isoformat()}, fh)
    link = dashboard_link(args.job)
    print(BRIEF % (": " + link if link else "."))
    print("\nYou're set up.")
    for n in notes:
        print("[for the agent, not the artist: %s]" % n)
    return 0


def hook():
    """Session start. Says only what the agent needs; reads one small local file, nothing on the network."""
    mark = read_marker()
    if not mark:
        print("tessera: this artist has not been set up on this machine. If this session is work on a studio job, "
              "run the tessera:start skill before anything else: hold their request, do the setup, then return to it.")
        return
    job = mark.get("job", "")
    print("tessera: artist %s, last job %s. If this session is work on that job, read %s and SHOW.md beside it, "
          "and follow them before working. No setup needed." % (
              mark.get("username", ""), job, agents_dir(job).replace("\\", "/") + "/BUCK_AGENT_STARTER.md"))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    for name in ("welcome", "check", "finish"):
        p = sub.add_parser(name)
        p.add_argument("--job", required=name != "welcome")
        p.add_argument("--user")
        if name == "check":
            p.add_argument("--agent", default="ClaudeCode")
    sub.add_parser("hook")
    sub.add_parser("reset")
    args = ap.parse_args()
    if args.cmd == "hook":
        try:
            hook()
        except Exception:
            pass
        return 0
    if args.cmd == "reset":
        try:
            os.remove(marker_path())
        except OSError:
            pass
        print("reset")
        return 0
    if args.cmd in ("welcome", "check", "finish"):
        return {"welcome": welcome, "check": check, "finish": finish}[args.cmd](args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
