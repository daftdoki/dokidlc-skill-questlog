# dokidlc-skill-questlog

A Claude Code plugin that tracks work as quests and chores. A quest runs
goal, research, design, implement, review; the agent drafts each stage and
the creator closes it. A chore skips straight to implement. Each one is a
directory under `docs/quests/` with a `quest.md` and its stage files, and
the quest log at `docs/quests/README.md` lists what is open, one line each.

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

## Usage

The command is `quest`, on PATH while the plugin is enabled. The agent runs
the read-side verbs itself. It runs the creator verbs only when you ask, and
Claude Code prompts you to approve each one.

```
quest log                                   what is open, newest first
quest show 2609041432-7k                    one quest; a unique id prefix works
quest new "Serve the API over mDNS"         open a quest (you ask, agent runs)
quest new "Fix the volume off-by-one" --chore
quest start 2609041432-7k                   backlog to active
quest draft 2609041432-7k goal              agent: goal.md is written, please review
quest close 2609041432-7k goal              you accepted the stage
quest skip 2609041432-7k research           waive research
quest close 2609041432-7k review            done
quest abandon 2609041432-7k "superseded"    stop; the files stay
quest doctor --fix                          check the tracker; regenerate a stale log
```

In conversation this looks like: "open a quest for mDNS discovery" and the
agent asks for the goal and the done-when, shows the command, and runs it.
"The design stage is complete" and the agent shows `quest close ... design`
and runs it. A hook denies hand edits to the quest log and to `quest.md`
frontmatter, so the verbs are the only way state changes.

Identifiers are `YYMMDDHHMM-xx`, a UTC minute plus two random characters,
so they sort by time and never collide across branches.

See `DEVELOPMENT.md` to work on the plugin itself.
