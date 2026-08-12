"""Tests fuer das Schwarm-Voting (v6, Layer 10 symbiom)."""
import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "10_symbiom"))

from voting import vote_on_test, swarm_vote, weighted_fitness


def test_vote_on_test_majority_pass():
    res = vote_on_test([True, True, False])
    assert res["passed"] is True
    assert res["yes"] == 2
    assert res["ratio"] == pytest.approx(0.667, abs=0.01)


def test_vote_on_test_majority_fail():
    res = vote_on_test([True, False, False])
    assert res["passed"] is False


def test_vote_on_test_empty_is_not_passed():
    res = vote_on_test([])
    assert res["passed"] is False
    assert res["ratio"] == 0.0


def test_vote_on_test_custom_threshold():
    assert vote_on_test([True, False], threshold=0.4)["passed"] is True
    assert vote_on_test([True, False], threshold=0.6)["passed"] is False


def test_swarm_vote_counts_passed_tests():
    results = {"a": [True, True, True], "b": [True, False, False],
               "c": [False, False, False]}
    v = swarm_vote(results)
    assert v["total_tests"] == 3
    assert v["passed_tests"] == 1
    assert v["votes"]["a"]["passed"] is True
    assert v["votes"]["c"]["passed"] is False


def test_swarm_vote_consensus():
    v = swarm_vote({"a": [True, True], "b": [True, False]})
    assert v["consensus"] == pytest.approx(0.75)


def test_swarm_vote_empty():
    v = swarm_vote({})
    assert v["total_tests"] == 0
    assert v["consensus"] == 0.0


def test_weighted_fitness():
    members = [("a", 1.0, 0.5), ("b", 0.5, 0.5)]
    assert weighted_fitness(members) == pytest.approx(0.75)


def test_weighted_fitness_zero_weights():
    assert weighted_fitness([("a", 1.0, 0.0)]) == 0.0
    assert weighted_fitness([]) == 0.0