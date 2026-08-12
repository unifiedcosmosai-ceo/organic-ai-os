"""Tests fuer die Fitness-Fruehwarnung (v6, Layer 11)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "11_evolution"))

from fitness_guard import FitnessGuard


def _guard(tmp_path):
    g = FitnessGuard(path=tmp_path / "fitness_guard.json", drop_threshold=0.05)
    g.load()
    return g


def test_first_candidate_promoted(tmp_path):
    g = _guard(tmp_path)
    res = g.check_candidate("adam", 0.8)
    assert res["decision"] == "promote"
    assert res["reason"] == "new-best"
    assert g.best == 0.8


def test_improvement_promoted(tmp_path):
    g = _guard(tmp_path)
    g.check_candidate("a", 0.8)
    res = g.check_candidate("b", 0.9, baseline=0.8)
    assert res["decision"] == "promote"


def test_small_decline_held(tmp_path):
    g = _guard(tmp_path)
    g.check_candidate("a", 0.8)
    res = g.check_candidate("b", 0.79, baseline=0.8)
    assert res["decision"] == "hold"
    assert res["reason"] == "below-baseline"


def test_big_drop_rejected_and_alarm(tmp_path):
    g = _guard(tmp_path)
    g.check_candidate("a", 0.8)
    res = g.check_candidate("b", 0.6, baseline=0.8)
    assert res["decision"] == "reject"
    assert res["reason"] == "score-drop"
    assert g.alarms == 1


def test_lethal_rejected(tmp_path):
    g = _guard(tmp_path)
    res = g.check_candidate("dead", 0.0, baseline=0.8)
    assert res["decision"] == "reject"
    assert res["reason"] == "lethal"


def test_allows_promotion_flag(tmp_path):
    g = _guard(tmp_path)
    assert g.allows_promotion("a", 0.8) is True
    assert g.allows_promotion("b", 0.7, baseline=0.8) is False


def test_persistence_roundtrip(tmp_path):
    g = _guard(tmp_path)
    g.check_candidate("a", 0.8)
    g.check_candidate("b", 0.6, baseline=0.8)
    g2 = FitnessGuard(path=tmp_path / "fitness_guard.json")
    g2.load()
    assert g2.best == 0.8
    assert g2.alarms == 1
    assert len(g2.history) == 2


def test_summary_shape(tmp_path):
    g = _guard(tmp_path)
    g.check_candidate("a", 0.8)
    s = g.summary()
    assert set(s) == {"best", "alarms", "checks", "last"}
    assert s["best"] == 0.8
    assert s["checks"] == 1
