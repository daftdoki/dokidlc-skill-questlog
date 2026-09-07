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
    assert quest.current_stage({"kind": "quest", "goal_accepted": "x", "research_skipped": "x"}) == "design"
    assert quest.current_stage({"kind": "quest", "goal_accepted": "x", "research_skipped": "x", "design_accepted": "x"}) == "plan"
    assert quest.current_stage({"kind": "chore"}) == "plan"
    assert quest.current_stage({"kind": "chore", "plan_accepted": "x"}) == "implement"
    assert quest.current_stage({"kind": "chore", "plan_accepted": "x", "implement_accepted": "x", "review_accepted": "x"}) is None


def _make(qdir, qid, title, kind="quest", state="backlog", **extra):
    d = qdir / f"{qid}-{quest.slugify(title)}"
    d.mkdir(parents=True)
    fm = {"id": qid, "title": title, "kind": kind, "state": state, "created": "2026-09-04T00:00:00Z", **extra}
    (d / "quest.md").write_text(quest.render_page(fm, quest.quest_body("g", "d")))
    return d


def test_log_excludes_terminal_and_sorts_newest_first(tmp_path):
    qdir = tmp_path / "docs" / "quests"
    _make(qdir, "2609011000-aa", "Old open")
    _make(qdir, "2609041432-bb", "New active", state="active", goal_accepted="x")
    _make(qdir, "2609031200-cc", "Finished", state="completed")
    _make(qdir, "2609021200-dd", "Dropped", state="abandoned")
    lines = quest.log_lines(quest.load_quests(qdir))
    assert len(lines) == 2
    assert lines[0] == "| [2609041432-bb](2609041432-bb-new-active/) | quest | active | research | New active |"
    assert lines[1] == "| [2609011000-aa](2609011000-aa-old-open/) | quest | backlog | goal | Old open |"
    text = quest.render_log(quest.load_quests(qdir), "abc1234", NOW)
    assert text.startswith("# Quest log\n\n<!-- questlog format 4, written by questlog abc1234 on 2026-09-04 -->")


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
    assert "| chore | backlog | plan | Fix a typo |" in log
    assert "| quest | backlog | goal | Build the thing |" in log
    assert "| Id | Kind | State | Stage | Title |" in log
    assert "a working thing" in next(d for d in dirs if "build" in d.name).joinpath("quest.md").read_text()


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
    with pytest.raises(SystemExit):          # cannot draft before start
        quest.main(["draft", qid, "goal"])
    with pytest.raises(SystemExit):          # cannot move on before start
        quest.main(["next", qid])
    quest.main(["start", qid])
    assert _fm(d)["state"] == "active"
    with pytest.raises(SystemExit):          # goal.md must exist to draft goal
        quest.main(["draft", qid, "goal"])
    (d / "goal.md").write_text("# Goal\n")
    quest.main(["draft", qid, "goal"])
    assert "goal_drafted" in _fm(d)
    quest.main(["next", qid])
    assert "goal_accepted" in _fm(d) and quest.current_stage(_fm(d)) == "research"
    quest.main(["skip", qid, "research"])
    assert quest.current_stage(_fm(d)) == "design"
    (d / "design.md").write_text("# Design\n")
    quest.main(["draft", qid, "design"]); quest.main(["next", qid])
    assert quest.current_stage(_fm(d)) == "plan"
    with pytest.raises(SystemExit):          # plan is not skippable
        quest.main(["skip", qid, "plan"])
    (d / "plan.md").write_text("# Plan\n")
    quest.main(["draft", qid, "plan"]); quest.main(["next", qid])
    quest.main(["next", qid])
    quest.main(["next", qid])
    fm = _fm(d)
    assert fm["state"] == "completed" and quest.current_stage(fm) is None
    assert qid not in (qdir / "README.md").read_text()
    with pytest.raises(SystemExit):          # terminal
        quest.main(["start", qid])


