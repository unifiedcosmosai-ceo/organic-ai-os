"""
LAYER 09 NEURO: NEURO-CORTEX-PERSISTENZ (v6)
Gen-Snapshots der Prompt-Population je Generation. Ermoeglicht Replay,
Regressions-Analyse und Verlaufs-Debugging nach Feiertagen - der Cortex
"erinnert" sich ueber den Prozess hinweg (kein Gedaechtnisverlust).

Speicherort: memory/cortex_snapshots.json (gitignored, regenerierbar).
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "memory" / "cortex_snapshots.json"
MAX_SNAPSHOTS = 50


def snapshot_population(pop, generation: int, path: Path = DEFAULT_PATH) -> dict:
    """Append-Snapshot: (generation, best, population[]) je Gen (safe IO)."""
    best = pop[0]
    data = {
        "generation": generation,
        "ts": datetime.now().isoformat(),
        "best": {"name": best.name, "fitness": round(best.fitness, 4)},
        "population": [{"name": p.name, "prompt": p.prompt_template,
                        "fitness": round(p.fitness, 4), "generation": p.generation,
                        "tokens": p.tokens} for p in pop],
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        history = []
        if path.exists():
            history = json.loads(path.read_text())
        history.append(data)
        path.write_text(json.dumps(history[-MAX_SNAPSHOTS:], indent=2,
                                   ensure_ascii=False))
    except Exception:
        history = []
    return data


def load_snapshots(path: Path = DEFAULT_PATH) -> List[dict]:
    """Liest die Snapshots; fehlend/kaputt -> leere Liste."""
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except Exception:
        return []