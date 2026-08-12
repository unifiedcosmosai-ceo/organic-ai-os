"""
LAYER 11: FITNESS-FRUEHWARNUNG (v6)
Score-Drop-Alarm: stoppt Regression, bevor sie promotet wird.

Lernt eine Baseline des besten Scores und alarmiert, wenn ein Kandidat
unter die Schwelle faellt - statt still die Qualitaet zu verschlechtern.
Entscheidungs-Regel:
  - fitness <= 0            -> reject (lethal)
  - fitness < base - th     -> reject (score-drop ALARM)
  - fitness < base          -> hold   (kein Promoten, kein Alarm)
  - sonst                   -> promote
Persistiert History + Baseline (memory/fitness_guard.json) fuer Ops.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_GUARD_PATH = Path("memory") / "fitness_guard.json"


@dataclass
class FitnessGuard:
    path: Path = DEFAULT_GUARD_PATH
    drop_threshold: float = 0.05
    history: List[Dict] = field(default_factory=list)
    best: float = 0.0
    alarms: int = 0
    _loaded: bool = False

    def load(self):
        if self._loaded or not self.path.exists():
            return
        data = json.loads(self.path.read_text())
        self.history = data.get("history", [])
        self.best = float(data.get("best", 0.0))
        self.alarms = int(data.get("alarms", 0))
        self._loaded = True

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({
            "best": self.best,
            "alarms": self.alarms,
            "history": self.history[-200:],
            "updated": datetime.now().isoformat(),
        }, indent=2))

    def check_candidate(self, name: str, fitness: float,
                        baseline: Optional[float] = None) -> Dict:
        """Bewertet einen Kandidaten und liefert promote/hold/reject."""
        base = baseline if baseline is not None else self.best
        if fitness <= 0.0:
            decision, reason = "reject", "lethal"
        elif base > 0.0 and fitness < base - self.drop_threshold:
            decision, reason = "reject", "score-drop"
            self.alarms += 1
        elif base > 0.0 and fitness < base:
            decision, reason = "hold", "below-baseline"
        else:
            decision, reason = "promote", "new-best"
        entry = {
            "name": name,
            "fitness": fitness,
            "baseline": round(base, 4),
            "decision": decision,
            "reason": reason,
            "time": datetime.now().isoformat(),
        }
        self.history.append(entry)
        if fitness > self.best:
            self.best = fitness
        self.save()
        return entry

    def allows_promotion(self, name: str, fitness: float,
                         baseline: Optional[float] = None) -> bool:
        return self.check_candidate(name, fitness, baseline)["decision"] == "promote"

    def summary(self) -> Dict:
        return {
            "best": round(self.best, 4),
            "alarms": self.alarms,
            "checks": len(self.history),
            "last": self.history[-1] if self.history else None,
        }
