---
name: quest
description: Track work as ideas, tasks, chores, and quests through one flat machine of states with three creator gates. Use when the creator asks to capture, open, start, defer, accept, skip, or abandon work, when a state's file is written and the quest should move, or when a session needs to know what is open or completed.
---

# Quest

Work lives under `docs/quests/STATE/`, one directory per quest or chore,
named `<id>-<slug>`, where STATE is `active`, `backlog`, `completed`, or
`abandoned`; the verbs move the directory when the state changes, so
`quest ID` is how you find one. `quest.md` holds the metadata, the
history, and the Goal and Done when. Stage files sit beside it. The quest
log at `docs/quests/README.md` is generated; the verbs are the only
writers of it, of any `quest.md` frontmatter, and of where a directory
sits. The command is `quest`, on PATH while this plugin is enabled. Read
tracker files with Read and write stage files with Write or Edit; Bash
that redirects into `docs/quests/` is denied.

Two command shapes. `quest log`, `quest history`, `quest new`, `quest
doctor`, and `quest init` stand alone. Everything about one quest puts
its id first: `quest ID`, `quest ID start`, `quest ID next`, `quest ID
accept`. Run `quest --help` for the list; every verb prints one state
line that says where the quest is and what to do next, and that line is
your next instruction.

## Who does what

You draft and run the states. The creator decides at three gates.

Yours at any time: `quest log`, `quest history`, `quest ID`, `quest
doctor`. Yours once a state's work is done: `quest ID next`, which
leaves every state but the three gates. It refuses at a gate.

The creator's, run only when the creator asked for it in this
conversation and after you have shown the exact command: `quest new`,
`quest ID start`, `quest ID defer`, `quest ID accept`, `quest ID skip`,
`quest ID abandon`, `quest init`. No permission rule prompts on them;
this rule is what keeps them the creator's. `quest ID next
--confirmed`, which leaves an agent gate whose loop stopped short, is
run on the creator's word too.

## States

One machine, in order: draft goal, review goal, research, review
research, design, review design, plan, review plan, implement, review
implementation, evaluate goal, then completed. Backlog sits before it
and abandoned beside it. Research and design can be skipped, and each
takes its review with it; every review state can be skipped, and
skipping a creator gate is the creator accepting without a review;
draft goal, plan, implement, and evaluate goal cannot.

An entry has one of four kinds, and the kind decides which states it
passes over. The skips are written into its history when it is shaped.

| Kind | For | States | Document |
|---|---|---|---|
| idea | a captured description, not yet shaped | none; it waits in the backlog | none |
| task | a change that fits one sentence and about three files | implement, evaluate goal | none; the commits are the record |
| chore | a Goal that fits two sentences and needs no design | draft goal, review goal, implement, review implementation, evaluate goal | `brief.md`: the goal and the steps |
| quest | anything else | all | `goal.md`, `research.md`, `design.md`, `plan.md` |

A chore's draft goal writes `brief.md` under `references/brief.md`, and
its review goal records into `brief-review.md`. A task has no reviewer
at any state. A chore opened before the brief existed keeps its recorded
skips and still writes `goal.md` and `plan.md`; `quest ID` names the
file either way.

| State | Writes | Reference | Reviewer | Record | Gate |
|---|---|---|---|---|---|
| draft goal | `goal.md` | `references/goal.md` | | | agent |
| review goal | | `references/goal.md` | `questlog:review-goal` | `goal-review.md` | creator |
| research | `research.md` | `references/research.md` | | | agent |
| review research | | `references/research.md` | `questlog:review-research` | `research-review.md` | agent |
| design | `design.md` | `references/design.md` | | | agent |
| review design | | `references/design.md` | `questlog:review-design` | `design-review.md` | creator |
| plan | `plan.md` | `references/plan.md` | | | agent |
| review plan | | `references/plan.md` | `questlog:review-plan` | `plan-review.md` | agent |
| implement | commits, deviations in `plan.md` | `references/implement.md` | | | agent |
| review implementation | | `references/implement.md` | `questlog:review-implement` | `implement-review.md` | agent |
| evaluate goal | the result, against Done when | `references/review.md` | `questlog:review-result` | `result-review.md` | creator |

`quest ID` and `quest ID start` print `guidance:` with the reference to
read first, `document:` with the absolute path of the file under
review, `gate:` with who leaves the state, `reviewer:` and `record:` in
a review state, `interview:` and `coverage:` at the goal states,
`checklist:` from implement on, and `overlay:` when the project has
`docs/quests/guidance/STAGE.md`, which is read second and wins where
they differ.

## The run

The creator accepts the goal, and you run: research, its review,
design, and you stop at review design. The creator accepts the design,
and you run: plan, its review, implement, its review, and you stop at
evaluate goal. For a chore, accepting the brief runs implement and its
review. A task runs implement and stops at evaluate goal. A quest with research or design skipped runs the
states that remain. Between gates you do not ask the creator whether
to move on; the state line says `next` and you run it.

The run pauses for four things and nothing else. The script wakes the
creator with a desktop notification when a verb refuses and when the
run lands on a creator gate; for a pause only you see, a question or an
irreversible action, run `quest ID notify "TEXT"`. Each pause is put to
the creator with its evidence:

- A Blocking finding still open after the loop's last pass: the
  `last pass:` line.
- A Deviation that touches a Done when line or a Success item: the
  Deviations section.
- A question the stage files do not answer and only the creator can: the
  numbered question, with a recommended answer.
- An action outside the repository that cannot be undone: the command,
  shown and not run.

## A state

1. Read the reference the state line names, and the overlay when there
   is one. Load the skill the `skill:` line names, or tell the creator
   it is missing; every stage file is read by an agent.
2. In a working state, write the file. Done when the file exists and
   says what the reference asks for.
3. Run `quest ID next`. The quest enters the review state and the state
   line names the reviewer and the record.
4. Run the loop in `references/review-loop.md`: the short loop at a
   document state, the long loop at a code state. Done when the loop
   ends; `quest ID` prints no `last pass:` line after a converged pass.
5. At an agent gate, run `quest ID next` and go to step 1 of the next
   state. At a creator gate, one message: the document's full path,
   with "open it in a Herdr pane, in the default viewer, or read on?",
   the open Clarifications as numbered questions, and the question the
   state line printed, in those words. The Herdr pane is offered when
   `HERDR_ENV=1` and opens through the `herdr-file-viewer` skill, given
   the path relative to the repository `quest` ran in; the default
   viewer is `open PATH` on macOS and `xdg-open PATH` on Linux. Wait.
6. On changes: revise, run the loop again, ask again. On "move on" or
   "the goal is met": show and run `quest ID accept`. The quest moves
   only then.

## Walk-throughs for creator verbs

When the creator gives a bare description to record, capture it: show
and run `quest new "Title"`. That is an idea; ask nothing more.

When the creator asks to open work and knows its shape, gather the
title, the Goal, and the Done when, then show and run `quest new "Title"
--task`, `--chore`, or `--quest`, with `--goal "..." --done-when "..."`.

When the creator says to start an idea whose description already names
the change and fits one sentence, ask nothing: say the shape in one
line and run `quest ID start --task` on their word. Otherwise shape it
in one message of at most three questions, each with a recommended
answer drawn from the description and the code, so the common reply is
"yes"; the later questions apply only when the first answer is no:

1. Can the change be said in one sentence, touching about three files?
   Yes is a task, and the run begins at implement. Add: is it a
   throwaway to learn from? Yes is `--prototype`.
2. Do you know what you want, or do you want to explore what is
   possible? That is `--define` or `--explore`, for a quest.
3. Will the work need decisions between alternatives, or is it clear how
   to build once the goal is written? Alternatives is a quest, clear is
   a chore.

Then show and run `quest ID start` with the flags the answers give. An
entry that never started can be reshaped the same way; one that started
resumes with plain `quest ID start`. Work that outgrows its shape, or a
prototype that taught what the real work is, gets a new entry: `quest
new "Title" --chore --from ID` or `--quest --from ID`, which cites the
earlier entry and copies its `## Learned` paragraph.

