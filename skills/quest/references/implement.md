# Implement stage

Read this before you build. If `quest show` or `quest start` printed an
`overlay:` line, read that file next; it adds to this one and wins where
they differ. The Review section at the end is the completion criterion
for this stage; read it before you start, and run its loop before
`quest draft`.

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
run the review loop below, and `quest draft ID implement`.

## Review

The completion criterion for this stage: every item in the checklist
holds. Run the loop before `quest draft`.

The loop. Dispatch `questlog:review-implement` with the paths to
`plan.md`, this reference file, the prior review record
`implement-review.md` when it exists, and the root of the code
repository, plus the commit range: from the earliest commit newer than
the plan's `plan_accepted` time in `quest.md` to HEAD, found with
`git log --since=TIME` on the working branch. The reviewer reads this
section, the plan and its Deviations, the record, and the commits, and
returns findings by tier with a verdict. You record the pass in
`implement-review.md`, fix what it found, and dispatch again. A pass that
reports no blocking and no clarification findings is converged, and the
loop stops. Three passes in one run that each report another pass also
stop the loop, and the open findings go to the creator. A run begins
when you start the loop and ends at `quest draft` or when the session
ends. A converged verdict is a recommendation; the creator's `quest next`
accepts the stage.

Tiers. A blocking finding: the commits do not do what the plan says and
the Deviations do not say why, a test the plan promised is missing or
fails, or a claim fails against the code. A clarification: the creator
would have to ask before reviewing. Polish: naming, wording, commit
message style; fixed on sight and not counted.

Reviewer rules. Authorship is not evidence; a claim holds when the code
or the test says so. Run the suite. Report; the session edits.

Checklist for implement:

- Each commit matches a plan step, or the Deviations say why not.
- Every test the plan named exists and passes; the suite passes.
- Every document the plan promised is updated.
- Each deviation is recorded with its date and reason.
- The project's code review ran, where the project has one, and its
  findings are fixed or recorded.

The record. `implement-review.md` in the quest directory, written by you,
one section per pass:

```
# Review record: implement

## Pass N, DATE

Reviewer: questlog:review-implement
Document: plan.md at HASH, document changed since pass N-1
Code: /path/to/repository
Commits: OLDEST^..HEAD

Blocking
- location: finding. Fixed: what changed.
Clarification
- ...
Polish
- fixed on sight
Verdict: converged | another pass
```

HASH is the first seven characters of `git hash-object plan.md`. Commits
holds `OLDEST^..HEAD` with OLDEST the earliest commit `--since` returned,
or `none` when it returned nothing. A later run reads the record, counts
the passes, and appends pass N+1.
