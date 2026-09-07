# Developing questlog

## Layout

```
.claude-plugin/plugin.json   manifest; no version field, the commit is the version
bin/quest                    the command; Python under uv run --script
skills/quest/SKILL.md        the agent's rules; short, and points at references/
skills/quest/references/     one file per stage: the process and the review checklist
agents/                      six stage reviewers and the fact finder, one markdown file each
hooks/hooks.json             PreToolUse guard and SessionStart doctor
scripts/guard.sh             POSIX shim: exits 0 unless the tracker is touched, 2 if uv is missing
scripts/guard.py             the checker: deny hand edits and writes into the tracker
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

## Agents

An agent file's frontmatter sets its `model` and `effort`. Every agent
ships with `model: inherit` and no `effort`, so it follows the session.
To give one stage a stronger reviewer, set those two keys in that agent's
file and nothing else changes. Plugin agents ignore `hooks`,
`mcpServers`, and `permissionMode`, and a test refuses them. The same
test parses each frontmatter block as YAML, because `claude plugin
validate` reports a malformed agent file as a warning and exits 0.

## Tests

```
uv run --quiet pytest
claude plugin validate .
```

CI runs both on ubuntu and macos.

## Hook contract

The guard reads PreToolUse JSON on stdin. It prints a `permissionDecision`
of `deny` for edits to `docs/quests/README.md` or any `quest.md` frontmatter
and for Bash that writes into the tracker by redirect or in-place tools.
Anything else prints nothing; creator verbs prompt through the `ask` rules
`quest init` writes to the project settings, not through the hook. A hook that cannot
run exits 2 only when the action touched the tracker; Claude Code treats
other non-zero exits as allow, which is why the shim is POSIX sh.

## Format and compatibility

The quest log header records `questlog format N` and the plugin commit.
`FORMAT` in `bin/quest` is the version the code understands. Older data is
migrated in place; newer data is refused with exit 2. Bump `FORMAT` only
with a migration.

- Format 2 added the plan stage; the migration marks `plan_skipped` on
  work that had already reached implement.
- Format 3 changed the log from list lines to a table; rewriting the log
  is the migration.
- Format 4 renamed the state `done` to `completed` and every `STAGE_closed`
  key to `STAGE_accepted`. It is the first migration that rewrites whole
  frontmatter blocks, through `update_quest(..., replace=True)`.

The format number is read from the log header, but the data that changes
lives in `quest.md`. Two paths used to skip the migration. `quest doctor
--fix` wrote a new header without touching the pages, and a missing log
made `check_format` a no-op so the next `quest new` stamped the new format
over old pages. Both are closed. `rename_to_format_4` keys off the page
contents, runs whenever the log is absent, and doctor reports pages that
predate format 4 with `--fix` as the cure. Keep the same shape for the
next format: a predicate on the frontmatter, a pure rewrite, and a doctor
row.

## Release

Commit to main, let CI pass, then change the `sha` for `questlog` in
`dokidlc-plugins/.claude-plugin/marketplace.json`. Consumers pick it up on
`/plugin marketplace update dokidlc`.
