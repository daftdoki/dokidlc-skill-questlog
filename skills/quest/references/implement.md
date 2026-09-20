# Implement stage

Read this at implement, before you build, and again at review
implementation. If `quest ID` or `quest ID start` printed an `overlay:`
line, read that file next; it adds to this one and wins where they
differ. The Review section at the end is the completion criterion for
review implementation; read it before you start, and run its loop once
`quest ID next` has entered review implementation.

## What the stage produces

Commits, in the order the plan lists, and a Deviations section in
`plan.md` that says where the work left the plan and why. The plan is the
contract; the design, for a quest, is the source of truth for what to
build.

## Before you build

Read the plan and its Deviations. Run `git log --oneline -20` in the code
repository and compare it with the plan's commits: a commit already there
means this is a resumption, and you continue from the first step not yet
committed. Record the commit at HEAD before your first change; the review
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
3. Record any departure from the plan in its Deviations section in the
   same turn, with the date: a step split, a helper the plan did not
   name, an order that worked better.
4. Move to the next step.

Stop mid-loop only for a blocking ambiguity, where the plan contradicts
the code and a decision is needed; for a test failure that survives a
fair attempt; or when context is running out. In each case commit the
complete work first, then tell the creator what is committed and what is
pending.

Keep context small: capture the failing assertion and its traceback, not
the whole test output; refer to code by file and line; read a file again
only when it changed.

## After the last step

Update the documentation the plan promised. Run the project's test suite
and its code review skill when it has one, and fix what they find. Then
run `quest ID next`, which enters review implementation, and run the
review loop below.

## Review

The loop, the tiers, the session's steps, the dispatch list, the
reviewer rules, and the record template are in `review-loop.md`, read
before this section. The reviewer is `questlog:review-implement` and
the record is `implement-review.md`.

Dispatch adds: `plan.md` is the stage file, and the prompt names the
root of the code repository and the commit range, from the earliest
commit newer than the `implement` entry's time in the `history` list of
`quest.md` to HEAD, found with `git log --since=TIME` on the working
branch. The reviewer reads the plan and its Deviations, the record, and
the commits, and runs the suite.

Findings at this stage. Blocking: a commit that does not do what the
plan says with no Deviation saying why, or a test the plan promised
that is missing or fails. Clarification: a deviation the creator would
have to ask about before reviewing.

Checklist for implement:

- Each commit matches a plan step, or the Deviations say why not.
- Every test the plan named exists and passes; the suite passes.
- Every document the plan promised is updated.
- Each deviation is recorded with its date and reason.
- The project's code review ran, where the project has one, and its
  findings are fixed or recorded.

The record adds two lines under `Document:`:

```
Code: /path/to/repository
Commits: OLDEST^..NEWEST
```

OLDEST is the earliest commit `--since` returned, or `none` when it
returned nothing; NEWEST is the sha HEAD resolved to when the pass was
recorded. A diff pass's Scope line reads `diff from HASH1, commits
NEWEST..HEAD-NOW`.