def test_chore_lifecycle_and_log_stage(tmp_path, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch, "Fix", chore=True)
    quest.main(["start", qid])
    assert "| chore | active | plan | Fix |" in (qdir / "README.md").read_text()
    with pytest.raises(SystemExit):          # a chore has no goal stage
        quest.main(["draft", qid, "goal"])
    with pytest.raises(SystemExit):          # chores have no research stage
        quest.main(["skip", qid, "research"])
    (d / "plan.md").write_text("# Plan\n")
    quest.main(["draft", qid, "plan"]); quest.main(["next", qid])
    assert "| chore | active | implement | Fix |" in (qdir / "README.md").read_text()
    quest.main(["next", qid]); quest.main(["next", qid])
    assert _fm(d)["state"] == "completed"


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
        quest.main(["next", qid])


def test_start_twice_fails(tmp_path, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    quest.main(["start", qid])
    with pytest.raises(SystemExit):
        quest.main(["start", qid])


def test_defer_returns_to_backlog_and_start_resumes(tmp_path, monkeypatch, capsys):
    qdir, d, qid = _fresh(tmp_path, monkeypatch, "Park", chore=True)
    quest.main(["start", qid])
    (d / "plan.md").write_text("# Plan\n")
    quest.main(["draft", qid, "plan"])
    started = _fm(d)["started"]
    capsys.readouterr()
    quest.main(["defer", qid])
    assert f"{qid} backlog; current stage plan" in capsys.readouterr().out
    fm = _fm(d)
    assert fm["state"] == "backlog" and fm["deferred"]
    assert fm["started"] == started and fm["plan_drafted"]      # progress is kept
    assert "| chore | backlog | plan | Park |" in (qdir / "README.md").read_text()
    for argv in (["draft", qid, "plan"], ["next", qid, "plan"], ["defer", qid]):
        with pytest.raises(SystemExit):
            quest.main(argv)
    quest.main(["start", qid])
    fm = _fm(d)
    assert fm["state"] == "active" and "deferred" not in fm
    assert fm["started"] >= started and quest.current_stage(fm) == "plan"   # rewritten; stamps have second resolution
    _make(qdir, "2609040000-zz", "Over", state="completed", review_accepted="2026-09-04T00:00:00Z")
    with pytest.raises(SystemExit):                              # require_open
        quest.main(["defer", "2609040000-zz"])


def test_update_quest_none_deletes_in_merge_mode_only(tmp_path):
    d = _make(tmp_path / "docs" / "quests", "2609040000-aa", "Keys", deferred="2026-09-04T00:00:00Z", abandoned_reason=None)
    fm = quest.update_quest(d, {"deferred": None, "missing": None, "state": "active"})
    assert "deferred" not in fm and "missing" not in fm and fm["state"] == "active"
    assert "abandoned_reason" in fm                              # a page value of None survives a merge
    fm = quest.update_quest(d, {"id": "2609040000-aa", "abandoned_reason": None}, replace=True)
    assert "abandoned_reason" in fm                              # replace mode keeps None-valued keys


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
    # one rule already there: six are added and the existing one stays
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
    # no settings file at all: one is created with just the rules
    bare = tmp_path / "bare"; bare.mkdir()
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(bare))
    quest.main(["init"])
    assert json.loads((bare / ".claude" / "settings.json").read_text()) == {"permissions": {"ask": list(quest.ASK_RULES)}}


def test_format_newer_refuses_older_migrates(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["init"])
    log = tmp_path / "docs/quests/README.md"
    log.write_text(log.read_text().replace("format 4", "format 5"))
    with pytest.raises(SystemExit) as e:
        quest.main(["log"])
    assert e.value.code == 2 and "newer questlog" in capsys.readouterr().err
    log.write_text("# Quest log\n\nno header\n")
    quest.main(["log"])
    assert "format 4" in log.read_text()
    assert "migrated" in capsys.readouterr().err


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
    (d / "quest.md").write_text("---\nid: nope\n---\nbody\n")
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 1 and "frontmatter invalid" in capsys.readouterr().out


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


