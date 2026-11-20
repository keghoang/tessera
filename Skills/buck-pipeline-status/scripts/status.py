#!/usr/bin/env python
"""Report what an agent session is working on, so the job's dashboard can show it.

    status.py set   --job <JOB> --shot <shot or asset> --task <task> --agent "<agent>"
                    --doing "<one line: what is happening now>" [--state working]
    status.py state <working|waiting|farm|idle> --doing "<one line>"
    status.py clear
    status.py hook  <prompt|stop|notify|end>      (called by the plugin, not by hand)

States:
    working   the agent is running a task
    waiting   the agent needs the artist: a question, an approval, a decision
    farm      the agent is waiting on a farm render
    idle      the session is open and nothing is running

The --doing line has a fixed form per state, and a line that breaks it is refused:
    working   starts with an -ing verb     "Adjusting key light ratio on the hero"
    waiting   "Need <name>'s input", then optionally ": <what is needed>"
                                           "Need Kien's input: rim light option A or B"
    farm      starts with "Rendering"      "Rendering test frames 1010, 1088"
    idle      starts with "Saved" or "Finished"   "Saved v015: key light notes applied"
English, one line, at most 72 characters, no full stop at the end, no paths, no "I",
no step counts, no vague verbs (Working on, Processing, Handling, Continuing).

"set" writes one small JSON file for this session into the job's activity folder
(<job>/Production/Common/Agents/Activity unless --dir is given) and removes the
file this session wrote before, so a session shows on one shot and task at a time.
"state" and "clear" act on that file. The file holds no prompt text and no file
contents: only the fields above, the person, the machine and two times.
Python 3.7+, standard library only.
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
import time

STATES = ("working", "waiting", "farm", "idle")
WORK_ROOT = os.environ.get("BUCK_WORK_ROOT", "//buck/work/current")


MAX_LINE = 72
VAGUE = ("working", "processing", "handling", "continuing", "doing", "trying", "starting", "proceeding", "performing")
EXAMPLE = {"working": "Adjusting key light ratio on the hero", "waiting": "Need Kien's input: rim light option A or B",
           "farm": "Rendering test frames 1010, 1088", "idle": "Saved v015: key light notes applied"}


def line_problem(state, text):
    """Why this --doing line is not allowed for this state, or None. One fixed form per state."""
    words = text.split()
    first = words[0] if words else ""
    if not text or text != text.strip() or "\n" in text or "\r" in text:
        return "write one line with no leading or trailing space"
    if len(text) > MAX_LINE:
        return "keep it to %d characters (this one is %d)" % (MAX_LINE, len(text))
    if any(ord(c) < 32 or ord(c) > 126 for c in text):
        return "plain English letters and punctuation only"
    if len(words) < 3:
        return "say what is being done and to what, in at least three words"
    if not first[0].isupper():
        return "start with a capital letter"
    if text.endswith((".", "!", "...")):
        return "no full stop or other mark at the end"
    if "\\" in text or "://" in text or re.search(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/", text) or re.search(r"\.(mb|ma|nk|py|exr|json)\b", text):
        return "no file paths or file names; name the thing in production terms"
    if re.search(r"(?i)\b(i|i'll|i'm|i've|let me|my|we|we'll|our)\b", text):
        return "no first person; describe the work, not the agent"
    if re.search(r"(?i)\bstep \d|\b\d+ ?(of|/) ?\d+\b|\d ?%", text):
        return "no step counts or percentages"
    if state == "working":
        if not re.match(r"^[A-Z][a-z]+ing$", first):
            return "a working line starts with an -ing verb"
        if first == "Waiting":
            return "waiting is a state of its own: use 'state waiting' (the artist) or 'state farm' (a render)"
        if first.lower() in VAGUE:
            return "'%s' says nothing; use the verb for what is actually happening" % first
    elif state == "waiting" and not re.match(r"^Need [A-Z][A-Za-z.-]*'s input(: \S.*)?$", text):
        return "a waiting line reads \"Need <name>'s input\", optionally followed by ': <what is needed>'"
    elif state == "farm" and first != "Rendering":
        return "a farm line starts with 'Rendering' and says what is rendering"
    elif state == "idle" and first not in ("Saved", "Finished"):
        return "an idle line starts with 'Saved' or 'Finished' and gives the outcome"
    return None


# The short task names used in file names. A session that gives the department's name gets the short one.
TASKS = {"animation": "anim", "anim": "anim", "layout": "lyt", "lighting": "lgt", "light": "lgt", "comp": "comp",
         "compositing": "comp", "fx": "fx", "previs": "prev", "modeling": "mdl", "modelling": "mdl", "model": "mdl",
         "rigging": "rig", "lookdev": "lkdv", "look dev": "lkdv", "styleframe": "style"}


def short_task(text):
    key = text.strip().lower()
    return TASKS.get(key, key)


def check_line(state, text):
    problem = line_problem(state, text)
    if problem:
        print("REJECTED: %s.\n  line:    %s\n  example: %s\nFix the line and run the command again."
              % (problem, text, EXAMPLE[state]), file=sys.stderr)
        return False
    return True


def slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def session_id(given=None):
    return slug(given or os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CODEX_SESSION_ID") or "nosession")


def pointer_dir():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, "tessera", "sessions")


def pointer_path(sid):
    return os.path.join(pointer_dir(), sid + ".json")


def read_pointer(sid):
    try:
        with open(pointer_path(sid), "r", encoding="utf-8") as fh:
            return load(fh).get("file", "")
    except (OSError, ValueError):
        return ""


def write_pointer(sid, path):
    folder = pointer_dir()
    os.makedirs(folder, exist_ok=True)
    with open(pointer_path(sid), "w", encoding="utf-8") as fh:
        json.dump({"file": path}, fh)
    # forget pointers of sessions that ended without saying so
    cutoff = time.time() - 7 * 86400
    for name in os.listdir(folder):
        p = os.path.join(folder, name)
        try:
            if os.path.getmtime(p) < cutoff:
                os.remove(p)
        except OSError:
            pass


def load(fh):
    """Read one JSON value and ignore anything after it.

    The job share does not always shorten a file that is rewritten with less text: the old tail stays
    behind as zero bytes, and a plain json.load then rejects the whole file.
    """
    return json.JSONDecoder().raw_decode(fh.read().lstrip("\ufeff"))[0]


def write_json(path, data):
    # Written in place: the job share refuses a rename onto an existing file.
    # A reader that catches the file half-written skips it until the next read.
    # Padded with spaces to a fixed length, so a rewrite never has to shorten the file (see load).
    text = json.dumps(data)
    text += " " * (-len(text.encode("utf-8")) % 512)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def remove(path):
    try:
        os.remove(path)
    except OSError:
        pass


def leave(path):
    """The session is done with this task: keep its last line, as idle, so the dashboard still shows who touched it last."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = load(fh)
        data["state"], data["ended"] = "idle", True
        write_json(path, data)
    except (OSError, ValueError):
        pass


