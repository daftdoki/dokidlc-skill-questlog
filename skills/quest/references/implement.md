# Implement stage

Read this at implement, before you build, and again at review
implementation. If `quest ID` or `quest ID start` printed an `overlay:`
line, read that file next; it adds to this one and wins where they
differ. The Review section at the end is the completion criterion for
review implementation; read it before you start, and run its loop once
`quest ID next` has entered review implementation.

Implement works the checklist, a failing test, the least code, a
commit, a tick; what to build belongs to the plan or the brief. It
reads the checklist and the code. It ends when every step is ticked
and the suite passes.

## What the stage produces

Commits, in the order the Steps checklist lists, each step ticked, and a
Deviations from plan section that says where the work left the steps and why. The
checklist is in `plan.md` for a quest and in `brief.md` for a chore;
`document:` names the file. The checklist is the contract; the design,
for a quest, is the source of truth for what to build. A task has no
checklist; its section is at the end.

## Before you build

Read the document `document:` names and its Deviations from plan. `quest` recorded
each step when the quest entered implement, and `quest ID` prints
`checklist: N of M ticked`: a ticked step is done, so on a resumption you
continue from the first unticked one. Run `git log --oneline -20` in the
code repository to confirm the ticked steps' commits are there. Record the commit at HEAD before your first change; the review
loop and the project's code review both start from it.

When a step will write a skill, an agent, or any document an agent
reads, load the `writing-for-agents` skill first.

## The loop

Work the steps in order, and keep going between steps. For each step:

1. Where the project has tests, write the failing test first and run it
   alone, so it fails for the right reason. Then write the least code
   that passes it, and run the suite.
2. Commit when the step's behaviour is complete, with a message that says
   what capability the commit adds. Stage the files the step touched.
3. Tick the step: `- [ ]` becomes `- [x]`, and nothing else on the item
   changes. Done when `quest ID` counts it.
4. Record any departure in the Deviations from plan section in the same turn, with
   the date: a step split, a helper the step did not name, an order that
   worked better. The step's words stay as the creator accepted them;
   `quest ID next` refuses a checklist whose words changed.
5. Move to the next step.

A step that cannot be done stays unticked. That is a Deviation that
goes to the creator: say what is committed and why the step is open, and
run `quest ID next --confirmed` only on their word.

Stop mid-loop only for a blocking ambiguity, where the plan contradicts
the code and a decision is needed; for a test failure that survives a
fair attempt; or when context is running out. In each case commit the
complete work first, then tell the creator what is committed and what is
pending.

Keep context small: capture the failing assertion and its traceback, not
the whole test output; refer to code by file and line; read a file again
only when it changed.

## After the last step

Update the documentation the steps promised. Run the project's test suite
and its code review skill when it has one, and fix what they find. Then
run `quest ID next`, which enters review implementation once every step
is ticked, and run the review loop in `review-loop.md`.

## A task

A task has no document and no reviewer. Read the Goal in `quest.md`.
Write the failing test and run it alone, so it fails for the right
reason; write the least code that passes it; run the project's checks
and its code review skill when it has one; commit. Then run `quest ID
next`, show the creator the commits, and ask whether it is done. If the
work grows past one sentence of diff, tell the creator: it is a chore,
opened with `quest new "Title" --chore --from ID` so the new entry
cites this one.

A prototype is a task started with `--prototype`: a throwaway built to
learn. Build it on a branch named after the id and leave it unmerged.
At evaluate goal, write what was learned under `## Learned` in
`quest.md`, one paragraph; `accept` refuses without it. The longer
piece of work that follows is opened with `--from ID`, and its goal's
Background opens with that paragraph and the branch.

## Review

The loop, the tiers, the session's steps, the dispatch list, the
reviewer rules, and the record template are in `review-loop.md`, read
before this section. The reviewer is `questlog:review-implement` and
the record is `implement-review.md`. Review implementation runs the
long loop and is an agent gate.

Dispatch adds: the file `document:` names is the stage file, `plan.md`
or a chore's `brief.md`, and the prompt names the
root of the code repository and the commit range, from the earliest
commit newer than the `implement` entry's time in the `history` list of
`quest.md` to HEAD, found with `git log --since=TIME` on the working
branch. The reviewer reads the checklist and the Deviations from plan, the record,
and the commits, and runs the suite.

Rubric for implement.

1. Blocking. Each commit does what its step says, every step is ticked,
   or a Deviation says why not. Fail: step 3's commit adds a flag the step never named
   and Deviations from plan is silent.
2. Blocking. Every test the plan named exists and passes, and the suite
   passes. Fail: a test the plan promised is absent.
3. Blocking. Every claim in Deviations from plan holds against the code. Fail: a
   Deviation says a helper was reused where the commit adds a new one.
4. Clarification. Every document the plan promised is updated. Fail:
   the README section the plan named is unchanged.
5. Clarification. Each deviation carries its date and reason, and the
   project's code review ran where the project has one. Fail: a
   Deviation with no date.

The record adds two lines under `Document:`:

```
Code: /path/to/repository
Commits: OLDEST^..NEWEST
```

OLDEST is the earliest commit `--since` returned, or `none` when it
returned nothing; NEWEST is the sha HEAD resolved to when the pass was
recorded. A diff pass's Scope line reads `diff from HASH1, commits
NEWEST..HEAD-NOW`.
