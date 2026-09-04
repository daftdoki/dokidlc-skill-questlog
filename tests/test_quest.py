"""Tests for bin/quest. No harness, no network."""

import importlib.util
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
    fm = {"id": "2609041432-7k", "title": "T", "kind": "quest", "state": "backlog", "created": "2026-09-04T14:32:00Z"}
    body = quest.quest_body("do the thing", "it works")
    text = quest.render_page(fm, body)
    assert "created: '2026-09-04T14:32:00Z'" in text
    assert quest.parse_page(text) == (fm, body)


def test_current_stage_by_kind():
    assert quest.current_stage({"kind": "quest"}) == "goal"
    assert quest.current_stage({"kind": "quest", "goal_closed": "x", "research_skipped": "x"}) == "design"
    assert quest.current_stage({"kind": "chore"}) == "implement"
    assert quest.current_stage({"kind": "chore", "implement_closed": "x", "review_closed": "x"}) is None


def _make(qdir, qid, title, kind="quest", state="backlog", **extra):
    d = qdir / f"{qid}-{quest.slugify(title)}"
    d.mkdir(parents=True)
    fm = {"id": qid, "title": title, "kind": kind, "state": state, "created": "2026-09-04T00:00:00Z", **extra}
    (d / "quest.md").write_text(quest.render_page(fm, quest.quest_body("g", "d")))
    return d


def test_log_excludes_terminal_and_sorts_newest_first(tmp_path):
    qdir = tmp_path / "docs" / "quests"
    _make(qdir, "2609011000-aa", "Old open")
    _make(qdir, "2609041432-bb", "New active", state="active", goal_closed="x")
    _make(qdir, "2609031200-cc", "Finished", state="done")
    _make(qdir, "2609021200-dd", "Dropped", state="abandoned")
    lines = quest.log_lines(quest.load_quests(qdir))
    assert len(lines) == 2
    assert lines[0].startswith("- [2609041432-bb](2609041432-bb-new-active/) quest active research: New active")
    assert lines[1].startswith("- [2609011000-aa](2609011000-aa-old-open/) quest backlog goal: Old open")
    text = quest.render_log(quest.load_quests(qdir), "abc1234", NOW)
    assert text.startswith("# Quest log\n\n<!-- questlog format 1, written by questlog abc1234 on 2026-09-04 -->")


def test_log_byte_bound_thirty_items(tmp_path):
    qdir = tmp_path / "docs" / "quests"
    for n in range(30):
        _make(qdir, f"2609041{n:03d}-aa", f"A realistic title of typical length number {n}", kind="chore" if n % 2 else "quest", state="active" if n % 3 else "backlog")
    text = quest.render_log(quest.load_quests(qdir), "abc1234", NOW)
    # measured 2026-09-04: about 147 bytes a line with 46-character titles
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


def test_new_log_show_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["new", "Build the thing", "--goal", "a working thing", "--done-when", "it runs"])
    quest.main(["new", "Fix a typo", "--chore"])
    qdir = tmp_path / "docs" / "quests"
    dirs = [d for d in qdir.iterdir() if d.is_dir()]
    assert len(dirs) == 2
    log = (qdir / "README.md").read_text()
    assert "chore backlog implement: Fix a typo" in log
    assert "quest backlog goal: Build the thing" in log
    assert "a working thing" in next(d for d in dirs if "build" in d.name).joinpath("quest.md").read_text()


def _fresh(tmp_path, monkeypatch, title="Build", chore=False):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["new", title] + (["--chore"] if chore else []))
    qdir = tmp_path / "docs" / "quests"
    d, fm = quest.load_quests(qdir)[0]
    return qdir, d, fm["id"]


def _fm(d):
    return quest.parse_page((d / "quest.md").read_text())[0]


def test_full_quest_lifecycle(tmp_path, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    with pytest.raises(SystemExit):          # cannot draft before start
        quest.main(["draft", qid, "goal"])
    quest.main(["start", qid])
    assert _fm(d)["state"] == "active"
    with pytest.raises(SystemExit):          # goal.md must exist to draft goal
        quest.main(["draft", qid, "goal"])
    (d / "goal.md").write_text("# Goal\n")
    quest.main(["draft", qid, "goal"])
    assert "goal_drafted" in _fm(d)
    with pytest.raises(SystemExit):          # not the current stage
        quest.main(["close", qid, "design"])
    quest.main(["close", qid, "goal"])
    quest.main(["skip", qid, "research"])
    assert quest.current_stage(_fm(d)) == "design"
    (d / "design.md").write_text("# Design\n")
    quest.main(["draft", qid, "design"]); quest.main(["close", qid, "design"])
    quest.main(["close", qid, "implement"])
    quest.main(["close", qid, "review"])
    fm = _fm(d)
    assert fm["state"] == "done" and quest.current_stage(fm) is None
    assert qid not in (qdir / "README.md").read_text()
    with pytest.raises(SystemExit):          # terminal
        quest.main(["start", qid])


def test_chore_lifecycle_and_log_stage(tmp_path, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch, "Fix", chore=True)
    quest.main(["start", qid])
    assert "chore active implement: Fix" in (qdir / "README.md").read_text()
    with pytest.raises(SystemExit):          # a chore has no goal stage
        quest.main(["close", qid, "goal"])
    with pytest.raises(SystemExit):          # only research is skippable, and chores lack it
        quest.main(["skip", qid, "research"])
    quest.main(["close", qid, "implement"]); quest.main(["close", qid, "review"])
    assert _fm(d)["state"] == "done"


def test_abandon_requires_reason_and_keeps_files(tmp_path, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    with pytest.raises(SystemExit):
        quest.main(["abandon", qid, "   "])
    quest.main(["abandon", qid, "superseded by a better idea"])
    fm = _fm(d)
    assert fm["state"] == "abandoned" and fm["abandoned_reason"] == "superseded by a better idea"
    assert (d / "quest.md").is_file()
    assert qid not in (qdir / "README.md").read_text()
    with pytest.raises(SystemExit):
        quest.main(["close", qid, "goal"])


def test_start_twice_fails(tmp_path, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    quest.main(["start", qid])
    with pytest.raises(SystemExit):
        quest.main(["start", qid])


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


def test_format_newer_refuses_older_migrates(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["init"])
    log = tmp_path / "docs/quests/README.md"
    log.write_text(log.read_text().replace("format 1", "format 2"))
    with pytest.raises(SystemExit) as e:
        quest.main(["log"])
    assert e.value.code == 2 and "newer questlog" in capsys.readouterr().err
    log.write_text("# Quest log\n\nno header\n")
    quest.main(["log"])
    assert "format 1" in log.read_text()
    assert "migrated" in capsys.readouterr().err


def test_doctor_reports_and_fixes(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 1 and "quest init" in capsys.readouterr().out
    quest.main(["init"]); quest.main(["new", "Thing"])
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 0
    log = tmp_path / "docs/quests/README.md"
    log.write_text(log.read_text().replace("- [", "- x ["))
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 1 and "matches the directories" in capsys.readouterr().out
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor", "--fix"])
    assert e.value.code == 0
    d = next(p for p in (tmp_path / "docs/quests").iterdir() if p.is_dir())
    (d / "quest.md").write_text("---\nid: nope\n---\nbody\n")
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 1 and "frontmatter invalid" in capsys.readouterr().out


def test_doctor_brief(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["doctor", "--brief"])
    assert capsys.readouterr().out == ""
    quest.main(["init"]); quest.main(["new", "Thing"])
    with pytest.raises(SystemExit):
        quest.main(["doctor", "--brief"])
    assert "questlog: ok, 1 open" in capsys.readouterr().out
