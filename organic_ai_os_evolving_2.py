
"""
ORGANIC AI OS v2 - SELBST-EVOLVIEREND
Layer 11 dockt an alle anderen Layer an

Architektur:
- Genom speichert alle Layer als DNA
- Evolution Engine mutiert Proteom/Transkriptom/etc
- Fitness = ob Layer funktioniert + ob Gesamt-OS überlebt
- Endlosschleife: Umgebung -> Mutation -> Selektion
"""

import ast, re, time, random, json, shelve
from dataclasses import dataclass, field
from typing import Dict, List, Callable
from pathlib import Path

# ==================== CORE ORGANIC ====================
@dataclass
class Strand:
    layer: str  # z.B. "03_proteom"
    name: str
    code: str
    fitness: float = 0.0
    generation: int = 0
    lineage: List[str] = field(default_factory=list)
    last_used: float = field(default_factory=time.time)

class Genom:
    def __init__(self):
        self.strands: Dict[str, Strand] = {}  # name -> Strand
    
    def add(self, strand: Strand):
        self.strands[strand.name] = strand
        print(f"🧬 [GENOM] {strand.layer}/{strand.name} Gen{strand.generation} eingefügt")
    
    def get_layer(self, layer_prefix: str) -> List[Strand]:
        return [s for s in self.strands.values() if s.layer.startswith(layer_prefix)]

# ==================== LAYER 11 - EVOLUTION ENGINE (angeschlossen) ====================
class EvolutionDock:
    """
    Dockt an das Genom an und evolviert Layer 3 (Proteom) und andere
    """
    def __init__(self, genom: Genom):
        self.genom = genom
        self.mutation_log = []
        self.MUTATIONS = {
            "point": "Ändere eine Logikstelle, behalte Signatur",
            "insert": "Füge robusten Check hinzu (strip, upper, try)",
            "optimize": "Nutze Generator, Comprehension, pre-compiled regex",
            "neo": "Erfinde neue Variante mit gleicher Aufgabe",
            "heal": "Repariere Bug, füge Error-Handling hinzu"
        }
    
    def _llm_mutate(self, strand: Strand, strategy: str) -> Strand:
        # Echte LLM Mutation simuliert - hier mit intelligenten Templates
        # In Produktion: ollama.chat() oder openai
        code = strand.code
        
        # Organische Mutations-Bibliothek
        if strategy == "heal":
            if "try:" not in code:
                # Füge Immunsystem hinzu
                lines = code.splitlines()
                # finde def zeile
                for i,l in enumerate(lines):
                    if "def " in l:
                        indent = len(l)-len(l.lstrip())
                        # wrap body in try
                        body_start = i+1
                        if body_start < len(lines):
                            lines.insert(body_start, " "*(indent+4)+"try:")
                            # indent rest
                            for j in range(body_start+1, len(lines)):
                                if lines[j].strip() and not lines[j].strip().startswith("#"):
                                    if not lines[j].startswith(" "* (indent+8)):
                                        lines[j] = "    " + lines[j]
                            lines.append(" "*(indent+4)+"except Exception as e:")
                            lines.append(" "*(indent+8)+'return {"error": str(e), "healed": True}')
                            break
                code = "\n".join(lines)
        
        elif strategy == "insert":
            if "strip()" not in code:
                code = code.replace("line", "line.strip()")
            if "upper()" not in code and "seq" in code.lower():
                code = code.replace(".strip()", ".strip().upper()")
        
        elif strategy == "optimize":
            code = code.replace('text.split("\\n")', 'text.splitlines()')
            code = code.replace('text.split("\n")', 'text.splitlines()')
            if "re." not in code and "for line in" in code:
                # füge pre-compiled regex hinzu
                code = code.replace("def ", 'import re\n\nWS = re.compile(r"\\s+")\n\ndef ', 1)
        
        elif strategy == "neo":
            # Erzeuge Generator Variante wenn noch keine
            if "yield" not in code and "def parse" in code:
                code = code.replace("return records", "return records\n\n    # Symbiont\n    # yield version available")
        
        # Erzeuge Kind
        child = Strand(
            layer=strand.layer,
            name=f"{strand.name}_g{strand.generation+1}",
            code=code,
            generation=strand.generation+1,
            lineage=strand.lineage + [strand.name]
        )
        child.fitness = 0  # wird neu bewertet
        self.mutation_log.append({
            "parent": strand.name,
            "child": child.name,
            "strategy": strategy,
            "time": time.time()
        })
        return child
    
    def evaluate_fitness(self, strand: Strand, test_suite: List[Callable]) -> float:
        try:
            ast.parse(strand.code)
        except:
            return 0.0  # lethal
        
        score = 0
        for test_fn, weight in test_suite:
            try:
                ns = {}
                exec(strand.code, {}, ns)
                res = test_fn(ns, strand)
                score += (res if isinstance(res, float) else (1.0 if res else 0.0)) * weight
            except:
                score += 0
        
        # Bonus für organische Merkmale
        if "try:" in strand.code: score += 0.05
        if "yield" in strand.code: score += 0.05
        if "re.compile" in strand.code: score += 0.03
        
        strand.fitness = min(1.0, score)
        return strand.fitness
    
    def evolve_layer(self, layer_prefix: str, test_suite, generations=5, pop_size=6):
        print(f"\n🧬 EVOLVIERE LAYER {layer_prefix} - {generations} Gen")
        population = self.genom.get_layer(layer_prefix)
        if not population:
            print(f"Kein Strand in {layer_prefix}")
            return
        
        for gen in range(generations):
            # Fitness
            for s in population:
                self.evaluate_fitness(s, test_suite)
            
            population.sort(key=lambda x: x.fitness, reverse=True)
            best = population[0]
            print(f" Gen {gen}: best={best.name} fit={best.fitness:.3f} gen={best.generation}")
            
            if best.fitness >= 0.95:
                break
            
            # Selektion + Mutation
            next_gen = [best]  # Elitismus
            while len(next_gen) < pop_size:
                parent = random.choice(population[:3])  # Tournament top3
                strategy = random.choice(list(self.MUTATIONS.keys()))
                child = self._llm_mutate(parent, strategy)
                # sofort ins Genom
                self.genom.add(child)
                next_gen.append(child)
            
            population = next_gen
        
        # Bestes zurück ins Genom als aktiv
        best = max(population, key=lambda x: x.fitness)
        print(f"✅ {layer_prefix} evolviert -> {best.name} fit={best.fitness:.3f}")
        return best

