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

## How work moves

Three states. The creator moves work between them; the agent works inside
`active`.

```
                quest start              quest close ID review
  ( new ) ──▶ backlog ───────▶ active ─────────────────────▶ done
                 │                │
                 │ quest abandon  │ quest abandon
                 ▼                ▼
              abandoned        abandoned
```

Inside `active`, a quest walks five stages in order and a chore walks the
last two. Each stage is drafted by the agent and closed by the creator.

```
  quest:  goal ──▶ research ──▶ design ──▶ implement ──▶ review ──▶ done
                    (or skip)                  ▲
  chore:                                       └── starts here

  one stage:   [not started] ──▶ [drafted] ──▶ [closed]
                agent writes the file   creator says so, agent runs
                and runs quest draft    quest close
```

| Stage | Produces | Who drives it |
|---|---|---|
| goal | `goal.md`, what you want and how you'll know | agent interviews you |
| research | `research.md`, options with a leaning; skippable | agent surveys |
| design | `design.md`, the plan to build from | agent asks, you decide |
| implement | commits | agent builds |
| review | your read against the done-when | you |

Abandoned keeps every file and leaves the log. Done leaves the log too.
The log shows only `backlog` and `active`.

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
