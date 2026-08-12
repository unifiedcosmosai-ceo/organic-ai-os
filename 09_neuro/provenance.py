"""
LAYER 09 NEURO: MRNA-PROVENIENZ (v6)
Traceback: welche Mutation (Strategie, Parent, Generation) erzeugte welchen
Prompt. Damit wird reproduzierbar, warum ein Prompt sich so verhaelt.

Grundlage: Provenienz-Tracking in Multi-Tool-Bioinformatik (BioMedAgent,
KBase, FEV) - jede Antwort traegt ihren Herkunfts-Pfad.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "memory" / "provenance_log.json"


@dataclass
class MutationEvent:
    ts: str
    parent: str
    child: str
    strategy: str
    generation: int
    fitness_before: float
    prompt_snippet: str

    def to_dict(self) -> dict:
        return asdict(self)


class ProvenanceTracker:
    """Sammelt Mutations-Events, erlaubt Query/Summary + Persistenz."""

    def __init__(self, path: Path = DEFAULT_PATH, cap: int = 500):
        self.path = path
        self.cap = cap
        self.events: List[MutationEvent] = []

    def record(self, parent: str, child: str, strategy: str, generation: int,
               fitness_before: float, prompt_snippet: str) -> MutationEvent:
        ev = MutationEvent(
            ts=datetime.now().isoformat(),
            parent=parent, child=child, strategy=strategy,
            generation=generation, fitness_before=round(fitness_before, 4),
            prompt_snippet=prompt_snippet[:120],
        )
        self.events.append(ev)
        if len(self.events) > self.cap:
            self.events = self.events[-self.cap:]
        return ev

    def query(self, name: str = None, strategy: str = None,
              last: int = 50) -> List[MutationEvent]:
        evs = self.events
        if name:
            evs = [e for e in evs if e.child == name or e.parent == name]
        if strategy:
            evs = [e for e in evs if e.strategy == strategy]
        return evs[-last:]

    def summary(self) -> dict:
        by_strategy: Dict[str, int] = {}
        for e in self.events:
            by_strategy[e.strategy] = by_strategy.get(e.strategy, 0) + 1
        return {
            "events": len(self.events),
            "by_strategy": dict(sorted(by_strategy.items())),
            "last": self.events[-1].to_dict() if self.events else None,
        }

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([e.to_dict() for e in self.events],
                                        indent=2, ensure_ascii=False))

    def load(self):
        if not self.path.exists():
            return self
        try:
            data = json.loads(self.path.read_text())
            self.events = [MutationEvent(**d) for d in data]
        except Exception:
            self.events = []
        return self


_tracker = None


def get_provenance() -> ProvenanceTracker:
    """Modul-Singleton (wird von NeuroMutator bei jeder Mutation befuellt)."""
    global _tracker
    if _tracker is None:
        _tracker = ProvenanceTracker()
        _tracker.load()
    return _tracker