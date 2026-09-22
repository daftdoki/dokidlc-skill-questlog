# The tracker on disk

How questlog stores a quest, what the guard denies, and which subagents the plugin ships. The [README](../README.md) covers installing and using it.

```
docs/quests/
  README.md                          the quest log, generated
  guidance/                          optional; your project's own rules per state
    research.md  design.md
  active/                            every quest at a machine state, draft goal through evaluate goal
    2609051012-k3-discover-the-bridge/
      quest.md                       metadata, history, and the goal, owned by the verbs
      goal.md  research.md  design.md  plan.md      written by the agent, read by you
      goal-review.md  design-review.md ...          one review record per review state, pass by pass
      result-review.md               evaluate goal's record
  backlog/                           opened or deferred, not started
  completed/                         finished; quest history lists them
  abandoned/                         dropped, with a reason in quest.md
    2609042210-7q-a-second-bridge/
```

A verb that changes the state moves the directory: `start` from
`backlog/` to `active/`, `defer` back, the last `next` to `completed/`,
`abandon` to `abandoned/`. Each of the four directories appears the first
time something lands in it. `ls docs/quests/active` is the shortest
answer to "what is going on".

Before the agent works a state it reads the plugin's reference for it,
six files under the skill's `references/`, one per working state, each
with the interview, the document's sections, and a review checklist.
`quest ID` prints the path. A file at `docs/quests/guidance/STAGE.md`
adds your project's rules; the agent reads it after the plugin's file,
and it wins where they differ. `quest doctor` checks that the directory
holds only files named after a reference.

Each stage file is reviewed before you see it. The agent dispatches a
fresh-context reviewer, records the findings by tier in the review record
beside the file, fixes them, and repeats until a pass finds nothing
blocking and nothing to clarify, or a cap stops it: three full passes
without convergence, or three diff passes in a row with something under
Blocking or Clarification. The record shows you how the document
converged, and a later session picks the loop up from the last pass.

`quest.md` is frontmatter and a short body:

```
---
id: 2609051012-k3
title: Discover the bridge over mDNS
kind: quest                # or chore
state: review plan         # a state name, or backlog, completed, abandoned
resume: review plan        # only while deferred; start removes it
history:
- state: backlog
  at: '2026-09-05T10:12:00Z'
- state: draft goal
  at: '2026-09-05T10:20:00Z'
- state: research
  at: '2026-09-05T11:02:00Z'
  skipped: true
- state: review research
  at: '2026-09-05T11:02:00Z'
  skipped: true
- state: design
  at: '2026-09-05T11:02:00Z'
---
## Goal

What you want.

## Done when

How you will know.
```

Every state the quest entered or skipped is one history entry with its
time; an abandoned entry carries the reason as its note. The quest log is
a heading, a comment naming the format and the plugin version, and a
table with one row per open entry: id, kind, state, title. `quest log`
prints the same table aligned for the terminal. Completed and abandoned
entries are not listed there, so the log stays small however long the
project runs; `quest history` reads them from the directories on demand.

**What is guarded.** The log and every `quest.md` frontmatter block are
written only by the verbs, so the log always matches the directories and
a time is never typed by hand. A `PreToolUse` hook on the Edit, Write,
and Bash tools enforces the first three rows; the `ask` rules in
`.claude/settings.json` give the fourth:

| Trigger | Result |
|---|---|
| Edit or Write to `docs/quests/README.md` | denied |
| Edit or Write that touches a `quest.md` frontmatter block | denied; the body below it is fine |
| Bash that redirects into `docs/quests`, or runs `sed -i`, `tee`, `cp`, `mv`, `dd`, or an inline script (`python3 -c`, `sh -c`) that names a file there | denied; the redirect's target is what counts, so `2>/dev/null` beside a tracker path passes |
| Bash that runs `quest init`, `quest new`, or `quest ID start`, `defer`, `next`, `skip`, or `abandon` | you are asked to approve, by the `ask` rules `quest init` writes to `.claude/settings.json`; a `*` in a rule stands for the id, and the rules match the command, so a commit message or heredoc that names a verb does not prompt |
| Anything else, including the agent writing a stage file | allowed |

A `SessionStart` hook runs `quest doctor --brief`, one line telling the
agent how many entries are open, that the tracker needs migrating, or
that the log was written by a newer plugin. A project initialized before
the rules existed gets them from `quest doctor --fix`, which the agent
may run on its own, since adding a prompt cannot loosen anything. If `uv`
is missing, guarded actions are refused rather than allowed, and
everything else proceeds.

The guard is for habit, not for an adversary. A command that reaches the
tracker without naming it, through an encoded payload, a variable, or a
script body on stdin, gets through; `quest doctor` is the check behind
it. A path to the script, such as `bin/quest ID next`, does not match the
rules; the skill always says `quest`. The script refuses a symlink at
`docs`, `docs/quests`, or anything inside it, at `.claude` or its
settings file, and a `CLAUDE.md` link that leaves the project or names a
file the script manages, before it reads or writes anything, so a cloned
repository cannot point those at another file.

## Migrating from an older format

The quest log's header names its format. This plugin writes format 7. A
format 6 tracker, its entries flat under `docs/quests/`, is refused by
every verb until `quest doctor --fix` moves each entry into the directory
its state names; plain `quest doctor` first lists the moves, one `ID ->
STATE/` line each, so you can read them before anything moves. A tracker
older than format 6 is refused with a pointer to the git tag `format-6`
on this repository, the last version that migrated those formats; run
that version's `quest doctor --fix` first.

## What the agent dispatches

The plugin ships seven subagents, named `questlog:NAME` once it is
enabled. Six are reviewers, `review-goal` through `review-plan`,
`review-implement`, and `review-result`, one per review state and one for
evaluate goal; each reads `references/review-loop.md` and then its
stage's Review section, and reports.
The seventh, `fact-finder`, answers a factual question from the code, the
docs, memory, or the web, so the agent asks you only what you alone know.
Each agent's model and effort are set in its own file under `agents/`;
all inherit the session's until you change one.

