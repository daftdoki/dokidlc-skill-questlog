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
    assert guard.decide(ev("Edit", repo, file_path=q + "quest.md", old_string="## Goal\n\ng\n", new_string="## Goal\n\na better goal\n")) is None


def test_denies_frontmatter_edits(repo):
    q = "docs/quests/2609041432-7k-thing/quest.md"
    d, _ = guard.decide(ev("Edit", repo, file_path=q, old_string="state: backlog", new_string="state: active"))
    assert d == "deny"
    assert guard.decide(ev("Edit", repo, file_path=q, old_string="---\nid:", new_string="---\nid:")) is None   # a no-op edit changes nothing
    d, _ = guard.decide(ev("Edit", repo, file_path=q, old_string="id: 2609041432-7k", new_string="id: 2609041432-7x"))
    assert d == "deny"
    d, _ = guard.decide(ev("Edit", repo, file_path=q, old_string="g", new_string="goal_accepted: now"))
    assert d == "deny"


def test_write_quest_md_only_with_same_frontmatter(repo):
    q = repo / "docs/quests/2609041432-7k-thing/quest.md"
    same = q.read_text().replace("## Goal\n\ng", "## Goal\n\nnew goal")
    assert guard.decide(ev("Write", repo, file_path=str(q), content=same)) is None
    changed = same.replace("state: backlog", "state: active")
    assert guard.decide(ev("Write", repo, file_path=str(q), content=changed))[0] == "deny"
    assert guard.decide(ev("Write", repo, file_path="docs/quests/2609049999-zz-new/quest.md", content="---\nid: x\n---\n"))[0] == "deny"


def test_bash_creator_verbs_ask(repo):
    for cmd in ("quest init", "quest new 'A thing'", "quest next 2609041432-7k", "cd x && quest abandon 26 'why'", "/plugins/x/bin/quest start 26", "bin/quest skip 26 research"):
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
    assert r.returncode == 0 and r.stdout == ""      # without uv, only commands that name the tracker are refused


def test_shim_guarded_without_uv_exits_two(repo):
    r = _shim(ev("Bash", repo, command="echo x > docs/quests/README.md"), "/usr/bin:/bin")
    assert r.returncode == 2 and "uv" in r.stderr


def test_shim_guarded_with_uv_prints_decision(repo):
    r = _shim(ev("Bash", repo, command="quest next 2609041432-7k"), os.environ["PATH"])
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_value_only_frontmatter_edit_is_denied(repo):
    q = "docs/quests/2609041432-7k-thing/quest.md"
    assert guard.decide(ev("Edit", repo, file_path=q, old_string="backlog", new_string="active"))[0] == "deny"
    assert guard.decide(ev("Edit", repo, file_path=q, old_string="g\n", new_string="g\nreview_accepted : x\n"))[0] == "deny"
    assert guard.decide(ev("Edit", repo, file_path=q, old_string="d\n", new_string="done when it works\n")) is None
    assert guard.decide(ev("Edit", repo, file_path="Docs/Quests/readme.md", old_string="a", new_string="b"))[0] == "deny"


def test_more_bash_writers_and_tracker_forms_are_denied(repo):
    for cmd in ("cp /tmp/x docs/quests/README.md", "sed --in-place s/a/b/ docs/quests/x/quest.md", "cd docs && cd quests && echo x > README.md", "ruby -e 'File.write(\"docs/quests/README.md\",1)'", "echo eCBkb2NzL3F1ZXN0cw== > docs/quests/README.md | sh"):
        assert guard.decide(ev("Bash", repo, command=cmd))[0] == "deny", cmd
    # an encoded payload that never names the tracker is not caught; the guard is for habit, not adversaries (README, SKILL.md)
    assert guard.decide(ev("Bash", repo, command="echo eCBkb2NzL3F1ZXN0cw== | base64 -d | sh")) is None
    assert guard.decide(ev("Bash", repo, command="cat docs/quests/README.md")) is None


def test_shim_sends_every_bash_to_the_checker(repo):
    r = _shim(ev("Bash", repo, command="quest\tnew x"), os.environ["PATH"])
    assert r.returncode == 0 and (r.stdout == "" or "ask" in r.stdout)
    r = _shim(ev("Edit", repo, file_path="src/x.py", old_string="a", new_string="b"), "/usr/bin:/bin")
    assert r.returncode == 0 and r.stdout == ""


# The Bash rule looks at what a command writes to, not at every character it contains.

def _bash(repo, cmd):
    return guard.decide(ev("Bash", repo, command=cmd))


