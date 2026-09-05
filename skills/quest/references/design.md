# Design stage

Read this before you draft `design.md`. If `quest show` or `quest start`
printed an `overlay:` line, read that file next; it adds to this one and
wins where they differ. The Review section at the end is the completion
criterion for this stage; read it before you write, and run its loop
before `quest draft`.

## What the stage produces

`design.md` is specific enough that implementation can begin from it
without another design decision. It has these parts, in this order: Goal,
Stories, Current state, Decisions, Design, Test changes, Implementation
plan, Out of scope, and Deviations, a section kept empty here and filled
during implementation.

## Before you write

Draft the Goal from the quest and the research, and put it to the creator
with one question: does this capture it? Collect the stories from the
creator in the same message: the outcomes each person wants, in their
words. Write none they did not give.

Explore the code the design touches: the modules, functions, data
structures, and tests it builds on or changes, and the patterns earlier
work set. Search memory for `decision` pages before you recommend
anything; a past decision stands until the creator reverses it.

Then settle every decision that shapes the design. Map them as a tree:
each decision branches into the decisions that hang off it. The frontier
is every decision whose prerequisites are settled, so it can be asked now
without guessing an answer not yet heard. Ask the whole frontier in one
round, wait, and repeat. A round is one message that asks every question
you can ask now. Number the questions and give each a recommended answer,
so the creator can reply "1 yes, 2 your call, 3 no". A fact that lives in
the code, the docs, or memory goes to `questlog:fact-finder`, and the
round does not wait for it. Ask only what would change the design:
research decisions to confirm or reverse, constraints to follow,
behaviours out of scope, how the work should be broken into commits.

The interview is complete when the frontier is empty. Write the design
after that, and after the creator says the understanding is shared.

## Writing

Current state names the code as it is, with paths, names, and short
examples where they make the structure clear.

Decisions is a numbered list. Each answers a how or a why, with its
reason, and names the research option it takes or the reason it departs.
Record the creator's answers as given; an answer of "your call" becomes
your decision, stated like the others.

Design describes each new or changed module, function, and structure:
its purpose, its logic, how it fits with what exists. Concrete examples:
interfaces, schemas, sketches, flows.

Test changes is grouped by test file. A new test says what it exercises
and what it asserts; a changed test says what changes and why.

Implementation plan breaks the work into two to five commits, each a
coherent unit that leaves the tree passing.

Out of scope lists what this design leaves for later, so the implementer
does not build it.

## Review

The completion criterion for this stage: every item in the checklist
holds. Run the loop before `quest draft`.

The loop. Dispatch `questlog:review-design` with four paths: the stage
file, this reference file, the prior review record `design-review.md`
when it exists, and the root of the code the document is about. The
reviewer reads this section, the document, and the record, and returns
findings by tier with a verdict. You record the pass in
`design-review.md`, fix what it found, and dispatch again. A pass that
reports no blocking and no clarification findings is converged, and the
loop stops. Three passes in one run that each report another pass also
stop the loop, and the open findings go to the creator. A run begins
when you start the loop and ends at `quest draft` or when the session
ends. A converged verdict is a recommendation; the creator's `quest next`
accepts the stage.

Tiers. A blocking finding: the document is wrong, contradicts itself, or
rests on a claim that fails against the code or the sources it cites. A
clarification: a reader would have to ask before acting. Polish: wording,
order, style; fixed on sight and not counted.

Reviewer rules. Authorship is not evidence; a claim holds when the file
or the cited source says so. Read the source for every code claim: start
with the files the design names and follow the imports where they lead.
Report; the session edits. The document reads as one pass by an author
who knew the answer all along, so a passage that narrates its own
revisions is a clarification finding.

Checklist for design:

- Every section is present, in order.
- Every file path, function, class, count, and described behaviour holds
  against the code.
- Decisions follow the research recommendation, or the departure is
  explained.
- Decisions, Design, and Test changes agree with each other.
- The Implementation plan's commits each leave the tree passing.
- Nothing an implementer would have to ask: no missing edge case, no
  ambiguous requirement, no manual step that should be a script.
- Stories are the creator's, and none was invented.

The record. `design-review.md` beside the stage file, written by you, one
section per pass:

```
# Review record: design

## Pass N, DATE

Reviewer: questlog:review-design
Document: design.md at HASH, document changed since pass N-1

Blocking
- location: finding. Fixed: what changed.
Clarification
- ...
Polish
- fixed on sight
Verdict: converged | another pass
```

HASH is the first seven characters of `git hash-object design.md`. The
"document changed" suffix appears when HASH differs from the previous
pass's. A later run reads the record, counts the passes, and appends
pass N+1.
