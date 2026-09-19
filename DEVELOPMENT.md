# Developing questlog

## Layout

```
.claude-plugin/plugin.json   manifest; no version field, the commit is the version
bin/quest                    the command; Python under uv run --script
skills/quest/SKILL.md        the agent's rules; short, and points at references/
skills/quest/references/     one file per working state: the process and the review checklist
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
`FORMAT` in `bin/quest` is the version the code understands. A format 6
tracker is migrated by `quest doctor --fix`; older ones are refused with a
pointer to the git tag `format-6`, the last version that carried their
migrations; newer data is refused with exit 2. Bump `FORMAT` only with a
migration.

- Format 2 added the plan stage; the migration marks `plan_skipped` on
  work that had already reached implement.
- Format 3 changed the log from list lines to a table; rewriting the log
  is the migration.
- Format 4 renamed the state `done` to `completed` and every `STAGE_closed`
  key to `STAGE_accepted`. It is the first migration that rewrites whole
  frontmatter blocks, through `update_quest(..., replace=True)`.
- Format 5 renamed `implement_drafted` to `implement_built`. Implement's
  product is commits, so its ready stamp says the work was built, where a
  document stage still says drafted.
- Format 6 replaced the stage stamps with one flat machine: `state` holds
  a verb phrase from draft goal to evaluate goal, `history` lists every
  state entered or skipped with its time, and `resume` names where a
  deferred entry picks up. The migration builds the history from the
  format 5 stamps in machine order, not time order, because the format 2
  migration dated `plan_skipped` after `implement_built` on three pages.
- Format 7 moved every entry under the directory its state names:
  `active/` for the machine states, `backlog/`, `completed/`, and
  `abandoned/`. The page did not change; its place did. The verbs write
  `quest.md` first and move the directory second, so an interruption
  between the two leaves a page whose state names one directory while it
  sits in another; the doctor's placement row names such an entry and
  `--fix` moves it. The migration is that same move, run over the
  entries at the root of `docs/quests/`.

The format number is read from the log header, but what a format changes
lives in `quest.md` or in where it sits. `check_format` runs on every
verb but doctor and refuses a tracker it cannot use: a header above
`FORMAT`; a header of 6, or any bucketed entry directly under
`docs/quests/` (`at_root`); or a header below 6, or any page
`predates_format_6` marks (the format 5 shape, or an older stamp). With
no header, or a foreign `README.md`, the pages and their places decide.
The doctor reports the same cases as rows; the format 6 row lists the
directory every root entry would move to and carries `regenerate_tracker`
as its repair, which runs `place_entries` over the misplaced entries and
rewrites the log. `misplaced` is the pure question and `move_entry` the
one move. The next format keeps that shape: a predicate, a pure
mapping, a doctor row that lists what `--fix` will do and carries the
repair, and nothing in the command path that knows the old shape.
`tracker_gate` and `settings_gate` refuse a linked or unwritable target
before any verb writes; a new writer goes through one of them, and a
move goes through `safe_write_path` at both ends.

## Release

Commit to main, let CI pass, then change the `sha` for `questlog` in
`dokidlc-plugins/.claude-plugin/marketplace.json`. Consumers pick it up on
`/plugin marketplace update dokidlc`.
