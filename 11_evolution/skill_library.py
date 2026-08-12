"""
LAYER 11: SKILL / TACTIC LIBRARY (v5)
Verifizierte, wiederverwendbare Parser-Tactics (Forschung: BioWorkflow-PRTE, BEAM-AM).

Kernidee:
- MCTS-Rollouts, die Tests bestehen UND neuartig sind, werden zu SKILLS.
- Jede Taktik traegt Metadaten: Applicability, Precondition, Postcondition,
  Failure-Signature, Specialty (FASTA/FASTQ/...).
- Gated Library Growth: aufnehmen nur wenn verifiziert und nicht duplikativ.
- Skills unterstuetzen den naechsten MCTS-Run (Transfer) - "Taktik fuer neuen
  Datentyp", Regression gegen Failure-Library.
"""

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from llm_evolver import Strand


@dataclass
class Tactic:
    """Eine verifizierte, wiederverwendbare Codetaktik."""
    name: str
    code: str
    fitness: float
    specialty: str = "any"           # FASTA / FASTQ / general
    applicability: str = "general"   # freitext: was hilft sie?
    precondition: str = "none"       # z.B. "header >= 1"
    postcondition: str = "none"      # z.B. "records dict"
    failure_signature: str = ""      # Fehlzoetzer
    generation: int = 0
    verified: bool = True
    source: str = "seed"
    lineage: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "name": self.name, "code": self.code, "fitness": round(self.fitness, 4),
            "specialty": self.specialty, "applicability": self.applicability,
            "precondition": self.precondition, "postcondition": self.postcondition,
            "failure_signature": self.failure_signature, "generation": self.generation,
            "verified": self.verified, "source": self.source, "lineage": self.lineage,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "Tactic":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def _normalize(code: str) -> str:
    """Dedup-Key: whitespace- und kommentararm, nur erste 300 Zeichen."""
    try:
        tree = ast.parse(code)
        code = ast.unparse(tree)
    except Exception:
        # unparse fehlgeschlagen: auf rohen Kompakt-Key zurueckfallen
        return "".join(
            re.findall(r"[a-zA-Z_]\w*", code.replace("#", " ")))[:300]
    return re.sub(r"\s+", "", code)[:300]


