#!/usr/bin/env python
"""Write and submit a Maya V-Ray job to the Buck Deadline farm, one job per render layer.

    farm_submit.py --scene <server scene> --layer <layer> [--layer ...] --frames <range>
                   --camera <shot camera> --width <px> --height <px> --maya <year>
                   --ocio <config.ocio> --kind test|full --agent "<agent>"
                   --task-id <id> --rxt <copied .rxt> --env <copied .env> --scratch <dir>
                   [--pool onprem] [--group core-farm] [--priority 50] [--allowlist a,b]
                   [--scale 0.5] [--submit] [--release]

Without --submit it is a dry run: the job files are written to scratch and
printed, and nothing reaches the farm. --submit sends each job SUSPENDED from
inside the Buck5 (rez) environment and checks that the farm recorded the show's
software packages. --release then resumes the jobs; without it they stay
suspended. Get --task-id from aquarium.py resolve, and --rxt / --env from
buck5_context.py find. Python 3.7+, standard library only.
"""
from __future__ import print_function

import argparse
import getpass
import json
import os
import re
import socket
import subprocess
import sys

REZ_ENV = r"c:\opt\rez\Scripts\rez\rez-env.exe"
DEADLINE = r"C:\Program Files\Thinkbox\Deadline10\bin\deadlinecommand.exe"


def fwd(path):
    return path.replace("\\", "/")


def build(args, layer):
    scene = fwd(args.scene)
    if "/maya/work/" not in scene or "/Production/" not in scene:
        sys.exit("FAIL: the scene must be a saved server file under <task>/maya/work/: %s" % scene)
    scene_name = os.path.splitext(os.path.basename(scene))[0]
    task_root = scene.split("/maya/work/")[0] + "/maya"
    render_root = task_root + "/render/"
    job_root = scene.split("/Production/")[0] + "/Production"
    job_name = job_root.split("/")[-2]
    width = int(round(args.width * args.scale))
    height = int(round(args.height * args.scale))
    job = [
        "Name=%s - %s" % (scene_name, layer),
        "BatchName=%s" % scene_name,
        "UserName=%s" % args.user,
        "MachineName=%s" % args.machine,
        "Comment=Submitted from %s" % args.agent,
        "Department=%s" % job_name,
        "Frames=%s" % args.frames,
        "ChunkSize=1",
        "Pool=%s" % args.pool,
        "Group=%s" % args.group,
        "Priority=%d" % args.priority,
        "LimitGroups=rez,vray",
        "Plugin=MayaBatch",
        "OutputDirectory0=%s%s/%s" % (render_root, scene_name, layer),
        "OutputFilename0=%s.####.exr" % layer,
        "ExtraInfoKeyValue0=BUCK5_TASK_ID=%s" % args.task_id,
        "ExtraInfoKeyValue1=BUCK_AGENT=%s" % args.agent,
        "ExtraInfoKeyValue2=BUCK_TRAIL=%s" % (os.path.splitext(scene)[0] + ".trail"),
        "ExtraInfoKeyValue3=BUCK_JOB_KIND=%s" % args.kind,
        "EnvironmentKeyValue0=USE_BUCK_ENVIRONMENT_FILE=1",
        "EnvironmentKeyValue1=BUCK_ENVIRONMENT_BLACKLIST=",
        "InitialStatus=Suspended",
    ]
    if args.allowlist:
        job.insert(12, "Allowlist=%s" % args.allowlist)
    plugin = [
        "Animation=1",
        "Renderer=vray",
        "Version=%s" % args.maya,
        "Build=64bit",
        "UsingRenderLayers=1",
        "UseLegacyRenderLayers=1",
        "RenderLayer=%s" % layer,
        "ProjectPath=%s/MAYA" % job_root,
        "SceneFile=%s" % scene,
        "OutputFilePath=%s" % render_root,
        "OutputFilePrefix=%s/<Layer>/<Layer>" % scene_name,
        "ImageWidth=%d" % width,
        "ImageHeight=%d" % height,
        "Camera=%s" % args.camera,
        "EnableOpenColorIO=1",
        "OCIOConfigFile=%s" % fwd(args.ocio),
    ]
    return scene_name, job, plugin


def write(path, lines):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:   # no byte-order mark
        fh.write("\n".join(lines) + "\n")