When the creator says to move on at a gate, name the state and
summarize in one line what they are accepting, then show and run
`quest ID accept`.

When the creator asks to park or defer work, show and run `quest ID
defer`. Nothing is lost; `quest ID start` resumes the entry at the state
it left.

When the creator abandons, take the reason in their words; the script
refuses an empty one.

## Rules

- A fact that the code, the docs, or memory holds goes to
  `questlog:fact-finder`, and the creator is asked only what the creator
  alone knows.
- A numbered question carries a recommended answer, and a bare "yes"
  from the creator takes it. Word a yes-or-no question so that "yes" is
  the recommendation.
- If the project has the memory plugin: `quest ID start` and `quest ID`
  name matching memory pages; read them. Search memory again at each
  state: the title before draft goal, each design question during
  research, `decision` pages before recommending in design, and each
  tool the plan touches. When `next` leaves research, design, or plan,
  the script prints the memory prompt: write one page per finding you
  established on your own, citing the stage file with `--ref`, before
  you run the next state.
- When the creator is unsure of the shape, recommend the smallest that
  fits: a task if the diff fits one sentence, a chore if the Goal fits
  two sentences and needs no design, a quest otherwise. Work that
  outgrows its shape goes to the creator: a task that needs steps is a
  chore, a chore that needs a decision between alternatives is a quest.
- At implement, tick each step as its commit lands and leave its words
  as accepted; `quest ID next` refuses an unticked or changed checklist.
- Picking an abandoned idea up again is a new quest with a new id.
- If `quest` refuses with "newer questlog", tell the creator to update
  the plugin. If `quest doctor` reports stale ask rules, an older
  plugin wrote them; `quest doctor --fix` drops them. If it refuses
  with "format 6", run `quest
  doctor` to see the moves it proposes, and ask the creator before
  `quest doctor --fix`. If it refuses with "format-6 first", the tracker
  predates format 6: the creator runs that tagged version's `quest
  doctor --fix` before this one can read it.
