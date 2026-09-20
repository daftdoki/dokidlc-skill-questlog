# Design stage

Read this at design, before you write `design.md`, and again at review
design. If `quest ID` or `quest ID start` printed an `overlay:` line, read
that file next; it adds to this one and wins where they differ. The
Review section at the end is the completion criterion for review design;
read it before you write, and run its loop once `quest ID next` has
entered review design.

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

The loop, the tiers, the session's steps, the dispatch list, the
reviewer rules, and the record template are in `review-loop.md`, read
before this section. The reviewer is `questlog:review-design` and the
record is `design-review.md`. The reviewer reads the source for every
code claim: the files the design names first, then the imports they
lead to.

Findings at this stage. Blocking: a described behaviour, function, or
commit order that fails against the code, or a decision that departs
from the research with no reason. Clarification: an edge case, an
ambiguous requirement, or a manual step an implementer would have to
ask about.

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
