# The review loop

Read this at every review state, before you dispatch a reviewer. Each
stage's reference points here from its Review section and keeps only
what is its own: the reviewer's name, the record's name, and the
rubric. This file holds the rest.

## Two loops

A document stage, goal, research, design, and plan, gets the short
loop: one full pass against the rubric, fixes, and at most one diff
pass over the fixes. A code stage, review implementation and evaluate
goal, gets the long loop: passes until one converges or a cap stops
it. The difference is the signal. Code has the tests; prose has only
the next reader, and a fresh reader always finds one more sentence to
question. Measured on 73 records in 2026-09, the long loop on prose ran
six passes per record and two thirds of its reruns had no Blocking
finding.

## Tiers

Blocking: the finding changes what gets built; the document is wrong or
contradicts itself on something an implementer would act on. A rubric
row marked Blocking that fails is a Blocking finding. Clarification: a
reader would have to ask before acting; a rubric row marked
Clarification that fails is one. Fact: a count, line number, date,
sha, or name the source gives differently. Polish: wording, order,
style. A reviewer reports Blocking and Clarification findings only
against a rubric row, and each bullet opens with the row's number; a
sentence that fails no row is Polish or nothing. Converged means
Blocking is empty and every Clarification bullet is marked `Answered.`
or `Open.`; Fact and Polish never gate a verdict.

## The short loop, document stages

1. Commit the stage file. Done when `git rev-parse HEAD:PATH` equals
   `git hash-object PATH`.
2. Dispatch the reviewer with the Dispatch list below, pass 1, scope
   `full`. Done when the report is in hand.
3. Record the pass: the Scope line, the Document line, the report by
   tier, the verdict. Done when the section matches the template.
4. For each finding, run its own check, the grep, the count, the
   command, before editing, and record the result. A finding whose
   check fails is marked `Disputed.` with the check's output and is not
   applied. Done when every bullet carries a marker.
5. Fact and Polish findings whose check holds: apply, write the Fixes
   line, mark `Fixed.`. A Polish fix that adds a sentence or a claim
   goes on the diff pass beside the Blocking fixes.
6. Clarification findings. At a creator gate, review goal and review
   design, hold each as a numbered question, mark it `Open.`, and ask
   it beside the accept question. At an agent gate, review research
   and review plan, answer it yourself from the goal, the code, or a
   fact-finder, write the answer into the stage file with the date,
   and mark it `Answered.` with the location. Done when no
   Clarification bullet is unmarked.
7. Blocking findings whose check holds: apply, write the Fixes line,
   mark `Fixed.`, commit, and dispatch pass 2 with scope `diff from
   HASH1`. The diff pass reads the fixes and nothing else and is the
   last pass. Done when its report is recorded. With no Blocking
   finding, or after pass 2, the loop ends.
8. At an agent gate run `quest ID next`. At a creator gate, name the
   document's path and the viewers in the same message as the accept
   question, with the open Clarifications numbered beside it.

A Blocking finding still open after pass 2, because its fix failed its
check or the diff pass raised a new one, stops an unattended run: put
it to the creator with the `last pass:` line, and run `quest ID next
--confirmed` only on their word.

## The long loop, code stages

The first pass is full. After a pass with a Blocking finding, or a
Clarification the session could not answer, the next pass is a diff
pass. A converged pass, full or diff, ends the loop. The run stops, and
the open findings go to the creator, after three passes without
convergence; run `quest ID next --confirmed` only on their word. Steps 1 to 5 are the short loop's; Clarifications are
answered by the session and marked `Answered.`; each diff pass is
dispatched with `diff from HASH1, commits B..C` as the diff pass below
describes.

## Dispatch

The prompt names: the stage file and its hash, the stage reference,
this file, the record when it exists, the root of the code the
document is about, the pass number, the scope, and the creator's words
the rubric asks about. A stage's Review section adds its own items.

## Reviewer rules

Authorship is not evidence; a claim holds when the file or the cited
source says so. One fact, one place: a fact stated twice is a Polish
finding that names both places. A number the code can change is
written as the command that produces it or with the commit it was
taken at. A passage that narrates the document's own revisions is a
Polish finding. Report; the session edits.

A memory page is read with `memory read NAME`, so it arrives with its
trust markers; the file under `.memory/` stays closed. A document that
names a memory page is a Clarification finding: memory cites documents,
a document cites the source the page cites.

## The diff pass

The reviewer runs `git diff HASH1 HASH2` and reads the hunks, the prior
pass's tier bullets, and its Fixes list. It reports: a finding without
a Fixes line whose check passes; a changed line that fails against the
code; each line where an old value from a Fixes line still appears,
found with `git cat-file -p HASH2 | grep -n`; each line that cites a
passage the diff deleted, found by grepping a distinctive word of the
deleted text. Under Verified it lists the greps it ran and what each
returned. It reads nothing else of the document.

At review implementation and evaluate goal the document is `plan.md`
and the work is commits. A diff pass there reads two diffs: `git diff
HASH1 HASH2` on `plan.md`, which is the Deviations the session added,
and `git log` and `git diff` over the commits since the prior pass's
range end, which the Scope line carries as `diff from HASH1, commits
B..C`. It checks each prior finding against those commits, runs the
tests the plan names for the changed steps, and at evaluate goal
re-checks each Done when line the prior pass marked unmet. The greps
run over `plan.md`.

## The record

`STAGE-review.md` beside the stage file, one section per pass:

```
# Review record: STAGE

## Pass N, DATE

Reviewer: questlog:review-STAGE
Scope: full | diff from HASH1
Document: STAGE.md at HASH

Blocking
- row 3, location: finding, one sentence why. Fixed.
Clarification
- row 5, location: finding. Answered: Background, 2026-09-29.
- row 5, location: finding. Open: question 2 to the creator.
Fact
- location: was X, is Y. Fixed.
Polish
- fixed on sight
Verdict: converged | another pass
Fixes
- location: the edit. Also at: none. Check: grep -c "X" STAGE.md
```

A tier with nothing under it holds one bullet, `- none`. HASH is the
first seven characters of `git hash-object STAGE.md`, taken after step
1's commit. A Check command's pattern excludes the line that states it,
or it counts itself. `quest ID` reads the last pass and prints `last
pass: 1 blocking (fixed), 0 clarification, 2 fact (fixed)` until a
pass converges. Review implementation and evaluate goal add `Code:` and
`Commits:` lines under `Document:`; the range's end is the sha HEAD
resolved to when the pass was recorded, never the word `HEAD`, so a
later diff pass has a fixed B to start from.
