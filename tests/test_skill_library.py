"""Tests fuer die Skill/Tactic Library (v5, Layer 11)."""
from skill_library import SkillLibrary, Tactic, _flatten_tree, _normalize
from llm_evolver import FitnessEvaluator, Strand


GOOD = "def f():\n    return 1\n"
DUP = "def f():\n    return 1    \n"
BAD = "def broken(:"
DIFFERENT = "def g(x):\n    return x + 1\n"


def _t_passes(ns):
    return callable(ns.get("f"))


TESTS = [(_t_passes, 1.0)]


def test_add_verified_and_novel():
    lib = SkillLibrary()
    assert lib.add(Tactic("a", GOOD, fitness=1.0, verified=True)) is True
    assert len(lib.skills) == 1


def test_gated_duplicates_rejected():
    lib = SkillLibrary()
    lib.add(Tactic("a", GOOD, fitness=1.0, verified=True))
    assert lib.add(Tactic("b", DUP, fitness=0.9, verified=True)) is False
    assert len(lib.skills) == 1


def test_unverified_rejected_by_gate():
    lib = SkillLibrary()
    assert lib.add(Tactic("a", GOOD, fitness=0.0, verified=False)) is False


def test_verify_syntax_error_records_failure():
    lib = SkillLibrary()
    tactic = Tactic("broken", BAD, fitness=0.0)
    ok, fit = lib.verify(tactic, FitnessEvaluator, TESTS)
    assert ok is False
    assert tactic.failure_signature.startswith("syntax:")
    assert lib.match_failure(BAD) is not None


def test_verify_below_threshold_not_verified():
    lib = SkillLibrary()
    tactic = Tactic("weak", "def f():\n    return 0\n", fitness=0.0)
    ok, _ = lib.verify(tactic, FitnessEvaluator, [(lambda ns: "f" in ns, 1.0),
                                                  (lambda ns: ns["f"]() == 7, 1.0)])
    assert ok is False
    assert tactic.failure_signature == "below_threshold"


def test_retrieval_ranks_by_fitness_and_specialty():
    lib = SkillLibrary()
    lib.add(Tactic("fasta", "def f():\n    return 1\n", fitness=0.9, specialty="FASTA"))
    lib.add(Tactic("weak_generic", "def g():\n    return 2\n", fitness=0.5, specialty="any"))
    got = lib.retrieve("FASTA", min_fitness=0.4, limit=2)
    assert got[0].name == "fasta"
    assert len(got) == 2


def test_retrieve_any_includes_all():
    lib = SkillLibrary()
    lib.add(Tactic("x", GOOD, fitness=0.7, specialty="FASTA"))
    lib.add(Tactic("y", DIFFERENT, fitness=0.6, specialty="FASTQ"))
    assert len(lib.retrieve("any")) == 2


def test_find_duplicate_via_ast_normalization():
    lib = SkillLibrary()
    lib.add(Tactic("a", GOOD, fitness=1.0))
    assert lib.find_duplicate("def f():\n    return 1\n") is not None
    assert lib.find_duplicate(DIFFERENT) is None


def test_hall_of_fame_cap_evicts_lowest():
    lib = SkillLibrary(size=2)
    lib.add(Tactic("a", GOOD, fitness=0.9, verified=True))
    lib.add(Tactic("b", DIFFERENT, fitness=0.7, verified=True))
    lib.add(Tactic("c", "def h():\n    return 3\n", fitness=0.5, verified=True))
    assert len(lib.skills) <= 2
    assert all(s.fitness >= 0.7 for s in lib.skills)


def test_persistence_roundtrip(tmp_path):
    path = tmp_path / "skills.json"
    lib = SkillLibrary()
    lib.add(Tactic("a", GOOD, fitness=0.9))
    lib._register_failure(Tactic("x", BAD, fitness=0.0), "syntax:broken")
    lib.save(path)
    loaded = SkillLibrary.load(path)
    assert len(loaded.skills) == 1
    assert loaded.skills[0].name == "a"
    assert len(loaded.failure_index) == 1


def test_flatten_tree_iterative():
    from mcts_evolver import MCTNode as MCTSNode
    root = MCTSNode(strand=Strand("r", code=""))
    c1 = MCTSNode(strand=Strand("c1", code=""), parent=root)
    c2 = MCTSNode(strand=Strand("c2", code=""), parent=root)
    gc = MCTSNode(strand=Strand("gc", code=""), parent=c1)
    root.children = [c1, c2]
    c1.children = [gc]
    names = {n.strand.name for n in _flatten_tree(root)}
    assert names == {"r", "c1", "c2", "gc"}


def test_normalize_strips_whitespace():
    assert _normalize("def f():\n    return 1\n") == _normalize("def f():  return 1")