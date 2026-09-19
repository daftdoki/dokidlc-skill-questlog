# dokidlc-skill-questlog

A Claude Code plugin that lets your agent track work as quests and chores,
with you deciding when each step is finished. A quest moves through one
flat machine of states, from draft goal to evaluate goal. The agent writes
each state's document and moves the quest into review; you read, you
iterate together, and the quest moves on when you say so. Each quest or
chore is a directory under `docs/quests/active/`, `backlog/`,
`completed/`, or `abandoned/` holding a `quest.md` and its stage files;
the directory moves when the state changes, so a file listing shows what
is active. The quest log at `docs/quests/README.md` lists what is open,
one line each.

With it enabled, the agent will on its own: tell you what is open at the
start of every session, read a quest before working on it, write the stage
documents, and move a quest into review when it wants your eyes. It will
not open, start, park, move on from review, skip, or abandon anything by
itself. Those happen only when you ask, and Claude Code prompts you to
approve the exact command each time.

## Process

Work comes in two sizes. A quest is a feature, a redesign, an
investigation: anything worth thinking through before it is built. A chore
is a bug fix, a small addition, a bit of upkeep: anything you could
describe in two sentences and hand over. Both get an identifier, a
directory, and a place in the log. They differ in which states they pass
through.

The states, in order:

```
draft goal -> review goal -> research -> review research -> design -> review design
  -> plan -> review plan -> implement -> review implementation -> evaluate goal -> completed
```

Each working state produces something the agent wrote: `goal.md`,
`research.md`, `design.md`, `plan.md`, or the commits. Each review state
is where you read it; the agent has already run a fresh-context reviewer
over it and fixed what that found. You iterate as long as you like; after
every revision the agent asks whether to move on, and the quest moves only
when you say so. At evaluate goal you judge the result against the Done
when you wrote at the start.

Research and design can be skipped, and each takes its review with it. Any
review can be skipped. Draft goal, plan, implement, and evaluate goal
cannot. A chore is a quest opened with research and design already
skipped: it runs draft goal, review goal, plan, review plan, implement,
review implementation, evaluate goal.

At any state you can defer the work; it goes back to `backlog/` and
resumes where it was. At any state you can abandon it; its files move to
`abandoned/` for the record, and it leaves the log.

## Usage

Talk to the agent. It runs the commands, and every command prints one
line that says where the quest is and what happens next:

```
2609051012-k3 is at review plan. Run the review-plan loop into plan-review.md, then ask: move on to implementing?
```

- "What's open?" The agent runs `quest log` and reads you the list.
- "What have we completed?" The agent runs `quest history`, the last ten
  completed newest first. `--all` adds abandoned ones. Completed work
  stays out of the log and out of the session until you ask.
- "Open a quest for discovering the bridge over mDNS." The agent asks for
  the goal and how you'll know it is done, shows you `quest new "Discover
  the bridge over mDNS" --goal "..." --done-when "..."`, runs it, and you
  approve the prompt.
- "Open a chore to fix the volume off-by-one." Same, with `--chore`.
- "Start the mDNS quest." The agent runs `quest 2609051012-k3 start`. The
  quest is at draft goal.
- "Draft the goal." The agent interviews you, writes `goal.md`, runs
  `quest 2609051012-k3 next`, which enters review goal, runs the review
  loop, and asks: move on to researching?
- "Change the second story." The agent revises, runs the loop again, and
  asks again, as many times as it takes.
- "Move on." The agent shows and runs `quest 2609051012-k3 next`. From
  evaluate goal, that completes the quest.
- "Skip research on this one." `quest 2609051012-k3 skip`, at research;
  review research goes with it.
- "Park the mDNS quest for now." `quest 2609051012-k3 defer`. The log
  shows `backlog, resume at review plan`, and `quest 2609051012-k3 start`
  picks it up there.
