"""Viewport review captures of a Maya scene from fixed views, run in mayapy.

    mayapy maya_review_capture.py --scene <scene> --out <local folder>
           [--camera <shot camera>] [--frames 1001,1050] [--views three_quarter,front,side,top]
           [--width 1920] [--height 1080] [--look asis|grey] [--label <text>]

Always the same views, framing and size, so captures of two versions can be
compared side by side. The scene is opened as saved (references loaded or not as
the artist left them), is never saved, and images go to a local folder. A
manifest.json lists every capture as "pass" or "not assessed"; a missing or
blank image is "not assessed", never a pass.

Viewport 2.0 drawn offscreen: this is a model and animation review look, not a
render. Scenes that carry V-Ray materials can draw white; use --look grey.
"""
from __future__ import print_function

import argparse
import json
import math
import os
import shutil
import sys

VIEWS = {  # name: (direction the camera looks from, orthographic)
    "three_quarter": ((1.0, 0.62, 1.0), False),
    "front": ((0.0, 0.0, 1.0), True),
    "side": ((1.0, 0.0, 0.0), True),
    "top": ((0.0, 1.0, 0.0), True),
    "back": ((0.0, 0.0, -1.0), True),
}


def parse():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--camera", help="shot camera (short name, no leading |)")
    ap.add_argument("--frames", help="comma-separated frames; default is the current frame")
    ap.add_argument("--views", default="three_quarter,front,side,top")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--look", default="asis", choices=("asis", "grey"))
    ap.add_argument("--label", default="")
    return ap.parse_args()


def scene_bounds(cmds):
    shapes = [s for s in cmds.ls(type="mesh", noIntermediate=True, long=True) or []
              if cmds.getAttr(s + ".visibility")]
    if not shapes:
        return None
    box = [1e30, 1e30, 1e30, -1e30, -1e30, -1e30]
    step = 500
    for i in range(0, len(shapes), step):
        b = cmds.exactWorldBoundingBox(shapes[i:i + step], ignoreInvisible=True)
        box = [min(box[k], b[k]) for k in range(3)] + [max(box[k + 3], b[k + 3]) for k in range(3)]
    return box


def make_camera(cmds, name, direction, ortho, box, aspect):
    """A camera looking at the bounding box from `direction`, framed on its projected extents."""
    centre = [(box[k] + box[k + 3]) / 2.0 for k in range(3)]
    length = math.sqrt(sum(v * v for v in direction))
    d = [v / length for v in direction]                       # from the centre toward the camera
    yaw = math.atan2(d[0], d[2])
    pitch = -math.asin(max(-1.0, min(1.0, d[1])))
    right = [math.cos(yaw), 0.0, -math.sin(yaw)]
    up = [d[1] * right[2] - d[2] * right[1], d[2] * right[0] - d[0] * right[2], d[0] * right[1] - d[1] * right[0]]
    half_w = half_h = half_d = 0.001
    for ix in (0, 3):
        for iy in (1, 4):
            for iz in (2, 5):
                rel = [box[ix] - centre[0], box[iy] - centre[1], box[iz] - centre[2]]
                half_w = max(half_w, abs(sum(rel[k] * right[k] for k in range(3))))
                half_h = max(half_h, abs(sum(rel[k] * up[k] for k in range(3))))
                half_d = max(half_d, abs(sum(rel[k] * d[k] for k in range(3))))
    cam, shape = cmds.camera(name="review_%s_cam" % name)
    margin = 1.08
    if ortho:
        cmds.setAttr(shape + ".orthographic", 1)
        cmds.setAttr(shape + ".orthographicWidth", 2.0 * margin * max(half_w, half_h * aspect))
        dist = half_d * 2.0 + max(half_w, half_h) * 2.0
    else:
        hfov = 2.0 * math.atan(cmds.getAttr(shape + ".horizontalFilmAperture") * 25.4 /
                               (2.0 * cmds.getAttr(shape + ".focalLength")))
        vfov = 2.0 * math.atan(math.tan(hfov / 2.0) / aspect)
        dist = half_d + margin * max(half_w / math.tan(hfov / 2.0), half_h / math.tan(vfov / 2.0))
    cmds.setAttr(cam + ".translate", *[centre[k] + d[k] * dist for k in range(3)])
    cmds.setAttr(cam + ".rotate", math.degrees(pitch), math.degrees(yaw), 0)
    cmds.setAttr(shape + ".nearClipPlane", max(0.001, (dist - half_d) * 0.2))
    cmds.setAttr(shape + ".farClipPlane", (dist + half_d) * 5.0)
    return cam


def review_lights(cmds):
    """Two plain directional lights, in this session only."""
    for name, rot, intensity in (("review_key_lgt", (-42, 35, 0), 1.5), ("review_fill_lgt", (-12, -130, 0), 0.5)):
        shape = cmds.directionalLight(name=name, intensity=intensity)
        xform = cmds.listRelatives(shape, parent=True)[0]
        cmds.setAttr(xform + ".rotate", *rot)


