# Plan stage

Read this before you draft `plan.md`. If `quest show` or `quest start`
printed an `overlay:` line, read that file next; it adds to this one and
wins where they differ. The Review section at the end is the completion
criterion for this stage; read it before you write, and run its loop
before `quest draft`.

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

The completion criterion for this stage: every item in the checklist
holds. Run the loop before `quest draft`.

The loop. Dispatch `questlog:review-plan` with four paths: the stage
file, this reference file, the prior review record `plan-review.md` when
it exists, and the root of the code the plan changes. The reviewer reads
this section, the document, and the record, and returns findings by tier
with a verdict. You record the pass in `plan-review.md`, fix what it
found, and dispatch again. A pass that reports no blocking and no
clarification findings is converged, and the loop stops. Three passes in
one run that each report another pass also stop the loop, and the open
findings go to the creator. A run begins when you start the loop and
ends at `quest draft` or when the session ends. A converged verdict is a
recommendation; the creator's `quest next` accepts the stage.

Tiers. A blocking finding: the document is wrong, contradicts itself, or
rests on a claim that fails against the code, the design, or the sources
it cites. A clarification: an implementer would have to ask before
acting. Polish: wording, order, style; fixed on sight and not counted.

Reviewer rules. Authorship is not evidence; a claim holds when the file
or the cited source says so. Verify function names, file paths, test
names, and commands against the code. Report; the session edits. The
document reads as one pass by an author who knew the answer all along,
so a passage that narrates its own revisions is a clarification finding.

Checklist for plan:

- Every step names its files and its test.
- The order leaves the tree passing at each commit.
- Every risk has a response.
- The steps cover every line of the quest's Done when.
- For a quest, the commits match the design's Implementation plan, or the
  difference is named.
- Every function, file, test, and command the plan names exists or is
  named as new.

The record. `plan-review.md` beside the stage file, written by you, one
section per pass:

```
# Review record: plan

## Pass N, DATE

Reviewer: questlog:review-plan
Document: plan.md at HASH, document changed since pass N-1

Blocking
- location: finding. Fixed: what changed.
Clarification
- ...
Polish
- fixed on sight
Verdict: converged | another pass
```

HASH is the first seven characters of `git hash-object plan.md`. The
"document changed" suffix appears when HASH differs from the previous
pass's. A later run reads the record, counts the passes, and appends
pass N+1.
