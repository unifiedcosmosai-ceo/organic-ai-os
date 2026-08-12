"""Tests fuer mRNA-Provenienz + Neuro-Cortex-Persistenz (v6, Layer 09)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "09_neuro"))

from provenance import ProvenanceTracker
from cortex_persist import snapshot_population, load_snapshots


def test_record_creates_event():
    t = ProvenanceTracker()
    ev = t.record("adam", "adam_g1", "insert", 0, 0.5, "Schreibe")
    assert ev.parent == "adam"
    assert ev.child == "adam_g1"
    assert ev.strategy == "insert"


def test_record_appends_to_events():
    t = ProvenanceTracker()
    t.record("a", "b", "point", 0, 0.0, "")
    t.record("b", "c", "role", 1, 0.1, "")
    assert len(t.events) == 2


def test_query_by_name_parent_and_child():
    t = ProvenanceTracker()
    t.record("adam", "adam_g1", "point", 0, 0.0, "x")
    t.record("adam", "adam_g2", "role", 1, 0.2, "y")
    t.record("other", "foo", "cot", 0, 0.0, "z")
    assert len(t.query(name="adam")) == 2
    assert len(t.query(name="adam_g1")) == 1
    assert len(t.query(name="adam_g2")) == 1


def test_query_by_strategy():
    t = ProvenanceTracker()
    t.record("a", "b", "insert", 0, 0.0, "")
    t.record("a", "c", "insert", 1, 0.0, "")
    t.record("a", "d", "delete", 2, 0.0, "")
    assert len(t.query(strategy="insert")) == 2


def test_summary_by_strategy_and_last():
    t = ProvenanceTracker()
    t.record("a", "b", "point", 0, 0.0, "")
    t.record("a", "c", "role", 1, 0.0, "")
    s = t.summary()
    assert s["events"] == 2
    assert s["by_strategy"] == {"point": 1, "role": 1}
    assert s["last"]["child"] == "c"


def test_cap_limits_events():
    t = ProvenanceTracker(cap=3)
    for i in range(10):
        t.record(f"p{i}", f"c{i}", "point", i, 1.0, "")
    assert len(t.events) == 3
    assert t.events[0].child == "c7"


def test_save_load_roundtrip(tmp_path):
    p = tmp_path / "prov.json"
    t = ProvenanceTracker(path=p)
    t.record("adam", "adam_g1", "insert", 0, 0.5, "hi")
    t.save()
    t2 = ProvenanceTracker(path=p)
    t2.load()
    assert len(t2.events) == 1
    assert t2.events[0].strategy == "insert"


def test_load_missing_is_empty(tmp_path):
    t = ProvenanceTracker(path=tmp_path / "none.json")
    t.load()
    assert t.events == []


def test_snapshot_population_shape(tmp_path):
    p = tmp_path / "snap.json"
    pop = [FakeStrand("best", "Schreibe", 0.9, 1, 6),
           FakeStrand("other", "Mach", 0.6, 0, 4)]
    data = snapshot_population(pop, 1, path=p)
    assert data["generation"] == 1
    assert data["best"]["name"] == "best"
    assert len(data["population"]) == 2


def test_snapshot_population_appends(tmp_path):
    p = tmp_path / "snap.json"
    s1 = snapshot_population([FakeStrand("a", "p1", 0.5, 0, 3)], 0, path=p)
    s2 = snapshot_population([FakeStrand("b", "p2", 0.8, 1, 4)], 1, path=p)
    assert load_snapshots(p) == [s1, s2]


def test_load_snapshots_missing_is_empty(tmp_path):
    assert load_snapshots(tmp_path / "none.json") == []


class FakeStrand:
    def __init__(self, name, prompt_template, fitness, generation, tokens):
        self.name = name
        self.prompt_template = prompt_template
        self.fitness = fitness
        self.generation = generation
        self.tokens = tokens