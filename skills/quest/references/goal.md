# Goal stage

Read this at draft goal, before you write `goal.md`, and again at
review goal. If `quest ID` or `quest ID start` printed an `overlay:`
line, read that file next; it adds to this one and wins where they
differ. The Review section at the end is the completion criterion for
review goal; read it before you write, and run its loop once `quest ID
next` has entered review goal.

## What the stage produces

`goal.md` records what the creator wants and how the finished work will be
judged. It has these parts, in this order: Background, Coverage,
Questions and answers, Success looks like, and after an explore
interview Options seen. The quest's `quest.md` already holds a
Goal and a Done when in the creator's first words; `goal.md` is where
those become precise.

## Interview

`quest ID start` recorded the depth, and `quest ID` prints it as
`interview: define` or `interview: explore`. Both end with the coverage
table filled; they differ in how they get there.

The coverage table has fixed rows: outcome, success measure, out of
scope, decisions already made, constraints the repository does not
show, and three the unattended stages read in place of the rounds they
once asked the creator: constraints research must respect, decisions
made for design, how the build should be broken up. Each row is Clear,
Partial, or Missing. A Partial row carries the assumption you made and
the recommended answer, so the creator sees it at the gate. `quest ID
next` refuses while a row is Missing; a goal written before the table
existed has none, and the script lets it pass.

```
## Coverage

| Row | Status | Note |
|---|---|---|
| outcome | Clear | |
| out of scope | Partial | assumed: eviction stays out |
```

Define is for a creator who knows what they want. A round is one
message of at most five questions, ordered by how much the answer
changes the work, each numbered with a recommended answer. The round
opens with the convention: a bare "yes" takes the recommendation, and a
yes-or-no question is worded so that "yes" is it. A question whose
answer depends on another in the same round belongs to the next round.
A fact that lives in the code, the docs, or memory goes to
`questlog:fact-finder`, and the round does not wait for it. The
interview ends when every row is Clear, or after two rounds with the
open rows written as Partial.

Explore is for a creator who has an outcome in mind and wants to find
what they do not know. You teach before you ask. Each message carries
one thing the creator may not know, an option, a prior-art example, a
constraint the code holds, an idea from another domain, and then at
most three questions about it. Dispatch fact-finders for prior art and
code facts while the conversation runs, so it does not wait on them.
There is no question cap and no coverage exit: explore ends when the
creator says they have what they need, and only then does the coverage
table fill and the goal get written. Explore is breadth about the
outcome, in conversation; research is depth on the surviving questions,
in a document, without the creator. A comparison matrix in an explore
conversation has crossed that line.

## Writing

Record each answer as it arrives under `## Questions and answers`, as
`Q: ... A: ...`, dated by round, in the creator's words where they gave
them, and edit the section the answer changes in the same turn.

Background says what exists today and why the work is wanted, with the
files or sources that show it. A hypothesis the goal turns on has its
test and result here.

Success looks like is a list. Each item can be judged true or false
against the finished work by someone who did not do it. A number, a file
that must exist, a command whose output must say a thing, a behaviour the
creator will watch for.

User stories belong here when they fit, in the creator's words. Write
none the creator did not give.

After explore, `## Options seen` lists one line per option the
conversation raised, with why it stayed or fell. The design reviewer
and a later session read it, and research deepens the survivors instead
of reopening the space. Each piece of prior art found gets a memory page
cited to its source.

## Review

The loop, the tiers, the session's steps, the dispatch list, the
reviewer rules, and the record template are in `review-loop.md`, read
before this section. The reviewer is `questlog:review-goal` and the
record is `goal-review.md`. Review goal is a creator gate: open
Clarifications go to the creator as numbered questions beside the
accept question.

Rubric for goal. Each row is graded pass or fail; a failure is a
finding at the row's tier, and the fail beside each row is an example.

1. Blocking. Every answer under Questions and answers matches the
   creator's words. Fail: an answer recorded as "yes" where the creator
   wrote "your call".
2. Blocking. Every item under Success looks like can be judged true or
   false against the finished work by someone who did not do it. Fail:
   "the viewer offer works well".
3. Clarification. The coverage table is present, and every row is Clear
   or Partial with its assumption written. Fail: a row Missing, or
   Partial with an empty note.
4. Clarification. Background names what exists and cites where a reader
   sees it. Fail: "the hook prompts on prose" with no transcript, file,
   or command named.
5. Clarification, belongs to plan. The goal names no file path, command,
   flag, or count, unless the Goal is itself technical and the creator
   gave the name. Fail: a goal for a viewer offer that names `open` and
   `xdg-open` and a launch flag.
6. Clarification. A hypothesis the goal turns on has its test and result
   in Background. Fail: "if Claude Code can put the marketplace name in
   the prefix" with no test run.
