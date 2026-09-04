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
