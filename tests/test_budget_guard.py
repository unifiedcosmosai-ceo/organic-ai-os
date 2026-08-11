"""Tests fuer den Budget-Guard (v5, Layer 11)."""
import sys
import time

from budget_guard import (
    BudgetExceeded, BudgetGuard, BudgetSnapshot, budgeted_mcts,
    greedy_or_search, pareto_front,
)
from llm_evolver import FitnessEvaluator, Strand
from mcts_evolver import MCTSEvolution


GOOD = "def f():\n    return 1\n"


def test_hard_budget_raises():
    guard = BudgetGuard(token_budget=1.0, soft=False)
    guard.spend_tokens(2.0)
    try:
        guard.check()
        raised = False
    except BudgetExceeded:
        raised = True
    assert raised


def test_soft_budget_returns_snapshot():
    guard = BudgetGuard(token_budget=1.0, soft=True)
    guard.spend_tokens(2.0)
    snap = guard.check()
    assert snap is not None
    assert isinstance(snap, BudgetSnapshot)


def test_iteration_budget_break():
    guard = BudgetGuard(iteration_budget=5, token_budget=100, time_budget=100, soft=True)
    for _ in range(10):
        guard.spend_iteration()
        if guard.check() is not None:
            break
    assert guard.iterations_used <= 6  # darf Obergrenze nur minimal ueberschreiten


def test_time_budget_break():
    guard = BudgetGuard(time_budget=0.05, token_budget=1000, iteration_budget=1000, soft=True)
    snap = None
    for _ in range(20):
        time.sleep(0.012)
        snap = guard.check()
        if snap is not None:
            break
    assert snap is not None
    assert snap.time_used >= 0.045


def test_adaptive_depth_degrades():
    guard = BudgetGuard(token_budget=100, soft=True, adaptive_depth=True, min_depth=2)
    guard.depth = 10
    guard.tokens_used = 99
    guard.adapt_depth()
    assert guard.depth < 10
    assert guard.depth >= 2


def test_adapt_depth_respects_min():
    guard = BudgetGuard(token_budget=1, soft=True, adaptive_depth=True, min_depth=2)
    guard.depth = 2
    for _ in range(5):
        guard.adapt_depth()
    assert guard.depth == 2


def test_beta_filter_rejects_low():
    guard = BudgetGuard()
    result = guard.beta_filter([1, 2, 3, 4, 5], lambda x: x, keep=0.6)
    assert len(result) == 3
    assert 1 not in result
    assert 5 in result


def test_pareto_energy_prefers_fast_lean():
    guard = BudgetGuard(token_budget=100)
    fast = guard.pareto_energy(1.0, speed=1.0, tokens=0)
    slow = guard.pareto_energy(1.0, speed=0.1, tokens=90)
    assert fast > slow
    assert 0.0 <= fast <= 1.0


def test_pareto_front_returns_dominating():
    points = [(5, 1), (10, 0.1), (8, 0.5)]  # (value, cost) - hoher value, niedrige Kosten
    # Pareto: nichts dominiert (10,0.1) und (8,0.5) verliert gegen (10,0.1)
    front = pareto_front(points, top_k=3)
    assert (10, 0.1) in front


def test_budgeted_mcts_enforces_caps():
    from budget_guard import BudgetGuard

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

    engine = MCTSEvolution(max_rollouts=40)
    tests = engine.adversarial_tests([(t_basic, 0.6), (t_messy, 0.4)])
    with BudgetGuard(token_budget=200, time_budget=30, iteration_budget=24, soft=True) as guard:
        root, snap = budgeted_mcts(engine, Strand(name="adam", code=seed),
                                   FitnessEvaluator, tests, 24, guard)
    assert snap.iterations_used <= 25
    assert snap.tokens_used <= snap.token_budget
    assert root is not None
    assert root.visits > 0


def test_greedy_path_skips_search_when_good():
    from budget_guard import BudgetGuard

    guard = BudgetGuard(soft=True)
    engine = MCTSEvolution(max_rollouts=40)
    best, fit = greedy_or_search(Strand("g", code=GOOD), engine,
                                 FitnessEvaluator, [(lambda ns: "f" in ns, 1.0)], guard,
                                 greedy_threshold=0.5)
    assert guard.greedy_passes == 1
    assert guard.searches_run == 0