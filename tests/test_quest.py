"""Tests for bin/quest. No harness, no network."""

import importlib.util
import json
import random
import subprocess
from datetime import UTC, datetime
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_loader = SourceFileLoader("quest", str(ROOT / "bin" / "quest"))
_spec = importlib.util.spec_from_loader("quest", _loader)
quest = importlib.util.module_from_spec(_spec)
_loader.exec_module(quest)

NOW = datetime(2026, 9, 4, 14, 32, tzinfo=UTC)
STAMP = "2026-09-04T00:00:00Z"
NAMES = [s.name for s in quest.STATES]


def test_alphabet_excludes_lookalikes():
    assert len(quest.ALPHABET) == 31
    for c in "01ilo":
        assert c not in quest.ALPHABET
    assert quest.ALPHABET == "".join(sorted(quest.ALPHABET))


def test_new_id_format_and_uniqueness():
    """A minute holds 31 * 31 = 961 suffixes. Fill it, then the next draw fails loudly."""
    rng = random.Random(1)
    seen = set()
    for _ in range(961):
        i = quest.new_id(seen, NOW, rng)
        assert quest.ID_RE.match(i), i
        assert i.startswith("2609041432-")
        assert i not in seen
        seen.add(i)
    with pytest.raises(SystemExit):
        quest.new_id(seen, NOW, rng)
    later = quest.new_id(seen, datetime(2026, 9, 4, 14, 33, tzinfo=UTC), rng)
    assert later.startswith("2609041433-")


def test_new_id_retries_on_collision():
    rng = random.Random(1)
    first = quest.new_id(set(), NOW, rng)
    second = quest.new_id({first}, NOW, random.Random(1))
    assert second != first


def test_slugify():
    assert quest.slugify("Evaluate memoryfields as the memory system!") == "evaluate-memoryfields-as-the-memory-syst"
    assert len(quest.slugify("x" * 100)) == 40
    assert quest.slugify("???") == "untitled"


def test_page_round_trip():
    fm = {"id": "2609041432-7k", "title": "T", "kind": "quest", "state": "backlog", "history": [{"state": "backlog", "at": "2026-09-04T14:32:00Z"}]}
    body = quest.quest_body("do the thing", "it works")
    text = quest.render_page(fm, body)
    assert "  at: '2026-09-04T14:32:00Z'" in text                 # the nested stamp is single-quoted like a top-level one
    assert quest.parse_page(text) == (fm, body)


def test_successor_skips_marked_states():
    quest_fm = {"history": [{"state": "backlog", "at": STAMP}]}
    assert quest.successor(quest_fm, "review goal") == "research"
    assert quest.successor(quest_fm, "evaluate goal") == "completed"
    chore_fm = {"history": [{"state": "backlog", "at": STAMP}] + [{"state": n, "at": STAMP, "skipped": True} for n in quest.CHORE_SKIPS]}
    assert quest.successor(chore_fm, "review goal") == "plan"
    assert quest.successor(chore_fm, "draft goal") == "review goal"
    assert quest.current(chore_fm["history"]) == "backlog"
    assert quest.current([]) == "backlog"


def _make(qdir, qid, title, kind="quest", state="backlog", history=None, **extra):
    d = qdir / f"{qid}-{quest.slugify(title)}"
    d.mkdir(parents=True)
    if history is None:
        history = [quest.entry(STAMP, "backlog")] + ([quest.entry(STAMP, state)] if state != "backlog" else [])
    fm = {"id": qid, "title": title, "kind": kind, "state": state, **extra, "history": history}
    (d / "quest.md").write_text(quest.render_page(fm, quest.quest_body("g", "d")))
    return d


def test_log_excludes_terminal_and_sorts_newest_first(tmp_path):
    qdir = tmp_path / "docs" / "quests"
    _make(qdir, "2609011000-aa", "Old open")
    _make(qdir, "2609041432-bb", "New active", state="research")
    _make(qdir, "2609031200-cc", "Finished", state="completed")
    _make(qdir, "2609021200-dd", "Dropped", state="abandoned")
    _make(qdir, "2609021300-ee", "Parked", state="backlog", resume="review plan")
    lines = quest.log_lines(quest.load_quests(qdir))
    assert len(lines) == 3
    assert lines[0] == "| [2609041432-bb](2609041432-bb-new-active/) | quest | research | New active |"
    assert lines[1] == "| [2609021300-ee](2609021300-ee-parked/) | quest | backlog, resume at review plan | Parked |"
    assert lines[2] == "| [2609011000-aa](2609011000-aa-old-open/) | quest | backlog | Old open |"
    text = quest.render_log(quest.load_quests(qdir), "abc1234", NOW)
    assert text.startswith(f"# Quest log\n\n<!-- questlog format {quest.FORMAT}, written by questlog abc1234 on 2026-09-04 -->")
    assert "| Id | Kind | State | Title |" in text


def test_log_byte_bound_thirty_items(tmp_path):
    qdir = tmp_path / "docs" / "quests"
    for n in range(30):
        _make(qdir, f"2609041{n:03d}-aa", f"A realistic title of typical length number {n}", kind="chore" if n % 2 else "quest", state="review implementation" if n % 3 else "backlog")
    text = quest.render_log(quest.load_quests(qdir), "abc1234", NOW)
    assert len(text.encode()) < 5120, len(text.encode())


def test_resolve_prefix(tmp_path):
    qdir = tmp_path / "docs" / "quests"
    _make(qdir, "2609041432-bb", "One")
    _make(qdir, "2609041432-bc", "Two")
    d, fm = quest.resolve(qdir, "2609041432-bb")
    assert fm["title"] == "One"
    with pytest.raises(SystemExit):
        quest.resolve(qdir, "2609041432-b")
    with pytest.raises(SystemExit):
        quest.resolve(qdir, "nope")


def test_project_root_from_env_and_git(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    assert quest.project_root() == tmp_path.resolve()
    monkeypatch.delenv("CLAUDE_PROJECT_DIR")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    monkeypatch.chdir(tmp_path)
    assert quest.project_root() == tmp_path.resolve()


def test_project_root_fails_outside_git(tmp_path, monkeypatch):
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit):
        quest.project_root()