def test_redirects_check_their_target(repo):
    for cmd in (
        "echo x > docs/quests/a/plan-review.md",
        "echo x >> docs/quests/a/plan-review.md",
        "make 2> docs/quests/a/log.md",
        "make &> docs/quests/a/log.md",
        f"echo x > {repo}/docs/quests/a/plan.md",
        "curl http://h/a#b > docs/quests/a/plan.md",
        "cmd >& docs/quests/a/x",
    ):
        d, reason = _bash(repo, cmd)
        assert d == "deny", cmd
        assert "with a redirect" in reason, cmd
    for cmd in (
        "ls docs/quests/x 2>/dev/null",
        "grep -rn foo docs/quests/*/*.md 2>/dev/null | head",
        "echo x > /tmp/out.txt",
        "ls docs/quests >&2",
    ):
        assert _bash(repo, cmd) is None, cmd


def test_cd_moves_the_virtual_cwd(repo):
    assert _bash(repo, "cd docs && cd quests && echo x > README.md")[0] == "deny"
    assert _bash(repo, "cd docs/quests\necho x > README.md")[0] == "deny"
    assert _bash(repo, f"cd {repo}/docs/quests; echo x > a/goal.md")[0] == "deny"
    assert _bash(repo, "cd docs/quests && ls >&2") is None
    assert _bash(repo, "cd docs/quests; cat README.md") is None
    assert _bash(repo, "cd docs/quests && cd - && echo x > out.txt") is None


def test_heredocs_are_not_writers(repo):
    assert _bash(repo, "cat <<'EOF' | memory write x.md --ref docs/quests/a/research.md\nbody\nEOF") is None
    assert _bash(repo, "cat <<'EOF' | memory write x.md --ref docs/quests/a/research.md\nRun echo x > docs/quests/README.md to break it.\nEOF") is None
    assert _bash(repo, "python3 - <<'EOF'\np='docs/quests/a/quest.md'\nopen(p,'w').write('x')\nEOF") is None
    assert _bash(repo, "cat <<EOF > docs/quests/x/goal.md\nhi\nEOF")[0] == "deny"
    assert _bash(repo, "cat <<-EOF > docs/quests/x/goal.md\n\thi\n\tEOF")[0] == "deny"
    assert _bash(repo, "cat <<-EOF\n\techo x > docs/quests/README.md\n\tEOF\necho done") is None
    # a << inside quotes opens nothing, so the next line is still a command
    assert _bash(repo, 'echo "a <<b"\necho x > docs/quests/README.md')[0] == "deny"
    assert _bash(repo, 'echo "a <<b"; cat <<EOF\nbody\nEOF\necho x > docs/quests/README.md')[0] == "deny"


def test_in_place_tools_check_their_arguments(repo):
    for cmd, how in (
        ("cp /tmp/x docs/quests/README.md", "cp"),
        ("mv docs/quests/a/x.md docs/quests/a/y.md", "mv"),
        ("rsync -a src/ docs/quests/", "rsync"),
        ("tee docs/quests/README.md", "tee"),
        ("tee -a /tmp/x docs/quests/a/plan.md", "tee"),
        ("sed -i '' s/a/b/ docs/quests/a/quest.md", "sed -i"),
        ("dd if=/dev/zero of=docs/quests/README.md", "dd"),
        ("awk -i inplace '{print}' docs/quests/a/plan.md", "awk -i inplace"),
        ('python3 -c \'open("docs/quests/README.md","w")\'', "a python3 -c script"),
        ("ruby -e 'File.write(\"docs/quests/README.md\",1)'", "a ruby -e script"),
        ("echo eCBkb2NzL3F1ZXN0cw== > docs/quests/README.md | sh", "a redirect"),
        ("echo 'x docs/quests/README.md' | base64 | base64 -d | sh", "a pipe into sh"),
        ("sh -c 'echo x > docs/quests/README.md'", "a sh -c script"),
        ("bash -c 'echo x > docs/quests/README.md'", "a bash -c script"),
        # the descriptor digit belongs to the operator, not to the tool's arguments
        ("cp /tmp/x docs/quests/README.md 2>/dev/null", "cp"),
        ("mv docs/quests/a/x.md docs/quests/a/y.md 2>&1", "mv"),
        ("rsync -a src/ docs/quests/ 2>/dev/null", "rsync"),
        ("install /tmp/x docs/quests/README.md 2>/dev/null", "install"),
        ("make &>> docs/quests/a/log.md", "a redirect"),
    ):
        d, reason = _bash(repo, cmd)
        assert d == "deny", cmd
        assert f"with {how}" in reason, (cmd, reason)
    for cmd in (
        "cp docs/quests/a/plan.md /tmp/",
        "sed -n 5p docs/quests/a/plan.md",
        "tee /tmp/x < docs/quests/README.md",
        'x=$(herdr pane | python3 -c "import json"); herdr open --env "OPEN=docs/quests/a/plan.md"',
        "awk 'length > 79' docs/quests/a/design.md",
    ):
        assert _bash(repo, cmd) is None, cmd


