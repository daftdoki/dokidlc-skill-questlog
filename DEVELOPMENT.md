# Developing questlog

## Layout

```
.claude-plugin/plugin.json   manifest; no version field, the commit is the version
bin/quest                    the command; Python under uv run --script
skills/quest/SKILL.md        the agent's rules
hooks/hooks.json             PreToolUse guard and SessionStart doctor
scripts/guard.sh             POSIX shim: exits 0 unless the tracker is touched, 2 if uv is missing
scripts/guard.py             the checker: deny hand edits, ask on creator verbs
tests/                       pytest; nothing needs Claude Code
```

## Run it from a checkout

```
claude --plugin-dir /path/to/dokidlc-skill-questlog
```

A checkout loaded this way overrides the installed plugin of the same name
for that session. After editing, `/reload-plugins`.

To run the command outside a session, set the project root explicitly:

```
CLAUDE_PROJECT_DIR=/path/to/repo bin/quest log
```

## Tests

```
uv run --quiet pytest
claude plugin validate .
```

CI runs both on ubuntu and macos.

## Hook contract

The guard reads PreToolUse JSON on stdin. It prints a `permissionDecision`
of `deny` for edits to `docs/quests/README.md` or any `quest.md` frontmatter
and for Bash that writes into the tracker by redirect or in-place tools, and
`ask` for creator verbs. Anything else prints nothing. A hook that cannot
run exits 2 only when the action touched the tracker; Claude Code treats
other non-zero exits as allow, which is why the shim is POSIX sh.

## Format and compatibility

The quest log header records `questlog format N` and the plugin commit.
`FORMAT` in `bin/quest` is the version the code understands. Older data is
migrated in place; newer data is refused with exit 2. Bump `FORMAT` only
with a migration.

## Release

Commit to main, let CI pass, then change the `sha` for `questlog` in
`dokidlc-plugins/.claude-plugin/marketplace.json`. Consumers pick it up on
`/plugin marketplace update dokidlc`.
