#!/usr/bin/env python
"""Package the skills as one versioned Claude Code plugin inside a marketplace folder.

The plugin goes by a code name. Its name, marketplace name, descriptions and author carry no
studio name, and the studio name is taken out of every skill description (the text shown in
skill listings). The skill bodies keep the real paths and tool names; they need them to work.

    python build_plugin.py <version> [--out <folder>] [--keep-prefix]

`Skills/` stays the single source. This writes:

    <out>/.claude-plugin/marketplace.json
    <out>/tessera/.claude-plugin/plugin.json
    <out>/tessera/skills/<skill>/SKILL.md (+ scripts/)
    <out>/tessera/hooks/hooks.json
    <out>/tessera/BUCK_AGENT_STARTER.md, INDEX_*.md, CHANGELOG.md

In the plugin, skill folders and names drop the leading `buck-`, so a skill shows as
`tessera:lighting-notes`, and every mention of a skill in the built text is rewritten to
that form. `Skills/` keeps the `buck-` names, which is what a copied-folder install
(Codex, a job's Agents folder) uses. --keep-prefix builds `tessera:buck-lighting-notes`.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKETPLACE = "tessera-hub"
PLUGIN = "tessera"


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
        """buck-lighting-notes -> tessera:lighting-notes, for every real skill name and the group wildcards."""
        text = re.sub(r"\]\((buck-[a-z0-9-]+)/SKILL\.md\)", lambda m: "](skills/%s/SKILL.md)" % m.group(1)[5:], text)
        for full in names:
            text = re.sub(r"(?<![A-Za-z0-9_/\-])%s(?![A-Za-z0-9_-])" % re.escape(full), PLUGIN + ":" + full[5:], text)
        return re.sub(r"(?<![A-Za-z0-9_/\-])buck-(lighting|modeling|pipeline)-\*", PLUGIN + r":\g<1>-*", text)

    def neutral(line):
        """Take the studio name out of a description line. 'Buck5' (the launcher) is reworded too."""
        line = re.sub(r"\ba Buck (?=[aeiouAEIOU])", "an ", line)
        line = re.sub(r"\bBuck5's local API", "the launcher's local API", line)
        line = re.sub(r"\bBuck5 \(rez\)", "launcher (rez)", line)
        line = re.sub(r"\bBuck5/Deadline", "the farm", line)
        line = re.sub(r"\bBuck5", "the launcher", line)
        line = re.sub(r"\b(?:Buck|BUCK) ", "", line)
        line = line.replace("the buck- skills", "the skills")
        if re.search(r"(?i)buck(?!3d)", line.replace(PLUGIN + ":", "")):
            sys.exit("studio name still in a description: " + line[:160])
        return line

    shorts = json.loads((HERE / "Skills" / "short_descriptions.json").read_text(encoding="utf-8"))

    def split_description(line, source_name):
        """A short line for menus; the full description becomes when_to_use (the agent reads both)."""
        short = shorts.get(source_name)
        if not short:
            sys.exit("no short description for %s in Skills/short_descriptions.json" % source_name)
        if len(short) > 70 or "buck" in short.lower() or ": " in short:
            sys.exit("bad short description for %s: %s" % (source_name, short))
        return "description: " + short + "\nwhen_to_use: " + line[len("description: "):]

    count = scripts = hidden = 0
    for src in sorted(p for p in (HERE / "Skills").iterdir() if p.is_dir()):
        name = src.name[len("buck-"):] if strip and src.name.startswith("buck-") else src.name
        dst = plugin / "skills" / name
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        skill = dst / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        if strip:
            text = rename(text)
            text = re.sub(r"(?m)^name: .*$", "name: " + name, text, count=1)
        text = re.sub(r"(?m)^description: .*$", lambda m: split_description(neutral(m.group(0)), src.name), text, count=1)
        if re.match(r"(buck-)?(lighting|modeling)-.+", src.name):
            # a procedure behind a front door: the agent still loads it, the artist's menu doesn't list it
            text = re.sub(r"(?m)^when_to_use: .*$", lambda m: m.group(0) + "\nuser-invocable: false", text, count=1)
            hidden += 1
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

    # sub-agents that come with the plugin (a read-only inspector, for one)
    agents = 0
    for src in sorted((HERE / "SubAgents").glob("*.md")):
        text = src.read_text(encoding="utf-8")
        if strip:
            text = rename(text)
        m = re.search(r"(?m)^description: .*$", text)
        if not m or re.search(r"(?i)buck", m.group(0).replace(PLUGIN + ":", "")):
            sys.exit("sub-agent %s: missing description, or the studio name is in it" % src.name)
        (plugin / "agents").mkdir(exist_ok=True)
        (plugin / "agents" / src.name).write_text(text, encoding="utf-8", newline="\n")
        agents += 1

    # hooks keep a session's reported state true: working / idle / waiting, and clear it at the end
    status = "%s/skills/%s/scripts/status.py" % ("${CLAUDE_PLUGIN_ROOT}", "pipeline-status" if strip else "buck-pipeline-status")

    def hook(event):
        return [{"hooks": [{"type": "command", "timeout": 15,
                            "command": 'c:/opt/rez/Scripts/python.exe "%s" hook %s' % (status, event)}]}]

    # at session start: point the agent at the job's rules, or at the first-session setup
    start = "%s/skills/%s/scripts/start.py" % ("${CLAUDE_PLUGIN_ROOT}", "start" if strip else "buck-start")
    session_start = [{"hooks": [{"type": "command", "timeout": 10,
                                 "command": 'c:/opt/rez/Scripts/python.exe "%s" hook' % start}]}]

    # on every new message: show the session the job's announcements it has not seen
    announce = "%s/skills/%s/scripts/announce.py" % ("${CLAUDE_PLUGIN_ROOT}", "pipeline-announce" if strip else "buck-pipeline-announce")
    prompt = hook("prompt")
    prompt[0]["hooks"].append({"type": "command", "timeout": 15,
                               "command": 'c:/opt/rez/Scripts/python.exe "%s" hook' % announce})

    (plugin / "hooks").mkdir()
    (plugin / "hooks" / "hooks.json").write_text(json.dumps({"hooks": {
        "SessionStart": session_start,
        "UserPromptSubmit": prompt, "PreToolUse": hook("tool"), "Stop": hook("stop"),
        "Notification": hook("notify"), "SessionEnd": hook("end"),
    }}, indent=2) + "\n", encoding="utf-8")

    (plugin / ".claude-plugin" / "plugin.json").write_text(json.dumps({
        "name": PLUGIN,
        "version": args.version,
        "description": "Working notes and skills for 3D lighting, modeling and pipeline tasks.",
        "author": {"name": "tessera"},
    }, indent=2) + "\n", encoding="utf-8")
    (out / ".claude-plugin" / "marketplace.json").write_text(json.dumps({
        "name": MARKETPLACE,
        "owner": {"name": "tessera"},
        "plugins": [{"name": PLUGIN, "source": "./" + PLUGIN,
                     "description": "Working notes and skills for 3D tasks.", "version": args.version}],
    }, indent=2) + "\n", encoding="utf-8")
    print("built %s %s: %d skills (%d with scripts, %d hidden from the menu), %d sub-agents -> %s"
          % (PLUGIN, args.version, count, scripts, hidden, agents, out))


if __name__ == "__main__":
    main()
