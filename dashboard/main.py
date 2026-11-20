"""Agent Dashboard: who is on which shot, what agents are doing now, and the last changes.

Entry point. Run it from Galt inside a Buck5 host (Maya, Nuke, Houdini), double-click
"Agent Dashboard.bat" with no host open, or use a terminal. It runs as its own process and its
own window: closing the host does not close it. Only one dashboard window is open at a time;
launching it again closes the one that is open and opens a fresh one.

    python main.py                 the job of the current Buck5 environment
    python main.py --job <JOB>     another job
    python main.py --stop          stop the local server

What it does: copies the page to a local folder, reads the job (folder listings, the newest
work file per task, the .trail beside it, and the agents' status files), serves the page on
this machine only, and opens it in its own window. Agent status is watched every couple of
seconds and pushed to the page as it changes; the whole job is read again once a minute. Everything it writes is local: %LOCALAPPDATA%\\tessera\\dashboard.
It only reads the job. Python 3.7+, standard library only.
"""
from __future__ import print_function

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE_FILES = ["index.html"]   # the page is one file: its styles and script are inside it
PYTHON = r"c:\opt\rez\Scripts\python.exe"   # on every BUCK workstation; a host's own executable is not a Python
WORK_ROOT = r"\\buck\work\current"
PORT = 8765
EVERY = 60            # seconds between full reads of the job (folders, versions, notes)
WATCH = 2             # seconds between looks at the agents' status files, which is one small folder
SERVER = "4"          # raised when the server changes, so an older one still running is replaced
IDLE_EXIT = 45 * 60   # the server stops when no page has asked for anything this long
NO_WINDOW = 0x08000000
DETACHED = 0x00000008 | 0x00000200 | NO_WINDOW


def local_dir():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, "tessera", "dashboard")


def slug(job):
    return re.sub(r"[^A-Za-z0-9_-]", "-", job).lower()


def current_job():
    """The job of the Buck5 environment this runs in, else of the newest environment Buck5 built."""
    job = os.environ.get("BUCK_PROJECT")
    if job:
        return job
    envs = glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "buck", "Buck5", "rez", "buck_*.env"))
    for path in sorted(envs, key=os.path.getmtime, reverse=True):
        try:
            with open(path, "r") as fh:
                job = json.load(fh).get("env", {}).get("BUCK_PROJECT", "")
        except (OSError, ValueError, AttributeError):
            continue
        if job:
            return job
    return ""


def job_root(job):
    root = (os.environ.get("BUCK_WORK_ROOT") or WORK_ROOT).replace("/", "\\")
    return os.path.join(root, job)


def python_exe():
    if os.path.isfile(PYTHON):
        return PYTHON
    exe = sys.executable or ""
    return exe if os.path.basename(exe).lower().startswith("python") else ""


def clean_env():
    """A host sets Python variables for its own interpreter; they must not reach ours."""
    env = dict(os.environ)
    for key in ("PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP"):
        env.pop(key, None)
    return env


def spawn(args):
    return subprocess.Popen([python_exe(), os.path.join(HERE, "main.py")] + args, env=clean_env(), close_fds=True,
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            creationflags=DETACHED if os.name == "nt" else 0)


# ---------------------------------------------------------------- local state

def read_state():
    try:
        with open(os.path.join(local_dir(), "server.json"), "r") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def write_state(state):
    path = os.path.join(local_dir(), "server.json")
    with open(path + ".tmp", "w") as fh:
        json.dump(state, fh)
    os.replace(path + ".tmp", path)


def server_alive(state):
    port = state.get("port")
    if not port:
        return False
    try:
        from urllib.request import urlopen
        with urlopen("http://127.0.0.1:%d/alive.txt" % port, timeout=2) as r:
            return r.read().strip() == ("tessera-dashboard " + SERVER).encode()
    except Exception:
        return False


def stop_old_server(state):
    """A server from an earlier version of this tool may still be running: stop it so the current one can start."""
    pid = state.get("pid")
    if pid and os.name == "nt":
        try:
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], timeout=10, stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=NO_WINDOW)
        except (OSError, subprocess.SubprocessError):
            pass
        time.sleep(0.5)


def copy_page():
    out = local_dir()
    for rel in PAGE_FILES:
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(HERE, rel), dst)
    os.makedirs(os.path.join(out, "data"), exist_ok=True)


def collect(job):
    """Read the job into data/<slug>.json. Returns an error line, or '' when it worked."""
    out = os.path.join(local_dir(), "data", slug(job) + ".json")
    tmp = os.path.join(local_dir(), "data", "_" + slug(job) + ".part")
    run = subprocess.run([python_exe(), os.path.join(HERE, "collect.py"), "--job-root", job_root(job), "--out", tmp],
                         env=clean_env(), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         creationflags=NO_WINDOW if os.name == "nt" else 0)
    if run.returncode != 0 or not os.path.isfile(tmp):
        lines = (run.stderr or run.stdout or b"").decode("utf-8", "replace").strip().splitlines()
        return lines[-1] if lines else "could not read the job"
    os.replace(tmp, out)
    return ""


