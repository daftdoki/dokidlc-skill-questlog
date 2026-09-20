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
record is `goal-review.md`.

Findings at this stage. Blocking: an answer recorded that is not what
the creator said, or a Success item that cannot be judged true or false.
Clarification: a Background claim with no source a reader can open.

Checklist for goal:

- Every question asked has its answer recorded, and the answer matches
  what the creator said.
- Every item under Success looks like can be judged true or false against
  the finished work.
- No decision that would change every downstream option is assumed.
- Background names what exists and cites where it is shown.
- Where the creator drew a line, out of scope says so.
