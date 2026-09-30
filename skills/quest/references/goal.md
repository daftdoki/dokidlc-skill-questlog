# Goal stage

Read this at draft goal, before you write `goal.md`, and again at
review goal. If `quest ID` or `quest ID start` printed an `overlay:`
line, read that file next; it adds to this one and wins where they
differ. The Review section at the end is the completion criterion for
review goal; read it before you write, and run its loop once `quest ID
next` has entered review goal.

## What the stage produces

`goal.md` records what the creator wants and how the finished work will be
judged. It has four parts, in this order: Background, Open questions,
Answers, and Success looks like. The quest's `quest.md` already holds a
Goal and a Done when in the creator's first words; `goal.md` is where
those become precise.

## Interview

The goal stage is an interview about outcomes. A round is one message that
asks every question you can ask now and then waits. Number the questions.
Give each a recommended answer, so the creator can reply "1 yes, 2 your
call, 3 no". A question whose answer depends on another question in the
same round belongs to the next round.

Ask about what would change the shape of the work: what success means and
how it is measured, what is out of scope, which decisions are already
made, and what constraint the creator holds that the repository does not
show. A fact that lives in the code, the docs, or memory goes to
`questlog:fact-finder`, and the round does not wait for it; only the
questions downstream of that fact wait.

The interview is complete when no decisive assumption is left: no decision
that would change every downstream option is left unasked.

## Writing

Record each answer as it arrives, under Answers, numbered to match its
question, in the creator's words where they gave them. When an answer
arrives later, add it with its date.

Background says what exists today and why the work is wanted, with the
files or sources that show it.

Success looks like is a list. Each item can be judged true or false
against the finished work by someone who did not do it. A number, a file
that must exist, a command whose output must say a thing, a behaviour the
creator will watch for.

User stories belong here when they fit, in the creator's words. Write
none the creator did not give.

## Review

The loop, the tiers, the session's steps, the dispatch list, the
reviewer rules, and the record template are in `review-loop.md`, read
before this section. The reviewer is `questlog:review-goal` and the
record is `goal-review.md`. Review goal is a creator gate: open
Clarifications go to the creator as numbered questions beside the
accept question.

Rubric for goal. Each row is graded pass or fail; a failure is a
finding at the row's tier, and the fail beside each row is an example.

1. Blocking. Every Answer matches the creator's words. Fail: an answer
   recorded as "yes" where the creator wrote "your call".
2. Blocking. Every item under Success looks like can be judged true or
   false against the finished work by someone who did not do it. Fail:
   "the viewer offer works well".
3. Clarification. No decision that would change every downstream option
   is assumed. Fail: the goal picks one of two skills without a question
   recording the choice.
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
