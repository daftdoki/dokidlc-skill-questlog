---
name: quest
description: Track work as quests and chores with staged review. Use when the creator asks to open, start, move on from a stage of, skip, or abandon a quest or chore, when a stage file is ready for review, or when a session needs to know what work is open or completed.
---

# Quest

Work lives under `docs/quests/`, one directory per quest or chore, named
`<id>-<slug>`. `quest.md` holds the metadata and the Goal and Done when.
Stage files sit beside it. The quest log at `docs/quests/README.md` is
generated; never edit it, or any `quest.md` frontmatter, by hand. The
command is `quest`, on PATH while this plugin is enabled. Read tracker
files with Read and write stage files with Write or Edit; Bash that
redirects into `docs/quests/` is denied.

## Who does what

You draft. The creator decides.

| Verb | Who | Effect |
|---|---|---|
| `quest log` | you | one line per open quest or chore |
| `quest complete [--all] [--limit N]` | you | completed work, newest first, ten by default; `--all` adds abandoned. Run it only when asked; completed work stays out of context otherwise |
| `quest show ID` | you | a quest's metadata, files, current stage, and the stage's guidance; a unique id prefix works |
| `quest draft ID STAGE` | you | the stage file is written, reviewed, and awaits the creator |
| `quest doctor [--fix]` | you | checks the tracker; `--fix` regenerates a stale log |
| `quest init` | creator asks | creates `docs/quests/` and the CLAUDE.md paragraph |
| `quest new "Title" [--chore] [--goal TEXT] [--done-when TEXT]` | creator asks | opens a quest or chore in the backlog |
| `quest start ID` | creator asks | backlog to active |
| `quest next ID STAGE` | creator asks | the creator accepted the current stage; the quest moves to the next one, or from review to completed. Always pass the stage: the script refuses one that is not current, and the approval prompt then names what is being accepted |
| `quest skip ID research` | creator asks | the creator waived research |
| `quest abandon ID "reason"` | creator asks | terminal; the files stay, the entry leaves the log |

Run a creator verb only when the creator asked for it in this conversation,
never because you judged it necessary. Show the exact command before you
run it. The hook turns every creator verb into an approval prompt.

## Stages

A quest: goal, research, design, plan, implement, review. A chore: plan,
implement, review. The current stage is the first one not accepted or
skipped. Only research can be skipped.

`guidance:` names the file to read before you draft. `quest show` and
`quest start` print it for the current stage, with `reviewer:` naming the
stage's review agent and `overlay:`, when the project has one, naming its
own rules for the stage, read second and winning where they differ.

| Stage | Produces | Guidance | Reviewer |
|---|---|---|---|
| goal | `goal.md` | `references/goal.md` | `questlog:review-goal` |
| research | `research.md`, skippable | `references/research.md` | `questlog:review-research` |
| design | `design.md` | `references/design.md` | `questlog:review-design` |
| plan | `plan.md`; a chore's whole plan | `references/plan.md` | `questlog:review-plan` |
| implement | commits, deviations in `plan.md` | `references/implement.md` | `questlog:review-implement` |
| review | the result, against Done when | `references/review.md` | `questlog:review-result` |

A stage is a loop, not a gate. Read the guidance, write the file, run the
review loop, run `quest draft ID STAGE`, and ask the creator one question:
keep iterating on this stage, or move to the next one? Name the next stage
and the last verdict. Wait. On changes, revise, loop, draft, and ask
again. On move on, show and run `quest next ID STAGE`; the quest moves
only then.

## Review loop

Dispatch the stage's reviewer with the paths its guidance lists. It
reports findings as blocking, clarification, or polish, and a verdict.
Record the pass in `STAGE-review.md` beside the stage file, or
`result-review.md` for the review stage, fix what it found, and dispatch
again. A pass with no blocking and no clarification
findings is converged. Three passes in one run without one stop the loop,
and the open findings go to the creator. A converged verdict is a
recommendation; the creator's `quest next` accepts the stage.

## Walk-throughs for creator verbs

When the creator asks to open work, gather in conversation: the title;
quest or chore; the Goal, what they want to accomplish; and Done when, how
we will know. Then show and run `quest new "Title" --goal "..." --done-when
"..."`, with `--chore` for a chore.

When the creator says to move on, name the stage and summarize in one
line what they are accepting, then show and run `quest next ID STAGE`.

A chore goes straight to plan: read the Goal, write `plan.md`, draft it,
and ask before building.

When the creator abandons, take the reason in their words; the script
refuses an empty one.

## Rules

- A fact that the code, the docs, or memory holds goes to
  `questlog:fact-finder`, and the creator is asked only what the creator
  alone knows.
- If the project has the memory plugin: `quest start` and `quest show`
  name matching memory pages; read them. Search memory again at each
  stage: the title before goal, each design question during research,
  `decision` pages before recommending in design, and each tool the plan
  touches. When you draft research, design, or plan, write one memory
  page per finding you established on your own, citing the stage file
  with `--ref`, before you ask the creator whether to move on.
- A chore is for small features, troubleshooting, and other chores. When
  the creator is unsure which to open, recommend a chore if the Goal fits
  in two sentences and needs no design. A chore still gets a plan.
- Never move an abandoned quest back. Picking the idea up again is a new
  quest with a new id.
- If `quest` refuses with "newer questlog", stop and tell the creator to
  update the plugin. Do not work around it.
