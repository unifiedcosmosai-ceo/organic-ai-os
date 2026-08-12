"""
LAYER 11: MCTS EVOLUTION CORE (v5)
MCTS-gesteuerte Code-Evolution statt reiner GA-Tournaments.

Bio-inspiriert (Research 2026):
- BEAM: aeusserer GA-Layer fuer Struktur + innerer MCTS-Layer fuer Funktionen
- ARIADNE: geteilter Blackboard-Zustand ueber Such-Branches
- AdverMCTS: Solver-vs-Attacker, gegnerische Tests decken Pseudo-Correctness auf

Kernschleife: Selection (UCB1) -> Expansion → Simulation (Fitness) → Backpropagation
"""

import ast
import math
import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple

from llm_evolver import Strand, LLMMutator


@dataclass
class MCTNode:
    """Ein Knoten im Monca-Carlo-Suchbaum. Ein Knoten = ein Code-Strand + Suchzustand."""
    strand: Strand
    parent: "MCTNode" = None
    children: List["MCTNode"] = field(default_factory=list)
    visits: int = 0
    value: float = 0.0          # kumulierte Fitness ueber Rollouts
    depth: int = 0
    is_terminal: bool = False

    @property
    def ucb1(self, exploitation: float = 1.4) -> float:
        """Upper-Confidence-Bound: Exploration/Exploitation Ausgleich."""
        if self.visits == 0 or self.parent is None:
            return float("inf") if self.visits == 0 else self.value / self.visits
        return self.value / self.visits + exploitation * math.sqrt(
            math.log(self.parent.visits + 1) / (self.visits + 1)
        )

    def best_child(self) -> "MCTNode":
        return max(self.children, key=lambda c: c.ucb1)


class MCTSEvolution:
    """
    Bi-level Evolution (BEAM-Stil) mit MCTS als Such-Kern:
      - aeusserer Layer: Mutation/Crossover-Strategien (Struktur-Operatoren)
      - innerer Layer: MCTS waehlt die besten Code-Varianten (Funktionen)
    Zusaetzlich Adversarial-Tests (Attacker-Gedanke): versteckte Grenzfaelle.
    """

    def __init__(self, mutator=None, pop_size=8, max_rollouts=400, seed_random=True):
        self.mutator = mutator or LLMMutator("fallback")
        self.pop_size = pop_size
        self.max_rollouts = max_rollouts
        self.root: MCTNode = None
        self.strategies = [s for s in self.mutator.MUTATION_PROMPTS.keys()] if hasattr(self.mutator, "MUTATION_PROMPTS") else ["point", "insert", "neo"]
        self._rng = random.Random() if seed_random else None

    # --- Bi-level: Struktur-Operatoren (aeusserer Layer) ---
    def _structure_ops(self, strand: Strand) -> List[str]:
        """Waehlt fuer einen Strand ein diversifiziertes Strategie-Set."""
        ops = set(self.strategies)
        return list(ops)

    # --- MCTS Phasen ---
    def selection(self, node: MCTNode) -> MCTNode:
        while node.children and not node.is_terminal:
            node = node.best_child()
        return node

    def expansion(self, node: MCTNode) -> MCTNode:
        """Erzeugt ein Kind pro Strategie (Faecherauf) und bewertet grob."""
        for strat in self._structure_ops(node.strand):
            child_strand = self.mutator.mutate(node.strand, strategy=strat)
            child_strand.name = f"{node.strand.name}@m{node.depth + 1}"
            child = MCTNode(
                strand=child_strand,
                parent=node,
                depth=node.depth + 1,
            )
            node.children.append(child)
        return node

    def simulation(self, node: MCTNode, fitness_fn: Callable, tests: List[Tuple[Callable, float]]) -> float:
        """Rollout: bewertet den Strand voll. Liefert Prozess-Reward (Kompaktheit + Korrektheit)."""
        fit = fitness_fn.evaluate(node.strand.code, tests)
        # Prozess-Reward (RPM-Idee): Zwischenschritte = Kompaktheit, robuster Code
        node.strand.fitness = fit
        return max(0.0, fit)

    def backpropagation(self, node: MCTNode, reward: float):
        while node is not None:
            node.visits += 1
            node.value += reward * (0.9 ** node.depth)   # Discount mit Tiefe (Prozess-Reward)
            node = node.parent

    def run_mcts(self, root_strand: Strand, fitness_fn: Callable, tests: List[Tuple[Callable, float]], iterations: int = None, root: MCTNode = None) -> MCTNode:
        """Fuehrt die MCTS-Suche aus und gibt den besten bestaetigten Strand.

        `root` (optional): vorhandener Baum, an den weiter expandiert wird
        (Budget-Modus: mehrere Batches teilen sich einen Suchbaum).
        """
        iterations = iterations or self.max_rollouts
        if root is None:
            root = MCTNode(strand=root_strand)
        for i in range(iterations):
            leaf = self.selection(root)
            if leaf.visits > 0 and not leaf.children:
                leaf = self.expansion(leaf)
            focus = random.choice(leaf.children) if leaf.children else leaf
            reward = self.simulation(focus, fitness_fn, tests)
            self.backpropagation(focus, reward)
            # Terminal-Check: perfekte Fitness
            if focus.strand.fitness >= 0.95:
                break
        self.root = root
        return self._best_confirmed(root)

    def _best_confirmed(self, root: MCTNode) -> MCTNode:
        """Bester Knoten mit genug Bestaetigung (visits>0) - anti-Pseudo-Correctness."""
        candidates = [n for n in self._flatten(root) if n.visits > 0]
        if not candidates:
            return root
        return max(candidates, key=lambda n: (n.strand.fitness, n.visits, -n.depth))

    def _flatten(self, node: MCTNode):
        yield node
        for c in node.children:
            yield from self._flatten(c)

    # --- Adversarial-Testbank (AdverMCTS-light) ---
    def adversarial_tests(self, tests: List[Tuple[Callable, float]]) -> List[Tuple[Callable, float]]:
        """Erweitert die Testsuite um hartnäckige Randfaelle (Attacker-Gedanke)."""
        base = list(tests)
        base.append((self._t_embedded_newline, 0.4))
        base.append((self._t_duplicate_headers, 0.3))
        base.append((self._t_lowercase_only, 0.3))
        return base

    @staticmethod
    def _t_embedded_newline(ns: Dict) -> bool:
        if "parse_fasta" not in ns:
            return False
        try:
            r = ns["parse_fasta"](">a\nATG\n\n\n>b\nGG\n")  # mehrere blanke Zeilen
            return len(r) == 2
        except Exception:
            return False

    @staticmethod
    def _t_duplicate_headers(ns: Dict) -> bool:
        if "parse_fasta" not in ns:
            return False
        try:
            r = ns["parse_fasta"](">a\nATGC\n>a\nGG\n")
            return r.get("a") == "ATGCGG"  # Duplikat muss konkatenieren ODER letzter gewinnt - aktueller: letzter gewinnt
        except Exception:
            return False

    @staticmethod
    def _t_lowercase_only(ns: Dict) -> bool:
        if "parse_fasta" not in ns:
            return False
        try:
            r = ns["parse_fasta"](">b\natgcatgc\n")
            return list(r.values())[0].isupper()  # Normalisierung gefordert
        except Exception:
            return False


