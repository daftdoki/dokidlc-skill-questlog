#!/bin/sh
# questlog guard, layer one. POSIX sh so it always parses.
# Reads the PreToolUse JSON on stdin. If it does not mention the tracker or
# the quest command, exit 0 at once. Otherwise hand it to guard.py under uv.
# If uv is missing for a guarded action, exit 2: fail closed, but only here.
input=$(cat)
# Bash always goes to the checker (a command can reach the tracker without naming it);
# Edit and Write short-circuit unless the path mentions the tracker.
case "$input" in
  *'"tool_name":'*'"Bash"'*|*'"tool_name": "Bash"'*) ;;
  *) printf '%s' "$input" | grep -q -i -E 'docs/quests|(^|[^a-z])quest([^a-z]|$)' || exit 0 ;;
esac
if ! command -v uv >/dev/null 2>&1; then
  # no checker available: refuse only what names the tracker or the quest command, allow the rest
  printf '%s' "$input" | grep -q -i -E 'docs/quests|(^|[^a-z])quest([^a-z]|$)' || exit 0
  echo "questlog guard: uv is not on PATH, so the guarded action is refused. Install uv." >&2
  exit 2
fi
dir=$(dirname "$0")
printf '%s' "$input" | uv run --quiet --script "$dir/guard.py"
