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

A quest moves through five stages. Each stage ends with a document the
agent has written and you have read, and it does not advance until you say
so.

1. **Goal.** The agent asks what you want and how you will know you have
   it. You answer, it writes, you correct it, and the two of you settle the
   text together. Everything that follows is judged against this.
2. **Research.** Optional. The agent surveys how others have solved the
   problem, measures what can be measured, and lays out the options with a
   recommendation. You read it, push back where you know better, and it
   revises. Skip this stage when the approach is already clear.
3. **Design.** The agent asks the questions the goal and research left
   open, one at a time with a recommendation for each. You decide. It
   writes the plan, specific enough to build from, and you review that
   too.
4. **Implement.** The agent builds it, in commits, and notes where it had
   to depart from the plan. When it is done it asks you to look.
5. **Review.** You check the result against the goal. When you are
   satisfied, the quest is done.

A chore skips the first three. The agent implements from your one-line
description, then you review.

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
quest draft 2609041432-7k goal              the stage file is written, please review
quest doctor --fix                          check the tracker; regenerate a stale log
quest new "Title" [--chore] [--goal TEXT] [--done-when TEXT]
quest start ID
quest close ID STAGE                        close ID review sets done
quest skip ID research
quest abandon ID "reason"
```

A hook denies hand edits to the quest log and to `quest.md` frontmatter,
so the verbs are the only way state changes. Identifiers are
`YYMMDDHHMM-xx`, a UTC minute plus two random characters, so they sort by
time and never collide across branches.

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

Then in each repository, ask the agent to run `quest init`, or run it
yourself. It creates `docs/quests/`, the quest log, and a short paragraph
in `CLAUDE.md`. Commit the result.

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