def test_new_log_show_end_to_end(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["new", "Build the thing", "--goal", "a working thing", "--done-when", "it runs"])
    quest.main(["new", "Fix a typo", "--chore"])
    qdir = tmp_path / "docs" / "quests"
    dirs = [d for d in qdir.iterdir() if d.is_dir()]
    assert len(dirs) == 2
    log = (qdir / "README.md").read_text()
    assert "| chore | backlog | Fix a typo |" in log
    assert "| quest | backlog | Build the thing |" in log
    assert "| Id | Kind | State | Title |" in log
    build = next(d for d in dirs if "build" in d.name)
    assert "a working thing" in (build / "quest.md").read_text()
    qid = _fm(build)["id"]
    capsys.readouterr()
    quest.main([qid])
    out = capsys.readouterr().out
    assert out.startswith(f"{qid} is in the backlog as a quest. Start it with: quest {qid} start\n")
    assert f"guidance: {REFERENCES / 'goal.md'}" in out and "reviewer:" not in out and "overlay:" not in out
    assert Path(out.split("guidance: ")[1].splitlines()[0]).is_file()
    quest.main([qid, "start"]); quest.main([qid, "show"])
    assert f"{qid} is at draft goal." in capsys.readouterr().out
    (build / "goal.md").write_text("# Goal\n"); quest.main([qid, "next"]); capsys.readouterr()
    quest.main([qid])
    out = capsys.readouterr().out
    assert "reviewer: questlog:review-goal" in out and "record: goal-review.md" in out
    overlay = qdir / "guidance" / "goal.md"
    overlay.parent.mkdir(); overlay.write_text("# Our goal rules\n")
    quest.main([qid])
    assert f"overlay: {overlay}" in capsys.readouterr().out
    quest.main([qid, "abandon", "done with it"]); capsys.readouterr()
    quest.main([qid])
    assert "guidance:" not in capsys.readouterr().out          # a finished entry


def _fresh(tmp_path, monkeypatch, title="Build", chore=False):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["new", title] + (["--chore"] if chore else []))
    qdir = tmp_path / "docs" / "quests"
    d, fm = quest.load_quests(qdir)[0]
    return qdir, d, fm["id"]


def _fm(d):
    return quest.parse_page((d / "quest.md").read_text())[0]


def _git_commit_all(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".claude").mkdir(exist_ok=True)
    if not (tmp_path / ".claude" / "settings.json").is_file():     # init may have written the ask rules already
        (tmp_path / ".claude" / "settings.json").write_text("{}")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x"], check=True)


