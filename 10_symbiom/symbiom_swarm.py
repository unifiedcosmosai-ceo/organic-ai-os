"""
LAYER 10: SYMBIOM SWARM - Multi-Agent Kollaboration
Prinzip: Einzelne spezialisierte Parser-Agenten (Symbionten) arbeiten parallel,
tauschen Entdeckungen (Knowledge-Sharing) und ein Koordinator (SwarmBrain)
komponiert die beste Gesamtloesung.

Wie in der Natur: Mykorrhiza-Netzwerke, Bienenstaaten, Ameisenkolonien.
"""

import ast
import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Tuple

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Symbiont:
    """Ein spezialisierter Parser-Agent im Schwarm."""
    name: str
    speciality: str          # z.B. "robust", "fast", "compact", "strict"
    code: str
    fitness: float = 0.0
    discoveries: List[str] = field(default_factory=list)
    lineage: List[str] = field(default_factory=list)

    def to_prompt(self):
        return f"# {self.name} [{self.speciality}] fit={self.fitness:.3f}\n{self.code}"


class SymbiomSwarm:
    """
    Schwarm aus Spezialisten, die gemeinsam einen Parser evolvieren.
    Jeder Symbiont hat einen Spezialisierungsdruck -> verschiedene Nischen.
    Der Koordinator teilt die besten Teile (Knowledge-Sharing) quer.
    """

    SPECIALTIES = {
        "robust": {
            "mut": lambda c: (f"import re\n{c}" if "import re" not in c else c).replace(
                "records={}", "records={}\n    ws=re.compile(r'\\s+')"
            ).replace("buf.append(s.upper())", "buf.append(ws.sub('', s).upper())"),
            "test": lambda ns: True,
        },
        "fast": {
            "mut": lambda c: c,
            "test": lambda ns: True,
        },
        "compact": {
            "mut": lambda c: re.sub(r"\n\s*\n+", "\n", c),
            "test": lambda ns: True,
        },
        "strict": {
            "mut": lambda c: c.replace("for line in text.splitlines():", "for line in [l for l in text.splitlines() if l.strip()]:")
                             .replace("        s=line.strip()\n        if not s: continue", "        s=line.strip()"),
            "test": lambda ns: True,
        },
    }

    def __init__(self, population_per_species=3, hall_of_fame_size=5):
        self.population_per_species = population_per_species
        self.hall_of_fame_size = hall_of_fame_size
        self.symbionts: List[Symbiont] = []
        self.hall_of_fame: List[Symbiont] = []
        self.history: List[dict] = []

    # --- Schwarm aufbauen ---
    def seed(self, base_code: str):
        self.symbionts = []
        for spec, rules in self.SPECIALTIES.items():
            for i in range(self.population_per_species):
                code = rules["mut"](base_code) if i else base_code
                self.symbionts.append(
                    Symbiont(name=f"{spec}_{i}", speciality=spec, code=code)
                )

    # --- Selektion: jeder Spezialist wird auf seine Nische getestet ---
    def evaluate(self, symbiont: Symbiont, tests: List[Tuple[Callable, float]]):
        score = 0.0
        total = 0.0
        try:
            ast.parse(symbiont.code)
        except Exception:
            symbiont.fitness = 0.0
            return
        for fn, w in tests:
            try:
                ns = {}
                exec(symbiont.code, ns, ns)
                res = fn(ns)
                score += (float(res) if isinstance(res, (int, float)) else (1.0 if res else 0.0)) * w
            except Exception:
                pass
            total += w
        # Spezialisierungs-Bonus: Kompaktheit
        lines = len(symbiont.code.splitlines())
        penalty = max(0, (lines - 20) * 0.01)
        symbiont.fitness = max(0.0, (score / total if total else 0) - penalty)

    # --- Knowledge-Sharing: Discovery aus bestem Spezialisten teilen ---
    def _share_knowledge(self):
        best = max(self.symbionts, key=lambda s: s.fitness)
        for s in self.symbionts:
            if s is best:
                continue
            # Wirte die Erkenntnis des Besten in den Schwarm ein (Inspiration)
            if best.fitness > s.fitness and random.random() < 0.5:
                s.code = s.code + f"\n    # [SWARM-SHARED from {best.name}]"
                s.discoveries.append(best.name)
        self._update_hall_of_fame()

    def _update_hall_of_fame(self):
        candidates = self.symbionts + self.hall_of_fame
        unique: List[Symbiont] = []
        seen = set()
        for s in sorted(candidates, key=lambda x: (x.fitness, -len(x.code)), reverse=True):
            key = re.sub(r"\s+", "", s.code)[:200]
            if key in seen:
                continue
            seen.add(key)
            unique.append(s)
        self.hall_of_fame = unique[: self.hall_of_fame_size]

    # --- Hauptschleife ---
    def evolve(self, tests, generations=8):
        print(f"\n🐝 SYMBIOM SWARM - {len(self.symbionts)} Symbionten, {generations} Generationen")
        for gen in range(generations):
            for s in self.symbionts:
                self.evaluate(s, tests)
            self.symbionts.sort(key=lambda x: x.fitness, reverse=True)
            best = self.symbionts[0]
            self._share_knowledge()
            self.history.append({
                "generation": gen,
                "best": {"name": best.name, "fitness": round(best.fitness, 4)},
                "species": [s.name for s in self.symbionts[:3]],
            })
            print(f" Gen {gen}: best={best.name} [{best.speciality}] fit={best.fitness:.3f}")
            if best.fitness >= 0.95:
                break
            # Naechste Generation: Elitismus + Mutation pro Spezialist
            next_gen = [best]
            for spec, rules in self.SPECIALTIES.items():
                for i in range(self.population_per_species - (1 if spec == best.speciality else 0)):
                    parent = random.choice(self.symbionts[:3])
                    child = Symbiont(
                        name=f"{spec}_{gen}_{i}",
                        speciality=spec,
                        code=rules["mut"](parent.code),
                    )
                    next_gen.append(child)
            self.symbionts = next_gen

        self.symbionts.sort(key=lambda x: x.fitness, reverse=True)
        return self.symbionts[0]

    def ensemble_score(self, tests, threshold: float = 0.5) -> dict:
        """Schwarm-Voting (v6): alle Symbionten stimmen je Test ab (Mehrheit)."""
        from voting import swarm_vote

        results = {}
        for i, (fn, w) in enumerate(tests):
            votes = []
            for s in self.symbionts:
                try:
                    ns = {}
                    exec(s.code, ns, ns)
                    res = fn(ns)
                    votes.append(bool(res) if not isinstance(res, (int, float))
                                 else res >= 0.5)
                except Exception:
                    votes.append(False)
            results[f"test_{i}"] = votes
        return swarm_vote(results, threshold)

    def export_hall_of_fame(self, path: Path = None):
        path = path or (ROOT / "memory" / "symbiom_hall_of_fame.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(
            [{"name": s.name, "speciality": s.speciality, "fitness": s.fitness, "discoveries": s.discoveries}
             for s in self.hall_of_fame],
            indent=2, ensure_ascii=False))
        return path


