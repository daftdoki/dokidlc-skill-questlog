# dokidlc-skill-questlog

A Claude Code plugin that lets your agent track work as quests and chores
with you in charge of every gate. A quest runs goal, research, design,
implement, review; the agent drafts each stage as a document and you close
it. A chore skips straight to implement. Each one is a directory under
`docs/quests/` holding a `quest.md` and its stage files, and the quest log
at `docs/quests/README.md` lists what is open, one line each.

With it enabled, the agent will on its own: tell you what is open at the
start of every session, read a quest before working on it, write the stage
documents, and mark a stage as drafted when it wants your review. It will
not open, start, close, skip, or abandon anything by itself. Those happen
only when you ask, and Claude Code prompts you to approve the exact command
each time.

## Process

Work comes in two sizes. A quest is a feature, a redesign, an
investigation: anything worth thinking through before it is built. A chore
is a bug fix, a small addition, a bit of upkeep: anything you could
describe in two sentences and hand over. Both get an identifier, a
directory, and a place in the log. They differ in how many stages they
pass through.

A quest moves through six stages. Each stage ends with a document the
agent has written and you have read, and it does not advance until you say
so.

1. **Define the goal.** The agent asks what you want and how you will know you have
   it. You answer, it writes, you correct it, and the two of you settle the
   text together. Everything that follows is judged against this.
2. **Do the research.** Optional. The agent surveys how others have solved the
   problem, measures what can be measured, and lays out the options with a
   recommendation. You read it, push back where you know better, and it
   revises. Skip this stage when the approach is already clear.
3. **Iterate on the design.** The agent asks the questions the goal and research left
   open, one at a time with a recommendation for each. You decide. It
   writes the plan, specific enough to build from, and you review that
   too.
4. **Plan the work.** The agent writes down what it is about to do: the
   steps in order, the files it will touch, the tests, and what could go
   wrong. You read it and adjust it before anything changes.
5. **Build it.** The agent builds it, in commits, and notes where it had
   to depart from the plan. When it has finished it asks you to look.
6. **Review the result.** You check the result against the goal. When you are
   satisfied, the quest is completed.

A chore skips the first three. The agent plans from your one-line
description, you read the plan, it builds, you review.

At any stage you can abandon the work. Its files stay for the record; it
leaves the log.

## Usage

Talk to the agent. It runs the commands.

- "What's open?" or "Show me the quest log." The agent runs `quest log`
  and reads you the list.
- "Open a quest for discovering the bridge over mDNS." The agent asks for
  the goal and how you'll know it is done, shows you `quest new "Discover
  the bridge over mDNS" --goal "..." --done-when "..."`, runs it, and you
  approve the prompt.
- "Open a chore to fix the volume off-by-one." Same, with `--chore`; the
  chore starts at implement.
- "Start the mDNS quest." The agent runs `quest start 2609041432-7k`.
- "Draft the goal." The agent interviews you, writes `goal.md`, runs
  `quest draft 2609041432-7k goal`, and asks whether the stage is complete.
- "Plan it." The agent writes `plan.md` and asks you to read it before it
  builds anything.
- "Yes, the goal stage is complete." The agent shows and runs
  `quest close 2609041432-7k goal`.
- "Skip research on this one." `quest skip 2609041432-7k research`.
- "Abandon the mDNS quest, we're going with the bridge's own discovery."
  `quest abandon 2609041432-7k "we're going with the bridge's own discovery"`.
  The files stay; the entry leaves the log.

### The commands

The agent runs the first four on its own and the rest only when you ask.

```
quest log                                   what is open, newest first
quest show 2609041432-7k                    one quest; a unique id prefix works
quest draft 2609041432-7k plan              the stage file is written, please review
quest doctor --fix                          check the tracker; regenerate a stale log
quest new "Title" [--chore] [--goal TEXT] [--done-when TEXT]
quest start ID
quest close ID STAGE                        close ID review completes it
quest skip ID research
quest abandon ID "reason"
```

A hook denies hand edits to the quest log and to `quest.md` frontmatter,
so the verbs are the only way state changes. Identifiers are
`YYMMDDHHMM-xx`, a UTC minute plus two random characters, so they sort by
time and never collide across branches.

### On disk

```
docs/quests/
  README.md                          the quest log, generated
  2609051012-k3-discover-the-bridge/
    quest.md                         metadata and the goal, owned by the verbs
    goal.md  research.md  design.md  plan.md      written by the agent, read by you
```

`quest.md` is frontmatter and a short body:

```
---
id: 2609051012-k3
title: Discover the bridge over mDNS
kind: quest                # or chore
state: active              # backlog, active, done, abandoned
created: '2026-09-05T10:12:00Z'
started: '2026-09-05T10:20:00Z'
goal_drafted: '...'        # one pair of keys per stage
goal_closed: '...'
research_skipped: '...'
abandoned_reason: ...      # only when abandoned
---
## Goal

What you want.

## Done when

How you will know.
```

The quest log is a heading, a comment naming the format and the plugin
version, and a table with one row per open entry: id, kind, state,
current stage, title. `quest log` prints the same table aligned for the
terminal. Completed and abandoned entries are not listed. The state key is
`done` in the file; in this document and in conversation, a quest or
chore is completed.

**What is guarded.** The log and every `quest.md` frontmatter block are
written only by the verbs, so the log always matches the directories and
a stage date is never typed by hand. A `PreToolUse` hook on the Edit,
Write, and Bash tools enforces it:

| Trigger | Result |
|---|---|
| Edit or Write to `docs/quests/README.md` | denied |
| Edit or Write that touches a `quest.md` frontmatter block | denied; the body below it is fine |
| Bash that names `docs/quests` and redirects, `sed -i`, `tee`, an inline Python or Perl, or a heredoc into it | denied |
| Bash that runs `quest init`, `new`, `start`, `close`, `skip`, or `abandon` | you are asked to approve, with the command shown |
| Anything else, including the agent writing a stage file | allowed |

A `SessionStart` hook runs `quest doctor --brief`, one line telling the
agent how many entries are open, or that the log was written by a newer
plugin. If `uv` is missing, guarded actions are refused rather than
allowed, and everything else proceeds.

The guard is for habit, not for an adversary. A command that reaches the
tracker without naming it, through an encoded payload or a variable, gets
through; `quest doctor` is the check behind it. The script itself never
writes through a symlink, so a cloned repository cannot point the quest
log or a quest directory at another file.

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
runs `quest init`, which creates `docs/quests/`, the quest log, and a
short paragraph in `CLAUDE.md`, and asks you to approve it. Commit the
result.

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