def tidy(folder, keep, person, host, job, shot, task):
    """Remove this person's own ended files for the same task on this machine: the newest report replaces them."""
    start = "_".join(slug(x) for x in (person, host)) + "_"
    try:
        names = [n for n in os.listdir(folder) if n.startswith(start) and n.endswith(".json") and n != keep]
    except OSError:
        return
    for n in names:
        p = os.path.join(folder, n)
        try:
            with open(p, "r", encoding="utf-8") as fh:
                d = load(fh)
        except (OSError, ValueError):
            continue
        if d.get("ended") and (d.get("job"), d.get("shot"), d.get("task")) == (job, shot, task):
            remove(p)


def activity_dir(args):
    """The job's activity folder. Created if the job's Agents folder exists; never anything above it."""
    if args.dir:
        return args.dir if os.path.isdir(args.dir) else None
    agents = os.path.join(WORK_ROOT, args.job, "Production", "Common", "Agents")
    if not os.path.isdir(agents):
        return None
    folder = os.path.join(agents, "Activity")
    if not os.path.isdir(folder):
        try:
            os.mkdir(folder)
        except OSError:
            return None
    return folder


def change_state(sid, state, doing=None, only_from=None):
    path = read_pointer(sid)
    if not path:
        return False
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = load(fh)
    except (OSError, ValueError):
        return False
    if only_from and data.get("state") not in only_from:
        return False
    data["state"] = state
    data["updated"] = now()
    if doing:
        data["doing"] = doing[:160]
        data.pop("auto", None)
    write_json(path, data)
    return True