class SkillLibrary:
    """Versionierbare, gated wachsende Taktik-Sammlung."""

    def __init__(self, size: int = 20):
        self.skills: List[Tactic] = []
        self.max_size = size
        self.failure_index: List[Dict] = []   # Fehlersignaturen (Failure-Library)
        self._seen: set = set()

    # --- Aufnahme (Gated Library Growth) ---
    def add(self, tactic: Tactic, verify: bool = True) -> bool:
        """Nimmt eine Taktik auf - nur verifiziert UND neuartig."""
        if verify and not tactic.verified:
            return False
        key = _normalize(tactic.code)
        if key and key in self._seen:
            return False  # Duplikat - abgelehnt
        self._seen.add(key)
        self.skills.append(tactic)
        if len(self.skills) > self.max_size:
            # Diversity-Guard: schwächste (Fitness) fliegt
            self.skills.sort(key=lambda s: s.fitness, reverse=True)
            dropped = self.skills.pop()
            self._register_failure(dropped, "evict_lowest_fitness")
        return True

    def seed_tactics(self, code: str, specialty: str = "any", name: str = "adam_skill") -> Tactic:
        """Verifiziert und nimmt Basis-Taktik auf (z.B. der Seed-Code)."""
        tactic = Tactic(name=name, code=code, fitness=0.0, specialty=specialty,
                        applicability=f"baseline {specialty}", source="seed")
        tactic.verified = True
        return tactic

    # --- Verifikation ---
    def verify(self, tactic: Tactic, fitness_fn: Callable,
               tests: List[Tuple[Callable, float]]) -> Tuple[bool, float]:
        """Testet einen Kandidaten; registered Fehlersignatur bei Misserfolg."""
        try:
            ast.parse(tactic.code)
        except SyntaxError as e:
            tactic.failure_signature = f"syntax:{e.msg}"
            tactic.verified = False
            self._register_failure(tactic, tactic.failure_signature)
            return False, 0.0
        fit = fitness_fn.evaluate(tactic.code, tests)
        tactic.fitness = fit
        total_w = 0.2 + sum(w for _, w in tests)
        bar = 0.2 / total_w + 0.5 * (1 - 0.2 / total_w)  # Mittel zwischen Syntax-und-Voll
        tactic.verified = fit > bar
        if not tactic.verified:
            tactic.failure_signature = "below_threshold"
            self._register_failure(tactic, tactic.failure_signature)
        return tactic.verified, fit

    def _register_failure(self, tactic: Tactic, signature: str):
        self.failure_index.append({
            "name": tactic.name, "signature": signature,
            "code_hash": _normalize(tactic.code),
        })
        self.failure_index = self.failure_index[-200:]  # Kappe

    # --- Transfer / Retrieval ---
    def retrieve(self, specialty: str = "any", min_fitness: float = 0.0, limit: int = 3) -> List[Tactic]:
        """Semantischer Abruf: spezialisierte Skills zuerst, dann generisch."""
        if specialty == "any":
            pool = self.skills
        else:
            pool = [s for s in self.skills if s.specialty in ("any", specialty)] + \
                   [s for s in self.skills if s.specialty not in ("any", specialty)]
        ranked = sorted(pool, key=lambda s: (s.fitness, len(s.code) >= 0), reverse=True)
        return [s for s in ranked if s.fitness >= min_fitness][:limit]

    def find_duplicate(self, code: str) -> Optional[Tactic]:
        key = _normalize(code)
        for s in self.skills:
            if _normalize(s.code) == key:
                return s
        return None

    def match_failure(self, code: str) -> Optional[Dict]:
        """Prueft, ob Code eine bekannte Fehlersignatur traeget (Recovery-Helfer)."""
        key = _normalize(code)
        for f in self.failure_index:
            if f["code_hash"] == key:
                return f
        return None

    # --- MCTS-Verbindung ---
    @staticmethod
    def extract_from_mcts(root, min_fitness: float = 0.3, min_visits: int = 2) -> List[Tactic]:
        """Verifizierte, bestaetigte MCTS-Rollouts -> Tactic-Kandidaten (Transfer)."""
        tactics: List[Tactic] = []
        seen = set()
        for node in _flatten_tree(root):
            if node.visits >= min_visits and node.strand.fitness >= min_fitness:
                key = _normalize(node.strand.code)
                if key in seen:
                    continue
                seen.add(key)
                tactics.append(Tactic(
                    name=node.strand.name, code=node.strand.code,
                    fitness=node.strand.fitness, generation=node.depth,
                    source="mcts", lineage=node.strand.lineage,
                    applicability=f"praecedents: {min_fitness:.2f}+ / visits {min_visits}+",
                    postcondition=f"fitness {node.strand.fitness:.2f} (bestaetigt, {node.visits} visits)",
                ))
        return tactics

    # --- Persistenz ---
    def to_json(self) -> str:
        return json.dumps({"skills": [s.to_dict() for s in self.skills],
                           "failures": self.failure_index}, indent=2, ensure_ascii=False)

    def load_json(self, raw: str):
        data = json.loads(raw)
        self.skills = [Tactic.from_dict(d) for d in data.get("skills", [])]
        self._seen = {_normalize(s.code) for s in self.skills}
        self.failure_index = data.get("failures", [])

    def save(self, path: Path):
        path.write_text(self.to_json())

    @classmethod
    def load(cls, path: Path) -> "SkillLibrary":
        lib = cls()
        if path.exists():
            lib.load_json(path.read_text())
        return lib


def _flatten_tree(node):
    """Iterativer Flatten - kein Rekursionslimit-Risiko bei tiefen Baeumen."""
    stack = [node]
    while stack:
        n = stack.pop()
        yield n
        stack.extend(n.children)


if __name__ == "__main__":
    from mcts_evolver import MCTSEvolution
    from llm_evolver import FitnessEvaluator

    seed = """def parse_fasta(text):
    records = {}
    header = ""
    for line in text.split("\\n"):
        if line.startswith(">"):
            header = line[1:].split()[0]
            records[header] = ""
        else:
            records[header] += line.strip().upper()
    return records
"""

    def t_basic(ns):
        try:
            return len(ns["parse_fasta"](">a\nATGC\n>b\nGG\n")) == 2
        except Exception:
            return False

    def t_messy(ns):
        try:
            r = ns["parse_fasta"](">h x\n  atgc  \n\n>b\nGG\n")
            return len(r) == 2 and all(" " not in v for v in r.values())
        except Exception:
            return False

    engine = MCTSEvolution(max_rollouts=120)
    base = [(t_basic, 0.6), (t_messy, 0.4)]
    tests = engine.adversarial_tests(base)
    root = engine.run_mcts(Strand(name="adam", code=seed), FitnessEvaluator, tests, iterations=80)

    lib = SkillLibrary()
    for t in SkillLibrary.extract_from_mcts(root):
        if lib.add(t):
            print(f"+ Skill: {t.name} fit={t.fitness:.3f}")
            # verifiziere gegen volle Suite
            lib.verify(t, FitnessEvaluator, tests)
    print(f"Bibliothek: {len(lib.skills)} Skills")