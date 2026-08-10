"""Tests fuer den MCTS-Evolutions-Kern (v5, Layer 11)."""
import sys

import mcts_evolver
from mcts_evolver import BizFitness, MCTNode, MCTSEvolution
from llm_evolver import FitnessEvaluator, Strand


SEED = '''def parse_fasta(text):
    records = {}
    header = ""
    for line in text.split("\\n"):
        if line.startswith(">"):
            header = line[1:].split()[0]
            records[header] = ""
        else:
            records[header] += line.strip().upper()
    return records
'''


def t_basic(ns):
    if "parse_fasta" not in ns:
        return False
    try:
        return len(ns["parse_fasta"](">a\nATGC\n>b\nGG\n")) == 2
    except Exception:
        return False


def t_messy(ns):
    if "parse_fasta" not in ns:
        return False
    try:
        r = ns["parse_fasta"](">h x\n  atgc  \n\n>b\nGG\n")
        return len(r) == 2 and all(" " not in v for v in r.values())
    except Exception:
        return False


BASE = [(t_basic, 0.6), (t_messy, 0.4)]


def test_ucb1_unvisited_infinite():
    node = MCTNode(strand=Strand("x", code=""))
    assert node.ucb1 == float("inf")


def test_ucb1_exploits_high_value():
    parent = MCTNode(strand=Strand("p", code=""))
    hi = MCTNode(strand=Strand("h", code=""), parent=parent, visits=10, value=8.0)
    lo = MCTNode(strand=Strand("l", code=""), parent=parent, visits=10, value=1.0)
    assert hi.ucb1 > lo.ucb1


def test_best_child():
    parent = MCTNode(strand=Strand("p", code=""))
    lo = MCTNode(strand=Strand("l", code=""), parent=parent, visits=5, value=1.0)
    hi = MCTNode(strand=Strand("h", code=""), parent=parent, visits=5, value=4.0)
    parent.children = [lo, hi]
    assert parent.best_child() is hi


def test_mcts_reaches_high_fitness():
    engine = MCTSEvolution(pop_size=6, max_rollouts=60)
    root = Strand(name="adam", code=SEED)
    best = engine.run_mcts(root, FitnessEvaluator, BASE, iterations=60)
    assert best.strand.fitness >= 0.9


def test_mcts_validates_with_adversarial():
    engine = MCTSEvolution(max_rollouts=40)
    root = Strand(name="adam", code=SEED)
    tests = engine.adversarial_tests(BASE)
    assert len(tests) == len(BASE) + 3
    best = engine.run_mcts(root, FitnessEvaluator, tests, iterations=40)
    assert best.strand.fitness >= 0.8


def test_embedded_newline_adversarial():
    ns = {}
    exec(SEED, {}, ns)
    assert MCTSEvolution._t_embedded_newline(ns) is True


def test_duplicate_headers_adversarial():
    ns = {}
    exec(SEED, {}, ns)
    assert MCTSEvolution._t_duplicate_headers(ns) is False  # seed overwrite -> Grenzfall schlaegt fehl


def test_biz_fitness_rewards_compact():
    good = "def f():\n    return 1\n"
    ns = {}
    exec(good, {}, ns)
    assert BizFitness.evaluate(good, []) > BizFitness.evaluate("def f():\n    " + "x=1\n" * 100 + "    return 1\n", [])


def test_biz_fitness_rejects_syntax_error():
    assert BizFitness.evaluate("def broken(:", []) == 0.0


def test_lowcase_normalization_adversarial():
    ns = {}
    exec(SEED, {}, ns)
    assert MCTSEvolution._t_lowercase_only(ns) is True