# The safety net. If a session never reports, the first job file it touches reports for it.
DEPTS = {"modeling": "mdl", "rigging": "rig", "lookdev": "lkdv", "animation": "anim", "layout": "lyt",
         "lighting": "lgt", "comp": "comp", "previs": "prev", "styleframe": "style", "fx": "fx"}
SEP = r"[\\/]+"
NAME = r"[^\\/\"'\s]+"
# Only a versioned work file counts, never a folder: <shot or asset>_<task>_v###, _wip### or _test###,
# under the job on the server or under the job's local scratch folder (Agents/<agent>/<JOB>/).
WORK_FILE = re.compile(r"([A-Za-z0-9]+(?:_[A-Za-z0-9]+)*?)_(" + "|".join(sorted(set(DEPTS.values())))
                       + r")_(?:v|wip|test)\d{3}\.[A-Za-z0-9]+", re.I)
IN_JOB = re.compile(SEP + "work" + SEP + "current" + SEP + "(" + NAME + ")" + SEP + "Production" + SEP, re.I)
IN_SCRATCH = re.compile("Agents" + SEP + NAME + SEP + "(" + NAME + ")" + SEP, re.I)


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            for s in strings(v):
                yield s
    elif isinstance(value, list):
        for v in value:
            for s in strings(v):
                yield s


def touched(tool_input):
    """The job, shot or asset and task of the work file named in one tool call, or None.

    Listing a folder or reading a note is not work on a task, so only a versioned work file counts.
    """
    for text in strings(tool_input):
        job = IN_JOB.search(text) or IN_SCRATCH.search(text)
        name = WORK_FILE.search(text)
        if job and name and not name.group(0).lower().endswith(".trail"):
            return job.group(1), name.group(1), name.group(2).lower()
    return None


def auto_report(sid, job, shot, task):
    """Report for a session that has not reported itself. The agent's own report replaces this."""
    agents = os.path.join(WORK_ROOT, job, "Production", "Common", "Agents")
    folder = os.path.join(agents, "Activity")
    if not os.path.isdir(agents):
        return
    if not os.path.isdir(folder):
        os.mkdir(folder)
    person, host = getpass.getuser().lower(), socket.gethostname()
    name = "_".join(slug(x) for x in (person, host, "Claude Code", sid[:8])) + ".json"
    path = os.path.join(folder, name)
    write_json(path, {"person": person, "machine": host, "agent": "Claude Code", "job": job, "shot": shot, "task": task,
                      "doing": "Working on this task (reported automatically)", "state": "working",
                      "since": now(), "updated": now(), "auto": True})
    write_pointer(sid, path)
    tidy(folder, name, person, host, job, shot, task)


def first_step_note(sid):
    script = os.path.abspath(__file__).replace("\\", "/")
    run = 'c:/opt/rez/Scripts/python.exe "%s"' % script
    data = {}
    path = read_pointer(sid)
    if path:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = load(fh)
        except (OSError, ValueError):
            data = {}
    if data:
        return ("tessera: the dashboard shows this session on %s %s: \"%s\". If this message is work on a job, "
                "your first step, before any other tool call, is to make that true for what you are about to do: "
                "%s state working --doing \"<-ing verb ...>\", or %s set ... if the shot, asset or task changed. "
                "Skip it only if the line already says exactly that."
                % (data.get("shot", "?"), data.get("task", "?"), data.get("doing", ""), run, run))
    return ("tessera: this session reports nothing to the dashboard yet. If this message is work on a job, "
            "your first step, before any other tool call on that work, is: %s set --job <JOB> --shot <shot or asset> "
            "--task <task> --agent \"Claude Code\" --doing \"<-ing verb ...>\". If you must find the shot or task first, "
            "do only that, report, then proceed. Not job work: ignore this." % run)


