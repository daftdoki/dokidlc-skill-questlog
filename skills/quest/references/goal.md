# Goal stage

Read this before you draft `goal.md`. If `quest show` or `quest start`
printed an `overlay:` line, read that file next; it adds to this one and
wins where they differ. The Review section at the end is the completion
criterion for this stage; read it before you write, and run its loop
before `quest draft`.

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

The completion criterion for this stage: every item in the checklist
holds. Run the loop before `quest draft`.

The loop. Dispatch `questlog:review-goal` with four paths: the stage
file, this reference file, the prior review record `goal-review.md` when
it exists, and the root of the code the document is about. The reviewer
reads this section, the document, and the record, and returns findings by
tier with a verdict. You record the pass in `goal-review.md`, fix what it
found, and dispatch again. A pass that reports no blocking and no
clarification findings is converged, and the loop stops. Three passes in
one run that each report another pass also stop the loop, and the open
findings go to the creator. A run begins when you start the loop and ends
at `quest draft` or when the session ends. A converged verdict is a
recommendation; the creator's `quest next` accepts the stage.

Tiers. A blocking finding: the document is wrong, contradicts itself, or
rests on a claim that fails against the code or the sources it cites. A
clarification: a reader would have to ask before acting. Polish: wording,
order, style; fixed on sight and not counted.

Reviewer rules. Authorship is not evidence; a claim holds when the file
or the cited source says so. Verify the claims the document rests on.
Report; the session edits. The document reads as one pass by an author
who knew the answer all along, so a passage that narrates its own
revisions is a clarification finding.

Checklist for goal:

- Every question asked has its answer recorded, and the answer matches
  what the creator said.
- Every item under Success looks like can be judged true or false against
  the finished work.
- No decision that would change every downstream option is assumed.
- Background names what exists and cites where it is shown.
- Where the creator drew a line, out of scope says so.

The record. `goal-review.md` beside the stage file, written by you, one
section per pass:

```
# Review record: goal

## Pass N, DATE

Reviewer: questlog:review-goal
Document: goal.md at HASH, document changed since pass N-1

Blocking
- location: finding. Fixed: what changed.
Clarification
- ...
Polish
- fixed on sight
Verdict: converged | another pass
```

HASH is the first seven characters of `git hash-object goal.md`. The
"document changed" suffix appears when HASH differs from the previous
pass's. A later run reads the record, counts the passes, and appends
pass N+1.