class BizFitness:
    """Bewertung: Korrektheit + Kompaktheit - minimal invasive Ergänzung zu FitnessEvaluator."""

    @staticmethod
    def evaluate(code: str, tests: List[Tuple[Callable, float]]) -> float:
        try:
            ast.parse(code)
        except Exception:
            return 0.0
        score, total = 0.0, 0.0
        for fn, w in tests:
            try:
                ns = {}
                exec(code, {}, ns)
                res = fn(ns)
                score += (1.0 if res else 0.0) * w
            except Exception:
                pass
            total += w
        # Kompaktheits-Praemie (Parsimonie)
        lines = len(code.splitlines())
        bonus = max(0.0, 0.05 - max(0, lines - 20) * 0.002)
        return max(0.0, (score / total if total else 0) + bonus)


if __name__ == "__main__":
    # Demo: MCTS evolviert parse_fasta mit Adversarial-Tests
    from llm_evolver import FitnessEvaluator

    seed = """
def parse_fasta(text):
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
        if "parse_fasta" not in ns: return False
        try:
            r = ns["parse_fasta"](">a\nATGC\n>b\nGG\n")
            return len(r) == 2
        except Exception:
            return False

    def t_messy(ns):
        if "parse_fasta" not in ns: return False
        try:
            r = ns["parse_fasta"](">h x\n  atgc  \n\n>b\nGG\n")
            return len(r) == 2 and all(" " not in v for v in r.values())
        except Exception:
            return False

    base = [(t_basic, 0.6), (t_messy, 0.4)]
    engine = MCTSEvolution(pop_size=6, max_rollouts=200)
    root = Strand(name="adam", code=seed)
    tests = engine.adversarial_tests(base)
    best = engine.run_mcts(root, FitnessEvaluator, tests, iterations=120)
    print(f"\n🏆 MCTS BEST: {best.strand.name}  fit={best.strand.fitness:.3f}  visits={best.visits}")
    print(best.strand.code)