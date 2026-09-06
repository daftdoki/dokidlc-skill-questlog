# Review stage

Read this when the quest reaches review. If `quest show` or `quest
start` printed an `overlay:` line, read that file next; it adds to this
one and wins where they differ. The Review section at the end is the
completion criterion for this stage; read it before you present, and run
its loop before `quest draft`.

## What the stage produces

The creator reads the result against the quest's Done when and says
whether the work is complete. You present the result, answer questions,
and fix what the creator finds. `quest draft ID review` says the result
is ready to read; `quest next ID review` completes the quest.

## Presenting the result

Present the result as the Done when, line by line, each with its
evidence: the file that exists, the command and its output, the test that
passes, the number that was measured. A line that is not met says so and
says why. A line met differently than planned points at the Deviations.

Answer each question with the evidence, and where a question finds a
gap, fix it, commit, and show the fix.

## Review

The completion criterion for this stage: every item in the checklist
holds. Run the loop before `quest draft`.

The loop. Dispatch `questlog:review-result` with the paths to `quest.md`
for the Done when, `goal.md` for Success looks like, `plan.md` for the
Deviations, this reference file, the
prior review record `result-review.md` when it exists, and the root of the
code repository, plus the commit range: from the earliest commit newer
than the plan's `plan_accepted` time in `quest.md` to HEAD, found with
`git log --since=TIME` on the working branch. The reviewer reads this
section, the Done when, the Deviations, the record, and the commits, and
returns findings by tier with a verdict. You record the pass in
`result-review.md`, fix what it found, and dispatch again. A pass that
reports no blocking and no clarification findings is converged, and the
loop stops. Three passes in one run that each report another pass also
stop the loop, and the open findings go to the creator. A run begins
when you start the loop and ends at `quest draft` or when the session
ends. A converged verdict is a recommendation; the creator's `quest next`
completes the quest.

Tiers. A blocking finding: a Done when line is not met and nothing says
so. A clarification: a line is met with evidence the creator would have
to ask about. Polish: presentation; fixed on sight and not counted.

Reviewer rules. Authorship is not evidence; a line holds when the file,
the command, or the test shows it. Run what can be run. Report; the
session edits.

Checklist for review:

- Every line of Done when is met, with evidence, or is marked not met
  with the reason.
- Every item under Success looks like in `goal.md` is met or marked.
- Every deviation is recorded, and none hides an unmet line.
- The documentation the work changed reads as current.

The record. `result-review.md` in the quest directory, written by you,
one section per pass:

```
# Review record: review

## Pass N, DATE

Reviewer: questlog:review-result
Document: plan.md at HASH, document changed since pass N-1
Code: /path/to/repository
Commits: OLDEST^..HEAD

Blocking
- Done when line: finding. Fixed: what changed.
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