# ---------------------------------------------------------------- the three modes

def launch(job):
    """From a host or a terminal: hand over to a background helper and return at once."""
    if not python_exe():
        print("Agent Dashboard: no Python found at %s." % PYTHON)
        return
    if not job:
        print("Agent Dashboard: no job found. Launch from a Buck5 host, or run: main.py --job <JOB>")
        return
    if not os.path.isdir(os.path.join(job_root(job), "Production")):
        print("Agent Dashboard: no Production folder under %s" % job_root(job))
        return
    spawn(["--open", "--job", job])
    print("Agent Dashboard: reading %s, the page opens in your browser in a moment." % job)


def open_job(job):
    """Background helper: make sure the page, the data and the server exist, then open the browser."""
    copy_page()
    state = read_state()
    jobs = state.get("jobs", [])
    if job not in jobs:
        jobs.append(job)
    alive = server_alive(state)
    if not alive:
        stop_old_server(state)
        state = {"port": 0, "jobs": jobs}
    state["jobs"] = jobs
    write_state(state)
    error = collect(job)
    if error:
        with open(os.path.join(local_dir(), "last_error.txt"), "w") as fh:
            fh.write(error)
        return
    if not alive:
        spawn(["--serve"])
        for _ in range(40):
            time.sleep(0.25)
            state = read_state()
            if server_alive(state):
                break
    show("http://127.0.0.1:%d/index.html#%s" % (state.get("port") or PORT, slug(job)))


WINDOW_PROFILE = "tessera-dashboard-window"   # the dashboard's own browser profile; also how its window is found again


def close_window():
    """Close the dashboard window that is already open, so there is only ever one.

    The window runs in its own browser profile, so its processes can be told apart from the
    artist's own browser by that profile's folder on their command line. Nothing else is touched.
    """
    if os.name != "nt":
        return
    find = ("$p = Get-CimInstance Win32_Process | Where-Object { ($_.Name -eq 'msedge.exe' -or $_.Name -eq 'chrome.exe') "
            "-and $_.CommandLine -like '*%s*' }; " % WINDOW_PROFILE)
    script = (find +
              # ask the window to close, the way clicking its close button would
              "$p | Where-Object { $_.CommandLine -notlike '*--type=*' } | ForEach-Object { "
              "$w = Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue; if ($w) { [void]$w.CloseMainWindow() } }; "
              "for ($i = 0; $i -lt 12; $i++) { " + find + "if (-not $p) { break }; Start-Sleep -Milliseconds 150 }; "
              # anything still there is stopped
              "$p | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }")
    try:
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], timeout=20,
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=NO_WINDOW)
    except (OSError, subprocess.SubprocessError):
        pass