def hook(event):
    """Keep the state true without the agent having to remember. Never fails.

    On a new message it also prints one note, which the agent reads before it acts:
    what this session reports now, and that correcting it comes first.
    """
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    sid = session_id(payload.get("session_id"))
    if event == "prompt":
        change_state(sid, "working")
        print(first_step_note(sid))
    elif event == "tool":
        # only a session that has not reported: once it has, this costs one local file check
        if sid != "nosession" and not read_pointer(sid):
            hit = touched(payload.get("tool_input"))
            if hit:
                auto_report(sid, *hit)
    elif event == "stop":
        change_state(sid, "idle", only_from=("working",))
    elif event == "notify":
        if payload.get("notification_type") != "idle_prompt":
            change_state(sid, "waiting", only_from=("working",))
    elif event == "end":
        path = read_pointer(sid)
        if path:
            leave(path)
        remove(pointer_path(sid))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("set")
    p.add_argument("--job", required=True)
    p.add_argument("--shot", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--agent", required=True)
    p.add_argument("--doing", required=True)
    p.add_argument("--state", default="working", choices=STATES)
    p.add_argument("--dir", help="activity folder, if not the job's own")
    p.add_argument("--person", default=getpass.getuser().lower())
    p.add_argument("--session")
    p = sub.add_parser("state")
    p.add_argument("state", choices=STATES)
    p.add_argument("--doing", required=True)
    p.add_argument("--session")
    p = sub.add_parser("clear")
    p.add_argument("--session")
    p = sub.add_parser("hook")
    p.add_argument("event", choices=("prompt", "tool", "stop", "notify", "end"))
    args = ap.parse_args()

    if args.cmd == "hook":
        try:
            hook(args.event)
        except Exception:
            pass
        return 0
    if args.cmd not in ("set", "state", "clear"):
        ap.print_help()
        return 2
    sid = session_id(args.session)

    if args.cmd == "set":
        args.task = short_task(args.task)
    if args.cmd in ("set", "state") and not check_line(args.state, args.doing):
        return 4

    if args.cmd == "state":
        if not change_state(sid, args.state, args.doing):
            print("NOT ASSESSED: this session has not reported yet; run 'set' first.", file=sys.stderr)
            return 3
        print("state", args.state)
        return 0

    if args.cmd == "clear":
        path = read_pointer(sid)
        if path:
            leave(path)
        remove(pointer_path(sid))
        print("cleared")
        return 0

    folder = activity_dir(args)
    if not folder:
        print("NOT ASSESSED: no activity folder for %s (the job has no Agents folder, or it is out of reach). "
              "Carry on with the task." % args.job, file=sys.stderr)
        return 3
    host = socket.gethostname()
    name = "_".join(slug(x) for x in (args.person, host, args.agent, sid[:8])) + ".json"
    path = os.path.join(folder, name)
    previous = read_pointer(sid)
    since = now()
    try:
        with open(previous, "r", encoding="utf-8") as fh:
            old = load(fh)
        if (old.get("job"), old.get("shot"), old.get("task")) == (args.job, args.shot, args.task):
            since = old.get("since", since)
    except (OSError, ValueError):
        pass
    if previous and os.path.normcase(os.path.normpath(previous)) != os.path.normcase(os.path.normpath(path)):
        leave(previous)
    write_json(path, {"person": args.person, "machine": host, "agent": args.agent, "job": args.job,
                      "shot": args.shot, "task": args.task, "doing": args.doing[:160], "state": args.state,
                      "since": since, "updated": now()})
    write_pointer(sid, path)
    tidy(folder, name, args.person, host, args.job, args.shot, args.task)
    print("reported", name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
