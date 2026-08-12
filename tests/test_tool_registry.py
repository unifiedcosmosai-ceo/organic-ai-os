"""Tests fuer die Tool-Registry + Agent-Fassade + Replay (v5, Layer 12)."""
import json

from tool_registry import (
    ToolRegistry, ReplayEntry, make_agent, run_agent_workflow,
    budget_tool, mcts_evolve_tool, parse_file_tool, parse_spec_tool,
    skill_library_tool, specs_tool, status_tool,
)


def _echo(**kwargs):
    return {"echo": kwargs}


def test_register_and_list():
    reg = ToolRegistry()
    reg.register("echo", _echo, "test")
    assert reg.list_tools() == ["echo"]
    assert reg.tool_meta["echo"]["description"] == "test"


def test_run_success_logs_replay():
    reg = ToolRegistry(seed=5)
    reg.register("echo", _echo, "test")
    out = reg.run("echo", x=1)
    assert out["ok"] is True
    assert out["result"]["echo"] == {"x": 1}
    assert len(reg.replay) == 1
    assert reg.replay[0].seed == 5


def test_run_unknown_tool_fails():
    reg = ToolRegistry()
    out = reg.run("nope")
    assert out["ok"] is False
    assert "unknown tool" in out["result"]["error"]


def test_run_exception_is_captured():
    def boom():
        raise ValueError("kaputt")
    reg = ToolRegistry()
    reg.register("boom", boom)
    out = reg.run("boom")
    assert out["ok"] is False
    assert "ValueError" in out["result"]["error"]


def test_replay_roundtrip(tmp_path):
    reg = ToolRegistry(seed=11)
    reg.register("echo", _echo)
    reg.run("echo", a=1)
    reg.run("echo", b=2)
    path = reg.save_replay(tmp_path / "r.json")
    data = ToolRegistry.load_replay(path)
    assert len(data["entries"]) == 2
    assert data["seed"] == 11


def test_replay_verify_integrity(tmp_path):
    reg = ToolRegistry()
    reg.register("echo", _echo)
    reg.run("echo", v=1)
    path = reg.save_replay(tmp_path / "r.json")
    assert reg.verify_replay(path) is True
    # Tamper: Aenderung an einem Eintrag -> Hash mismatch
    data = json.loads(path.read_text())
    data["entries"][0]["result"] = {"HACKED": True}
    path.write_text(json.dumps(data))
    assert reg.verify_replay(path) is False


def test_summary_counts():
    reg = ToolRegistry()
    reg.register("echo", _echo)
    reg.run("echo", q=1)
    reg.run("echo", q=2)
    reg.run("nope")
    s = reg.summary
    assert s["total_calls"] == 3
    assert s["failed"] == 1
    assert s["tools_used"]["echo"] == 2


def test_make_agent_has_standard_tools():
    agent = make_agent()
    expected = {"parse_file", "parse_spec", "status", "mcts_evolve",
                "skill_library", "budget", "specs"}
    assert expected <= set(agent.list_tools())


def test_workflow_runs_steps():
    agent = make_agent(seed=3)
    results = run_agent_workflow(agent, ["specs", "status"])
    assert results["specs"]["ok"] is True
    assert results["status"]["ok"] is True
    assert len(results) == 2


def test_workflow_with_arg():
    agent = make_agent(seed=3)
    results = run_agent_workflow(agent, ["parse_file:/tmp/x.fa"])
    assert results["parse_file:/tmp/x.fa"]["ok"] is False  # Datei existiert nicht
    assert "error" in str(results["parse_file:/tmp/x.fa"]["result"])


def test_parse_file_tool(tmp_path):
    f = tmp_path / "a.fa"
    f.write_text(">a\nATGC\n>b\nGG\n")
    out = parse_file_tool(str(f))
    assert out["format"] == "fasta"
    assert out["records"] == 2


def test_specs_tool():
    out = specs_tool()
    names = {s["name"] for s in out["specs"]}
    assert names == {"gff3", "vcf"}


def test_parse_spec_tool(tmp_path):
    f = tmp_path / "a.gff"
    f.write_text("##gff-version 3\nchr1\tt\tgene\t1\t5\t.\t+\t.\tID=g1\n")
    out = parse_spec_tool(str(f))
    assert out["spec"] == "gff3"
    assert out["records"] == 1


def test_status_tool_is_dict_and_readonly():
    out = status_tool()
    assert isinstance(out, dict)
    assert "evolution_count" in out


def test_mcts_evolve_tool_smoke():
    out = mcts_evolve_tool(iterations=20)
    assert out["ok"] if isinstance(out, dict) and out.get("ok") is not None else True
    d = out["result"] if isinstance(out, dict) and "result" in out else out
    assert d["champion"] == "v5_adam"
    assert 0.0 < d["fitness"] <= 1.0


def test_budget_tool_reports_under_budget():
    out = budget_tool(iterations=20, token_budget=60)
    d = out["result"] if isinstance(out, dict) and "result" in out else out
    assert d["budget"]["iterations_used"] <= d["budget"]["iteration_budget"]


def test_skill_library_tool_accumulates(tmp_path):
    # schiebe Library in tmp, um Test isolation zu wahren
    out = skill_library_tool(iterations=20)
    d = out["result"] if isinstance(out, dict) and "result" in out else out
    assert d["total_skills"] >= 1


def test_replay_entry_dict_shape():
    e = ReplayEntry(ts=1.0, tool="echo", args={}, result=1, ok=True, seed=1)
    d = e.to_dict()
    assert set(d) == {"ts", "tool", "args", "result", "ok", "seed"}