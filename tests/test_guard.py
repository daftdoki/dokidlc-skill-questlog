"""Tests for the guard shim and checker. The checker is fed JSON directly."""

import importlib.util
import json
import os
import subprocess
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_loader = SourceFileLoader("guard", str(ROOT / "scripts" / "guard.py"))
_spec = importlib.util.spec_from_loader("guard", _loader)
guard = importlib.util.module_from_spec(_spec)
_loader.exec_module(guard)


def ev(tool, cwd, **tool_input):
    return {"tool_name": tool, "tool_input": tool_input, "cwd": str(cwd)}


@pytest.fixture
def repo(tmp_path):
    d = tmp_path / "docs" / "quests" / "2609041432-7k-thing"
    d.mkdir(parents=True)
    (d / "quest.md").write_text("---\nid: 2609041432-7k\ntitle: Thing\nkind: quest\nstate: backlog\ncreated: '2026-09-04T14:32:00Z'\n---\n## Goal\n\ng\n\n## Done when\n\nd\n")
    (tmp_path / "docs" / "quests" / "README.md").write_text("# Quest log\n")
    return tmp_path


def test_allows_unrelated_edits(repo):
    assert guard.decide(ev("Edit", repo, file_path=str(repo / "src/x.py"), old_string="a", new_string="b")) is None
    assert guard.decide(ev("Write", repo, file_path="README.md", content="hi")) is None
    assert guard.decide(ev("Bash", repo, command="ls docs/quests")) is None
    assert guard.decide(ev("Bash", repo, command="git status")) is None


def test_denies_quest_log_edits(repo):
    d, reason = guard.decide(ev("Edit", repo, file_path="docs/quests/README.md", old_string="a", new_string="b"))
    assert d == "deny" and "generated" in reason
    d, _ = guard.decide(ev("Write", repo, file_path=str(repo / "docs/quests/README.md"), content="x"))
    assert d == "deny"


def test_allows_stage_files_and_quest_body(repo):
    q = "docs/quests/2609041432-7k-thing/"
    assert guard.decide(ev("Write", repo, file_path=q + "goal.md", content="# Goal\n")) is None
    assert guard.decide(ev("Edit", repo, file_path=q + "quest.md", old_string="g\n", new_string="a better goal\n")) is None


def test_denies_frontmatter_edits(repo):
    q = "docs/quests/2609041432-7k-thing/quest.md"
    d, _ = guard.decide(ev("Edit", repo, file_path=q, old_string="state: backlog", new_string="state: active"))
    assert d == "deny"
    d, _ = guard.decide(ev("Edit", repo, file_path=q, old_string="---\nid:", new_string="---\nid:"))
    assert d == "deny"
    d, _ = guard.decide(ev("Edit", repo, file_path=q, old_string="g", new_string="goal_closed: now"))
    assert d == "deny"


def test_write_quest_md_only_with_same_frontmatter(repo):
    q = repo / "docs/quests/2609041432-7k-thing/quest.md"
    same = q.read_text().replace("## Goal\n\ng", "## Goal\n\nnew goal")
    assert guard.decide(ev("Write", repo, file_path=str(q), content=same)) is None
    changed = same.replace("state: backlog", "state: active")
    assert guard.decide(ev("Write", repo, file_path=str(q), content=changed))[0] == "deny"
    assert guard.decide(ev("Write", repo, file_path="docs/quests/2609049999-zz-new/quest.md", content="---\nid: x\n---\n"))[0] == "deny"


def test_bash_creator_verbs_ask(repo):
    for cmd in ("quest init", "quest new 'A thing'", "quest close 2609041432-7k goal", "cd x && quest abandon 26 'why'", "/plugins/x/bin/quest start 26", "bin/quest skip 26 research"):
        d, reason = guard.decide(ev("Bash", repo, command=cmd))
        assert d == "ask", cmd
        assert cmd.strip() in reason


def test_bash_agent_verbs_allowed(repo):
    for cmd in ("quest log", "quest show 2609", "quest draft 2609041432-7k goal", "quest doctor", "request new thing"):
        assert guard.decide(ev("Bash", repo, command=cmd)) is None, cmd


def test_bash_writers_into_tracker_denied(repo):
    for cmd in ("echo x > docs/quests/README.md", "sed -i '' 's/a/b/' docs/quests/2609041432-7k-thing/quest.md", "cat <<EOF > docs/quests/x/goal.md\nhi\nEOF", "python3 -c 'open(\"docs/quests/README.md\",\"w\")'", "tee docs/quests/README.md"):
        d, _ = guard.decide(ev("Bash", repo, command=cmd))
        assert d == "deny", cmd
    assert guard.decide(ev("Bash", repo, command="cat docs/quests/README.md")) is None
    assert guard.decide(ev("Bash", repo, command="grep -r state docs/quests/ | sort")) is None
    assert guard.decide(ev("Bash", repo, command="echo x > /tmp/out.txt")) is None


def _shim(event, path_env):
    return subprocess.run(["sh", str(ROOT / "scripts" / "guard.sh")], input=json.dumps(event), capture_output=True, text=True, env={**os.environ, "PATH": path_env})


def test_shim_unrelated_exits_zero_without_uv(repo):
    r = _shim(ev("Bash", repo, command="git status"), "/usr/bin:/bin")
    assert r.returncode == 0 and r.stdout == ""


def test_shim_guarded_without_uv_exits_two(repo):
    r = _shim(ev("Bash", repo, command="echo x > docs/quests/README.md"), "/usr/bin:/bin")
    assert r.returncode == 2 and "uv" in r.stderr


def test_shim_guarded_with_uv_prints_decision(repo):
    r = _shim(ev("Bash", repo, command="quest close 2609041432-7k goal"), os.environ["PATH"])
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"
