---
name: quest
description: Track work as quests and chores through one flat machine of states with creator review. Use when the creator asks to open, start, defer, move on, skip, or abandon work, when a state's file is written and the quest should move, or when a session needs to know what is open or completed.
---

# Quest

Work lives under `docs/quests/`, one directory per quest or chore, named
`<id>-<slug>`. `quest.md` holds the metadata, the history, and the Goal
and Done when. Stage files sit beside it. The quest log at
`docs/quests/README.md` is generated; the verbs are the only writers of
it and of any `quest.md` frontmatter. The command is `quest`, on PATH
while this plugin is enabled. Read tracker files with Read and write
stage files with Write or Edit; Bash that redirects into `docs/quests/`
is denied.

Two command shapes. `quest log`, `quest history`, `quest new`, `quest
doctor`, and `quest init` stand alone. Everything about one quest puts
its id first: `quest ID`, `quest ID start`, `quest ID next`. Run
`quest --help` for the list; every verb prints one state line that says
where the quest is and what to do next, and that line is your next
instruction.

## Who does what

You draft. The creator decides.

Yours at any time: `quest log`, `quest history`, `quest ID`, `quest
doctor`. Yours once the state's file exists: `quest ID next` out of a
working state (draft goal, research, design, plan, implement).

The creator's, run only when the creator asked for it in this
conversation and after you have shown the exact command: `quest new`,
`quest ID start`, `quest ID defer`, `quest ID next` out of a review state
or evaluate goal, `quest ID skip`, `quest ID abandon`, `quest init`. The
`ask` rules in the project's settings prompt the creator on every one of
these; no permission mode approves one on its own, and your own `next`
prompts too.

## States

One machine, in order: draft goal, review goal, research, review
research, design, review design, plan, review plan, implement, review
implementation, evaluate goal, then completed. Backlog sits before it
and abandoned beside it. Research and design can be skipped, and each
takes its review with it; every review state can be skipped; draft
goal, plan, implement, and evaluate goal cannot. A chore is a quest
opened with research and design already marked skipped, so it runs draft
goal, review goal, plan, review plan, implement, review implementation,
evaluate goal.

| State | Writes | Reference | Reviewer | Record |
|---|---|---|---|---|
| draft goal | `goal.md` | `references/goal.md` | | |
| review goal | | `references/goal.md` | `questlog:review-goal` | `goal-review.md` |
| research | `research.md` | `references/research.md` | | |
| review research | | `references/research.md` | `questlog:review-research` | `research-review.md` |
| design | `design.md` | `references/design.md` | | |
| review design | | `references/design.md` | `questlog:review-design` | `design-review.md` |
| plan | `plan.md` | `references/plan.md` | | |
| review plan | | `references/plan.md` | `questlog:review-plan` | `plan-review.md` |
| implement | commits, deviations in `plan.md` | `references/implement.md` | | |
| review implementation | | `references/implement.md` | `questlog:review-implement` | `implement-review.md` |
| evaluate goal | the result, against Done when | `references/review.md` | `questlog:review-result` | `result-review.md` |

`quest ID` and `quest ID start` print `guidance:` with the reference to
read first, `reviewer:` and `record:` in a review state, and `overlay:`
when the project has `docs/quests/guidance/STAGE.md`, which is read
second and wins where they differ.

## The loop

A state is a loop, not a gate.

1. Read the reference the state line names, and the overlay when there
   is one.
2. In a working state, write the file. Done when the file exists and
   says what the reference asks for.
3. Run `quest ID next`. The quest enters the review state and the state
   line names the reviewer, the record, and the question to ask.
4. Run the review loop below until it converges or three passes have
   run. Done when the record's last verdict says so.
5. Ask the creator the question the state line printed, in those words,
   with the last verdict beside it. Wait.
6. On changes: revise, loop, ask again. On "move on": show and run
   `quest ID next`. The quest moves only then.

When `next` refuses because the last verdict has not converged, put the
verdict to the creator; run `quest ID next --confirmed` only on their
word.

## Review loop

Dispatch the state's reviewer with the paths its reference lists. It
reports findings as blocking, clarification, or polish, and a verdict.
Record the pass in the state's record beside the stage file, fix what it
found, and dispatch again. A pass with no blocking and no clarification
findings is converged. Three passes in one run without one stop the
loop, and the open findings go to the creator. A converged verdict is a
recommendation; the creator's `next` accepts the state.

## Walk-throughs for creator verbs

When the creator asks to open work, gather in conversation: the title;
quest or chore; the Goal, what they want to accomplish; and Done when,
how we will know. Then show and run `quest new "Title" --goal "..."
--done-when "..."`, with `--chore` for a chore.

When the creator says to move on, name the state and summarize in one
line what they are accepting, then show and run `quest ID next`.

When the creator asks to park or defer work, show and run `quest ID
defer`. Nothing is lost; `quest ID start` resumes the entry at the state
it left.

When the creator abandons, take the reason in their words; the script
refuses an empty one.

## Rules

- A fact that the code, the docs, or memory holds goes to
  `questlog:fact-finder`, and the creator is asked only what the creator
  alone knows.
- If the project has the memory plugin: `quest ID start` and `quest ID`
  name matching memory pages; read them. Search memory again at each
  state: the title before draft goal, each design question during
  research, `decision` pages before recommending in design, and each
  tool the plan touches. When `next` leaves research, design, or plan,
  the script prints the memory prompt: write one page per finding you
  established on your own, citing the stage file with `--ref`, before
  you ask the creator whether to move on.
- A chore is for small features, troubleshooting, and other chores. When
  the creator is unsure which to open, recommend a chore if the Goal fits
  in two sentences and needs no design. A chore still gets a goal and a
  plan.
- Picking an abandoned idea up again is a new quest with a new id.
- If `quest` refuses with "newer questlog", tell the creator to update
  the plugin. If it refuses with "format 5", run `quest doctor` to see
  the migration it proposes, and ask the creator before `quest doctor
  --fix`.
