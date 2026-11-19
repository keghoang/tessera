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
this machine only, and opens it in the browser. The job is read again every minute and the
page refreshes itself. Everything it writes is local: %LOCALAPPDATA%\\tessera\\dashboard.
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
EVERY = 60            # seconds between reads of the job
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
            return r.read().strip() == b"tessera-dashboard"
    except Exception:
        return False


def copy_page():
    out = local_dir()
    for rel in PAGE_FILES:
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(HERE, rel), dst)
    os.makedirs(os.path.join(out, "data"), exist_ok=True)
    with open(os.path.join(out, "alive.txt"), "w") as fh:
        fh.write("tessera-dashboard")


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


def serve():
    """The local server: this machine only, re-reads the listed jobs every minute, stops when unused."""
    import functools
    import socket
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    last = [time.time()]

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if not self.path.startswith("/alive.txt"):
                last[0] = time.time()
            SimpleHTTPRequestHandler.do_GET(self)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            SimpleHTTPRequestHandler.end_headers(self)

        def log_message(self, *args):
            pass

    handler = functools.partial(Handler, directory=local_dir())
    server = None
    for port in [PORT] + list(range(PORT + 1, PORT + 20)):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), handler)
            break
        except (OSError, socket.error):
            continue
    if server is None:
        return
    state = read_state()
    state["port"] = server.server_address[1]
    state["pid"] = os.getpid()
    write_state(state)

    def refresh():
        while True:
            time.sleep(EVERY)
            if time.time() - last[0] > IDLE_EXIT or read_state().get("pid") != os.getpid():
                server.shutdown()
                return
            for job in read_state().get("jobs", []):
                try:
                    collect(job)
                except Exception:
                    pass

    threading.Thread(target=refresh, daemon=True).start()
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
