#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# ///
"""questlog guard, layer two. Reads PreToolUse JSON on stdin, prints a decision.

Denies hand edits to the quest log and to quest.md frontmatter, and Bash
whose redirect target or in-place tool argument is a path inside the
tracker. Asks the creator to approve creator verbs. Allows everything else
by printing nothing.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

ROOT_NAME = "docs/quests"
CREATOR_VERBS = ("init", "new", "start", "next", "skip", "abandon")
VERB_RE = re.compile(r"(?:^|[\s;&|(]|/)(?:bin/)?quest\s+(" + "|".join(CREATOR_VERBS) + r")\b")
# the wide rule: any writer near any tracker mention. Kept only for a command shlex cannot parse.
WRITER_RE = re.compile(r"(?:(?<![<>])>{1,2}(?!&)|\bsed\s+(-i|--in-place)|\btee\b|\b(cp|mv|install|dd|rsync)\b|\b(python3?|perl|ruby|node)\s+-[ce]|\bawk\b.*-i\s*inplace|<<-?\s*['\"]?\w+|\|\s*(sh|bash|zsh)\b)")
TRACKER_RE = re.compile(r"docs/quests|\bquests\b")
FM_DENY = "quest.md frontmatter is owned by the quest verbs. Edit only the body below it."
BASH_DENY = "Bash writes to {where} with {how}. Write a stage file with Write or Edit; the log and quest.md frontmatter belong to the quest verbs."

PUNCTUATION = ";&|<>()\n"
REDIRECTS = {">", ">>", "&>", "&>>", ">|", ">&"}
INPUTS = {"<", "<<", "<&"}
COPIERS = ("cp", "mv", "install", "rsync")   # the last positional is the destination
SCRIPTERS = ("python", "python3", "perl", "ruby", "node")
SHELLS = ("sh", "bash", "zsh")


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


def strip_heredocs(cmd: str) -> str:
    """The command without heredoc bodies. The opener line stays, so what follows `<<WORD` on it still parses."""
    lines = cmd.split("\n")
    kept: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        kept.append(line)
        i += 1
        delim = _heredoc_delimiter(line)
        if delim is None:
            continue
        strip_tabs = delim.startswith("-")
        delim = delim.lstrip("-")
        while i < len(lines):
            body = lines[i]
            i += 1
            if (body.lstrip("\t") if strip_tabs else body).rstrip() == delim:
                break
    return "\n".join(kept)


def _heredoc_delimiter(line: str) -> str | None:
    """The word after the first `<<` operator on the line, or None. `<<-EOF` gives `-EOF`; quotes are already gone."""
    try:
        tokens = _tokens(line)
    except ValueError:
        return None
    for i, t in enumerate(tokens):
        if t == "<<" and i + 1 < len(tokens):
            return tokens[i + 1]
    return None


def _tokens(cmd: str) -> list[str]:
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=PUNCTUATION)
    lex.whitespace_split = True
    lex.commenters = ""
    lex.whitespace = " \t\r"
    return list(lex)


def _segments(tokens: list[str]) -> list[list[str]]:
    """Simple commands, split at every separator token. Redirect and input operators stay inside their segment."""
    out: list[list[str]] = []
    seg: list[str] = []
    for t in tokens + ["\n"]:
        if t and t not in REDIRECTS and t not in INPUTS and set(t) <= set(PUNCTUATION):
            if seg:
                out.append(seg)
            seg = []
        else:
            seg.append(t)
    return out


def _inside(target: str, vcwd: str) -> str | None:
    """The tracker path a target names, shown as docs/quests/REL, or None."""
    if not target:
        return None
    rel = tracker_path(os.path.expanduser(target), vcwd)
    if rel is None:
        return None
    return f"{ROOT_NAME}/{rel}" if rel else ROOT_NAME


def bash_write_target(cmd: str, cwd: str) -> tuple[str, str] | None:
    """(how, where) for the first write into the tracker the command makes, or None.

    Walks the simple commands in order with a virtual cwd that follows `cd`. A
    redirect's target and an in-place tool's argument are resolved as paths.
    A one-line script and a pipe into a shell are opaque, so any tracker
    mention inside them counts. A script body on stdin is not inspected.
    """
    try:
        tokens = _tokens(strip_heredocs(cmd))
    except ValueError:
        m = TRACKER_RE.search(cmd)
        if m and WRITER_RE.search(cmd):
            return "an unparsable command", m.group(0)
        return None
    vcwd = prev = cwd
    for seg in _segments(tokens):
        words: list[str] = []
        i = 0
        while i < len(seg):
            t = seg[i]
            if t in REDIRECTS or t in INPUTS:
                target = seg[i + 1] if i + 1 < len(seg) else ""
                i += 2
                if words and words[-1].isdigit():
                    words.pop()   # the descriptor in 2>/dev/null is part of the operator
                if t in INPUTS or (t == ">&" and target.isdigit()):
                    continue
                where = _inside(target, vcwd)
                if where:
                    return "a redirect", where
                continue
            words.append(t)
            i += 1
        while words and (words[0] in ("sudo", "env") or ("=" in words[0] and not words[0].startswith("-"))):
            words.pop(0)
        if not words:
            continue
        name, args = os.path.basename(words[0]), words[1:]
        positional = [a for a in args if a and not a.startswith("-")]
        if name == "cd":
            if not args:
                vcwd, prev = os.path.expanduser("~"), vcwd
            elif args[0] == "-":
                vcwd, prev = prev, vcwd
            else:
                vcwd, prev = os.path.normpath(os.path.join(vcwd, os.path.expanduser(args[0]))), vcwd
            continue
        checked: list[str] = []
        how = name
        if name in COPIERS and positional:
            checked = positional[-1:]
        elif name == "tee":
            checked = positional
        elif name == "dd":
            checked = [a[3:] for a in args if a.startswith("of=")]
        elif name == "sed" and any(a == "--in-place" or a.startswith("-i") for a in args):
            checked, how = positional, "sed -i"
        elif name == "awk" and "-i" in args and "inplace" in args:
            checked, how = [a for a in positional if a != "inplace"], "awk -i inplace"
        elif (name in SCRIPTERS and any(a in ("-c", "-e") for a in args)) or (name in SHELLS and "-c" in args):
            flag = "-c" if "-c" in args else "-e"
            for a in args:
                m = TRACKER_RE.search(a)
                if m:
                    return f"a {name} {flag} script", m.group(0)
        elif name in SHELLS and not positional:
            m = TRACKER_RE.search(cmd)
            if m:
                return f"a pipe into {name}", m.group(0)
        for a in checked:
            where = _inside(a, vcwd)
            if where:
                return how, where
    return None



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
        hit = bash_write_target(cmd, cwd)
        if hit:
            how, where = hit
            return "deny", BASH_DENY.format(where=where, how=how)
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
