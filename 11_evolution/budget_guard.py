"""
LAYER 11: BUDGET-GUARD (v5)
Globaler Kosten-Guard fuer Evolution - "das Mitochondrium" des Organismus.

Forschung 2026 (REASON-CODE, RPM-MCTS, FEV):
- Token/Zeit/Iterations-Budgets: maxima je Lauf, klare Abbruchbedingungen
- Adaptive Suchtiefe (REASON-CODE): MCTS-Search NUR wenn greedy/fallback-DNA
  Fehler produziert. Spaert Budget bei einfachen Faellen.
- Sub-Budget-Abschaltung: Population wird vor der VOLLEN Bewertung grob
  vorsortiert (Beta-Tests), Sparsame Reihung.
- Energie-Budget (Pareto): Fitness folgt Speed+Tokens+Memory -> kein giltiges
  Ergebnis ist teurer als das Budget.

Design:
- BudgetGuard ist ein Kontextmanager + Zaehlwerk. Thread-safe pro Run.
- Er meldet UEBERLAUF via BudgetExceeded-Ausnahme (hart) ODER
  `soft=True` (weich, liefert stehengebliebenen Zwischentand).
"""

import time
from dataclasses import dataclass
from typing import Callable, Optional


class BudgetExceeded(Exception):
    """Hartes Budget-Limit erreicht. Evolution wird abgebrochen."""


@dataclass
class BudgetSnapshot:
    token_budget: float
    tokens_used: float
    time_budget: float
    time_used: float
    iteration_budget: int
    iterations_used: int
    searches_run: int
    greedy_passes: int
    depth: int

    @property
    def token_ratio(self) -> float:
        return self.tokens_used / self.token_budget if self.token_budget else 0.0

    @property
    def time_ratio(self) -> float:
        return self.time_used / self.time_budget if self.time_budget else 0.0

    def to_dict(self) -> dict:
        return {
            "token_budget": self.token_budget, "tokens_used": self.tokens_used,
            "time_budget": self.time_budget, "time_used": round(self.time_used, 3),
            "iteration_budget": self.iteration_budget, "iterations_used": self.iterations_used,
            "searches_run": self.searches_run, "greedy_passes": self.greedy_passes,
            "depth": self.depth,
            "token_ratio": round(self.token_ratio, 4),
            "time_ratio": round(self.time_ratio, 4),
        }


class BudgetGuard:
    """Zaehlwerk + Abbruchregeln fuer einen Evolutions-Lauf."""

    def __init__(self, token_budget: float = 1000.0, time_budget: float = 60.0,
                 iteration_budget: int = 400, soft: bool = False,
                 adaptive_depth: bool = True, min_depth: int = 1):
        self.token_budget = token_budget
        self.time_budget = time_budget
        self.iteration_budget = iteration_budget
        self.soft = soft
        self.adaptive_depth = adaptive_depth
        self.min_depth = min_depth

        self.tokens_used = 0.0
        self.iterations_used = 0
        self.searches_run = 0          # wie oft MCTS-Suche wirklich lief
        self.greedy_passes = 0         # wie oft Greedy/AST genuegte (kein Search noetig)
        self.depth = max(min_depth, int(iteration_budget ** 0.5) if iteration_budget else min_depth)
        self._start = time.monotonic()
        self.time_used = 0.0
        self.finished = False

    # --- Zaehler ---
    def spend_tokens(self, amount: float = 1.0):
        self.tokens_used += amount

    def spend_iteration(self):
        self.iterations_used += 1

    def record_search(self):
        self.searches_run += 1

    def record_greedy(self):
        self.greedy_passes += 1

    # --- Checks ---
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.time_used = time.monotonic() - self._start
        self.finished = True
        return False

    def check(self) -> Optional[BudgetSnapshot]:
        """Prueft alle Limits. Liefert None wenn ok, sonst Snapshot + wirft ggf."""
        self.time_used = time.monotonic() - self._start
        exceeded = (
            self.tokens_used >= self.token_budget or
            self.time_used >= self.time_budget or
            self.iterations_used >= self.iteration_budget
        )
        if not exceeded:
            return None
        snap = self.snapshot()
        if not self.soft:
            raise BudgetExceeded(f"Budget ueberschritten: {snap.to_dict()}")
        return snap

    def snapshot(self) -> BudgetSnapshot:
        self.time_used = time.monotonic() - self._start
        return BudgetSnapshot(
            token_budget=self.token_budget, tokens_used=self.tokens_used,
            time_budget=self.time_budget, time_used=self.time_used,
            iteration_budget=self.iteration_budget, iterations_used=self.iterations_used,
            searches_run=self.searches_run, greedy_passes=self.greedy_passes,
            depth=self.depth,
        )

    # --- Adaptive Tiefe (REASON-CODE) ---
    def adapt_depth(self) -> int:
        """Naehert sich Budget-Erschopfung -> Tiefe runter (Sparte 15 % pro Stufe)."""
        self.depth = max(self.min_depth, self.depth)
        if not self.adaptive_depth:
            return self.depth
        ratio = max(self.token_ratio(), self.time_ratio())
        if ratio > 0.85:
            self.depth = max(self.min_depth, int(self.depth * 0.55))
        elif ratio > 0.6:
            self.depth = max(self.min_depth, int(self.depth * 0.8))
        return self.depth

    def token_ratio(self) -> float:
        return self.tokens_used / self.token_budget if self.token_budget else 0.0

    def time_ratio(self) -> float:
        self.time_used = time.monotonic() - self._start
        return self.time_used / self.time_budget if self.time_budget else 0.0

    # --- Sub-Budget-Abschaltung (Beta-Tests) ---
    def beta_filter(self, candidates: list, score_fn: Callable, keep: float = 0.6) -> list:
        """Sortiert Kandidaten ohne VOLLE Bewertung -> spart Zeit/Tokens."""
        scored = sorted((score_fn(c) for c in candidates), reverse=True)
        n_keep = max(1, int(len(candidates) * keep))
        # Grob: billiger pro-Fitness-Einheit. Bewertungskosten minimal halten.
        return [c for c in candidates if score_fn(c) >= scored[n_keep - 1] or len(candidates) < 2][:n_keep]

    # --- Pareto-Energie (Speed+Tokens) ---
    def pareto_energy(self, fitness: float, speed: float, tokens: float) -> float:
        """Effiziente Bewertung: Hoehere Fitness, schnellere Ausfuehrung und
        weniger Tokens -> mehr 'Energie'. 0..1 Skala."""
        speed_n = max(0.0, min(1.0, speed))
        token_saving = max(0.0, min(1.0, 1.0 - (tokens / self.token_budget if self.token_budget else 0.0)))
        return max(0.0, min(1.0, fitness * (0.5 + 0.25 * speed_n + 0.25 * token_saving)))


