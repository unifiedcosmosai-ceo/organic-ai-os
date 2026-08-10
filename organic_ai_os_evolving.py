
import ast, re, time, random, json
from dataclasses import dataclass, field
from typing import Dict, List, Callable

@dataclass
class Strand:
    layer: str
    name: str
    code: str
    fitness: float = 0.0
    generation: int = 0
    lineage: List[str] = field(default_factory=list)

class Genom:
    def __init__(self):
        self.strands: Dict[str, Strand] = {}
    def add(self, strand: Strand):
        self.strands[strand.name] = strand
        print(f"[GENOM] {strand.layer}/{strand.name} Gen{strand.generation}")
    def get_layer(self, prefix: str) -> List[Strand]:
        return [s for s in self.strands.values() if s.layer.startswith(prefix)]

class EvolutionDock:
    def __init__(self, genom: Genom):
        self.genom = genom
        self.mutation_log = []
    
    def mutate(self, strand: Strand, strategy: str) -> Strand:
        code = strand.code
        if strategy == "heal" and "try:" not in code:
            code = code.replace("    records = {}", "    try:\n        records = {}")
            if "return records" in code:
                code = code.replace("    return records", "        return records\n    except Exception as e:\n        return {\"error\": str(e)}")
        elif strategy == "insert":
            if "strip()" not in code:
                code = code.replace("line", "line.strip()")
        elif strategy == "optimize":
            code = code.replace('split("\\n")', 'splitlines()')
        elif strategy == "neo":
            code = code + "\n    # neo symbiont"
        
        child = Strand(layer=strand.layer, name=f"{strand.name}_g{strand.generation+1}", code=code, generation=strand.generation+1, lineage=strand.lineage+[strand.name])
        self.genom.add(child)
        self.mutation_log.append({"parent": strand.name, "child": child.name, "strat": strategy})
        return child

    def evaluate(self, strand: Strand, tests) -> float:
        try:
            ast.parse(strand.code)
        except:
            return 0.0
        score=0
        for fn, w in tests:
            try:
                ns={}
                exec(strand.code, {}, ns)
                r=fn(ns, strand)
                score+= (r if isinstance(r,float) else (1.0 if r else 0.0))*w
            except:
                pass
        if "try:" in strand.code: score+=0.05
        if "yield" in strand.code: score+=0.05
        strand.fitness = min(1.0, score)
        return strand.fitness

    def evolve_layer(self, prefix, tests, generations=6, pop_size=6):
        print(f"\n EVOLVIERE {prefix}")
        pop = self.genom.get_layer(prefix)
        for gen in range(generations):
            for s in pop:
                self.evaluate(s, tests)
            pop.sort(key=lambda x: x.fitness, reverse=True)
            best=pop[0]
            print(f" Gen {gen}: best={best.name} fit={best.fitness:.3f}")
            if best.fitness>=0.95:
                break
            next_gen=[best]
            while len(next_gen)<pop_size:
                parent=random.choice(pop[:3])
                strat=random.choice(["heal","insert","optimize","neo"])
                child=self.mutate(parent, strat)
                next_gen.append(child)
            pop=next_gen
        best=max(pop, key=lambda x: x.fitness)
        print(f" WINNER {best.name} fit={best.fitness:.3f}")
        return best

class OrganicAI_OS_Evolving:
    def __init__(self):
        self.genom=Genom()
        self.evolution=EvolutionDock(self.genom)
        self.boot()
    def boot(self):
        seeds={
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
"""
        }
        for name, c in seeds.items():
            self.genom.add(Strand(layer="03_proteom", name=name, code=c))
    def run(self):
        print("=== ORGANIC OS ===")
        for s in self.genom.strands.values():
            print(f" {s.layer}/{s.name}")

if __name__=="__main__":
    osys=OrganicAI_OS_Evolving()
    osys.run()
    def test_basic(ns, strand):
        if "parse_fasta" not in ns: return False
        try:
            r=ns["parse_fasta"](">a\nATGC\n>b\nGG")
            return len(r)==2
        except:
            return False
    def test_robust(ns, strand):
        if "parse_fasta" not in ns: return 0
        try:
            r=ns["parse_fasta"](">a messy\n  atgc  \n\n>b\nGG")
            return 1.0 if len(r)==2 and all(" " not in v for v in r.values()) else 0.5
        except:
            return 0
    winner=osys.evolution.evolve_layer("03_proteom", [(test_basic,0.5),(test_robust,0.5)], generations=8)
    print("\nFINAL WINNER:\n", winner.code)
