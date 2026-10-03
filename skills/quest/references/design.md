# Design stage

Read this at design, before you write `design.md`, and again at review
design. If `quest ID` or `quest ID start` printed an `overlay:` line, read
that file next; it adds to this one and wins where they differ. The
Review section at the end is the completion criterion for review design;
read it before you write, and run its loop once `quest ID next` has
entered review design.

Design decides, with reasons, and is the document a reader opens later
to learn how and why; the order of the build belongs to plan and the
code belongs to implement. It reads the goal, the research, the code,
and `decision` memory pages. It ends when no decision an implementer
would need is open.

## What the stage produces

`design.md` is specific enough that implementation can begin from it
without another design decision. It has these parts, in this order: Goal,
Stories, Current state, Decisions, Design, Test changes, Implementation
plan, Out of scope, and Deviations from plan, a section kept empty here and filled
during implementation.

## Before you write

Design runs after research, without the creator, and ends at a creator
gate. Draft the Goal from the quest and the research, and take the
stories from the goal's Answers, in the creator's words. Write none
they did not give.

Explore the code the design touches: the modules, functions, data
structures, and tests it builds on or changes, and the patterns earlier
work set. Search memory for `decision` pages before you recommend
anything; a past decision stands until the creator reverses it.

Then settle every decision that shapes the design. Map them as a tree:
each decision branches into the decisions that hang off it. Settle each
from the goal's Questions and answers and its readiness question "What
is decided for design?", the research's Recommendation, the code, and
`decision` memory pages; a fact goes to `questlog:fact-finder`. Record
each as a Decision with its reason. A decision that none of those
settle and only the creator can pauses the run: ask the whole frontier
of such decisions in one numbered round with a recommended answer each,
and wait. Write the design when every decision is settled; the creator
reads it at review design.

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
lead to. Review design is a creator gate: open Clarifications go to the
creator as numbered questions beside the accept question.

Rubric for design.

1. Blocking. Every file path, function, class, count, and described
   behaviour holds against the code. Fail: a predicate described as
   reading a key the code does not write.
2. Blocking. Each decision follows the research recommendation or names
   why it departs. Fail: a decision that reverses the recommendation
   with no reason.
3. Blocking. Each commit in the Implementation plan leaves the tree
   passing. Fail: commit 2 changes a signature whose callers commit 3
   updates.
4. Clarification. Decisions, Design, and Test changes agree with each
   other. Fail: decision 4 names two flags and the Design section shows
   one.
5. Clarification. Nothing an implementer would have to ask: no missing
   edge case, no ambiguous requirement, no manual step that should be a
   script. Fail: "migrate the settings" with no command.
6. Clarification. Every story is the creator's. Fail: a story the
   interview never recorded.
7. Clarification. Every section is present, in order. Fail: Out of
   scope missing.
8. Clarification, belongs to implement. A function body written out
   where a signature, a purpose, and an example would do. Fail: a2
   design pass 1, a body using helper names the design never defined.
