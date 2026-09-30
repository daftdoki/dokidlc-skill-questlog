# Plan stage

Read this at plan, before you write `plan.md`, and again at review
plan. If `quest ID` or `quest ID start` printed an `overlay:` line, read
that file next; it adds to this one and wins where they differ. The
Review section at the end is the completion criterion for review plan;
read it before you write, and run its loop once `quest ID next` has
entered review plan.

## What the stage produces

`plan.md` says what will happen during implementation, in order, before
anything is built. The creator reads it and adjusts it first. It has
these parts, in this order: What exists, Steps, Files touched, Commits
expected, Tests, What could go wrong, Out of scope, and Deviations, kept
empty here and filled during implementation.

For a quest, the plan turns the design's Implementation plan into steps.
For a chore, there is no design; the plan is the whole plan for the fix,
written from the chore's Goal, and it is the one document the creator
reads before the work.

## Before you write

Read the design, or for a chore the Goal and Done when. Read the code
each step touches, so the plan names real functions and real files.
Search memory for each tool the plan touches: the build, the test runner,
the package manager, the deploy path.

Plan runs without the creator. A fact that lives in the code, the docs,
or memory goes to `questlog:fact-finder`. A question the design and the
goal do not answer and only the creator can pauses the run: ask it,
numbered, with a recommended answer, and wait.

## Writing

What exists states the code as it is, in the words the steps will use.

Each step names what changes, in which files, and which test proves it.
Steps are in the order they will run. A step that another depends on
comes first. Each step ends where a commit lands, and the commit leaves
the tests passing.

Files touched is the full list, new and changed, so the creator sees the
blast radius.

Commits expected names each commit's message in a line.

Tests names each new or changed test and the command that runs the
suite.

What could go wrong lists each risk with its response: the check that
catches it, or the fallback when it happens.

Out of scope names what the plan leaves alone, including what the design
listed.

## Review

The loop, the tiers, the session's steps, the dispatch list, the
reviewer rules, and the record template are in `review-loop.md`, read
before this section. The reviewer is `questlog:review-plan` and the
record is `plan-review.md`. For a quest, the reviewer reads the
design's Implementation plan beside the plan. Review plan is an agent
gate: the session answers each Clarification from the design, the
code, or a fact-finder and records the answer.

Rubric for plan.

1. Blocking. Each step's commit leaves the tree passing. Fail: a step
   that removes a function before the step that removes its callers.
2. Blocking. No step contradicts the design or the code. Fail: a step
   edits a function the code does not have and no step adds.
3. Blocking. The steps cover every line of the quest's Done when. Fail:
   Done when names a document update no step touches.
4. Clarification. Every step names its files and the test that proves
   it. Fail: "update the skill" with no file and no test.
5. Clarification. Every risk under What could go wrong has a response.
   Fail: a risk with no check and no fallback.
6. Clarification. For a quest, the commits match the design's
   Implementation plan or the difference is named. Fail: four commits
   where the design listed two, unexplained.