def blank(om, path):
    """True if the image is one flat colour (nothing drawn)."""
    img = om.MImage()
    img.readFromFile(path)
    w, h = img.getSize()
    import ctypes
    count = w * h * 4
    buf = (ctypes.c_ubyte * count).from_address(int(img.pixels()))
    first = bytes(buf[0:4])
    stride = max(4, (count // 4000) // 4 * 4)
    for i in range(0, count - 4, stride):
        if bytes(buf[i:i + 4]) != first:
            return False
    return True


def main():
    args = parse()
    out = os.path.abspath(args.out).replace("\\", "/")
    if out.startswith("//"):
        sys.exit("REFUSED: review captures stay in local scratch, not on the server.")
    os.makedirs(out, exist_ok=True)

    import maya.standalone
    maya.standalone.initialize(name="python")
    from maya import cmds
    import maya.api.OpenMaya as om

    manifest = {"scene": args.scene, "look": args.look, "size": [args.width, args.height],
                "maya": cmds.about(version=True), "captures": [], "notes": []}
    cmds.file(args.scene, open=True, force=True)          # as saved: no loadReferenceDepth, no ignoreVersion
    manifest["scene_units"] = cmds.currentUnit(query=True, linear=True)

    light_types = [t for t in ("light", "VRayLightRectShape", "VRayLightDomeShape", "VRayLightSphereShape",
                               "VRaySunShape", "VRayLightIESShape", "VRayLightMeshLightLinking")
                   if t in (cmds.allNodeTypes() or []) or t == "light"]
    has_lights = bool(cmds.ls(type=light_types))
    if args.look == "grey":
        meshes = cmds.ls(type="mesh", noIntermediate=True, long=True) or []
        shader = cmds.shadingNode("lambert", asShader=True, name="review_grey_mtl")
        cmds.setAttr(shader + ".color", 0.7, 0.7, 0.7, type="double3")
        group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="review_grey_SG")
        cmds.connectAttr(shader + ".outColor", group + ".surfaceShader")
        missed = 0
        for i in range(0, len(meshes), 500):
            try:
                cmds.sets(meshes[i:i + 500], edit=True, forceElement=group)
            except RuntimeError:
                missed += 1
        if missed:
            manifest["notes"].append("grey look not applied to every mesh (%d batches failed)" % missed)
        for light in cmds.ls(type=light_types) or []:
            parent = cmds.listRelatives(light, parent=True, fullPath=True)
            try:
                cmds.setAttr((parent[0] if parent else light) + ".visibility", 0)
            except RuntimeError:
                pass
        review_lights(cmds)
        manifest["notes"].append("grey look: review material and two review lights, scene lights hidden")
    elif not has_lights:
        review_lights(cmds)
        manifest["notes"].append("the scene has no lights: two review lights added for the capture")
    cmds.displayPref(displayGradient=False)
    cmds.displayRGBColor("background", 0.27, 0.27, 0.27)

    cmds.workspace(fileRule=["images", out])
    cmds.setAttr("defaultRenderGlobals.imageFormat", 32)            # png
    cmds.setAttr("defaultRenderGlobals.animation", 0)
    cmds.setAttr("defaultResolution.width", args.width)
    cmds.setAttr("defaultResolution.height", args.height)
    cmds.setAttr("defaultResolution.deviceAspectRatio", float(args.width) / args.height)
    if cmds.objExists("hardwareRenderingGlobals"):
        cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
        cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)

    frames = [float(f) for f in args.frames.split(",")] if args.frames else [cmds.currentTime(query=True)]
    box = scene_bounds(cmds)
    cams = []
    if args.camera:
        if cmds.objExists(args.camera):
            cams.append(("shotcam", args.camera))
        else:
            manifest["captures"].append({"view": "shotcam", "result": "not assessed",
                                         "why": "camera %s not found" % args.camera})
    wanted = [v for v in args.views.split(",") if v]
    if box is None:
        for v in wanted:
            manifest["captures"].append({"view": v, "result": "not assessed", "why": "no visible meshes in the scene"})
    else:
        manifest["bounds"] = [round(v, 3) for v in box]
        for v in wanted:
            if v not in VIEWS:
                manifest["captures"].append({"view": v, "result": "not assessed", "why": "unknown view"})
                continue
            direction, ortho = VIEWS[v]
            cams.append((v, make_camera(cmds, v, direction, ortho, box, float(args.width) / args.height)))

    for frame in frames:
        cmds.currentTime(frame)
        for view, cam in cams:
            stem = "%s%s_f%04d" % ((args.label + "_") if args.label else "", view, int(frame))
            cmds.setAttr("defaultRenderGlobals.imageFilePrefix", stem, type="string")
            entry = {"view": view, "frame": int(frame)}
            try:
                written = cmds.ogsRender(camera=cam, currentFrame=True, width=args.width, height=args.height)
            except RuntimeError as err:
                entry.update(result="not assessed", why="ogsRender failed: %s" % err)
                manifest["captures"].append(entry)
                continue
            target = "%s/%s.png" % (out, stem)
            if written and os.path.isfile(written) and os.path.abspath(written) != os.path.abspath(target):
                shutil.move(written, target)
            if not os.path.isfile(target) or os.path.getsize(target) == 0:
                entry.update(result="not assessed", why="no image written (reported: %s)" % written)
            elif blank(om, target):
                entry.update(result="not assessed", why="image is one flat colour", file=target)
            else:
                entry.update(result="pass", file=target)
            manifest["captures"].append(entry)

    done = sum(1 for c in manifest["captures"] if c["result"] == "pass")
    manifest["summary"] = "%d captured, %d not assessed" % (done, len(manifest["captures"]) - done)
    with open(out + "/manifest.json", "w") as fh:
        json.dump(manifest, fh, indent=1)
    print("REVIEW_CAPTURE", manifest["summary"], "->", out + "/manifest.json")
    sys.stdout.flush()
    os._exit(0 if done and done == len(manifest["captures"]) else 3)   # skip Maya's slow, crash-prone teardown


if __name__ == "__main__":
    main()
