# Evaluate goal

Read this when the quest reaches evaluate goal. If `quest ID` or `quest
ID start` printed an `overlay:` line, read that file next; it adds to
this one and wins where they differ. The Review section at the end is
the completion criterion for evaluate goal; read it before you present,
and run its loop before you ask the creator whether the goal is met.

## What the stage produces

The creator reads the result against the quest's Done when and says
whether the goal is met. You present the result, answer questions, and
fix what the creator finds. The creator's `quest ID next` completes the
quest.

## Presenting the result

Present the result as the Done when, line by line, each with its
evidence: the file that exists, the command and its output, the test that
passes, the number that was measured. A line that is not met says so and
says why. A line met differently than planned points at the Deviations.

Answer each question with the evidence, and where a question finds a
gap, fix it, commit, and show the fix.

## Review

The loop, the tiers, the session's steps, the dispatch list, the
reviewer rules, and the record template are in `review-loop.md`, read
before this section. The reviewer is `questlog:review-result` and the
record is `result-review.md`. Run the loop before you ask the creator
whether the goal is met; the creator's `quest ID next` completes the
quest.

Dispatch adds: `plan.md` is the stage file, and the prompt names
`quest.md` for the Done when, `goal.md` for Success looks like, the root
of the code repository, and the commit range, from the earliest commit
newer than the `implement` entry's time in the `history` list of
`quest.md` to HEAD, found with `git log --since=TIME` on the working
branch. The reviewer reads the Done when, the Deviations, the record,
and the commits, and runs what can be run.

Findings at this stage. Blocking: a Done when line not met with nothing
saying so. Clarification: a line met with evidence the creator would
have to ask about.

Checklist for evaluate goal:

- Every line of Done when is met, with evidence, or is marked not met
  with the reason.
- Every item under Success looks like in `goal.md` is met or marked.
- Every deviation is recorded, and none hides an unmet line.
- The documentation the work changed reads as current.

The record adds two lines under `Document:`:

```
Code: /path/to/repository
Commits: OLDEST^..NEWEST
```

OLDEST is the earliest commit `--since` returned, or `none` when it
returned nothing; NEWEST is the sha HEAD resolved to when the pass was
recorded. A diff pass's Scope line reads `diff from HASH1, commits
NEWEST..HEAD-NOW`.
