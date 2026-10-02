# dokidlc-skill-questlog

A Claude Code plugin that tracks your agent's work as ideas, tasks, chores, and quests, with you deciding at the goal, the design, and the result.

A quest moves through one flat machine of states, from draft goal to evaluate goal. The agent writes each state's document, reviews it, and runs the states between your three gates; at a gate you read, you iterate together, and the quest moves on when you say so. Each quest is a directory under `docs/quests/active/`, `backlog/`, `completed/`, or `abandoned/`, holding a `quest.md` and its stage files. The directory moves when the state changes, so a file listing shows what is active, and the quest log at `docs/quests/README.md` lists what is open, one line each.

Work is captured first and shaped later. `quest new "Title"` records an idea in one line and asks nothing. When you start it you give it one of three sizes. A task is a change that fits one sentence: no document, no reviewer, the tests are the review. A chore is a bug fix, a small addition, a bit of upkeep: one document, the brief, which holds the goal and a checklist of steps. A quest is a feature, a redesign, an investigation: goal, research, design, and plan. All get an identifier, a directory, and a place in the log; they differ in which states they pass through. In a quest, research and design can be skipped, and each takes its review with it.

```
draft goal -> review goal -> research -> review research -> design -> review design
  -> plan -> review plan -> implement -> review implementation -> evaluate goal -> completed
```

With the plugin enabled, the agent tells you what is open at the start of every session, reads a quest before working on it, writes the stage documents, and runs the states between your gates on its own. You decide at three gates: the goal, the design, and the result. Before you see a document it has already run a fresh-context reviewer over it and fixed what that found. It will not open, start, park, accept, skip, or abandon anything by itself. Those happen only when you ask, and the agent shows you the command before it runs it.

## Why questlog

A tracker aimed at people, whether GitHub issues or Taskwarrior, records that work exists. This one records how work is decided: the goal you agreed, the research behind it, the plan, and a review record per stage showing what a reviewer found and what changed. The agent reads that record at the start of a session instead of asking you again, and the state machine is what stops it running from an idea straight to a commit.

The cost is ceremony. A one-line fix does not want a goal document, and if your agent mostly answers questions rather than building things, this will feel like paperwork. It suits a project where the same agent returns to the same work across many sessions.

Status: maintained, used daily since 2026-09-05. The tracker format is at version 8; `quest doctor --fix` migrates a format 6 tracker, and older ones need the `format-6` git tag first.

## Requirements