def show(url):
    """Open the page as its own window (no tabs, no address bar, its own taskbar button), else as a browser tab.

    Only one dashboard window exists at a time: opening it again closes the one that is open.
    """
    close_window()
    profile = os.path.join(local_dir(), WINDOW_PROFILE)
    roots = [os.environ.get(k, "") for k in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA")]
    for rel in (r"Microsoft\Edge\Application\msedge.exe", r"Google\Chrome\Application\chrome.exe"):
        for root in roots:
            exe = os.path.join(root, rel) if root else ""
            if exe and os.path.isfile(exe):
                try:
                    subprocess.Popen([exe, "--app=" + url, "--user-data-dir=" + profile, "--no-first-run",
                                      "--no-default-browser-check", "--hide-crash-restore-bubble", "--window-size=1500,950"],
                                     close_fds=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                     creationflags=0x00000008 | 0x00000200 if os.name == "nt" else 0)
                    return
                except OSError:
                    pass
    import webbrowser
    webbrowser.open(url)


def read_live(folder, job, seen):
    """The agent sessions on this job, from the status files in the job's Agents/Activity folder.

    One directory listing and one look at each file per call. A file is only opened again when its size
    or time changed. `seen` is the cache, kept between calls.
    """
    import datetime
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from collect import settle
    found, here = [], {}
    try:
        entries = [e for e in os.scandir(folder) if e.name.endswith(".json")]
    except OSError:
        return found
    for e in entries:
        try:
            st = os.stat(e.path)      # asked of the file itself: the folder listing's times can be minutes behind
        except OSError:
            continue
        stamp = (st.st_mtime_ns, st.st_size)
        got = seen.get(e.name)
        if not got or got[0] != stamp:
            try:
                with open(e.path, "r", encoding="utf-8") as fh:
                    got = (stamp, json.JSONDecoder().raw_decode(fh.read().lstrip("\ufeff"))[0])
            except (OSError, ValueError):
                continue
        here[e.name] = got
        if isinstance(got[1], dict) and got[1].get("job") == job:
            found.append(got[1])
    seen.clear()
    seen.update(here)
    # nothing is dropped for being old: an ended or silent session stays as its task's last state, idle
    return settle(found, datetime.datetime.now())


def serve():
    """The local server, on this machine only.

    It looks at the agents' status files every couple of seconds and pushes a change to the open page the
    moment it sees one. The full read of the job (folders, versions, notes) runs once a minute, and at once
    when an agent's status changes, since that is when a version is likely to have been saved.
    It stops by itself when no page has been open for a while.
    """
    import datetime
    import functools
    import queue
    import socket
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    from urllib.parse import parse_qs, urlparse

    last = [time.time()]
    clients, lock = {}, threading.Lock()       # data name -> the queues of the pages showing it

    def push(name, event, payload):
        with lock:
            waiting = list(clients.get(name, ()))
        for q in waiting:
            q.put((event, payload))

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/alive.txt"):
                body = ("tessera-dashboard " + SERVER).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            last[0] = time.time()
            if self.path.startswith("/events"):
                return self.events()
            SimpleHTTPRequestHandler.do_GET(self)

        def events(self):
            """One open page. The connection stays open and changes are written to it as they happen."""
            name = (parse_qs(urlparse(self.path).query).get("job") or [""])[0]
            q = queue.Queue()
            with lock:
                clients.setdefault(name, set()).add(q)
            try:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                self.wfile.write(b": connected\n\n")
                self.wfile.flush()
                while True:
                    try:
                        event, payload = q.get(timeout=15)
                        message = "event: %s\ndata: %s\n\n" % (event, json.dumps(payload))
                    except queue.Empty:
                        message = ": still here\n\n"
                    self.wfile.write(message.encode("utf-8"))
                    self.wfile.flush()
                    last[0] = time.time()
            except (OSError, ValueError):
                pass
            finally:
                with lock:
                    clients.get(name, set()).discard(q)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            SimpleHTTPRequestHandler.end_headers(self)

        def log_message(self, *args):
            pass

    class Server(ThreadingHTTPServer):
        # On Windows the default lets a second server bind a port that is already in use, and the
        # older one keeps getting the requests. Refuse instead, so the next free port is taken.
        allow_reuse_address = False

    handler = functools.partial(Handler, directory=local_dir())
    server = None
    for port in [PORT] + list(range(PORT + 1, PORT + 20)):
        try:
            server = Server(("127.0.0.1", port), handler)
            break
        except (OSError, socket.error):
            continue
    if server is None:
        return
    server.daemon_threads = True
    state = read_state()
    state["port"] = server.server_address[1]
    state["pid"] = os.getpid()
    write_state(state)

    def data_file(job):
        return os.path.join(local_dir(), "data", slug(job) + ".json")

    def watch():
        shown, seen, full_at = {}, {}, {}
        while True:
            time.sleep(WATCH)
            current = read_state()
            if time.time() - last[0] > IDLE_EXIT or current.get("pid") != os.getpid():
                server.shutdown()
                return
            for job in current.get("jobs", []):
                name = slug(job)
                try:
                    live = read_live(os.path.join(job_root(job), "Production", "Common", "Agents", "Activity"),
                                     job, seen.setdefault(job, {}))
                    if job in shown and live != shown[job]:
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        push(name, "live", {"live": live, "now": now})
                        try:          # keep the stored copy true too, for a page that opens right now
                            with open(data_file(job), "r", encoding="utf-8") as fh:
                                data = json.load(fh)
                            data["live"], data["now"] = live, now
                            data["people"] = sorted(set(data.get("people", [])) | {s["person"] for s in live})
                            with open(data_file(job) + ".tmp", "w", encoding="utf-8") as fh:
                                json.dump(data, fh)
                            os.replace(data_file(job) + ".tmp", data_file(job))
                        except (OSError, ValueError):
                            pass
                        full_at[job] = time.time() + 3      # a status change often means a version was just saved
                    shown[job] = live
                    if time.time() >= full_at.setdefault(job, time.time() + EVERY):
                        full_at[job] = time.time() + EVERY
                        if not collect(job):
                            push(name, "data", {})
                except Exception:
                    pass

    threading.Thread(target=watch, daemon=True).start()
    server.serve_forever()


def stop():
    os.makedirs(local_dir(), exist_ok=True)
    state = read_state()
    state["pid"] = 0   # the running server sees it is no longer the owner and stops within a minute
    state["jobs"] = []
    write_state(state)
    print("Agent Dashboard: the local server stops within a minute.")


def main(argv=None):
    # Galt calls main() with nothing; a terminal passes arguments.
    argv = [] if argv is None else list(argv)
    job = ""
    if "--job" in argv and argv.index("--job") + 1 < len(argv):
        job = argv[argv.index("--job") + 1]
    if "--serve" in argv:
        return serve()
    if "--stop" in argv:
        return stop()
    if "--open" in argv:
        return open_job(job)
    return launch(job or current_job())


if __name__ == "__main__":
    main(sys.argv[1:])
