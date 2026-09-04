#!/bin/sh
# questlog guard, layer one. POSIX sh so it always parses.
# Reads the PreToolUse JSON on stdin. If it does not mention the tracker or
# the quest command, exit 0 at once. Otherwise hand it to guard.py under uv.
# If uv is missing for a guarded action, exit 2: fail closed, but only here.
input=$(cat)
printf '%s' "$input" | grep -q -e 'docs/quests' -e 'quest ' -e '/quest"' -e 'bin/quest' || exit 0
if ! command -v uv >/dev/null 2>&1; then
  echo "questlog guard: uv is not on PATH, so the guarded action is refused. Install uv." >&2
  exit 2
fi
dir=$(dirname "$0")
printf '%s' "$input" | uv run --quiet --script "$dir/guard.py"
