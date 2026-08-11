"""
LAYER 13 UI / BRAINSTORM: SEED CONCEPT LIBRARY (v6)
Codebase-grounded Ideen-Gene fuer den 3x3 MCTS-Wald.

Jedes Seed = ein Gen mit Layer-Bezug (09..12, core, api), Achse
(core/data/ops) und Skala (atomic/component/system). MCTS kombiniert,
spezialisiert und kreuzt diese Gene zu neuen Ideen.
"""

from dataclasses import dataclass, field, asdict
from typing import List


@dataclass(frozen=True)
class Gene:
    name: str
    desc: str
    layer: str                      # 09_neuro, 10_symbiom, 11_evolution, 12_phenotype, core, api
    axis: str                       # core | data | ops
    scale: str                      # atomic | component | system
    impact: float                   # 0..1
    feasibility: float              # 0..1
    tags: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


SEEDS = [
    # ---- Layer 09 Neuro / Prompt-Evolution ----
    Gene("Prompt-Selbstmutation", "Eigene Evolutions-Prompts per Fitness-Rueckkopplung neu kombinieren", "09_neuro", "core", "component", 0.85, 0.7, ["prompt", "mutation", "self"]),
    Gene("mRNA-Provenienz", "Nachvollziehbarkeit: welche Mutation erzeugte welches Prompt-Verhalten", "09_neuro", "core", "atomic", 0.6, 0.85, ["trace", "audit"]),
    Gene("Neuro-Cortex-Persistenz", "Cortex-Zustaende (Populationen) als Snapshots fuer Replay sichern", "09_neuro", "core", "component", 0.7, 0.8, ["state", "snapshot"]),

    # ---- Layer 10 Symbiom / Schwarm + Co-Evolution ----
    Gene("Symbiont-Nischendruck", "Spezialisierungs-Taxen erzwingen diverge Nischen (robust/fast/compact)", "10_symbiom", "core", "component", 0.8, 0.85, ["swarm", "niche"]),
    Gene("Symbiont-Lineage", "Ahnengeschichte je Symbiont fuer Provenienz und Replay", "10_symbiom", "core", "atomic", 0.55, 0.9, ["lineage", "tree"]),
    Gene("Co-Evo-Prompt-Hint", "Bester Code wird Prompt-Vorlage fuer naechste Prompt-Generation", "10_symbiom", "core", "component", 0.75, 0.85, ["coevolution", "feedback"]),
    Gene("Schwarm-Voting", "Mehrheits-Fitness der Spezialisten statt Einzel-Bestwert", "10_symbiom", "core", "component", 0.6, 0.75, ["voting", "ensemble"]),

    # ---- Layer 11 Evolution ----
    Gene("AdverMCTS-Testbank", "Gegnerische Randfaelle decken Pseudo-Korrektheit auf", "11_evolution", "core", "component", 0.9, 0.7, ["mcts", "adversarial"]),
    Gene("Process-Reward (RPM)", "Belohnung fuer Zwischenschritte (Kompaktheit, Robustheit)", "11_evolution", "core", "atomic", 0.7, 0.85, ["reward", "shaping"]),
    Gene("MCTS-Budget-Guard", "Rollout-Budget nach Token/Kosten deckeln (PRM)", "11_evolution", "ops", "component", 0.75, 0.8, ["budget", "cost"]),
    Gene("Skill-Tactic-Bibliothek", "Erfolgreiche MCTS-Rollouts als wiederverwendbare Skills", "11_evolution", "core", "component", 0.8, 0.75, ["skills", "library"]),
    Gene("Hall-of-Fame-Meta", "Champions dienen als Population-Matrix fuer neue Generationen", "11_evolution", "core", "component", 0.65, 0.9, ["hof", "meta"]),

    # ---- Layer 12 Phenotyp / API / Reporter ----
    Gene("Distanz-Tracking", "Latenz/Fehlerrate je API-Endpoint messen und loggen", "12_phenotype", "ops", "atomic", 0.55, 0.9, ["metrics", "observability"]),
    Gene("Tagesreport-Erweiterung", "Report um Skill-Bibliothek + Symbiom-HoF + Co-Evo-Felder erweitern", "12_phenotype", "ops", "component", 0.6, 0.85, ["report", "insight"]),
    Gene("Fitness-Sparklines", "Fitness-Historie als JSON-Serie fuer Visualisierung", "12_phenotype", "ops", "atomic", 0.5, 0.9, ["viz", "history"]),

    # ---- Core / Organismus ----
    Gene("Naechtliche Evolution als Loop", "Evolution taeglich als selbst-heilender Event-Loop", "core", "ops", "system", 0.85, 0.9, ["loop", "nightly"]),
    Gene("Immunsystem-Memory", "Failures als Antikoerper-Muster fuer Heilung wiederverwenden", "core", "core", "component", 0.8, 0.7, ["immune", "heal"]),
    Gene("Fitness-Fruehwarnung", "Score-Drop-Alarm stoppt Regression vor Promotions", "core", "ops", "atomic", 0.7, 0.85, ["guard", "regression"]),

    # ---- Data / Formate ----
    Gene("FASTQ-Support", "Qualitaets-Scores parsen und validieren", "core", "data", "component", 0.85, 0.8, ["fastq", "format"]),
    Gene("GFF3/VCF-Parser", "Genom-Annotationen und Varianten unterstuetzen", "core", "data", "system", 0.8, 0.7, ["gff3", "vcf"]),
    Gene("Kmer-Index", "k-mer-Inventar pro Sequenz fuer Analyse", "core", "data", "component", 0.75, 0.7, ["kmer", "analysis"]),
    Gene("Streaming-Parser", "Sehr grosse FASTA in Chunks statt RAM", "core", "data", "component", 0.8, 0.65, ["stream", "memory"]),
    Gene("Validierungs-Schema", "Format-Spec als maschinenlesbares Schema", "core", "data", "atomic", 0.65, 0.9, ["spec", "schema"]),

    # ---- Ops / API ----
    Gene("REST-Dashboard", "Web-UI fuer Organismus-Zustand und Evolution", "api", "ops", "system", 0.9, 0.75, ["ui", "dashboard"]),
    Gene("Prompt-Hint-API", "Co-Evo-Ergebnis (prompt_hint) per Endpoint auslesen", "api", "core", "atomic", 0.5, 0.95, ["api", "coevo"]),
    Gene("Memory-Atomar-Save", "Konsistente atomare Schreibzugriffe verhindern Korruption", "core", "ops", "atomic", 0.6, 0.9, ["atomic", "durability"]),
    Gene("Webhook-Out", "Evolution-Events als Webhooks nach aussen", "api", "ops", "component", 0.55, 0.8, ["webhook", "events"]),
]


def seed_pool(axis=None, scale=None):
    """Filtert die Seed-Gene nach Achse und/oder Skala."""
    out = []
    for g in SEEDS:
        if axis and g.axis != axis:
            continue
        if scale and g.scale != scale:
            continue
        out.append(g)
    return out


def gene_by_layer(layer):
    return [g for g in SEEDS if g.layer == layer]
