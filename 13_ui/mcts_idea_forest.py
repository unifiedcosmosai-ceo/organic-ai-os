"""
LAYER 13 UI / BRAINSTORM: 3x3 MONTE-CARLO-TREE FOREST (v6)

Ideen-Raum = Kombinationen aus Seed-Genen (idea_seeds.py).
Ein 3x3-Wald aus 9 MCTS-Baeumen deckt den Raum ab:
  - Achse  : core | data | ops
  - Skala  : atomic | component | system

Je Baum: Selection (UCB1) -> Expansion (Mutationsoperatoren) ->
Simulation (Idea-Fitness) -> Backpropagation. Die besten Kandidaten
aller 9 Baeume werden nach Kategorie sortiert -> TOP 100 je Kategorie.

Deterministisch (Seed), dependency-frei, pure stdlib.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Dict, List, Optional

from idea_seeds import Gene, seed_pool

CATEGORIES = {
    "upgrades": "UPGRADE",
    "optimisations": "OPTIMISATION",
    "extensions": "EXTENSION",
    "automatisation": "AUTOMATISATION",
}


@dataclass
class Idea:
    """Eine MCTS-erzeugte Idee = Kombination von Genen + Mutation."""
    title: str
    category: str
    axis: str
    scale: str
    score: float
    impact: float
    feasibility: float
    genes: List[str] = field(default_factory=list)
    body: str = ""

    def to_dict(self):
        d = asdict(self)
        d["category_label"] = CATEGORIES[self.category]
        return d


# --------------------------------------------------------------------------
# Mutationsoperatoren
# --------------------------------------------------------------------------
def op_merge(a: Gene, b: Gene, rng: random.Random) -> Gene:
    """Kombiniert zwei Gene zu einem Hybrid-Idea."""
    if a.name == b.name:
        return op_specialize(a, rng)
    axis = a.axis if a.axis == b.axis else "core"
    scale = "component" if a.scale != b.scale else a.scale
    layer = a.layer if a.layer == b.layer else "core"
    return Gene(
        name=f"{a.name}+{b.name}",
        desc=f"{a.desc}; kombiniert mit {b.desc}",
        layer=layer, axis=axis, scale=scale,
        impact=min(1.0, a.impact * 0.6 + b.impact * 0.6 + 0.15),
        feasibility=min(1.0, a.feasibility * 0.5 + b.feasibility * 0.5),
        tags=sorted(set(a.tags) | set(b.tags)),
    )


def op_specialize(g: Gene, rng: random.Random, layer_hint: str = None) -> Gene:
    """Verfeinert ein Gen auf einen konkreten Layer/Datei-Bezug."""
    layer = layer_hint or g.layer
    return Gene(
        name=f"{g.name}@conv",
        desc=f"{g.desc} — umgesetzt als konkrete, testbare Erweiterung in Layer {layer}",
        layer=layer, axis=g.axis, scale=g.scale,
        impact=g.impact, feasibility=min(1.0, g.feasibility + 0.1),
        tags=g.tags + ["concrete"],
    )


def op_cross(g: Gene, target_layer: str, rng: random.Random) -> Gene:
    """Transferiert ein Gen auf einen anderen Layer (Cross-Pollination)."""
    return Gene(
        name=f"{g.name}->{target_layer}",
        desc=f"{g.desc} — uebertragen nach Layer {target_layer}",
        layer=target_layer, axis=g.axis, scale=g.scale,
        impact=min(1.0, g.impact + 0.05), feasibility=max(0.1, g.feasibility - 0.1),
        tags=g.tags + ["cross"],
    )


def op_category(g: Gene, category: str, rng: random.Random) -> Gene:
    """Framed ein Gen in eine Ziel-Kategorie um (Upgrade/Optim/Extension/Auto)."""
    verb = {
        "upgrades": "vertieft", "optimisations": "optimiert",
        "extensions": "erweitert", "automatisation": "automatisiert",
    }[category]
    return Gene(
        name=f"{g.name}#{category[:4]}",
        desc=f"{verb.capitalize()}: {g.desc}",
        layer=g.layer, axis=g.axis, scale=g.scale,
        impact=g.impact, feasibility=g.feasibility,
        tags=g.tags + [category],
    )


# --------------------------------------------------------------------------
# MCTS Baum
# --------------------------------------------------------------------------
@dataclass
class MCTSNode:
    gene: Gene
    parent: Optional["MCTSNode"] = None
    children: List["MCTSNode"] = field(default_factory=list)
    visits: int = 0
    value: float = 0.0
    depth: int = 0

    @property
    def ucb1(self, c: float = 1.4) -> float:
        if self.visits == 0 or self.parent is None:
            return float("inf") if self.visits == 0 else self.value / self.visits
        return self.value / self.visits + c * math.sqrt(
            math.log(self.parent.visits + 1) / (self.visits + 1)
        )

    def best_child(self):
        return max(self.children, key=lambda c: c.ucb1)


class IdeaMCTS:
    """Ein einzelner MCTS-Baum ueber dem Ideen-Raum."""

    def __init__(self, root_gene: Gene, rng: random.Random,
                 fitness_fn: Callable, category: str, max_depth: int = 4):
        self.root = MCTSNode(gene=root_gene)
        self.rng = rng
        self.fitness_fn = fitness_fn
        self.category = category
        self.max_depth = max_depth
        self._all: List[MCTSNode] = []

    def selection(self, node: MCTSNode) -> MCTSNode:
        while node.children and node.depth < self.max_depth:
            node = node.best_child()
        return node

    def expansion(self, node: MCTSNode) -> MCTSNode:
        g = node.gene
        variants = []
        for _ in range(2):
            b = self.rng.choice(seed_pool(axis=g.axis))
            variants.append(op_merge(g, b, self.rng))
        for target in ("09_neuro", "10_symbiom", "11_evolution", "12_phenotype", "api"):
            variants.append(op_cross(g, target, self.rng))
        variants.append(op_specialize(g, self.rng))
        for child in variants:
            if child == g:
                continue
            node.children.append(MCTSNode(gene=child, parent=node, depth=node.depth + 1))
        return node

    def simulate(self, node: MCTSNode) -> float:
        return self.fitness_fn(node.gene, self.category)

    def backprop(self, node: MCTSNode, reward: float):
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent

    def run(self, iterations: int):
        for _ in range(iterations):
            leaf = self.selection(self.root)
            if not leaf.children and leaf.depth < self.max_depth:
                leaf = self.expansion(leaf)
            focus = self.rng.choice(leaf.children) if leaf.children else leaf
            r = self.simulate(focus)
            self.backprop(focus, r)
        # alle besuchten Kandidaten sammeln
        self._collect(self.root)

    def _collect(self, node: MCTSNode):
        if node.visits > 0:
            self._all.append(node)
        for c in node.children:
            self._collect(c)


# --------------------------------------------------------------------------
# Fitness: Deterministische Ideen-Bewertung
# --------------------------------------------------------------------------
def idea_fitness(g: Gene, category: str) -> float:
    """Bewertet ein Gen/Idea: Impact + Machbarkeit + Kategorie-Passung + Neuartigkeit.

    Je Kategorie eigene Gewichtung -> die vier Top-100-Listen divergieren
    (Upgrades = Tiefe, Optimisations = Machbarkeit, Extensions = Neuheit,
    Automatisation = Automatisierbarkeit).
    """
    weights = {
        "upgrades":       {"impact": 0.50, "feas": 0.20, "cat": 0.20, "nov": 0.10},
        "optimisations":  {"impact": 0.25, "feas": 0.50, "cat": 0.15, "nov": 0.10},
        "extensions":     {"impact": 0.30, "feas": 0.20, "cat": 0.15, "nov": 0.35},
        "automatisation": {"impact": 0.25, "feas": 0.35, "cat": 0.15, "nov": 0.25},
    }
    w = weights[category]
    cat_fit = 0.6 if category in g.tags else 0.3 if not g.tags else 0.4
    novelty = 0.7 if "concrete" in g.tags else 0.55 if "cross" in g.tags else 0.45
    score = (w["impact"] * g.impact + w["feas"] * g.feasibility
             + w["cat"] * cat_fit + w["nov"] * novelty)
    return round(min(1.0, score), 4)


# --------------------------------------------------------------------------
# 3x3 Wald & Ranking
# --------------------------------------------------------------------------
def run_forest(seed: int = 42, iterations_per_tree: int = 400,
               top_per_category: int = 100) -> Dict[str, List[Idea]]:
    rng = random.Random(seed)
    axes = ("core", "data", "ops")
    scales = ("atomic", "component", "system")

    candidates: Dict[str, List[Idea]] = {c: [] for c in CATEGORIES}

    for axis in axes:
        for scale in scales:
            pool = seed_pool(axis=axis, scale=scale) or seed_pool(axis=axis)
            root_gene = rng.choice(pool)
            tree = IdeaMCTS(root_gene, rng, idea_fitness, "upgrades")
            tree.run(iterations_per_tree)
            for node in tree._all:
                g = node.gene
                for category in CATEGORIES:
                    framed = op_category(g, category, rng)
                    score = idea_fitness(framed, category) * min(1.0, node.visits / 5)
                    candidates[category].append(Idea(
                        title=_clean_title(framed.name),
                        category=category, axis=framed.axis, scale=framed.scale,
                        score=score, impact=framed.impact, feasibility=framed.feasibility,
                        genes=[g.name for g in seed_pool()][:3] or [root_gene.name],
                        body=_clean_title(framed.desc),
                    ))

    ranked: Dict[str, List[Idea]] = {}
    for cat in CATEGORIES:
        seen, out = set(), []
        for idea in sorted(candidates[cat], key=lambda i: (-i.score, i.title)):
            key = (idea.title, idea.body)
            if key in seen:
                continue
            seen.add(key)
            out.append(idea)
            if len(out) >= top_per_category:
                break
        ranked[cat] = out
    return ranked


# --------------------------------------------------------------------------
# Artefakte
# --------------------------------------------------------------------------
def _clean_title(s: str) -> str:
    """Entfernt interne Mutations-Suffixe (@conv, #upgr) aus Titeln/Body."""
    import re
    s = re.sub(r"@conv", "", s)
    s = re.sub(r"#[a-z]{4}", "", s)
    s = re.sub(r"->\w+", "", s)
    return s.replace("_", " ").strip().replace("  ", " ")


def build_forest_output(seed: int = 42, iterations_per_tree: int = 400,
                        out_dir: str = "reports/brainstorm_v6") -> Path:
    ranked = run_forest(seed=seed, iterations_per_tree=iterations_per_tree)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    full = {cat: [i.to_dict() for i in items] for cat, items in ranked.items()}
    (out / "top100.json").write_text(
        json.dumps({"seed": seed, "counts": {k: len(v) for k, v in ranked.items()},
                    "categories": full}, indent=2))

    # Markdown Mindmap (indented)
    md = ["# 🧠 Organic AI OS — MCTS 3x3 Forest (v6) Ideen-Mindmap", ""]
    for cat, label in CATEGORIES.items():
        md.append(f"## {label} — TOP {len(ranked[cat])}")
        for i, idea in enumerate(ranked[cat], 1):
            md.append(f"{i}. **{idea.title}** ({idea.score:.3f}) — {idea.body}")
        md.append("")
    (out / "mindmap.md").write_text("\n".join(md))

    return out


if __name__ == "__main__":
    p = build_forest_output()
    data = json.loads((p / "top100.json").read_text())
    for cat, count in data["counts"].items():
        print(f"{cat:16s}: {count}")
    print(f"\nArtefakte -> {p}")
