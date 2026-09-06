# Research stage

Read this before you draft `research.md`. If `quest show` or `quest
start` printed an `overlay:` line, read that file next; it adds to this
one and wins where they differ. The Review section at the end is the
completion criterion for this stage; read it before you write, and run
its loop before `quest draft`.

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

Then ask the creator, in one round, about the assumptions that would
change every downstream option if guessed wrong. A round is one message
that asks every question you can ask now and then waits. Number the
questions and give each a recommended answer. A fact that lives in the
code, the docs, or memory goes to `questlog:fact-finder`, and the round
does not wait for it. The round is complete when no decision that would
change every downstream option is left assumed.

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

The completion criterion for this stage: every item in the checklist
holds. Run the loop before `quest draft`.

The loop. Dispatch `questlog:review-research` with four paths: the stage
file, this reference file, the prior review record `research-review.md`
when it exists, and the root of the code the document is about. The
reviewer reads this section, the document, and the record, and returns
findings by tier with a verdict. You record the pass in
`research-review.md`, fix what it found, and dispatch again. A pass that
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
or the cited source says so. Verify the claims the recommendation rests
on: counts, paths, tool behaviour, anything marked verified. Report; the
session edits. The document reads as one pass by an author who knew the
answer all along, so a passage that narrates its own revisions is a
clarification finding. Two of the checks below are generative: a review
that only attacks has done half the job.

Checklist for research:

- Every option is distinct, and every one opens with a viability line
  from the three values.
- Every matrix marks one recommended column.
- The Recommendation is one design, not a list of option codes, and it
  agrees with the sections above it.
- Every approach says how it fits with the cataloged capabilities.
- Load-bearing counts, paths, and behaviours hold against the code.
- Options the document did not consider are named, from other domains
  where they exist.
- Simpler options are named: a smaller deliverable that covers most of
  the need, or two proposals that solve one problem.
- Design questions are settled or explicitly deferred; none is raised
  and dropped.

The record. `research-review.md` beside the stage file, written by you,
one section per pass:

```
# Review record: research

## Pass N, DATE

Reviewer: questlog:review-research
Document: research.md at HASH, document changed since pass N-1

Blocking
- location: finding. Fixed: what changed.
Clarification
- ...
Polish
- fixed on sight
Verdict: converged | another pass
```

HASH is the first seven characters of `git hash-object research.md`. The
"document changed" suffix appears when HASH differs from the previous
pass's. A later run reads the record, counts the passes, and appends
pass N+1.