def test_full_quest_lifecycle(tmp_path, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    with pytest.raises(SystemExit):          # cannot move on before start
        quest.main([qid, "next"])
    quest.main([qid, "start"])
    assert _fm(d)["state"] == "draft goal"
    with pytest.raises(SystemExit):          # goal.md must exist to leave draft goal
        quest.main([qid, "next"])
    files = {"research": "research.md", "design": "design.md", "plan": "plan.md"}
    (d / "goal.md").write_text("# Goal\n")
    for expected in NAMES[1:]:
        quest.main([qid, "next"])
        fm = _fm(d)
        assert fm["state"] == expected and fm["history"][-1]["state"] == expected
        if expected in files:
            (d / files[expected]).write_text(f"# {expected}\n")
    quest.main([qid, "next"])
    fm = _fm(d)
    assert fm["state"] == "completed" and len(fm["history"]) == 13 and set(fm) == {"id", "title", "kind", "state", "history"}
    assert qid not in (qdir / "README.md").read_text()
    with pytest.raises(SystemExit):          # terminal
        quest.main([qid, "start"])
    with pytest.raises(SystemExit):
        quest.main([qid, "next"])


def test_chore_lifecycle_and_log_stage(tmp_path, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch, "Fix", chore=True)
    fm = _fm(d)
    assert [e["state"] for e in fm["history"] if e.get("skipped")] == list(quest.CHORE_SKIPS)
    assert all(e["note"] == "chore" for e in fm["history"] if e.get("skipped"))
    quest.main([qid, "start"])
    assert "| chore | draft goal | Fix |" in (qdir / "README.md").read_text()
    (d / "goal.md").write_text("# Goal\n")
    quest.main([qid, "next"]); quest.main([qid, "next"])
    assert _fm(d)["state"] == "plan"                              # research and design passed over
    assert "| chore | plan | Fix |" in (qdir / "README.md").read_text()
    (d / "plan.md").write_text("# Plan\n")
    for _ in range(5):
        quest.main([qid, "next"])
    assert _fm(d)["state"] == "completed"


def test_skip_research_skips_its_review(tmp_path, monkeypatch, capsys):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    quest.main([qid, "start"]); (d / "goal.md").write_text("# Goal\n")
    quest.main([qid, "next"]); quest.main([qid, "next"]); capsys.readouterr()
    assert _fm(d)["state"] == "research"
    quest.main([qid, "skip"])
    fm = _fm(d)
    assert fm["state"] == "design" and f"{qid} is at design." in capsys.readouterr().out
    assert [e["state"] for e in fm["history"] if e.get("skipped")] == ["research", "review research"]
    (d / "design.md").write_text("# Design\n"); quest.main([qid, "next"])
    quest.main([qid, "skip"])                                     # skipping a review state skips only itself
    assert _fm(d)["state"] == "plan"
    assert [e["state"] for e in _fm(d)["history"] if e.get("skipped")] == ["research", "review research", "review design"]


def test_skip_at_review_state(tmp_path, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    quest.main([qid, "start"]); (d / "goal.md").write_text("# Goal\n"); quest.main([qid, "next"])
    assert _fm(d)["state"] == "review goal"
    quest.main([qid, "skip"])
    fm = _fm(d)
    assert fm["state"] == "research" and fm["history"][-2] == {**fm["history"][-2], "state": "review goal", "skipped": True}


def test_skip_refuses_unskippable(tmp_path, monkeypatch, capsys):
    qdir, d, qid = _fresh(tmp_path, monkeypatch, "Fix", chore=True)
    quest.main([qid, "start"])
    for state, file in (("draft goal", "goal.md"), ("plan", "plan.md"), ("implement", None), ("evaluate goal", None)):
        while _fm(d)["state"] != state:
            quest.main([qid, "skip"] if quest.BY_NAME[_fm(d)["state"]].skippable else [qid, "next"])
        with pytest.raises(SystemExit):
            quest.main([qid, "skip"])
        assert f"{state} cannot be skipped" in capsys.readouterr().err
        if file:
            (d / file).write_text("x\n")
        quest.main([qid, "next"])
    assert _fm(d)["state"] == "completed"


def test_next_refuses_missing_file(tmp_path, monkeypatch, capsys):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    quest.main([qid, "start"])
    for state, file in (("draft goal", "goal.md"), ("research", "research.md"), ("design", "design.md"), ("plan", "plan.md")):
        assert _fm(d)["state"] == state
        with pytest.raises(SystemExit):
            quest.main([qid, "next"])
        assert f"{file} does not exist yet" in capsys.readouterr().err
        (d / file).write_text("x\n")
        quest.main([qid, "next"]); quest.main([qid, "next"])
    assert _fm(d)["state"] == "implement"
    quest.main([qid, "next"])                                     # implement has no file check


def test_next_refuses_unconverged_verdict_until_confirmed(tmp_path, monkeypatch, capsys):
    qdir, d, qid = _fresh(tmp_path, monkeypatch, "Fix", chore=True)
    quest.main([qid, "start"]); (d / "goal.md").write_text("# Goal\n"); quest.main([qid, "next"]); quest.main([qid, "next"])
    (d / "plan.md").write_text("# Plan\n"); quest.main([qid, "next"]); capsys.readouterr()
    assert _fm(d)["state"] == "review plan"
    quest.main([qid, "next"])                                     # no record yet: nothing to confirm
    assert _fm(d)["state"] == "implement"
    quest.main([qid, "next"]); capsys.readouterr()
    (d / "implement-review.md").write_text("# Review record: implement\n\n## Pass 1\n\nVerdict: another pass\n")
    with pytest.raises(SystemExit) as e:
        quest.main([qid, "next"])
    err = capsys.readouterr().err
    assert e.value.code == 1 and "last verdict: another pass" in err and f"quest {qid} next --confirmed" in err
    assert _fm(d)["state"] == "review implementation"
    quest.main([qid, "next", "--confirmed"])
    assert _fm(d)["state"] == "evaluate goal"
    (d / "result-review.md").write_text("Verdict: another pass\n\nVerdict: converged\n")
    quest.main([qid, "next"])                                     # the last verdict converged
    assert _fm(d)["state"] == "completed"
    with pytest.raises(SystemExit) as e:
        quest.main([qid, "next", "--force"])
    assert e.value.code == 2


def test_abandon_requires_reason_and_keeps_files(tmp_path, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    with pytest.raises(SystemExit):
        quest.main([qid, "abandon", "   "])
    with pytest.raises(SystemExit):
        quest.main([qid, "abandon"])
    quest.main([qid, "abandon", "superseded by a better idea"])
    fm = _fm(d)
    assert fm["state"] == "abandoned" and fm["history"][-1]["note"] == "superseded by a better idea" and "resume" not in fm
    assert (d / "quest.md").is_file()
    assert qid not in (qdir / "README.md").read_text()
    with pytest.raises(SystemExit):
        quest.main([qid, "next"])
    with pytest.raises(SystemExit):
        quest.main([qid, "abandon", "again"])


def test_start_twice_fails(tmp_path, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    quest.main([qid, "start"])
    with pytest.raises(SystemExit):
        quest.main([qid, "start"])


def test_defer_returns_to_backlog_and_start_resumes(tmp_path, monkeypatch, capsys):
    qdir, d, qid = _fresh(tmp_path, monkeypatch, "Park", chore=True)
    quest.main([qid, "start"]); (d / "goal.md").write_text("# Goal\n"); quest.main([qid, "next"]); quest.main([qid, "next"])
    (d / "plan.md").write_text("# Plan\n"); quest.main([qid, "next"])
    assert _fm(d)["state"] == "review plan"
    capsys.readouterr()
    quest.main([qid, "defer"])
    assert f"{qid} is in the backlog, to resume at review plan. Start it with: quest {qid} start" in capsys.readouterr().out
    fm = _fm(d)
    assert fm["state"] == "backlog" and fm["resume"] == "review plan" and fm["history"][-1]["state"] == "backlog"
    assert "| chore | backlog, resume at review plan | Park |" in (qdir / "README.md").read_text()
    for argv in ([qid, "next"], [qid, "skip"], [qid, "defer"]):
        with pytest.raises(SystemExit):
            quest.main(argv)
    quest.main([qid, "start"])
    fm = _fm(d)
    assert fm["state"] == "review plan" and "resume" not in fm and fm["history"][-1]["state"] == "review plan"
    _make(qdir, "2609040000-zz", "Over", state="completed")
    with pytest.raises(SystemExit):                              # finished entries do not defer
        quest.main(["2609040000-zz", "defer"])


def test_say_lines():
    fm = {"id": "2609040000-aa", "kind": "quest", "state": "backlog", "history": [quest.entry(STAMP, "backlog")]}
    assert quest.say(fm) == "2609040000-aa is in the backlog as a quest. Start it with: quest 2609040000-aa start"
    assert quest.say({**fm, "resume": "review plan"}) == "2609040000-aa is in the backlog, to resume at review plan. Start it with: quest 2609040000-aa start"
    assert quest.say({**fm, "state": "completed"}) == "2609040000-aa is completed."
    assert quest.say({**fm, "state": "abandoned"}) == "2609040000-aa is abandoned."
    expected = {
        "draft goal": "Write goal.md, then run: quest 2609040000-aa next",
        "review goal": "Run the review-goal loop into goal-review.md, then ask the creator: move on to researching?",
        "research": "Write research.md, then run: quest 2609040000-aa next",
        "review research": "Run the review-research loop into research-review.md, then ask: move on to designing?",
        "design": "Write design.md, then run: quest 2609040000-aa next",
        "review design": "Run the review-design loop into design-review.md, then ask: move on to planning?",
        "plan": "Write plan.md, then run: quest 2609040000-aa next",
        "review plan": "Run the review-plan loop into plan-review.md, then ask: move on to implementing?",
        "implement": "Build in the order plan.md lists, then run: quest 2609040000-aa next",
        "review implementation": "Run the review-implement loop into implement-review.md, then ask: move on to evaluating the goal?",
        "evaluate goal": "Run the review-result loop into result-review.md, then ask: is the goal met?",
    }
    for name, tail in expected.items():
        assert quest.say({**fm, "state": name}) == f"2609040000-aa is at {name}. {tail}", name
    chore = {**fm, "kind": "chore", "state": "review goal", "history": fm["history"] + [quest.entry(STAMP, n, skipped=True, note="chore") for n in quest.CHORE_SKIPS]}
    assert quest.say(chore).endswith("move on to planning?")


def test_unknown_command_and_verb_exit_2(tmp_path, monkeypatch, capsys):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    for argv in (["next", qid], ["draft", qid, "plan"], ["complete"], ["show", qid], ["start", qid]):
        with pytest.raises(SystemExit) as e:
            quest.main(argv)
        err = capsys.readouterr().err
        assert e.value.code == 2 and f"unknown command: {argv[0]}" in err and "quest ID next" in err, argv
    with pytest.raises(SystemExit) as e:
        quest.main([qid, "fly"])
    assert e.value.code == 2 and "unknown verb: fly" in capsys.readouterr().err
    with pytest.raises(SystemExit) as e:
        quest.main(["log", "extra"])
    assert e.value.code == 2
    quest.main(["--help"])
    out = capsys.readouterr().out
    assert "quest ID next [--confirmed]" in out and "States, in order: draft goal, review goal" in out and "evaluate goal" in out


def test_update_quest_none_deletes_in_merge_mode_only(tmp_path):
    d = _make(tmp_path / "docs" / "quests", "2609040000-aa", "Keys", resume="review plan", note=None)
    fm = quest.update_quest(d, {"resume": None, "missing": None, "state": "review plan"})
    assert "resume" not in fm and "missing" not in fm and fm["state"] == "review plan"
    assert "note" in fm                                          # a page value of None survives a merge
    fm = quest.update_quest(d, {"id": "2609040000-aa", "note": None}, replace=True)
    assert "note" in fm                                          # replace mode keeps None-valued keys


def test_init_is_idempotent_and_appends_paragraph(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    (tmp_path / "CLAUDE.md").write_text("# Me\n\nrules\n")
    quest.main(["init"])
    text = (tmp_path / "CLAUDE.md").read_text()
    assert text.startswith("# Me\n\nrules\n") and quest.CLAUDE_MD_MARK in text and "quest log" in text
    assert (tmp_path / "docs/quests/README.md").is_file()
    quest.main(["init"])
    assert (tmp_path / "CLAUDE.md").read_text().count(quest.CLAUDE_MD_MARK) == 1
    assert "nothing changed" in capsys.readouterr().out


def test_init_writes_ask_rules_and_keeps_other_keys(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir()
    settings.write_text('{"enabledPlugins": {"questlog@dokidlc": true}, "permissions": {"allow": ["Bash(git status)"]}}')
    quest.main(["init"])
    data = json.loads(settings.read_text())
    assert data["enabledPlugins"] == {"questlog@dokidlc": True} and data["permissions"]["allow"] == ["Bash(git status)"]
    assert data["permissions"]["ask"] == list(quest.ASK_RULES) and len(quest.ASK_RULES) == 7
    assert "7 ask rules in .claude/settings.json" in capsys.readouterr().out
    before = settings.read_bytes()
    quest.main(["init"])
    assert settings.read_bytes() == before and "already initialized; nothing changed" in capsys.readouterr().out
    # one rule already there. init adds six and keeps the existing one.
    settings.write_text('{"permissions": {"ask": ["Bash(quest next *)"]}}')
    quest.main(["init"])
    assert json.loads(settings.read_text())["permissions"]["ask"] == ["Bash(quest next *)"] + [r for r in quest.ASK_RULES if r != "Bash(quest next *)"]
    assert "6 ask rules" in capsys.readouterr().out
    # an unparsable file stops init before it touches anything
    fresh = tmp_path / "fresh"; (fresh / ".claude").mkdir(parents=True)
    (fresh / ".claude" / "settings.json").write_text("{")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(fresh))
    with pytest.raises(SystemExit) as e:
        quest.main(["init"])
    assert e.value.code == 2 and ".claude/settings.json" in capsys.readouterr().err
    assert (fresh / ".claude" / "settings.json").read_text() == "{" and not (fresh / "docs").exists()
    # no settings file at all. init creates one with just the rules.
    bare = tmp_path / "bare"; bare.mkdir()
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(bare))
    quest.main(["init"])
    assert json.loads((bare / ".claude" / "settings.json").read_text()) == {"permissions": {"ask": list(quest.ASK_RULES)}}


def test_format_newer_refuses(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["init"])
    log = tmp_path / "docs/quests/README.md"
    log.write_text(log.read_text().replace(f"format {quest.FORMAT}", f"format {quest.FORMAT + 1}"))
    with pytest.raises(SystemExit) as e:
        quest.main(["log"])
    assert e.value.code == 2 and "newer questlog" in capsys.readouterr().err
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 1 and f"format {quest.FORMAT + 1} is newer" in capsys.readouterr().out


def test_doctor_reports_and_fixes(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 1 and "quest init" in capsys.readouterr().out
    quest.main(["init"]); quest.main(["new", "Thing"])
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 1                      # not a git repo yet, so persistence fails
    assert "git repository" in capsys.readouterr().out
    _git_commit_all(tmp_path)
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 0
    log = tmp_path / "docs/quests/README.md"
    log.write_text(log.read_text().replace("| [", "| x ["))
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 1 and "matches the directories" in capsys.readouterr().out
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor", "--fix"])
    assert e.value.code == 0                      # a tracked file that is modified still counts as committed
    d = next(p for p in (tmp_path / "docs/quests").iterdir() if p.is_dir())
    good = (d / "quest.md").read_text()
    (d / "quest.md").write_text("---\nid: nope\n---\nbody\n")
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 1 and "frontmatter invalid" in capsys.readouterr().out
    (d / "quest.md").write_text(good.replace("\nstate: backlog\n", "\nstate: plan\n"))
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 1 and "state plan disagrees with its history (backlog)" in capsys.readouterr().out
    (d / "quest.md").write_text(good.replace("kind: quest", "kind: epic"))
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 1 and "frontmatter invalid" in capsys.readouterr().out
    (d / "quest.md").write_text(good)
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor", "--brief"])
    assert e.value.code == 0 and "questlog: ok, 1 open" in capsys.readouterr().out


def test_doctor_brief(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["doctor", "--brief"])
    assert "no docs/quests/" in capsys.readouterr().out
    quest.main(["init"]); quest.main(["new", "Thing"]); capsys.readouterr()
    with pytest.raises(SystemExit):
        quest.main(["doctor", "--brief"])
    assert "git repository" in capsys.readouterr().out          # persistence problem named at session start
    _git_commit_all(tmp_path)
    with pytest.raises(SystemExit):
        quest.main(["doctor", "--brief"])
    assert "questlog: ok, 1 open" in capsys.readouterr().out


def test_memory_hits_fail_open_and_parse(monkeypatch):
    monkeypatch.setattr(quest.shutil, "which", lambda name: None)
    assert quest.memory_hits("anything") == []
    monkeypatch.setattr(quest.shutil, "which", lambda name: "/x/memory")
    class P: stdout = 'embedding failed: x\n[{"filename": "a.md", "summary": "A"}, {"filename": "b.md", "summary": "B"}]\n'
    monkeypatch.setattr(quest.subprocess, "run", lambda *a, **k: P())
    assert quest.memory_hits("q") == ["`memory read a.md` (A)", "`memory read b.md` (B)"]


def test_next_prints_memory_nudge_after_a_document_state(tmp_path, monkeypatch, capsys):
    qdir, d, qid = _fresh(tmp_path, monkeypatch, "Fix", chore=True)
    quest.main([qid, "start"]); (d / "goal.md").write_text("# Goal\n"); quest.main([qid, "next"]); quest.main([qid, "next"])
    (d / "plan.md").write_text("# Plan\n"); capsys.readouterr()
    monkeypatch.setattr(quest.shutil, "which", lambda name: "/x/memory")
    monkeypatch.setattr(quest, "memory_hits", lambda q: [])
    quest.main([qid, "next"])
    out = capsys.readouterr().out
    assert "memory: what did you learn while planning on your own?" in out and f"--ref {d.name}/plan.md" in out
    quest.main([qid, "next"])
    assert "memory:" not in capsys.readouterr().out            # implement gets no write prompt


def test_terminal_table_aligns():
    rows = [("2609041432-bb", "d", "quest", "research", "New active"), ("2609011000-aa", "d", "chore", "backlog", "Old")]
    out = quest.terminal_table(rows).splitlines()
    assert out[0].startswith("Id             Kind   State     Title")
    assert out[2].startswith("2609041432-bb  quest  research  New active")


def test_pipe_in_title_is_escaped_in_the_log(tmp_path):
    qdir = tmp_path / "docs" / "quests"
    _make(qdir, "2609041432-bb", "Fix a | b")
    line = quest.log_lines(quest.load_quests(qdir))[0]
    assert "Fix a \\| b |" in line and line.count("|") == 6


def test_symlinked_log_and_quest_are_refused(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    target = tmp_path / "victim.md"; target.write_text("precious\n")
    qdir = tmp_path / "docs" / "quests"; qdir.mkdir(parents=True)
    (qdir / "README.md").symlink_to(target)
    quest.main(["log"]); capsys.readouterr()          # reading never follows the link into a write
    assert target.read_text() == "precious\n"
    with pytest.raises(SystemExit):                    # writing refuses it
        quest.main(["new", "Anything"])
    assert target.read_text() == "precious\n"
    (qdir / "README.md").unlink()
    (qdir / "README.md").write_text("Not our file\n")
    quest.main(["log"])                                   # unrecognised file: left alone
    assert (qdir / "README.md").read_text() == "Not our file\n"
    real = _make(qdir, "2609041432-bb", "Real"); link = qdir / "2609041433-cc-link"; link.symlink_to(real)
    assert [fm["id"] for _, fm in quest.load_quests(qdir)] == ["2609041432-bb"]


def test_symlinked_settings_and_claude_md_are_refused(tmp_path, monkeypatch, capsys):
    # a cloned repository can carry a symlink at .claude, .claude/settings.json, or CLAUDE.md; init refuses each before writing anything
    outside = tmp_path / "outside"; outside.mkdir()
    victim = outside / "settings.json"; victim.write_text('{"theirs": true}')
    for name, link, target in (("settings.json", ".claude/settings.json", victim), (".claude", ".claude", outside), ("CLAUDE.md", "CLAUDE.md", outside / "CLAUDE.md")):
        repo = tmp_path / f"repo-{name}"
        (repo / ".claude").mkdir(parents=True) if link != ".claude" else repo.mkdir()
        (repo / link).symlink_to(target)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
        with pytest.raises(SystemExit) as e:
            quest.main(["init"])
        assert e.value.code == 1 and "symlink" in capsys.readouterr().err, name
        assert not (repo / "docs").exists(), name
    assert victim.read_text() == '{"theirs": true}' and not (outside / "CLAUDE.md").exists() and sorted(p.name for p in outside.iterdir()) == ["settings.json"]


def test_multiline_title_is_one_log_line(tmp_path):
    qdir = tmp_path / "docs" / "quests"
    _make(qdir, "2609041432-bb", "First line\nsecond line")
    assert "\n" not in quest.log_lines(quest.load_quests(qdir))[0]


def _finished(at, state="completed"):
    return [quest.entry(STAMP, "backlog"), quest.entry(at, state)]


def test_history_lists_finished_newest_first_bounded(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    qdir = tmp_path / "docs" / "quests"
    _make(qdir, "2609011000-aa", "Open")
    _make(qdir, "2609011001-bb", "Active", state="design")
    # ids say cc is older than dd, but cc finished later; the finish time wins
    _make(qdir, "2609011002-cc", "Later finish", state="completed", history=_finished("2026-09-05T03:03:00Z"))
    _make(qdir, "2609011003-dd", "Earlier finish", kind="chore", state="completed", history=_finished("2026-09-05T03:00:00Z"))
    _make(qdir, "2609011004-ee", "Dropped", state="abandoned", history=_finished("2026-09-05T04:00:00Z", "abandoned"))
    rows = quest.history_rows(quest.load_quests(qdir))
    assert [r[0] for r in rows] == ["2609011002-cc", "2609011003-dd"]
    assert rows[0][4] == "2026-09-05" and rows[0][2] == "quest" and rows[1][2] == "chore"
    assert [r[0] for r in quest.history_rows(quest.load_quests(qdir), include_abandoned=True)] == ["2609011004-ee", "2609011002-cc", "2609011003-dd"]
    assert [r[0] for r in quest.history_rows(quest.load_quests(qdir), limit=1)] == ["2609011002-cc"]
    quest.main(["init"]); capsys.readouterr()
    quest.main(["history", "--limit", "1"])
    out = capsys.readouterr().out.splitlines()
    assert out[0].split() == ["Id", "Kind", "State", "Finished", "Title"]
    assert len(out) == 3 and out[2].split() == ["2609011002-cc", "quest", "completed", "2026-09-05", "Later", "finish"]
    quest.main(["history", "--all"])
    assert "Dropped" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        quest.main(["history", "--limit", "0"])
    assert "at least 1" in capsys.readouterr().err


def test_history_empty_and_log_unchanged(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["init"]); quest.main(["new", "Thing"]); capsys.readouterr()
    before = (tmp_path / "docs/quests/README.md").read_text()
    quest.main(["history"])
    assert capsys.readouterr().out.strip() == "Nothing completed."
    assert (tmp_path / "docs/quests/README.md").read_text() == before   # read only


def test_next_line_passes_over_skipped_research():
    fm = {"id": "2609040000-aa", "state": "review goal", "history": [quest.entry(STAMP, "research", skipped=True), quest.entry(STAMP, "review research", skipped=True)]}
    assert quest.successor(fm, "review goal") == "design"
    assert quest.say(fm).endswith("move on to designing?")


def test_next_prints_state_line(tmp_path, capsys, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch, "Fix", chore=True)
    quest.main([qid, "start"]); (d / "goal.md").write_text("# Goal\n"); capsys.readouterr()
    quest.main([qid, "next"])
    assert f"{qid} is at review goal. Run the review-goal loop into goal-review.md, then ask the creator: move on to planning?" in capsys.readouterr().out
    quest.main([qid, "next"]); (d / "plan.md").write_text("# Plan\n"); quest.main([qid, "next"]); capsys.readouterr()
    quest.main([qid, "next"])
    assert "is at implement. Build in the order plan.md lists" in capsys.readouterr().out
    quest.main([qid, "next"]); quest.main([qid, "next"]); capsys.readouterr()
    quest.main([qid, "next"])
    assert f"{qid} is completed." in capsys.readouterr().out


def test_parse_page_normalizes_unquoted_stamps():
    """A hand-edited page may leave a stamp unquoted; YAML then yields a datetime or date. Every consumer must see the quoted form."""
    def page(line):
        return quest.parse_page(f"---\nid: x\n{line}\n---\nbody\n")[0]
    assert page("at: '2026-09-05T01:00:00Z'")["at"] == "2026-09-05T01:00:00Z"
    assert page("at: 2026-09-05T23:00:00Z")["at"] == "2026-09-05T23:00:00Z"
    assert page("at: 2026-09-06T01:00:00+02:00")["at"] == "2026-09-05T23:00:00Z"
    assert page("at: 2026-09-05T12:00:00")["at"] == "2026-09-05T12:00:00Z"
    assert page("at: 2026-09-04")["at"] == "2026-09-04T00:00:00Z"
    nested = page("history:\n- state: backlog\n  at: 2026-09-05T23:00:00Z")["history"]
    assert nested == [{"state": "backlog", "at": "2026-09-05T23:00:00Z"}]          # a nested unquoted stamp loads as a string too


def test_doctor_compares_the_marked_paragraph_with_the_template(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    (tmp_path / "CLAUDE.md").write_text("# Me\n\nrules\n")
    quest.main(["init"]); _git_commit_all(tmp_path); capsys.readouterr()
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 0 and "FAIL" not in capsys.readouterr().out        # freshly written: matches
    text = (tmp_path / "CLAUDE.md").read_text()
    (tmp_path / "CLAUDE.md").write_text(text + "\n## After\n\nunrelated, must not count\n")
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 0                                                   # the section ends at the next heading
    (tmp_path / "CLAUDE.md").write_text(text.replace("creator verb", "quest close"))
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    out = capsys.readouterr().out
    assert e.value.code == 1 and "FAIL CLAUDE.md quests paragraph matches" in out and "quest init` writes" in out
    assert quest.marked_section("no mark here\n") is None


def test_doctor_reports_missing_ask_rules(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["init"]); _git_commit_all(tmp_path); capsys.readouterr()
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 0 and "ok   settings.json asks for every creator verb" in capsys.readouterr().out
    settings = tmp_path / ".claude" / "settings.json"
    data = json.loads(settings.read_text())
    data["permissions"]["ask"].remove("Bash(quest next *)")
    settings.write_text(json.dumps(data))
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 1 and "FAIL settings.json asks for every creator verb; missing: Bash(quest next *)  (quest doctor --fix)" in capsys.readouterr().out
    # --fix writes the rules, an agent verb: a project initialized by an older plugin gets its prompts back without a creator verb
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor", "--fix"])
    assert e.value.code == 0 and "Bash(quest next *)" in settings.read_text()
    assert f"<!-- questlog format {quest.FORMAT}" in (tmp_path / "docs/quests/README.md").read_text()


def test_settings_shapes_are_refused_without_a_traceback(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["init"]); _git_commit_all(tmp_path); capsys.readouterr()
    settings = tmp_path / ".claude" / "settings.json"
    page = tmp_path / "CLAUDE.md"; page_text = page.read_text()
    for content, problem in (("{", "is not valid JSON"), ("null", "is not a JSON object"), ("[]", "is not a JSON object"),
                             ('{"permissions": null}', "permissions is not an object"), ('{"permissions": []}', "permissions is not an object"),
                             ('{"permissions": {"ask": null}}', "permissions.ask is not a list"), ('{"permissions": {"ask": "Bash(quest next *)"}}', "permissions.ask is not a list")):
        settings.write_text(content)
        with pytest.raises(SystemExit) as e:
            quest.main(["doctor", "--brief"])                 # runs at every session start; must never traceback
        out = capsys.readouterr().out
        assert e.value.code == 0 and problem in out and "fix it by hand" in out, content
        with pytest.raises(SystemExit) as e:
            quest.main(["doctor"])
        assert e.value.code == 1 and f"FAIL .claude/settings.json {problem}  (fix it by hand)" in capsys.readouterr().out, content
        with pytest.raises(SystemExit) as e:
            quest.main(["init"])
        assert e.value.code == 2 and problem in capsys.readouterr().err, content
        assert settings.read_text() == content and page.read_text() == page_text
    # .claude as a regular file, and settings.json as a directory
    settings.unlink(); settings.mkdir()
    with pytest.raises(SystemExit) as e:
        quest.main(["init"])
    assert e.value.code == 2 and "not a file" in capsys.readouterr().err
    settings.rmdir(); settings.parent.rmdir(); settings.parent.write_text("x")
    with pytest.raises(SystemExit) as e:
        quest.main(["init"])
    assert e.value.code == 2 and ".claude is not a directory" in capsys.readouterr().err


def _format5_page(qdir, qid, title, **stamps):
    """A page as format 5 wrote it: five keys plus stage stamps, no history."""
    d = qdir / f"{qid}-{quest.slugify(title)}"
    d.mkdir(parents=True)
    fm = {"id": qid, "title": title, "kind": stamps.pop("kind", "quest"), "state": stamps.pop("state", "backlog"), "created": STAMP, **stamps}
    (d / "quest.md").write_text(quest.render_page(fm, quest.quest_body("g", "d")))
    return d


def test_init_refuses_settings_before_migrating(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    qdir = tmp_path / "docs" / "quests"
    d = _format5_page(qdir, "2609011000-aa", "At plan", state="active", goal_accepted="x")
    (qdir / "README.md").write_text("# Quest log\n\n<!-- questlog format 5, written by questlog old on 2026-09-04 -->\n")
    (tmp_path / ".claude").mkdir(); (tmp_path / ".claude" / "settings.json").write_text("{")
    page = (d / "quest.md").read_text()
    with pytest.raises(SystemExit) as e:
        quest.main(["init"])
    assert e.value.code == 2
    assert (d / "quest.md").read_text() == page and "format 5" in (qdir / "README.md").read_text()   # nothing written


def test_symlinked_settings_is_a_row_with_no_repair(tmp_path, monkeypatch, capsys):
    # doctor loads through the link, but the repair refuses it; the row must say so instead of advertising --fix
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["init"]); _git_commit_all(tmp_path); capsys.readouterr()
    settings = tmp_path / ".claude" / "settings.json"
    real = tmp_path / "real.json"; real.write_text('{"permissions": {"ask": []}}')
    settings.unlink(); settings.symlink_to(real)
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor", "--fix"])
    out = capsys.readouterr().out
    assert e.value.code == 1 and "; the file is a symlink  (add them by hand)" in out
    assert real.read_text() == '{"permissions": {"ask": []}}'


def test_unreadable_files_are_rows_not_tracebacks(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["init"]); _git_commit_all(tmp_path); capsys.readouterr()
    log = tmp_path / "docs" / "quests" / "README.md"; page = tmp_path / "CLAUDE.md"; settings = tmp_path / ".claude" / "settings.json"
    good_log, good_page = log.read_bytes(), page.read_bytes()
    log.write_bytes(b"# Quest log\n\xff\n"); page.write_bytes(b"caf\xe9\n"); settings.chmod(0)
    try:
        with pytest.raises(SystemExit) as e:
            quest.main(["doctor", "--brief"])
        out = capsys.readouterr().out
        assert e.value.code == 0 and "README.md is not a quest log" in out and "CLAUDE.md is not UTF-8" in out and "settings.json cannot be read" in out
    finally:
        settings.chmod(0o644)
    log.write_bytes(good_log); page.write_bytes(good_page)
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor", "--brief"])
    assert e.value.code == 0 and "questlog: ok" in capsys.readouterr().out


def test_doctor_fix_runs_every_repair_and_leaves_a_foreign_or_newer_log_alone(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    qdir = tmp_path / "docs" / "quests"
    d = _make(qdir, "2609011001-cc", "Done one", kind="chore", state="completed")
    page = (d / "quest.md").read_text()
    # a foreign README: the tracker repair refuses, the settings repair still runs, the page is not touched
    (qdir / "README.md").write_text("hello\n")
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor", "--fix"])
    out = capsys.readouterr().out
    assert e.value.code == 1 and "FAIL docs/quests/README.md is not a quest log, or cannot be read  (fix it by hand)" in out
    assert (qdir / "README.md").read_text() == "hello\n" and (d / "quest.md").read_text() == page
    assert "Bash(quest next *)" in (tmp_path / ".claude" / "settings.json").read_text()
    # a newer plugin's log: never downgraded
    (qdir / "README.md").write_text("# Quest log\n\n<!-- questlog format 9, written by questlog new on 2026-09-04 -->\n")
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor", "--fix"])
    assert e.value.code == 1 and "format 9" in (qdir / "README.md").read_text() and (d / "quest.md").read_text() == page
    # a missing log is written by --fix
    (qdir / "README.md").unlink()
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor", "--fix"])
    assert f"<!-- questlog format {quest.FORMAT}" in (qdir / "README.md").read_text() and (d / "quest.md").read_text() == page


def test_linked_tracker_is_refused_before_any_migration(tmp_path, monkeypatch, capsys):
    # a clone can link docs/quests, or docs, outside the project; no verb may write pages there, read verbs included
    outside = tmp_path / "outside"; oq = outside / "docs" / "quests"
    d = _format5_page(oq, "2609011000-aa", "At plan", state="active", goal_accepted="x")
    (oq / "README.md").write_text("# Quest log\n\n<!-- questlog format 5, written by questlog old on 2026-09-04 -->\n")
    page = (d / "quest.md").read_text()
    for link, target in (("docs/quests", oq), ("docs", outside / "docs")):
        repo = tmp_path / link.replace("/", "-"); (repo / "docs").mkdir(parents=True) if link != "docs" else repo.mkdir()
        (repo / link).symlink_to(target)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
        for verb in (["log"], ["2609011000-aa"], ["init"]):
            with pytest.raises(SystemExit) as e:
                quest.main(verb)
            assert e.value.code != 0 and "symlink" in capsys.readouterr().err, (link, verb)
        for verb in (["doctor"], ["doctor", "--fix"], ["doctor", "--brief"]):     # doctor names the link as its one row; --fix runs nothing
            with pytest.raises(SystemExit) as e:
                quest.main(verb)
            assert f"{link} is a symlink" in capsys.readouterr().out, (link, verb)
            assert (d / "quest.md").read_text() == page and "format 5" in (oq / "README.md").read_text(), (link, verb)
    # a linked docs with no tracker behind it: new must not create one there
    empty = tmp_path / "empty"; empty.mkdir()
    repo = tmp_path / "repo-new"; repo.mkdir(); (repo / "docs").symlink_to(empty)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
    with pytest.raises(SystemExit) as e:
        quest.main(["new", "Hello"])
    assert e.value.code == 1 and "symlink" in capsys.readouterr().err and list(empty.iterdir()) == []
    for verb in (["doctor"], ["doctor", "--fix"], ["doctor", "--brief"]):
        with pytest.raises(SystemExit):
            quest.main(verb)
        assert "docs is a symlink" in capsys.readouterr().out, verb
    assert list(empty.iterdir()) == []


def test_init_refuses_a_claude_md_link_to_a_managed_or_non_file_target(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    (tmp_path / ".claude").mkdir(); (tmp_path / ".claude" / "settings.json").write_text("{}")
    (tmp_path / ".git").mkdir(); (tmp_path / ".git" / "config").write_text("[core]\n")
    (tmp_path / "docs" / "quests" / "x").mkdir(parents=True); (tmp_path / "docs" / "quests" / "x" / "quest.md").write_text("---\nid: x\n---\n")
    for target in (".claude/settings.json", ".claude", "missing.md", ".git/config", "docs/quests/x/quest.md", "Docs/quests/x/quest.md"):
        (tmp_path / "CLAUDE.md").symlink_to(target)
        with pytest.raises(SystemExit) as e:
            quest.main(["init"])
        assert e.value.code == 1 and "CLAUDE.md" in capsys.readouterr().err, target
        assert not (tmp_path / "docs" / "quests" / "README.md").exists() and (tmp_path / ".claude" / "settings.json").read_text() == "{}", target
        assert (tmp_path / "docs" / "quests" / "x" / "quest.md").read_text() == "---\nid: x\n---\n", target
        (tmp_path / "CLAUDE.md").unlink()


def test_init_accepts_claude_md_linked_inside_the_repo(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    (tmp_path / "AGENTS.md").write_text("# Me\n"); (tmp_path / "CLAUDE.md").symlink_to("AGENTS.md")
    quest.main(["init"]); _git_commit_all(tmp_path)
    assert quest.CLAUDE_MD_MARK in (tmp_path / "AGENTS.md").read_text()
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 0


def test_init_keeps_settings_indent_and_final_newline(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    settings = tmp_path / ".claude" / "settings.json"; settings.parent.mkdir()
    settings.write_text('{\n    "enabledPlugins": {\n        "x@y": true\n    }\n}')
    quest.main(["init"])
    text = settings.read_text()
    assert text.startswith('{\n    "enabledPlugins": {\n        "x@y": true\n    },\n    "permissions"') and not text.endswith("\n")


def test_init_keeps_non_ascii_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    settings = tmp_path / ".claude" / "settings.json"; settings.parent.mkdir()
    settings.write_text('{\n    "hooks": {"command": "echo ✓ café"}\n}\n', encoding="utf-8")
    quest.main(["init"])
    text = settings.read_text(encoding="utf-8")
    assert "echo ✓ café" in text and "\\u" not in text and json.loads(text)["hooks"] == {"command": "echo ✓ café"}


REFERENCES = ROOT / "skills" / "quest" / "references"


def test_reference_files_exist_for_every_stage():
    for reference in {s.reference for s in quest.STATES}:
        text = (REFERENCES / reference).read_text()
        assert text.strip(), reference
        assert "\n## Review\n" in text, f"{reference} has no Review section"


def test_review_sections_state_the_stop_rule():
    for s in quest.STATES:
        if not s.reviewer:
            continue
        text = (REFERENCES / s.reference).read_text()
        review = text[text.index("\n## Review\n"):].lower()
        for word in ("blocking", "clarification", "polish", "converged", "three passes", f"questlog:{s.reviewer}", s.record):
            assert word in review, f"{s.reference} Review section lacks {word}"


def test_agents_exist_with_required_frontmatter():
    """`claude plugin validate` warns and exits 0 on a malformed agent file, so this parse is the syntax check."""
    import yaml
    names = [s.reviewer for s in quest.STATES if s.reviewer] + ["fact-finder"]
    assert "review-result" in names and "review-review" not in names and len(names) == 7
    assert quest.BY_NAME["evaluate goal"].record == "result-review.md" and quest.BY_NAME["review goal"].record == "goal-review.md"
    for name in names:
        text = (ROOT / "agents" / f"{name}.md").read_text()
        assert text.startswith("---\n"), name
        fm = yaml.safe_load(text[4:text.index("\n---\n", 4)])
        assert fm["name"] == name and fm["description"] and fm["model"], name
        for banned in ("hooks", "mcpServers", "permissionMode"):
            assert banned not in fm, f"{name}: plugin agents ignore {banned}"


def test_guidance_dir_is_not_a_quest(tmp_path, monkeypatch, capsys):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    (qdir / "guidance").mkdir(); (qdir / "guidance" / "design.md").write_text("# rules\n")
    _git_commit_all(tmp_path); capsys.readouterr()
    quest.main(["log"])
    assert "guidance" not in capsys.readouterr().out
    with pytest.raises(SystemExit):          # the fixture has no CLAUDE.md paragraph, so doctor fails on that row alone
        quest.main(["doctor"])
    out = capsys.readouterr().out
    assert "guidance/ has no quest.md" not in out and "ok   guidance/ holds only STAGE.md files" in out
    (qdir / "guidance" / "notes.txt").write_text("stray\n")
    with pytest.raises(SystemExit):
        quest.main(["doctor"])
    assert "FAIL guidance/ holds only STAGE.md files; stray: notes.txt" in capsys.readouterr().out
