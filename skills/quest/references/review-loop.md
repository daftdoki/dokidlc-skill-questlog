# The review loop

Read this at every review state, before you dispatch a reviewer. Each
stage's reference points here from its Review section and keeps only
what is its own: the reviewer's name, the record's name, two example
findings, and the checklist. This file holds the rest.

## Passes

A full pass reads the whole document against the stage checklist. A
diff pass reads the diff between two committed blobs, the prior pass's
findings, and its Fixes list, and nothing else of the document.

The first pass of a run is full. After a pass with something under
Blocking or Clarification, the next pass is a diff pass. When a diff
pass reports nothing under Blocking or Clarification, the session
claims convergence and dispatches one full pass. A converged full pass
ends the loop. A converged diff pass ends nothing; `quest ID next`
refuses it because a full pass is owed.

## Runs and caps

A run begins at the session's first pass and after a creator revision.
A creator revision starts with a full pass; if the revision touches an
Approaches section of `research.md`, the generative checklist items run
again. The run stops, and the open findings go to the creator, after
three full passes without convergence or three diff passes in a row
with something under Blocking or Clarification. A converged verdict is
a recommendation; the creator's `quest ID next` accepts the state.

## Tiers

Blocking: the finding changes what gets built; the document is wrong or
contradicts itself on something an implementer would act on.
Clarification: a reader would have to ask before acting. Fact: a count,
line number, date, sha, or name the source gives differently. Polish:
wording, order, style. Converged means Blocking and Clarification are
empty; Fact and Polish never gate a verdict.

## The session's steps

1. Commit the stage file. Done when `git rev-parse HEAD:PATH` equals
   `git hash-object PATH`.
2. Dispatch the reviewer with the Dispatch list below, the pass number,
   and the scope: `full, new run`, `full`, or `diff from HASH1`. Done
   when the report is in hand.
3. Record the pass: the Scope line, the Document line, the report by
   tier, the verdict. Done when the section matches the template.
4. For each Blocking, Clarification, and Fact finding, and for each
   Polish item whose fix adds a claim: run the finding's own check (the
   grep, the count, the command) before editing. Write a Fixes line:
   the location, the edit, `Also at:` every other place the fact
   appears, `Check:` the command that shows the edit holds. Mark the
   bullet `Fixed.` or `Open.` Done when every such bullet carries a
   marker and every `Fixed.` bullet has a Fixes line whose check
   passes.
5. Apply the edits, commit, and go to step 2: with `diff from HASH1`
   when the pass had something under Blocking or Clarification, with
   `full` when it was a diff pass with nothing there. Done when the
   loop ends or a cap stops it.

## Dispatch

The prompt names: the stage file and its hash, the stage reference,
this file, the record when it exists, the root of the code the
document is about, the pass number, the scope, and the creator's words
the stage checklist asks about. A stage's Review section adds its own
items.

## Reviewer rules

Authorship is not evidence; a claim holds when the file or the cited
source says so. One fact, one place: a fact stated twice is a Polish
finding that names both places. A number the code can change is
written as the command that produces it or with the commit it was
taken at. A passage that narrates the document's own revisions is a
Clarification finding. Report; the session edits.

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
returned.

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
Scope: full, new run | full | diff from HASH1
Document: STAGE.md at HASH

Blocking
- location: finding, one sentence why. Fixed.
Clarification
- location: finding. Open.
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
or it counts itself. `quest ID` reads the last pass and prints
`last pass: 1 blocking (fixed), 0 clarification, 2 fact (fixed)` until
a full pass converges. Review implementation and evaluate goal add
`Code:` and `Commits:` lines under `Document:`; the range's end is the
sha HEAD resolved to when the pass was recorded, never the word `HEAD`,
so a later diff pass has a fixed B to start from.
