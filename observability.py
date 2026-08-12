"""
LAYER 12 OPS: OBSERVABILITY (v6)
Distributed-Tracing-lite: Latenz + Fehlerrate je API-Endpoint.
Ein MetricsRegistry-Singleton wird von der FastAPI-Middleware befuellt
und ist via GET /metrics sowie als Tool/CLI abfragbar.

Grundlage der Idee: Telemetrie-Daten (Jaeger/OpenTelemetry) reduzieren
auf das Minimum, das fuer einen autonomen Organismus noetig ist.
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

DEFAULT_PATH = Path("memory") / "metrics.json"


@dataclass
class EndpointMetrics:
    endpoint: str
    calls: int = 0
    errors: int = 0
    total_ms: float = 0.0

    def record(self, ms: float, ok: bool):
        self.calls += 1
        self.total_ms += ms
        if not ok:
            self.errors += 1

    def to_dict(self) -> dict:
        return {"endpoint": self.endpoint, "calls": self.calls,
                "errors": self.errors,
                "error_rate": round(self.errors / self.calls, 3) if self.calls else 0.0,
                "total_ms": round(self.total_ms, 2),
                "avg_ms": round(self.total_ms / self.calls, 2) if self.calls else 0.0}

    @classmethod
    def from_dict(cls, data: dict) -> "EndpointMetrics":
        m = cls(data["endpoint"])
        m.calls = data.get("calls", 0)
        m.errors = data.get("errors", 0)
        m.total_ms = float(data.get("total_ms", 0))
        return m


class MetricsRegistry:
    """Erfasst Latenz/Fehler pro Endpoint und kann persistiert werden."""

    def __init__(self, path: Path = DEFAULT_PATH):
        self.path = path
        self.metrics: Dict[str, EndpointMetrics] = {}

    def record(self, endpoint, ms: float, ok: bool = True):
        m = self.metrics.setdefault(endpoint, EndpointMetrics(endpoint))
        m.record(ms, ok)

    def summary(self) -> dict:
        return {
            "endpoints": [m.to_dict() for m in self.metrics.values()],
            "total_calls": sum(m.calls for m in self.metrics.values()),
            "total_errors": sum(m.errors for m in self.metrics.values()),
        }

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.summary(), indent=2))

    def load(self):
        if not self.path.exists():
            return self
        try:
            data = json.loads(self.path.read_text())
            for e in data.get("endpoints", []):
                m = EndpointMetrics.from_dict(e)
                self.metrics[m.endpoint] = m
        except Exception:
            self.metrics = {}
        return self


_registry = None


def get_registry() -> MetricsRegistry:
    """Modul-Singleton fuer API-Middleware & Tools."""
    global _registry
    if _registry is None:
        _registry = MetricsRegistry()
    return _registry


def timed_call(fn, *args, **kwargs):
    """Fuehrt eine Funktion aus und zeichnet Latenz als Metric 'lambda'."""
    start = time.monotonic()
    try:
        result = fn(*args, **kwargs)
        get_registry().record("lambda", (time.monotonic() - start) * 1000, ok=True)
        return result
    except Exception:
        get_registry().record("lambda", (time.monotonic() - start) * 1000, ok=False)
        raise