# ==================== ORGANIC OS MIT EVOLUTION ====================
class OrganicAI_OS_Evolving:
    def __init__(self):
        self.genom = Genom()
        self.evolution = EvolutionDock(self.genom)
        self.boot()
    
    def boot(self):
        # Seed alle 12 Layer als DNA
        seeds = {
            "01_genom": 'def store(key, code): return f"stored {key}"',
            "02_transkriptom": 'def transcribe(code): import ast; return compile(ast.parse(code), "<dna>", "exec")',
            "03_proteom_fasta": """def parse_fasta(text):
    records = {}
    header = ""
    for line in text.split("\\n"):
        if line.startswith(">"):
            header = line[1:]
            records[header] = ""
        else:
            records[header] += line
    return records
""",
            "03_proteom_gc": """def gc_content(seq):
    gc = seq.count("G") + seq.count("C")
    return gc / len(seq) if seq else 0
""",
            "09_neuro_prompt": "def build_prompt(kind): return f'Du bist {kind} Experte.'",
        }
        for name, code in seeds.items():
            layer = name.rsplit("_", 1)[0]
            self.genom.add(Strand(layer=layer, name=name, code=code))

    def run(self, generations=8, pop_size=6):
        print("=== ORGANIC AI OS v2 ===")
        for s in self.genom.strands.values():
            print(f" 🧬 {s.layer}/{s.name} Gen{s.generation}")

        def test_basic(ns, strand):
            if "parse_fasta" not in ns: return False
            try:
                r = ns["parse_fasta"](">a\nATGC\n>b\nGG")
                return len(r) == 2
            except:
                return False

        def test_robust(ns, strand):
            if "parse_fasta" not in ns: return 0
            try:
                r = ns["parse_fasta"](">a messy\n  atgc  \n\n>b\nGG")
                return 1.0 if len(r) == 2 and all(" " not in v for v in r.values()) else 0.5
            except:
                return 0

        winner = self.evolution.evolve_layer(
            "03_proteom",
            [(test_basic, 0.5), (test_robust, 0.5)],
            generations=generations,
            pop_size=pop_size,
        )
        if winner:
            print("\nFINAL WINNER:\n", winner.code)
        return winner


if __name__ == "__main__":
    osys = OrganicAI_OS_Evolving()
    osys.run() 