- Claude Code 2.1.195 or later
- `uv` on PATH (https://docs.astral.sh/uv/)
- A git repository to track work in
- The `writing-for-agents@dokidlc` plugin, installed and enabled. Every stage file is read by an agent, so the agent writes each one under that skill; `quest` names it at every state and `quest doctor` fails a row without it.

## Install

From the `dokidlc` marketplace, once per machine:

```
/plugin marketplace add daftdoki/dokidlc-plugins
claude plugin install questlog@dokidlc
claude plugin install writing-for-agents@dokidlc
```

Then start a session in a repository and say "set up quests." The agent runs `quest init`, which creates `docs/quests/`, the quest log, and a short paragraph in `CLAUDE.md`. Commit the result.

To have a repository declare the plugin for everyone who clones it, add to `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": { "dokidlc": { "source": { "source": "github", "repo": "daftdoki/dokidlc-plugins" } } },
  "enabledPlugins": { "questlog@dokidlc": true }
}
```

Settings enable the plugin; each machine still runs the `claude plugin install` line once.

## Run it

Talk to the agent. Every command prints one line saying where the quest is and what happens next:

```
2609051012-k3 is at review goal. Run the review-goal loop into goal-review.md, then ask the creator: move on to researching? On their word, run: quest 2609051012-k3 accept
```

- "What's open?" The agent runs `quest log` and reads you the list.
- "What have we completed?" `quest history`, the last ten newest first. `--all` adds abandoned ones. Completed work stays out of the log and out of the session until you ask.
- "Note this down: discover the bridge over mDNS." `quest new "Discover the bridge over mDNS"`. An idea is in the backlog, and nothing else is asked.
- "Open a quest for discovering the bridge over mDNS." The agent asks for the goal and how you'll know it is done, shows you `quest new "Discover the bridge over mDNS" --quest --goal "..." --done-when "..."`, and runs it. Say "chore" or "task" for the smaller sizes.
- "Start the bridge idea." The agent asks at most three questions with a recommended answer each, and on your word runs `quest 2609051012-k3 start --chore`, or `--quest --explore` when you want to find what you do not know, or `--task --prototype` for a throwaway to learn from.
- "What did we learn from the prototype?" Its `quest.md` holds a `## Learned` paragraph, and `quest new "Title" --quest --from 2609051012-k3` opens the real work with that paragraph copied in.
- "Start the mDNS quest." `quest 2609051012-k3 start`. The quest is at draft goal.
- "Draft the goal." The agent interviews you, writes `goal.md`, runs `quest 2609051012-k3 next`, runs the review loop, and asks: move on to researching?
- "Change the second story." The agent revises, runs the loop again, and asks again, as many times as it takes.
- "Move on." The agent shows and runs `quest 2609051012-k3 accept`, then runs research, its review, and design on its own and stops at review design. After you accept the design it runs plan, its review, implement, and its review, and stops at evaluate goal. From there, accept completes the quest. It pauses in between only for a Blocking finding it could not fix, a deviation that touches Done when, a question only you can answer, or an irreversible action outside the repository.
- "Skip research on this one." `quest 2609051012-k3 skip`; review research goes with it.
- "Park the mDNS quest." `quest 2609051012-k3 defer`. The log shows `backlog, resume at review plan`, and `start` picks it up there.
- "Abandon it, we're going with the bridge's own discovery." `quest 2609051012-k3 abandon "reason"`.

The commands behind those sentences:

```
quest new "Title" [--task|--chore|--quest] [--goal TEXT] [--done-when TEXT] [--from ID]   capture an idea, or open a shaped entry
quest log                                   what is open, newest first
quest history [--all] [--limit N]           what is completed, newest first, ten by default
quest doctor [--fix] [--brief]              check the tracker; --fix migrates and repairs
quest init                                  set up a repository; drops quest ask rules an older plugin wrote

quest 2609051012-k3                         show one quest; a unique id prefix works
quest 2609051012-k3 start [--task [--prototype] | --chore | --quest [--define|--explore]]
                                            leave the backlog; an idea needs its shape; a deferred entry resumes
quest 2609051012-k3 notify [TEXT]           the state line, and a desktop notification where the platform has one
quest 2609051012-k3 defer                   back to the backlog; the state is kept
quest 2609051012-k3 next [--confirmed]      the current state is done; enter the next one; refuses at a gate
quest 2609051012-k3 accept                  your word at review goal, review design, and evaluate goal
quest 2609051012-k3 skip                    skip the current state
quest 2609051012-k3 abandon "reason"        terminal; files stay, the entry leaves the log
```

The agent runs `log`, `history`, `doctor`, `ID`, `ID next`, and `ID notify` on its own. The rest are yours: the agent runs one only when you say so, after showing you the command.

## Caveats

- A hook denies hand edits to the quest log and to `quest.md` frontmatter, so the verbs are the only way state changes. Edit the body of a `quest.md` freely; the frontmatter is refused. [docs/on-disk.md](docs/on-disk.md) has the full trigger table.
- The guard is for habit, not for an adversary. A command that reaches the tracker without naming it, through an encoded payload or a script on stdin, gets through. `quest doctor` is the check behind it.
- Without `uv` on PATH, guarded actions are refused rather than allowed, and everything else proceeds.
- A document review is one pass and at most one diff pass; a code review runs until it converges or three passes are spent. Findings still open come to you; nothing blocks.
- The plugin installs once per machine. `.claude/settings.json` can enable it for every clone but cannot install it.

## Other docs

- [docs/on-disk.md](docs/on-disk.md) is the tracker layout, the `quest.md` format, the guard's trigger table, and the seven subagents the plugin ships.
- [DEVELOPMENT.md](DEVELOPMENT.md) is for working on the plugin itself: the checkout, the tests, the hook contract, and the release steps.
- The skill and its references, one per working state and one for a chore's brief, are under `skills/quest/`; `quest ID` prints the path to the one a state needs.

Questions and bugs go to the [issue tracker](https://github.com/daftdoki/dokidlc-skill-questlog/issues).

## License

MIT, DaftDoki. See [LICENSE](LICENSE).
