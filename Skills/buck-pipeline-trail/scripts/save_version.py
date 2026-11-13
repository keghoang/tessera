#!/usr/bin/env python
"""Put a new version on the server without ever overwriting a file.

Command line (any file: .mb, .ma, .nk, ...):

    save_version.py <local file> <server path>
    save_version.py --next <server work folder> <Shot>_<task> <ext>     -> prints the next free version path

Inside mayapy (saves the open scene):

    import save_version
    path = save_version.save_maya("//buck/work/current/<JOB>/.../SH010_lgt_v011.mb", "D:/Agents/<agent>/<JOB>")

How it works: the file is saved or built in local scratch, then copied to the
server with an exclusive create, which fails if anything is already there. The
copy is compared with the local file by size and hash before it is reported as
saved. Python 3.7+, standard library only.
"""
from __future__ import print_function

import hashlib
import os
import re
import shutil
import sys

BLOCKED_PARTS = ("publish",)
BLOCKED_ROOTS = ("//buck/globalprefs",)
VERSION_RE = re.compile(r"_v(\d{3})(?:_[A-Za-z0-9]+)?\.[A-Za-z0-9]+$")


class Refused(Exception):
    pass


def _norm(path):
    return path.replace("\\", "/")


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_target(server_path):
    """Raise Refused unless server_path is a legal place for a new version."""
    p = _norm(server_path)
    if not (p.startswith("//") or re.match(r"^[A-Za-z]:/", p)):
        raise Refused("not an absolute path: %s" % server_path)
    low = p.lower()
    if any(part in BLOCKED_PARTS for part in low.split("/")):
        raise Refused("the path is inside a publish folder; the artist publishes through Buck5.")
    if any(low.startswith(root) for root in BLOCKED_ROOTS):
        raise Refused("the path is inside GlobalPrefs.")
    if not VERSION_RE.search(p):
        raise Refused("the file name has no _v### version: %s" % os.path.basename(p))
    folder = os.path.dirname(p)
    if not os.path.isdir(folder):
        raise Refused("folder does not exist: %s. Ask the artist to generate the task folders through Buck5." % folder)
    if os.path.lexists(p):
        raise Refused("already exists: %s. Save to the next free version." % p)
    return p


def next_version(folder, stem, ext):
    """Next free <stem>_v###.<ext> in folder, counting every existing version and suffix."""
    ext = ext.lstrip(".")
    pat = re.compile(r"^%s_v(\d{3})(?:_[A-Za-z0-9]+)?\.[A-Za-z0-9]+$" % re.escape(stem), re.I)
    used = [int(m.group(1)) for m in (pat.match(n) for n in os.listdir(folder)) if m]
    return _norm(os.path.join(folder, "%s_v%03d.%s" % (stem, max(used or [0]) + 1, ext)))


def put(local_file, server_path):
    """Copy local_file to server_path with an exclusive create. Returns the server path."""
    target = check_target(server_path)
    size = os.path.getsize(local_file)
    if size == 0:
        raise Refused("the local file is empty: %s" % local_file)
    free = shutil.disk_usage(os.path.dirname(target)).free
    if free < size * 2:
        raise Refused("not enough free space on the server share for %d bytes." % size)
    try:
        with open(target, "xb") as dst, open(local_file, "rb") as src:   # "x": fails if the file exists
            shutil.copyfileobj(src, dst, 8 << 20)
    except FileExistsError:
        raise Refused("already exists (someone saved it just now): %s" % target)
    if os.path.getsize(target) != size or _sha(target) != _sha(local_file):
        raise Refused("the server copy does not match the local file. The partial file is at %s: "
                      "tell the artist, do not delete it yourself." % target)
    return target


def save_maya(server_path, scratch, file_type=None):
    """Save the open Maya scene as a new server version. Call from mayapy or Maya."""
    from maya import cmds   # noqa: only available inside Maya

    target = check_target(server_path)
    ext = os.path.splitext(target)[1].lower()
    file_type = file_type or {".mb": "mayaBinary", ".ma": "mayaAscii"}.get(ext)
    if not file_type:
        raise Refused("not a Maya file: %s" % target)
    stage = os.path.join(scratch, "save_stage")
    os.makedirs(stage, exist_ok=True)
    local = _norm(os.path.join(stage, os.path.basename(target)))
    if shutil.disk_usage(stage).free < (2 << 30):
        raise Refused("under 2 GB free on the scratch drive; a full drive truncates saves silently.")
    cmds.file(rename=local)
    cmds.file(save=True, type=file_type, force=True)      # force only replaces the local staging copy
    saved = put(local, target)
    cmds.file(rename=saved)                               # the session now points at the server file
    os.remove(local)
    return saved


def main(argv):
    try:
        if len(argv) == 4 and argv[0] == "--next":
            print(next_version(argv[1], argv[2], argv[3]))
            return 0
        if len(argv) == 2:
            saved = put(argv[0], argv[1])
            print("saved", saved, os.path.getsize(saved), "bytes, hash verified")
            return 0
    except Refused as err:
        print("REFUSED:", err, file=sys.stderr)
        return 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
