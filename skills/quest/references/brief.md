# Brief stage

Read this at draft goal for a chore, before you write `brief.md`, and
again at review goal. If `quest ID` or `quest ID start` printed an
`overlay:` line, read that file next; it adds to this one and wins where
they differ. The Review section at the end is the completion criterion
for review goal; read it before you write, and run its loop once `quest
ID next` has entered review goal.

A brief states a chore's goal and its steps in one document; a
decision between alternatives belongs to a quest's design. It reads
`quest.md`, the code the steps touch, and the creator. It ends when
every question in the readiness table is answered and every step names
its files and its test.

## What the stage produces

`brief.md` is a chore's one document: what the creator wants, how the
result will be judged, and the steps that build it. The creator reads it
once, at review goal, and the implementer ticks its Steps. It has these
parts, in this order: Goal, Background, Ready to start when, Questions
and answers,
How we will know it is done, Steps, Out of scope, and Deviations from plan, kept empty here
and filled during implementation.

## Before you write

Read the Goal and Done when in `quest.md`, and the code each step will
touch, so the steps name real functions and real files. Search memory
for the title and for each tool the steps touch.

A chore that turns on an untested hypothesis runs the test now, and its
result goes into Background. A chore that needs a decision between
alternatives is a quest: tell the creator before you write.

Ask the creator one round of at most five questions: only what the
creator alone knows, numbered, each with a recommended answer, opening
with the convention that a bare "yes" takes the recommendation. A fact
that lives in the code, the docs, or memory goes to
`questlog:fact-finder`, and the round does not wait for it. The brief's
readiness table asks the goal's first five questions and a sixth:
"Are the steps clear?" `quest ID next` refuses while a question is
answered by nobody, and an answer by assumption carries its note.

## Writing

Goal is two sentences, in the creator's words where they gave them.

Background says what exists today, in a few lines, with the files that
show it and the result of any test you ran.

The readiness table, `## Ready to start when`, is the one
`references/goal.md` shows, with questions 1 to 5 and a sixth:
"Are the steps clear?" It is answered by the creator once every step
names its files and its test.

Questions and answers records each as `Q: ... A: ...`, the answer in the
creator's words.

How we will know it is done is a list. Each item can be judged true or false
against the finished work by someone who did not do it.

Steps is a checklist, in the order the steps will run. One item per
step:

```
## Steps

- [ ] 1. `bin/quest`: print the `document:` line.
  Test: `test_guidance_names_the_document` in `tests/test_quest.py`;
  red: no `document:` line.
  Commit: "quest: document: names the file under review".
```

Each item names what changes, in which files, and the test that fails
first and proves it, and ends where a commit lands with the tests
passing. Only items sit under Steps. When the creator accepts the brief,
`quest` records each item; from then the implementer ticks a box and
changes no step's words, and a step that must change is written under
Deviations from plan.

Out of scope names what the chore leaves alone.

## Review

The loop, the tiers, the session's steps, the dispatch list, the
reviewer rules, and the record template are in `review-loop.md`, read
before this section. The reviewer is `questlog:review-goal` and the
record is `brief-review.md`. Review goal is a creator gate: open
Clarifications go to the creator as numbered questions beside the
accept question.

Rubric for brief. Each row is graded pass or fail; a failure is a
finding at the row's tier, and the fail beside each row is an example.

1. Blocking. Every Answer matches the creator's words. Fail: an answer
   recorded as "yes" where the creator wrote "your call".
2. Blocking. Every item under How we will know it is done can be judged true or
   false against the finished work. Fail: "the offer works well".
3. Blocking. No step contradicts the code, and each step's commit leaves
   the tests passing. Fail: a step edits a function the code does not
   have and no step adds.
4. Blocking. The steps cover every line of the Done when in `quest.md`.
   Fail: Done when names a document update no step touches.
5. Clarification. Steps is a checklist: every step is a `- [ ]` item
   that names its files and its test. Fail: a numbered list with no
   boxes, or "update the skill" with no file.
6. Clarification. A hypothesis the chore turns on has its test and
   result in Background. Fail: "if the hook can match the id" with no
   test run.
7. Clarification. No decision between alternatives is left open. Fail:
   a step that reads "pick a viewer".
