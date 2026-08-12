"""
LAYER 10 SYMBIOM: SCHWARM-VOTING (v6)
Ensemble-Fitness: Spezialisten (Symbionten) stimmen pro Test ab, statt nur den
Einzel-Bestwert zu nutzen. Majority-Voting + gewichtetes Ensemble-Mass.

Grundlage: Ensemble-Klassifikation / Stacking in der Bioinformatik -
mehrere Modelle kompensieren individuelle Fehler (bagging/ponderierte Fusion).
"""

from typing import Dict, List, Tuple


def vote_on_test(member_results: List[bool], threshold: float = 0.5) -> dict:
    """Majority-Vote ueber die Mitglieder-Ergebnisse EINES Tests."""
    yes = sum(1 for r in member_results if r)
    total = len(member_results)
    ratio = round(yes / total, 3) if total else 0.0
    return {"passed": total > 0 and ratio >= threshold,
            "yes": yes, "total": total, "ratio": ratio}


def swarm_vote(results: Dict[str, List[bool]], threshold: float = 0.5) -> dict:
    """results: {test_name: [member_pass_booleans]} -> Ensemble-Bewertung."""
    votes = {name: vote_on_test(rs, threshold) for name, rs in results.items()}
    ratios = [v["ratio"] for v in votes.values()]
    return {
        "votes": votes,
        "passed_tests": sum(1 for v in votes.values() if v["passed"]),
        "total_tests": len(votes),
        "consensus": round(sum(ratios) / len(ratios), 3) if ratios else 0.0,
    }


def weighted_fitness(members: List[Tuple[str, float, float]]) -> float:
    """Gewichtete Ensemble-Fitness: members = [(name, fitness, weight), ...]."""
    total_w = sum(w for _, _, w in members)
    if total_w <= 0:
        return 0.0
    return round(sum(f * w for _, f, w in members) / total_w, 4)