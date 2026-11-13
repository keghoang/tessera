"""Print what a farm job or a trail needs to know about a Maya scene, as JSON. Run in mayapy.

    mayapy maya_scene_info.py --scene <scene> [--out <local json file>]

Reports the Maya and renderer versions, frame range, resolution, renderable
cameras, render layers and which are renderable, the OCIO config and the
references with their loaded state. The scene is opened as saved and never saved.
"""
from __future__ import print_function

import argparse
import json
import os
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", required=True)
    ap.add_argument("--out")
    args = ap.parse_args()
    if args.out and args.out.replace("\\", "/").startswith("//"):
        sys.exit("REFUSED: write the JSON to local scratch, not the server.")

    import maya.standalone
    maya.standalone.initialize(name="python")
    from maya import cmds

    cmds.file(args.scene, open=True, force=True)          # as saved: no loadReferenceDepth, no ignoreVersion
    info = {"scene": args.scene, "maya": cmds.about(installedVersion=True), "not_assessed": []}

    def attr(name, key):
        try:
            info[key] = cmds.getAttr(name)
        except (RuntimeError, ValueError) as err:
            info["not_assessed"].append("%s: %s" % (key, str(err).strip()))

    attr("defaultRenderGlobals.currentRenderer", "renderer")
    attr("defaultRenderGlobals.startFrame", "start_frame")
    attr("defaultRenderGlobals.endFrame", "end_frame")
    attr("defaultResolution.width", "width")
    attr("defaultResolution.height", "height")
    if cmds.objExists("vraySettings"):                      # V-Ray renders at these, not defaultResolution
        attr("vraySettings.width", "vray_width")
        attr("vraySettings.height", "vray_height")
    info["playback_range"] = [cmds.playbackOptions(query=True, minTime=True),
                              cmds.playbackOptions(query=True, maxTime=True)]
    info["fps_unit"] = cmds.currentUnit(query=True, time=True)
    for plugin in ("vrayformaya", "mtoa", "redshift4maya"):
        if cmds.pluginInfo(plugin, query=True, loaded=True):
            info.setdefault("renderer_plugins", {})[plugin] = cmds.pluginInfo(plugin, query=True, version=True)
    info["renderable_cameras"] = [(cmds.listRelatives(c, parent=True) or [c])[0]
                                  for c in cmds.ls(type="camera") or [] if cmds.getAttr(c + ".renderable")]
    info["render_layers"] = [{"name": l, "renderable": bool(cmds.getAttr(l + ".renderable"))}
                             for l in cmds.ls(type="renderLayer") or [] if ":" not in l]
    try:
        info["ocio_config"] = cmds.colorManagementPrefs(query=True, configFilePath=True)
        info["ocio_enabled"] = bool(cmds.colorManagementPrefs(query=True, cmConfigFileEnabled=True))
    except RuntimeError as err:
        info["not_assessed"].append("colour management: %s" % str(err).strip())
    refs = []
    for node in cmds.ls(type="reference") or []:
        try:
            refs.append({"node": node, "file": cmds.referenceQuery(node, filename=True),
                         "loaded": bool(cmds.referenceQuery(node, isLoaded=True))})
        except RuntimeError:
            continue
    info["references"] = refs

    text = json.dumps(info, indent=1)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text)
    print("SCENE_INFO_BEGIN")
    print(text)
    print("SCENE_INFO_END")
    sys.stdout.flush()
    os._exit(0)                                            # skip Maya's slow, crash-prone teardown


if __name__ == "__main__":
    main()
