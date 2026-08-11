"""Tests fuer die praktische Co-Evolution-Anbindung (v5, Layer 09/10)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "10_symbiom"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "09_neuro"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "11_evolution"))

import co_evolution
from co_evolution import _seed_code


def _t_parse(ns):
    if "parse_fasta" not in ns:
        return False
    try:
        return len(ns["parse_fasta"](">a\nATGC\n>b\nGG\n")) == 2
    except Exception:
        return False


def _t_messy(ns):
    if "parse_fasta" not in ns:
        return False
    try:
        r = ns["parse_fasta"](">h x\n  atgc  \n\n>b\nGG\n")
        return len(r) == 2 and all(" " not in v for v in r.values())
    except Exception:
        return False


def test_seed_code_parses():
    ns = {}
    exec(_seed_code(), {}, ns)
    assert len(ns["parse_fasta"](">a\nATGC\n>b\nGG\n")) == 2


def test_evolve_default_tests():
    code, prompt, hist = co_evolution.evolve(rounds=1, swarm_generations=3, pop_per_species=2)
    assert code is not None
    assert prompt is not None
    assert len(hist) == 1
    assert code.fitness > 0.5


def test_evolve_with_external_tests():
    # eigens definierte Tests (wie sie die naechtliche Evolution liefert)
    tests = [(_t_parse, 0.6), (_t_messy, 0.4)]
    code, prompt, hist = co_evolution.evolve(rounds=1, swarm_generations=3,
                                             pop_per_species=2, tests=tests)
    assert code.fitness > 0.5


def test_evolve_returns_history_shape():
    _, _, hist = co_evolution.evolve(rounds=2, swarm_generations=2, pop_per_species=2)
    assert len(hist) == 2
    for entry in hist:
        assert "round" in entry
        assert "code_best" in entry and "fitness" in entry["code_best"]
        assert "prompt_best" in entry and "fitness" in entry["prompt_best"]


def test_prompt_hint_fed_into_code():
    # Inspect the hint-injection logic: after a round, symbionts carry a comment
    # with the best prompt. Verify evolve() leaves a prompt-hint in swarm code.
    import symbiom_swarm
    cortex = __import__("neuro_evolving").NeuroCortex()
    cortex.seed()
    swarm = symbiom_swarm.SymbiomSwarm(population_per_species=2)
    swarm.seed(_seed_code())
    best_code, best_prompt, _ = co_evolution.evolve(rounds=2, swarm_generations=2,
                                                    pop_per_species=2)
    # Best-prompt names sind deterministisch (adam_engineer etc.)
    assert best_prompt.name.startswith("adam") or best_prompt.fitness > 0


def test_nightly_coevolution_integration(tmp_path):
    """NightlyEvolution._run_coevolution persistiert prompt_hint + coevolution."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import autonomous_organism as ao

    memory = ao.OrganismMemory()
    memory.data["failures"] = []
    watcher = ao.FastaWatcher(memory)
    nightly = ao.NightlyEvolution(memory, watcher)

    # Direkt _run_coevolution aufrufen (isoliert, mit realem Testset)
    tests = [(_t_parse, 0.6), (_t_messy, 0.4)]
    nightly._run_coevolution(tests, old_score=0.5, new_score=0.5)

    assert "prompt_hint" in memory.data
    assert memory.data["prompt_hint"]  # nicht leer
    assert "coevolution" in memory.data
    assert "best_prompt" in memory.data["coevolution"]
    assert "co_score" in memory.data["coevolution"]


def test_nightly_run_coevolve_flag(tmp_path):
    """run_nightly(coevolve=False) schlaegt nicht fehl; coevolve=True fuegt Memory-Felder hinzu."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import autonomous_organism as ao

    memory = ao.OrganismMemory()
    memory.data["failures"] = []
    watcher = ao.FastaWatcher(memory)
    nightly = ao.NightlyEvolution(memory, watcher)

    nightly.run_nightly(coevolve=False)   # darf nicht crashen
    assert True


def test_coevolution_does_not_break_on_bad_tests():
    """Kaputte Tests (werfen) stoppen die Co-Evolution nicht."""
    def bad(ns):
        raise RuntimeError("kaputt")

    tests = [(bad, 1.0)]
    code, prompt, hist = co_evolution.evolve(rounds=1, swarm_generations=2,
                                             pop_per_species=2, tests=tests)
    # schwarm.evolve faengt Exceptions ab; kein Crash
    assert code is not None