# Evaluate goal

Read this when the quest reaches evaluate goal. If `quest ID` or `quest
ID start` printed an `overlay:` line, read that file next; it adds to
this one and wins where they differ. The Review section at the end is
the completion criterion for evaluate goal; read it before you present,
and run its loop before you ask the creator whether the goal is met.

Evaluate goal checks the result against Done when, the documentation,
and the tree; fixing a step belongs to implement, reached on the
creator's word. It reads `quest.md`, the goal or the brief, the
checklist, and the commits. It ends when every Done when line is met or
marked and the creator accepts.

## What the stage produces

The creator reads the result against the quest's Done when and says
whether the goal is met. You present the result, answer questions, and
fix what the creator finds. The creator's `quest ID accept` completes
the quest.

## Presenting the result

Present the result as the Done when, line by line, each with its
evidence: the file that exists, the command and its output, the test that
passes, the number that was measured. A line that is not met says so and
says why. A line met differently than planned points at the Deviations.
Beside it, the `checklist:` line `quest ID` prints: every step ticked,
none changed.

For a task there is no loop and no record: show the commits, the test
that failed first and passes now, and ask whether it is done. For a
prototype, write the `## Learned` paragraph into `quest.md` first and
show it beside the commits; `accept` refuses without it.

Answer each question with the evidence, and where a question finds a
gap, fix it, commit, and show the fix.

## Review

The loop, the tiers, the session's steps, the dispatch list, the
reviewer rules, and the record template are in `review-loop.md`, read
before this section. The reviewer is `questlog:review-result` and the
record is `result-review.md`. Evaluate goal runs the long loop and is a
creator gate: run the loop before you ask the creator whether the goal
is met, and put open Clarifications beside that question. The creator's
`quest ID accept` completes the quest.

Dispatch adds: the file `document:` names is the stage file, `plan.md`
or a chore's `brief.md`, and the prompt names `quest.md` for the Done
when, `goal.md` or the brief for Success looks like, the root
of the code repository, and the commit range, from the earliest commit
newer than the `implement` entry's time in the `history` list of
`quest.md` to HEAD, found with `git log --since=TIME` on the working
branch. The reviewer reads the Done when, the Deviations, the record,
and the commits, and runs what can be run.

Rubric for evaluate goal.

1. Blocking. Every line of Done when is met, with evidence, or is marked
   not met with the reason. Fail: a line with no evidence and no mark.
2. Blocking. Every item under Success looks like, in `goal.md` or the
   brief, is met or marked. Fail: an item the presentation skips.
3. Clarification. No deviation hides an unmet line. Fail: a Deviation
   that narrows a Done when line without saying the line is not met.
4. Clarification. The documentation the work changed reads as current
   and is about the product, not the process: the README says what it
   does, how to install and start it, and where the rest is; a fact is
   stated once. Fail: a README section that narrates the quest.
5. Clarification. The working tree is clean and the branch is where the
   plan said it would be. Fail: uncommitted files under `docs/`.

The record adds two lines under `Document:`:

```
Code: /path/to/repository
Commits: OLDEST^..NEWEST
```

OLDEST is the earliest commit `--since` returned, or `none` when it
returned nothing; NEWEST is the sha HEAD resolved to when the pass was
recorded. A diff pass's Scope line reads `diff from HASH1, commits
NEWEST..HEAD-NOW`.
