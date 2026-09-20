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

A fact that lives in the code, the docs, or memory goes to
`questlog:fact-finder`. A question only the creator can answer goes to
the creator in one numbered round with a recommended answer each. A
round is one message that asks every question you can ask now and then
waits.

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
record is `plan-review.md`. For a quest, the reviewer reads the design's
Implementation plan beside the plan.

Findings at this stage. Blocking: a step whose commit leaves the tree
failing, or a step that contradicts the design or the code. Clarification:
a step an implementer would have to ask about before acting.

Checklist for plan:

- Every step names its files and its test.
- The order leaves the tree passing at each commit.
- Every risk has a response.
- The steps cover every line of the quest's Done when.
- For a quest, the commits match the design's Implementation plan, or the
  difference is named.
- Every function, file, test, and command the plan names exists or is
  named as new.