def buck_vars(env_file):
    with open(env_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    env = data.get("env", data)
    return {k: str(env[k]) for k in ("BUCK_PROJECT", "BUCK_PROJECT_ID", "BUCK_SOFTWARE_ID") if k in env}


def deadline(*cmd):
    return subprocess.run([DEADLINE] + list(cmd), capture_output=True, text=True).stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", required=True)
    ap.add_argument("--layer", required=True, action="append")
    ap.add_argument("--frames", required=True)
    ap.add_argument("--camera", required=True, help="the shot camera, without a leading |")
    ap.add_argument("--width", required=True, type=int, help="the scene's own width")
    ap.add_argument("--height", required=True, type=int, help="the scene's own height")
    ap.add_argument("--scale", type=float, default=1.0, help="resolution scale for a test, only if the artist chose one")
    ap.add_argument("--maya", required=True, help="Maya year, for example 2026")
    ap.add_argument("--ocio", required=True)
    ap.add_argument("--kind", required=True, choices=("test", "full"))
    ap.add_argument("--agent", required=True, help='"Claude Code", "Codex", ...')
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--rxt", required=True)
    ap.add_argument("--env", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--pool", default="onprem")
    ap.add_argument("--group", default="core-farm")
    ap.add_argument("--priority", type=int, default=50)
    ap.add_argument("--allowlist")
    ap.add_argument("--user", default=getpass.getuser())
    ap.add_argument("--machine", default=socket.gethostname())
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--release", action="store_true")
    args = ap.parse_args()

    if not os.path.isfile(args.scene):
        sys.exit("FAIL: scene not found on the server: %s" % args.scene)
    if not re.match(r"^\d+$", str(args.task_id)):
        sys.exit("FAIL: --task-id must be the Aquarium task id (a number).")
    if "|" in args.camera:
        sys.exit("FAIL: strip the leading | from the camera path.")
    if args.release and not args.submit:
        sys.exit("FAIL: --release needs --submit.")

    out_dir = os.path.join(args.scratch, "farm_jobs")
    os.makedirs(out_dir, exist_ok=True)
    built = []
    for layer in args.layer:
        scene_name, job, plugin = build(args, layer)
        job_file = os.path.join(out_dir, "%s_%s_job.job" % (scene_name, layer))
        plugin_file = os.path.join(out_dir, "%s_%s_plugin.job" % (scene_name, layer))
        write(job_file, job)
        write(plugin_file, plugin)
        built.append((layer, job_file, plugin_file))
        print("--- %s\n%s\n--- %s\n%s" % (job_file, "\n".join(job), plugin_file, "\n".join(plugin)))

    if not args.submit:
        print("\nDRY RUN: %d job file pair(s) written, nothing submitted. Add --submit to send them suspended."
              % len(built))
        return 0

    for needed in (REZ_ENV, DEADLINE, args.rxt, args.env):
        if not os.path.isfile(needed):
            sys.exit("NOT ASSESSED: missing %s" % needed)
    env = dict(os.environ)
    env.update(buck_vars(args.env))
    failed = 0
    results = []
    for layer, job_file, plugin_file in built:
        proc = subprocess.run([REZ_ENV, "--input", args.rxt, "--", "deadlinecommand", job_file, plugin_file, args.env],
                              capture_output=True, text=True, env=env)
        m = re.search(r"JobID=([0-9a-f]{24})", proc.stdout)
        if not m:
            print("FAIL: %s was not submitted.\n%s\n%s" % (layer, proc.stdout[-800:], proc.stderr[-800:]))
            failed += 1
            continue
        job_id = m.group(1)
        info = deadline("-GetJob", job_id)
        packages = re.search(r"DEADLINE_REZ_REQUEST_PACKAGES=([^,\n]*)", info)
        ok = bool(packages and packages.group(1).strip())
        results.append({"layer": layer, "id": job_id, "rez_packages": packages.group(1).strip() if ok else "",
                        "state": "suspended"})
        if not ok:
            print("FAIL: job %s (%s) has no DEADLINE_REZ_REQUEST_PACKAGES: it was submitted outside the Buck5 "
                  "environment. It stays suspended; do not release it." % (job_id, layer))
            failed += 1
            continue
        print("submitted suspended: %s  %s  packages: %s" % (job_id, layer, packages.group(1).strip()[:80]))
        if args.release:
            deadline("-ResumeJob", job_id)
            results[-1]["state"] = "released"
            print("released:", job_id)
    print(json.dumps(results, indent=1))
    print("Record each job id in the version's .trail (trail.py job ...).")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
