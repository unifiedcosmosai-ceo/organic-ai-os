"""Tests fuer die Observability-Endpoint-Metriken (v6, Layer 12 ops)."""
import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from observability import EndpointMetrics, MetricsRegistry, timed_call


def test_record_increments_calls():
    m = EndpointMetrics("a")
    m.record(10.0, ok=True)
    m.record(20.0, ok=False)
    assert m.calls == 2
    assert m.errors == 1


def test_error_rate():
    m = EndpointMetrics("a")
    m.record(5.0, ok=True)
    m.record(5.0, ok=False)
    assert m.to_dict()["error_rate"] == pytest.approx(0.5)


def test_avg_ms():
    m = EndpointMetrics("a")
    m.record(10.0, ok=True)
    m.record(30.0, ok=True)
    assert m.to_dict()["avg_ms"] == pytest.approx(20.0)


def test_registry_summary_totals():
    reg = MetricsRegistry()
    reg.record("/x", 10.0, ok=True)
    reg.record("/x", 10.0, ok=False)
    reg.record("/y", 5.0, ok=True)
    s = reg.summary()
    assert s["total_calls"] == 3
    assert s["total_errors"] == 1
    assert len(s["endpoints"]) == 2


def test_registry_save_load_roundtrip(tmp_path):
    reg = MetricsRegistry(tmp_path / "metrics.json")
    reg.record("/x", 20.0, ok=True)
    reg.record("/x", 40.0, ok=False)
    reg.save()

    reg2 = MetricsRegistry(tmp_path / "metrics.json")
    reg2.load()
    s = reg2.summary()
    assert s["total_calls"] == 2
    assert s["total_errors"] == 1
    assert s["endpoints"][0]["avg_ms"] == pytest.approx(30.0)


def test_registry_load_missing_is_empty(tmp_path):
    reg = MetricsRegistry(tmp_path / "nope.json")
    reg.load()
    assert reg.summary() == {"endpoints": [], "total_calls": 0, "total_errors": 0}


def test_timed_call_records_latency():
    from observability import get_registry
    before = len(get_registry().metrics)
    timed_call(lambda: 1 + 1)
    assert len(get_registry().metrics) == before + 1
    assert "lambda" in get_registry().metrics


def test_to_dict_shape():
    m = EndpointMetrics("/x")
    m.record(1.0, ok=True)
    d = m.to_dict()
    assert set(d) == {"endpoint", "calls", "errors", "error_rate",
                      "total_ms", "avg_ms"}