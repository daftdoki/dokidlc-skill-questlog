#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# ///
"""questlog guard, layer two. Reads PreToolUse JSON on stdin, prints a decision.

Denies hand edits to the quest log and to quest.md frontmatter, and Bash
that writes into the tracker by redirect or in-place tools. Asks the creator
to approve creator verbs. Allows everything else by printing nothing.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT_NAME = "docs/quests"
CREATOR_VERBS = ("init", "new", "start", "next", "skip", "abandon")
VERB_RE = re.compile(r"(?:^|[\s;&|(]|/)(?:bin/)?quest\s+(" + "|".join(CREATOR_VERBS) + r")\b")
# ways a shell command writes a file; a habit guard, not an adversary guard (see SKILL.md)
WRITER_RE = re.compile(r"(?:(?<![<>])>{1,2}(?!&)|\bsed\s+(-i|--in-place)|\btee\b|\b(cp|mv|install|dd|rsync)\b|\b(python3?|perl|ruby|node)\s+-[ce]|\bawk\b.*-i\s*inplace|<<-?\s*['\"]?\w+|\|\s*(sh|bash|zsh)\b)")
TRACKER_RE = re.compile(r"docs/quests|\bquests\b")
FM_DENY = "quest.md frontmatter is owned by the quest verbs. Edit only the body below it."


def tracker_path(path: str, cwd: str) -> str | None:
    """The path relative to the tracker root, or None if outside it. Case-insensitive, so Docs/Quests/readme.md counts."""
    p = Path(path)
    if not p.is_absolute():
        p = Path(cwd) / p
    parts = p.resolve().parts
    for i in range(len(parts) - 1):
        if parts[i].lower() == "docs" and parts[i + 1].lower() == "quests":
            return "/".join(parts[i + 2 :])
    return None


def apply_edit(text: str, old: str, new: str, replace_all: bool) -> str:
    return text.replace(old, new) if replace_all else text.replace(old, new, 1)



def decide(event: dict) -> tuple[str, str] | None:
    """(decision, reason) or None to allow."""
    tool = event.get("tool_name", "")
    inp = event.get("tool_input", {}) or {}
    cwd = event.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    if tool in ("Edit", "Write"):
        rel = tracker_path(str(inp.get("file_path", "")), cwd)
        if rel is None:
            return None
        if rel.lower() == "readme.md":
            return "deny", "docs/quests/README.md is the generated quest log. Run a quest verb; it regenerates."
        if rel.lower().endswith("/quest.md"):
            existing = Path(cwd, ROOT_NAME, rel)
            if not existing.is_file():
                return "deny", "quest.md is created by `quest new`, not written by hand."
            before = existing.read_text()
            if tool == "Write":
                after = str(inp.get("content", ""))
            else:
                after = apply_edit(before, str(inp.get("old_string", "")), str(inp.get("new_string", "")), bool(inp.get("replace_all")))
            if _frontmatter(before) != _frontmatter(after):
                return "deny", FM_DENY
        return None

    if tool == "Bash":
        cmd = str(inp.get("command", ""))
        m = VERB_RE.search(cmd)
        if m:
            return "ask", f"Creator verb: quest {m.group(1)}. Approve only if you asked for this. Command: {cmd.strip()}"
        if TRACKER_RE.search(cmd) and WRITER_RE.search(cmd):
            return "deny", "Writing into docs/quests/ with a redirect or in-place tool bypasses the quest verbs. Use them, or edit a stage file with Edit or Write."
        return None
    return None


def _frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 4)
    return text[4:end] if end > 0 else text


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    result = decide(event)
    if result is None:
        sys.exit(0)
    decision, reason = result
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision, "permissionDecisionReason": reason}}))
    sys.exit(0)


if __name__ == "__main__":
    main()
