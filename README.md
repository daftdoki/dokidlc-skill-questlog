# dokidlc-skill-questlog

A Claude Code plugin that tracks work as quests and chores. A quest runs
goal, research, design, implement, review, each stage drafted by the agent
and closed by the creator. A chore skips to implement. Every quest or chore
is a directory under `docs/quests/` with a `quest.md` and its stage files,
and the quest log at `docs/quests/README.md` lists what is open in one line
each.

The command is `quest`, on PATH while the plugin is enabled. Run `quest log`
to see what is open. The `quest` skill has the rules.

Requires `uv` on the machine. Nothing else.

Install from the `dokidlc` marketplace:

```
/plugin marketplace add daftdoki/dokidlc-plugins
/plugin install questlog@dokidlc
```

Develop against a local checkout:

```
claude --plugin-dir ../dokidlc-skill-questlog
```