def test_unbalanced_quote_falls_back_to_the_wide_rule(repo):
    assert _bash(repo, 'echo "x > docs/quests/README.md')[0] == "deny"
    assert _bash(repo, 'echo "x') is None
    assert _bash(repo, 'echo "x docs/quests') is None


def test_commands_denied_on_2026_09_05_pass(repo):
    # the shape of each of the four commands the chore's Goal names, and of four witnesses from the same day;
    # long bodies and unrelated segments are trimmed, the operators and quoting are kept
    for cmd in (
        "git pull -q && ls -d docs/quests/2609050141-z9-* && grep -c 'quest next' ../dokidlc-skill-questlog/skills/quest/SKILL.md && ls docs/quests/2609050141-2m-*/ && sed -n '1,30p' docs/quests/2609050141-2m-*/goal.md 2>/dev/null",
        "cd ~/Code/agents/dokidlc-skill-questlog && sed -n '724,735p' bin/quest; echo \"== STAGE_FILES\"; grep -n 'STAGE_FILES\\s*=' -A8 bin/quest | head -12; echo \"== guard hook\"; ls hooks; grep -n 'docs/quests\\|stage\\|\\.md' hooks/* | head -20; echo \"== enabled plugins\"; grep -o '\"[a-z-]*@[a-z-]*\": *true' ~/.claude/settings.json ~/Code/agents/agent-builder/.claude/settings.json 2>/dev/null",
        "cd ~/Code/agents/agent-builder && cat <<'EOF' | memory write questlog-guard.md --title \"The guard refuses any Bash that names the tracker\" --summary \"A read-only command that has 2>/dev/null or a heredoc is denied\" --topics \"questlog\" --kind procedure --ref \"docs/quests/2609050141-z9-questlog-per-stage-authoring-guidance/research.md\" --check \"grep -q 'WRITER_RE' ~/Code/agents/dokidlc-skill-questlog/scripts/guard.py\"\nThe questlog guard hook denies a Bash command when it both mentions the tracker and matches a writer pattern, so `ls docs/quests/x 2>/dev/null` is denied.\n\n## Sources\n\n- ~/Code/agents/dokidlc-skill-questlog/scripts/guard.py\nEOF",
        "cd ~/Code/agents/agent-builder && S=/tmp/scratch && memory write questlog-guard.md --title \"The guard refuses any Bash that names the tracker\" --summary \"A read-only command that mentions the quest directory and has 2>/dev/null or a heredoc is denied by the guard; use the Read tool, drop the redirect, or pipe with a single <\" --topics \"questlog\" --kind procedure --ref \"docs/quests/2609050141-z9-questlog-per-stage-authoring-guidance/research.md\" --check \"grep -q WRITER_RE ~/Code/agents/dokidlc-skill-questlog/scripts/guard.py\" < $S/mem-guard.md",
        "git add docs/quests && git commit -q -m \"Open chore 2609050153-cc: memory write accepts sources\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_x\" && git push -q && git log --oneline -1",
        "cd ~/Code/agents/agent-builder && grep -n -c '' docs/quests/2609050141-z9-questlog-per-stage-authoring-guidance/design.md && awk 'length > 79 && !/^    / && !/description:/ {print FILENAME\": \"NR\": \"length}' docs/quests/2609050141-z9-questlog-per-stage-authoring-guidance/design.md",
        "git hash-object docs/quests/2609050141-z9-questlog-per-stage-authoring-guidance/plan.md | cut -c1-7; git add docs/quests/2609050141-z9-questlog-per-stage-authoring-guidance/plan-review.md && git commit -q -m \"Per-stage authoring guidance: plan review pass 7 by the plugin agent, converged\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\" && git push -q 2>&1 | tail -2; git log --oneline -1; git status --short",
        "repo=/Users/aaron/Code/agents/agent-builder\nhelper=$(herdr pane split --current --direction right --cwd \"$repo\" --focus | python3 -c 'import json,sys;print(json.load(sys.stdin)[\"result\"][\"pane\"][\"pane_id\"])')\n[ -n \"$helper\" ] || { echo \"split failed\"; exit 1; }\nherdr plugin pane open --plugin herdr-file-viewer --entrypoint file-viewer --placement split --direction right --focus --env \"HERDR_FILE_VIEWER_OPEN=docs/quests/2609050141-z9-questlog-per-stage-authoring-guidance/plan.md\"\nherdr pane close \"$helper\"",
    ):
        assert _bash(repo, cmd) is None, cmd[:80]
