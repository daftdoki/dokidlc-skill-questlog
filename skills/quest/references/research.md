# Research stage

Read this at research, before you write `research.md`, and again at review
research. If `quest ID` or `quest ID start` printed an `overlay:` line, read
that file next; it adds to this one and wins where they differ. The
Review section at the end is the completion criterion for review research;
read it before you write, and run its loop once `quest ID next` has
entered review research.

## What the stage produces

Research opens the design space; design narrows it. `research.md` gives
the design stage a full menu: what exists, what the change must fit with,
every approach worth considering, one recommendation, and the decisions
deferred to design. It has these parts, in this order: Current state,
Requirements, Non-goals, Design questions, one Approaches section per
design question, Creative ideas, Experiments, Comparison, Recommendation,
and Decisions for design.

## Before you write

Read the research and design of related quests first, so this document
builds on them instead of repeating them. Search memory for each design
question as you form it.

Research runs after the creator accepted the goal, without the creator.
Take the assumptions that would change every downstream option from
the goal's Answers; a fact that lives in the code, the docs, or memory
goes to `questlog:fact-finder`. Only a question the goal does not
answer and only the creator can pauses the run: ask it, numbered, with
a recommended answer, and wait.

Catalog what already exists that the change must fit with: the features,
data structures, and conventions it will touch. Every approach you write
later says how it fits with each of them; an approach that sidesteps an
existing capability to simplify itself says so and says why.

Search for prior art: how other projects, libraries, and other domains
solved the same problem. Use web search through `questlog:fact-finder`.

## Writing

Requirements come from the quest's Goal, marked explicit, and from the
architecture and use, marked inferred. Non-goals name what is adjacent
and tempting and belongs elsewhere.

Each Approaches section answers one design question with distinct
options. Two options are distinct when choosing one leads to different
code, architecture, or experience; merge options that differ only in
detail. Each option opens with a viability line holding one of three
values: Recommended, Not recommended, or Worth prototyping. Then how it
works, with a concrete example, its pros, its cons, and its dependencies
on options in other sections when a choice here constrains a choice
there.

Creative ideas holds what challenges an assumption, borrows from another
domain, or radically simplifies. An idea that is a variation on an
approach above belongs above.

Experiments lists what would settle an uncertain option: the question it
answers, how to run it, what a positive and a negative result look like,
and the effort. Run the ones you can and put the results inline; a
measured result outranks a page of analysis.

The Comparison matrix scores every option on the criteria that matter.
Bold the recommended column's header and append a star, so the reader
sees the choice without reading the Recommendation.

The Recommendation is one integrated design, described so it can be
understood without the sections above: what the interface looks like,
how the data flows, how it fits with what exists. Then why, and which
creative ideas are worth prototyping.

Decisions for design lists what is deferred: exact schemas, error
wording, migration, signatures. Each is a question with enough context
to answer it.

Write in passes when the document will not fit one write, and add a
table of contents when it passes 300 lines. Depth follows the size of the
design space, not a line count.

## Review

The loop, the tiers, the session's steps, the dispatch list, the
reviewer rules, and the record template are in `review-loop.md`, read
before this section. The reviewer is `questlog:review-research` and
the record is `research-review.md`. Review research is an agent gate:
the session answers each Clarification from the goal, the code, or a
fact-finder and records the answer. Options the document did not
consider and a smaller deliverable that covers most of the need are not
rows; the session asks the creator about them at the design gate.

Rubric for research.

1. Blocking. The Recommendation is one design and agrees with the
   sections above it. Fail: the Recommendation takes option B where the
   matrix stars A.
2. Blocking. A count, path, or behaviour an option's viability rests on
   holds against the code. Fail: "58 call sites" where `grep -c` gives
   45.
3. Clarification. Every option is distinct and opens with a viability
   line from the three values. Fail: two options that differ only in a
   flag's name.
4. Clarification. Every approach says how it fits each cataloged
   capability, or says why it sidesteps one. Fail: an option that
   ignores the existing guard hook.
5. Clarification. Every design question is settled in an Approaches
   section or listed under Decisions for design. Fail: a question in
   Design questions with neither.
6. Clarification. The Comparison matrix marks one recommended column.
   Fail: two starred columns, or none.
