"""Integrationstests fuer v6 Phase B: API-Endpoints, Tools, Neuro/Symbiom-Hooks."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "09_neuro"))
sys.path.insert(0, str(ROOT / "10_symbiom"))

from fastapi.testclient import TestClient
from api_server import app

from tool_registry import (
    make_agent, stream_tool, kmer_tool, metrics_tool, vote_tool,
)
from provenance import ProvenanceTracker
from voting import swarm_vote

client = TestClient(app)


def test_metrics_endpoint_shape():
    r = client.get("/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "endpoints" in data and "total_calls" in data
    assert "total_errors" in data


def test_webhooks_get_status():
    r = client.get("/webhooks")
    assert r.status_code == 200
    body = r.json()
    assert "hooks" in body and "sent" in body


def test_webhooks_test_post():
    r = client.post("/webhooks/test", json={"event": "test", "payload": {"k": 1}})
    assert r.status_code == 200
    body = r.json()
    assert body["event"] == "test"
    assert "targets" in body


def test_provenance_endpoint_empty():
    r = client.get("/provenance")
    assert r.status_code == 200
    body = r.json()
    assert "summary" in body and "events" in body


def test_provenance_endpoint_filters(tmp_path):
    t = ProvenanceTracker(path=tmp_path / "p.json")
    t.record("adam", "adam_g1", "insert", 0, 0.5, "hi")
    assert len(t.query(strategy="insert")) == 1
    assert len(t.query(name="adam")) == 1


def test_stream_tool(tmp_path):
    f = tmp_path / "reads.fa"
    f.write_text(">a\nATGC\n>b\nGG\n")
    out = stream_tool(str(f))
    assert out["records"] == 2
    assert out["head"][0]["header"] == "a"


def test_kmer_tool(tmp_path):
    f = tmp_path / "reads.fa"
    f.write_text(">a\nAAAATTTT\n")
    out = kmer_tool(str(f), k=3, top=2)
    assert out["k"] == 3
    assert out["records"] == 1
    assert out["top"][0][0] == "AAA"


def test_metrics_tool():
    out = metrics_tool()
    assert "endpoints" in out and "total_calls" in out


def test_vote_tool():
    out = vote_tool()
    assert "consensus" in out
    assert out["total_tests"] == 2


def test_agent_has_phase_b_tools():
    agent = make_agent()
    names = set(agent.list_tools())
    assert {"stream", "kmers", "webhook", "metrics", "provenance", "vote"} <= names


def test_agent_webhook_tool_returns_entry(monkeypatch):
    import webhook_out

    def _fake_ok(request, timeout=None):
        class R:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        return R()

    monkeypatch.setattr(webhook_out.urllib.request, "urlopen", _fake_ok)
    from tool_registry import webhook_tool

    out = webhook_tool(event="alarm", payload={"f": 0.1}, url="http://hook.test/x")
    assert out["event"] == "alarm"
    assert out["targets"] == 1
    assert out["results"][0]["ok"] is True


def test_neuro_mutation_records_provenance():
    from neuro_evolving import NeuroMutator, PromptStrand
    from provenance import get_provenance

    get_provenance().events.clear()
    m = NeuroMutator()
    parent = PromptStrand(name="adam", prompt_template="Schreibe parse_fasta.",
                          fitness=0.5)
    child = m.mutate(parent, strategy="insert")
    assert len(get_provenance().events) == 1
    ev = get_provenance().events[-1]
    assert ev.strategy == "insert"
    assert ev.parent == "adam"
    assert ev.child == child.name


def test_symbiom_ensemble_score():
    import symbiom_swarm

    swarm = symbiom_swarm.SymbiomSwarm(population_per_species=2)
    seed_code = """
def parse_fasta(text):
    records={}
    h=None
    for line in text.splitlines():
        s=line.strip()
        if not s: continue
        if s.startswith(">"):
            h=s[1:].split()[0]
            records[h]=""
        else:
            records[h]=records.get(h,"")+s.upper()
    return records
"""
    swarm.seed(seed_code)

    def t_parse(ns):
        try:
            return len(ns["parse_fasta"](">a\nATGC\n>b\nGG\n")) == 2
        except Exception:
            return False

    def t_messy(ns):
        try:
            r = ns["parse_fasta"](">h x\n  atgc  \n")
            return len(r) == 1 and " " not in r["h"]
        except Exception:
            return False

    vote = swarm.ensemble_score([(t_parse, 0.6), (t_messy, 0.4)])
    assert vote["total_tests"] == 2
    assert vote["passed_tests"] >= 1


def test_swarm_vote_importable_and_usable():
    res = swarm_vote({"basic": [True, True], "edges": [False, False]})
    assert res["passed_tests"] == 1