def test_migration_to_format_2_marks_plan_skipped_only_past_implement(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    qdir = tmp_path / "docs" / "quests"
    a = _make(qdir, "2609011000-aa", "At design", state="active", goal_closed="x", research_skipped="x")
    b = _make(qdir, "2609011001-bb", "Implementing", state="active", goal_closed="x", research_closed="x", design_closed="x", implement_drafted="x")
    c = _make(qdir, "2609011002-cc", "Finished", state="done", goal_closed="x", research_closed="x", design_closed="x", implement_closed="x", review_closed="x")
    (qdir / "README.md").write_text("# Quest log\n\n<!-- questlog format 1, written by questlog old on 2026-09-01 -->\n")
    quest.main(["log"])
    assert "plan_skipped" not in _fm(a)
    assert quest.current_stage(_fm(a)) == "design"
    assert _fm(b)["plan_skipped"] and quest.current_stage(_fm(b)) == "implement"
    assert _fm(c)["plan_skipped"] and quest.current_stage(_fm(c)) is None
    assert _fm(c)["state"] == "completed" and "review_closed" not in _fm(c) and _fm(c)["review_accepted"] == "x"
    assert "format 4" in (qdir / "README.md").read_text()


def test_memory_hits_fail_open_and_parse(monkeypatch):
    monkeypatch.setattr(quest.shutil, "which", lambda name: None)
    assert quest.memory_hits("anything") == []
    monkeypatch.setattr(quest.shutil, "which", lambda name: "/x/memory")
    class P: stdout = 'embedding failed: x\n[{"filename": "a.md", "summary": "A"}, {"filename": "b.md", "summary": "B"}]\n'
    monkeypatch.setattr(quest.subprocess, "run", lambda *a, **k: P())
    assert quest.memory_hits("q") == ["`memory read a.md` (A)", "`memory read b.md` (B)"]


def test_terminal_table_aligns():
    rows = [("2609041432-bb", "d", "quest", "active", "research", "New active"), ("2609011000-aa", "d", "chore", "backlog", "plan", "Old")]
    out = quest.terminal_table(rows).splitlines()
    assert out[0].startswith("Id             Kind   State    Stage     Title")
    assert out[2].startswith("2609041432-bb  quest  active   research  New active")


def test_pipe_in_title_is_escaped_in_the_log(tmp_path):
    qdir = tmp_path / "docs" / "quests"
    _make(qdir, "2609041432-bb", "Fix a | b")
    line = quest.log_lines(quest.load_quests(qdir))[0]
    assert "Fix a \\| b |" in line and line.count("|") == 7


def test_list_style_log_from_format_2_is_migrated(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    qdir = tmp_path / "docs" / "quests"
    _make(qdir, "2609011000-aa", "Open one", state="active", goal_closed="x")
    (qdir / "README.md").write_text("# Quest log\n\n<!-- questlog format 2, written by questlog old on 2026-09-04 -->\n\n- [2609011000-aa](2609011000-aa-open-one/) quest active research: Open one\n")
    quest.main(["log"]); capsys.readouterr()
    text = (qdir / "README.md").read_text()
    assert "format 4" in text and "| [2609011000-aa]" in text and _fm(qdir / "2609011000-aa-open-one")["goal_accepted"] == "x"
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert "quest log matches the directories" in capsys.readouterr().out


def test_symlinked_log_and_quest_are_refused(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    target = tmp_path / "victim.md"; target.write_text("precious\n")
    qdir = tmp_path / "docs" / "quests"; qdir.mkdir(parents=True)
    (qdir / "README.md").symlink_to(target)
    quest.main(["log"]); capsys.readouterr()          # reading never follows the link into a migration
    assert target.read_text() == "precious\n"
    with pytest.raises(SystemExit):                    # writing refuses it
        quest.main(["new", "Anything"])
    assert target.read_text() == "precious\n"
    (qdir / "README.md").unlink()
    (qdir / "README.md").write_text("Not our file\n")
    quest.main(["log"])                                   # unrecognised file: left alone, no migration
    assert (qdir / "README.md").read_text() == "Not our file\n"
    real = _make(qdir, "2609041432-bb", "Real"); link = qdir / "2609041433-cc-link"; link.symlink_to(real)
    assert [fm["id"] for _, fm in quest.load_quests(qdir)] == ["2609041432-bb"]


def test_multiline_title_is_one_log_line(tmp_path):
    qdir = tmp_path / "docs" / "quests"
    _make(qdir, "2609041432-bb", "First line\nsecond line")
    assert "\n" not in quest.log_lines(quest.load_quests(qdir))[0]


def test_complete_lists_finished_newest_first_bounded(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    qdir = tmp_path / "docs" / "quests"
    _make(qdir, "2609011000-aa", "Open")
    _make(qdir, "2609011001-bb", "Active", state="active")
    # ids say cc is older than dd, but cc finished later; the finish time wins
    _make(qdir, "2609011002-cc", "Later finish", state="completed", review_accepted="2026-09-05T03:03:00Z")
    _make(qdir, "2609011003-dd", "Earlier finish", kind="chore", state="completed", review_accepted="2026-09-05T03:00:00Z")
    _make(qdir, "2609011004-ee", "Dropped", state="abandoned", abandoned="2026-09-05T04:00:00Z", abandoned_reason="no")
    rows = quest.complete_rows(quest.load_quests(qdir))
    assert [r[0] for r in rows] == ["2609011002-cc", "2609011003-dd"]
    assert rows[0][4] == "2026-09-05" and rows[0][2] == "quest" and rows[1][2] == "chore"
    assert [r[0] for r in quest.complete_rows(quest.load_quests(qdir), include_abandoned=True)] == ["2609011004-ee", "2609011002-cc", "2609011003-dd"]
    assert [r[0] for r in quest.complete_rows(quest.load_quests(qdir), limit=1)] == ["2609011002-cc"]
    quest.main(["init"]); capsys.readouterr()
    quest.main(["complete", "--limit", "1"])
    out = capsys.readouterr().out.splitlines()
    assert out[0].split() == ["Id", "Kind", "State", "Finished", "Title"]
    assert len(out) == 3 and out[2].split() == ["2609011002-cc", "quest", "completed", "2026-09-05", "Later", "finish"]
    quest.main(["complete", "--all"])
    assert "Dropped" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        quest.main(["complete", "--limit", "0"])
    assert "at least 1" in capsys.readouterr().err


def test_complete_empty_and_log_unchanged(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    quest.main(["init"]); quest.main(["new", "Thing"]); capsys.readouterr()
    before = (tmp_path / "docs/quests/README.md").read_text()
    quest.main(["complete"])
    assert capsys.readouterr().out.strip() == "Nothing completed."
    assert (tmp_path / "docs/quests/README.md").read_text() == before   # read only


def test_draft_prompt_passes_over_skipped_research():
    fm = {"kind": "quest", "research_skipped": "x"}
    assert quest.stage_after(fm, "goal") == "design"


def test_draft_asks_iterate_or_move(tmp_path, capsys, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch, "Fix", chore=True)
    quest.main(["start", qid]); (d / "plan.md").write_text("# Plan\n"); capsys.readouterr()
    quest.main(["draft", qid, "plan"])
    assert "keep iterating on plan, or move to implement?" in capsys.readouterr().out
    quest.main(["next", qid]); quest.main(["next", qid]); capsys.readouterr()
    quest.main(["draft", qid, "review"])
    assert "whether the work is complete" in capsys.readouterr().out


def test_doctor_reports_old_format_and_fix_migrates_pages(tmp_path, monkeypatch, capsys):
    """doctor --fix used to stamp a new header without renaming the pages, which stranded them forever."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    qdir = tmp_path / "docs" / "quests"
    a = _make(qdir, "2609011000-aa", "At plan", state="active", goal_closed="x", research_skipped="x", design_closed="x")
    c = _make(qdir, "2609011001-cc", "Old done", kind="chore", state="done", plan_closed="x", implement_closed="x", review_closed="x")
    (qdir / "README.md").write_text("# Quest log\n\n<!-- questlog format 3, written by questlog old on 2026-09-04 -->\n")
    (tmp_path / "CLAUDE.md").write_text("## Quests <!-- questlog -->\n\nRun `quest close` when asked.\n")
    _git_commit_all(tmp_path)
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    out = capsys.readouterr().out
    assert e.value.code == 1
    assert "format 3 is older" in out and "2 quest.md files predate format 4" in out and "paragraph matches" in out
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor", "--fix"])
    out = capsys.readouterr().out
    assert e.value.code == 1 and "predate" not in out and "older" not in out      # only the CLAUDE.md wording is left, and that is a hand edit
    assert _fm(a)["design_accepted"] == "x" and "design_closed" not in _fm(a) and quest.current_stage(_fm(a)) == "plan"
    assert _fm(c)["state"] == "completed" and _fm(c)["review_accepted"] == "x"
    assert "format 4" in (qdir / "README.md").read_text()
    with pytest.raises(SystemExit):
        quest.main(["abandon", "2609011001-cc", "no"])           # completed stays terminal


def test_missing_log_still_renames_old_pages(tmp_path, monkeypatch, capsys):
    """With no log header the format is unknown, but the page contents say what they need."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    qdir = tmp_path / "docs" / "quests"
    a = _make(qdir, "2609011000-aa", "At plan", state="active", goal_closed="x", research_skipped="x", design_closed="x")
    quest.main(["new", "Fresh one"])
    assert "renamed pre-format-4 keys in 1 quest.md file" in capsys.readouterr().err
    assert _fm(a)["design_accepted"] == "x" and "design_closed" not in _fm(a)
    text = (qdir / "README.md").read_text()
    assert "format 4" in text and "| quest | active | plan | At plan |" in text


def test_done_page_that_escaped_migration_is_still_terminal(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    qdir = tmp_path / "docs" / "quests"
    _make(qdir, "2609011000-aa", "Old", state="done")
    (qdir / "README.md").write_text("Not our file\n")           # unrecognised log: no migration runs
    with pytest.raises(SystemExit):
        quest.main(["abandon", "2609011000-aa", "no"])
    assert _fm(qdir / "2609011000-aa-old")["state"] == "done"


def test_next_refuses_wrong_stage_undrafted_stage_and_repeats(tmp_path, monkeypatch, capsys):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    quest.main(["start", qid])
    with pytest.raises(SystemExit):          # goal has a file and was never drafted
        quest.main(["next", qid])
    assert "never drafted" in capsys.readouterr().err
    (d / "goal.md").write_text("# Goal\n"); quest.main(["draft", qid, "goal"])
    with pytest.raises(SystemExit):          # names a stage that is not current
        quest.main(["next", qid, "design"])
    assert "is at goal, not design" in capsys.readouterr().err
    quest.main(["next", qid, "goal"])
    assert quest.current_stage(_fm(d)) == "research"
    with pytest.raises(SystemExit):          # a repeat with the old stage is refused instead of accepting research
        quest.main(["next", qid, "goal"])
    assert "research_accepted" not in _fm(d)


def test_next_completes_in_one_write(tmp_path, monkeypatch):
    qdir, d, qid = _fresh(tmp_path, monkeypatch, "Fix", chore=True)
    quest.main(["start", qid]); (d / "plan.md").write_text("# Plan\n")
    quest.main(["draft", qid, "plan"]); quest.main(["next", qid]); quest.main(["next", qid])
    writes = []
    real = quest.update_quest
    def counting(*a, **k):
        writes.append(a)
        return real(*a, **k)
    monkeypatch.setattr(quest, "update_quest", counting)
    quest.main(["next", qid])
    assert len(writes) == 1
    fm = _fm(d)
    assert fm["state"] == "completed" and "None_accepted" not in fm
    with pytest.raises(SystemExit):
        quest.main(["next", qid])


def test_parse_page_normalizes_unquoted_stamps():
    """A hand-edited page may leave a stamp unquoted; YAML then yields a datetime or date. Every consumer must see the quoted form."""
    def page(line):
        return quest.parse_page(f"---\nid: x\n{line}\n---\nbody\n")[0]
    assert page("review_accepted: '2026-09-05T01:00:00Z'")["review_accepted"] == "2026-09-05T01:00:00Z"
    assert page("review_accepted: 2026-09-05T23:00:00Z")["review_accepted"] == "2026-09-05T23:00:00Z"
    assert page("abandoned: 2026-09-06T01:00:00+02:00")["abandoned"] == "2026-09-05T23:00:00Z"
    assert page("review_accepted: 2026-09-05T12:00:00")["review_accepted"] == "2026-09-05T12:00:00Z"
    assert page("review_accepted: 2026-09-04")["review_accepted"] == "2026-09-04T00:00:00Z"
    assert quest.finished_at(page("review_accepted: 2026-09-05T23:00:00Z")) > quest.finished_at(page("review_accepted: '2026-09-05T01:00:00Z'"))
    assert quest.finished_at({}) == ""


def test_unknown_kind_falls_back_to_quest_stages_everywhere():
    fm = {"id": "2609011000-aa", "kind": "epic", "state": "active"}
    assert quest.stages_for(fm) == quest.STAGES["quest"]
    assert quest.current_stage(fm) == "goal" and quest.stage_after(fm, "goal") == "research"
    with pytest.raises(SystemExit):
        quest.require_stage(fm, "plan", "draft")   # not current; must not raise KeyError


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
    assert e.value.code == 1 and "FAIL settings.json asks for every creator verb; missing: Bash(quest next *)  (quest init)" in capsys.readouterr().out
    quest.main(["init"]); capsys.readouterr()
    with pytest.raises(SystemExit) as e:
        quest.main(["doctor"])
    assert e.value.code == 0


REFERENCES = ROOT / "skills" / "quest" / "references"


def test_reference_files_exist_for_every_stage():
    for stage in quest.STAGES["quest"]:
        text = (REFERENCES / f"{stage}.md").read_text()
        assert text.strip(), stage
        assert "\n## Review\n" in text, f"{stage}.md has no Review section"


def test_review_sections_state_the_stop_rule():
    for stage in quest.STAGES["quest"]:
        text = (REFERENCES / f"{stage}.md").read_text()
        review = text[text.index("\n## Review\n"):].lower()
        for word in ("blocking", "clarification", "polish", "converged", "three passes", f"questlog:{quest.reviewer_for(stage)}", quest.record_for(stage)):
            assert word in review, f"{stage}.md Review section lacks {word}"


def test_agents_exist_with_required_frontmatter():
    """`claude plugin validate` warns and exits 0 on a malformed agent file, so this parse is the syntax check."""
    import yaml
    names = [quest.reviewer_for(stage) for stage in quest.STAGES["quest"]] + ["fact-finder"]
    assert "review-result" in names and "review-review" not in names
    assert quest.record_for("review") == "result-review.md" and quest.record_for("goal") == "goal-review.md"
    for name in names:
        text = (ROOT / "agents" / f"{name}.md").read_text()
        assert text.startswith("---\n"), name
        fm = yaml.safe_load(text[4:text.index("\n---\n", 4)])
        assert fm["name"] == name and fm["description"] and fm["model"], name
        for banned in ("hooks", "mcpServers", "permissionMode"):
            assert banned not in fm, f"{name}: plugin agents ignore {banned}"


def test_show_prints_guidance_paths(tmp_path, monkeypatch, capsys):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    capsys.readouterr()
    quest.main(["show", qid])
    out = capsys.readouterr().out
    assert f"guidance: {REFERENCES / 'goal.md'}" in out and "reviewer: questlog:review-goal" in out and "overlay:" not in out
    assert Path(out.split("guidance: ")[1].splitlines()[0]).is_file()
    quest.main(["start", qid])
    started = capsys.readouterr().out
    assert "reviewer: questlog:review-goal" in started and "overlay:" not in started
    overlay = qdir / "guidance" / "goal.md"
    overlay.parent.mkdir(); overlay.write_text("# Our goal rules\n")
    quest.main(["show", qid])
    assert f"overlay: {overlay}" in capsys.readouterr().out
    quest.main(["abandon", qid, "done with it"]); capsys.readouterr()
    quest.main(["show", qid])
    assert "guidance:" not in capsys.readouterr().out          # a finished entry, even one that still reports a stage


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


def test_draft_prints_last_verdict(tmp_path, monkeypatch, capsys):
    qdir, d, qid = _fresh(tmp_path, monkeypatch)
    quest.main(["start", qid])
    (d / "goal.md").write_text("# Goal\n"); capsys.readouterr()
    quest.main(["draft", qid, "goal"])
    assert "last verdict" not in capsys.readouterr().out
    (d / "goal-review.md").write_text("# Review record: goal\n\n## Pass 1\n\nVerdict: another pass\n\n## Pass 2\n\nVerdict: converged\n")
    quest.main(["draft", qid, "goal"])
    assert "last verdict: converged" in capsys.readouterr().out