- "Abandon the mDNS quest, we're going with the bridge's own discovery."
  `quest 2609051012-k3 abandon "we're going with the bridge's own discovery"`.

### The commands

```
quest new "Title" [--chore] [--goal TEXT] [--done-when TEXT]   open a quest or chore in the backlog
quest log                                   what is open, newest first
quest history [--all] [--limit N]           what is completed, newest first, ten by default
quest doctor [--fix] [--brief]              check the tracker; --fix migrates and repairs
quest init                                  set up a repository

quest 2609051012-k3                         show one quest; a unique id prefix works
quest 2609051012-k3 start                   leave the backlog; a deferred quest resumes where it was
quest 2609051012-k3 defer                   back to the backlog; the state is kept
quest 2609051012-k3 next [--confirmed]      the current state is done; enter the next one
quest 2609051012-k3 skip                    skip the current state
quest 2609051012-k3 abandon "reason"        terminal; files stay, the entry leaves the log
```

The agent runs `log`, `history`, `doctor`, `ID`, and `ID next` out of a
working state on its own. `new`, `init`, `start`, `defer`, `skip`,
`abandon`, and `next` out of a review state are yours, and every `next`
prompts you. When the review record's last verdict has not converged,
`next` out of a review state refuses and asks the agent to confirm with
you; the rerun carries `--confirmed`, so the confirmation is visible in
the command you approve.

A hook denies hand edits to the quest log and to `quest.md` frontmatter,
so the verbs are the only way state changes. Identifiers are
`YYMMDDHHMM-xx`, a UTC minute plus two random characters, so they sort by
time and never collide across branches.

### On disk

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
blocking and nothing to clarify, or three passes have run. The record
shows you how the document converged, and a later session picks the loop
up from the last pass.

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

### Migrating from an older format

The quest log's header names its format. This plugin writes format 7. A
format 6 tracker, its entries flat under `docs/quests/`, is refused by
every verb until `quest doctor --fix` moves each entry into the directory
its state names; plain `quest doctor` first lists the moves, one `ID ->
STATE/` line each, so you can read them before anything moves. A tracker
older than format 6 is refused with a pointer to the git tag `format-6`
on this repository, the last version that migrated those formats; run
that version's `quest doctor --fix` first.

### What the agent dispatches

The plugin ships seven subagents, named `questlog:NAME` once it is
enabled. Six are reviewers, `review-goal` through `review-plan`,
`review-implement`, and `review-result`, one per review state and one for
evaluate goal; each reads only the checklist for its state and reports.
The seventh, `fact-finder`, answers a factual question from the code, the
docs, memory, or the web, so the agent asks you only what you alone know.
Each agent's model and effort are set in its own file under `agents/`;
all inherit the session's until you change one.

## Requirements

- Claude Code 2.1.195 or later
- `uv` on PATH (https://docs.astral.sh/uv/)
- A git repository to track work in

## Installation

From the `dokidlc` marketplace, once per machine:

```
/plugin marketplace add daftdoki/dokidlc-plugins
claude plugin install questlog@dokidlc
```

Then start a session in a repository and say "set up quests." The agent
runs `quest init`, which creates `docs/quests/`, the quest log, a short
paragraph in `CLAUDE.md`, and one `ask` rule per creator verb in
`.claude/settings.json`. Approve that first run when Claude Code asks;
from then on the rules prompt for every creator verb. Commit the result.

To have a repository declare the plugin for everyone who clones it, add to
`.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": { "dokidlc": { "source": { "source": "github", "repo": "daftdoki/dokidlc-plugins" } } },
  "enabledPlugins": { "questlog@dokidlc": true }
}
```

This adds the marketplace on each machine when the folder is trusted. The
plugin itself still needs the `claude plugin install` line once per machine.

Manual install, without the marketplace: clone this repository and start
Claude Code with `claude --plugin-dir /path/to/dokidlc-skill-questlog`.

See `DEVELOPMENT.md` to work on the plugin itself.