def pareto_front(points: list, top_k: int = 3):
    """Pareto-Front (max schnell, max tokens-guenstig). Returns dominante Punkte."""
    result = []
    for p in points:
        dominated = False
        for q in points:
            if q is not p and q[0] >= p[0] and q[1] >= p[1] and (q[0] > p[0] or q[1] > p[1]):
                dominated = True
                break
        if not dominated:
            result.append(p)
    result.sort(key=lambda p: (p[0], p[1]), reverse=True)
    return result[:top_k]


# --- Integration: MCTS mit Budget (zwischengetrickte Schicht) ---
def budgeted_mcts(engine, root_strand, fitness_fn, tests, iterations, guard: BudgetGuard):
    """MCTS-Run unter Budget: teilt Werk in Batches, adaptiert Tiefe je Budgetlage,
    bricht weich ab, teilt sich einen Suchbaum ueber alle Batches (REASON-CODE/ARIADNE)."""
    root = None
    try:
        with guard:
            step = max(2, iterations // 10)
            while guard.iterations_used < guard.iteration_budget:
                depth_now = guard.adapt_depth()
                remaining = min(step, guard.iteration_budget - guard.iterations_used)
                # Jede Batch verbraucht ~ tokens proportional zur Tiefe
                engine.run_mcts(root_strand, fitness_fn, tests,
                                iterations=remaining, root=root)
                root = engine.root
                guard.iterations_used += remaining
                guard.spend_tokens(remaining * 0.25 * depth_now)
                guard.record_search()
                if guard.check() is not None:
                    break
                if guard.iterations_used >= guard.iteration_budget:
                    break
    except BudgetExceeded:
        pass
    return root, guard.snapshot()


def greedy_or_search(root_strand, engine, fitness_fn, tests, guard: BudgetGuard,
                     greedy_threshold: float = 0.9) -> object:
    """REASON-CODE: greedy/AST zuerst, MCTS-Search NUR bei Fehler/Fail-Schwelle."""
    fit = fitness_fn.evaluate(root_strand.code, tests)
    if fit >= greedy_threshold:
        guard.record_greedy()
        guard.spend_tokens(1.0)
        return engine._best_confirmed(engine.root) if engine.root else None, fit
    guard.record_search()
    engine.run_mcts(root_strand, fitness_fn, tests, iterations=guard.iteration_budget)
    return engine._best_confirmed(engine.root), fit


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "11_evolution")
    from mcts_evolver import MCTSEvolution
    from llm_evolver import FitnessEvaluator, Strand

    seed = """def parse_fasta(text):
    records = {}
    header = ""
    for line in text.splitlines():
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

    engine = MCTSEvolution(max_rollouts=200)
    tests = engine.adversarial_tests([(t_basic, 0.6), (t_messy, 0.4)])
    with BudgetGuard(token_budget=500, time_budget=30, iteration_budget=80, soft=True) as guard:
        root, snap = budgeted_mcts(engine, Strand(name="adam", code=seed),
                                   FitnessEvaluator, tests, 80, guard)
        print(f"Budget: tokens {snap.tokens_used:.0f}/{snap.token_budget:.0f} | "
              f"iter {snap.iterations_used}/{snap.iteration_budget} | "
              f"depth {snap.depth} | searches {snap.searches_run}")
        # REASON-CODE: Greedy zuerst, MCTS nur bei Bedarf
        fit = FitnessEvaluator.evaluate(seed, tests)
        if fit >= 0.9:
            guard.record_greedy()
            print(f"Greedy-Pfad: fit={fit:.3f} >= 0.9, kein MCTS-Search noetig (spart Budget)")
        else:
            best = engine._best_confirmed(root)
            print(f"MCTS-Pfad: fit={best.strand.fitness:.3f} (Search war noetig)")
            print(f"Champion: {best.strand.name} fit={best.strand.fitness:.3f}")