#!/usr/bin/env python
"""Package the buck- skills as one versioned Claude Code plugin inside a marketplace folder.

    python build_plugin.py <version> [--out <folder>] [--keep-prefix]

`Skills/` stays the single source. This writes:

    <out>/.claude-plugin/marketplace.json
    <out>/buck3d/.claude-plugin/plugin.json
    <out>/buck3d/skills/<skill>/SKILL.md (+ scripts/)
    <out>/buck3d/BUCK_AGENT_STARTER.md, INDEX_*.md, CHANGELOG.md

In the plugin, skill folders and names drop the leading `buck-`, so a skill shows as
`buck3d:lighting-notes`, and every mention of a skill in the built text is rewritten to
that form. `Skills/` keeps the `buck-` names, which is what a copied-folder install
(Codex, a job's Agents folder) uses. --keep-prefix builds `buck3d:buck-lighting-notes`.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKETPLACE = "buck-studio"
PLUGIN = "buck3d"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version", help="semantic version, for example 0.9.0; bump it on every release")
    ap.add_argument("--out", default=str(HERE))
    ap.add_argument("--keep-prefix", action="store_true")
    args = ap.parse_args()
    if not re.match(r"^\d+\.\d+\.\d+$", args.version):
        sys.exit("version must look like 1.2.3")
    changelog = (HERE / "CHANGELOG.md").read_text(encoding="utf-8")
    if "## %s" % args.version not in changelog:
        sys.exit("CHANGELOG.md has no '## %s' entry. Write what changed first." % args.version)

    out = Path(args.out)
    plugin = out / PLUGIN
    if plugin.exists():
        shutil.rmtree(plugin)
    (plugin / ".claude-plugin").mkdir(parents=True)
    (out / ".claude-plugin").mkdir(parents=True, exist_ok=True)

    strip = not args.keep_prefix
    names = sorted((p.name for p in (HERE / "Skills").iterdir() if p.is_dir()), key=len, reverse=True)

    def rename(text):
        """buck-lighting-notes -> buck3d:lighting-notes, for every real skill name and the group wildcards."""
        text = re.sub(r"\]\((buck-[a-z0-9-]+)/SKILL\.md\)", lambda m: "](skills/%s/SKILL.md)" % m.group(1)[5:], text)
        for full in names:
            text = re.sub(r"(?<![A-Za-z0-9_/\-])%s(?![A-Za-z0-9_-])" % re.escape(full), PLUGIN + ":" + full[5:], text)
        return re.sub(r"(?<![A-Za-z0-9_/\-])buck-(lighting|modeling|pipeline)-\*", PLUGIN + r":\g<1>-*", text)

    count = scripts = 0
    for src in sorted(p for p in (HERE / "Skills").iterdir() if p.is_dir()):
        name = src.name[len("buck-"):] if strip and src.name.startswith("buck-") else src.name
        dst = plugin / "skills" / name
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        skill = dst / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        if strip:
            text = rename(text)
            text = re.sub(r"(?m)^name: .*$", "name: " + name, text, count=1)
        if (dst / "scripts").is_dir():
            scripts += 1
            text = text.rstrip("\n") + ("\n\n## Where the scripts are\n\nThis skill's folder is `${CLAUDE_SKILL_DIR}`; "
                                         "its scripts are in `${CLAUDE_SKILL_DIR}/scripts/`.\n")
        skill.write_text(text, encoding="utf-8", newline="\n")
        count += 1
    extras = [HERE / n for n in ("BUCK_AGENT_STARTER.md", "CHANGELOG.md", "ARTIST_TEMPLATE.md")]
    for extra in extras + sorted((HERE / "Skills").glob("INDEX_*.md")):
        text = extra.read_text(encoding="utf-8")
        if strip and extra.name != "CHANGELOG.md":
            text = rename(text)
        (plugin / extra.name).write_text(text, encoding="utf-8", newline="\n")

    (plugin / ".claude-plugin" / "plugin.json").write_text(json.dumps({
        "name": PLUGIN,
        "version": args.version,
        "description": "Buck studio skills for AI agents: lighting, modeling and pipeline (Buck5, Aquarium, farm, version records).",
        "author": {"name": "Buck"},
    }, indent=2) + "\n", encoding="utf-8")
    (out / ".claude-plugin" / "marketplace.json").write_text(json.dumps({
        "name": MARKETPLACE,
        "owner": {"name": "Buck"},
        "plugins": [{"name": PLUGIN, "source": "./" + PLUGIN,
                     "description": "Buck studio skills for AI agents.", "version": args.version}],
    }, indent=2) + "\n", encoding="utf-8")
    print("built %s %s: %d skills (%d with scripts) -> %s" % (PLUGIN, args.version, count, scripts, out))


if __name__ == "__main__":
    main()