def _test_parse(ns):
    if "parse_fasta" not in ns:
        return False
    try:
        r = ns["parse_fasta"](">a\nATGC\n>b\nGG\n")
        return len(r) == 2 and r["a"] == "ATGC"
    except Exception:
        return False


def _test_messy(ns):
    if "parse_fasta" not in ns:
        return False
    try:
        r = ns["parse_fasta"](">a b\n  atgc  \n\n>b\nGG\n")
        return len(r) == 2 and all(" " not in v for v in r.values())
    except Exception:
        return False


if __name__ == "__main__":
    seed_code = """
def parse_fasta(text):
    records={}
    curr=None
    buf=[]
    for line in text.splitlines():
        s=line.strip()
        if not s: continue
        if s.startswith(">"):
            if curr: records[curr]="".join(buf)
            curr=s[1:].split()[0]
            buf=[]
        else:
            buf.append(s.upper())
    if curr: records[curr]="".join(buf)
    return records
"""
    swarm = SymbiomSwarm(population_per_species=3)
    swarm.seed(seed_code)
    winner = swarm.evolve([(_test_parse, 0.6), (_test_messy, 0.4)], generations=8)
    print(f"\nSWARM WINNER [{winner.speciality}] fit={winner.fitness:.3f}")
    swarm.export_hall_of_fame()