
"""
LAYER 11: EVOLUTION - Echte Code-Mutation via LLM
Prinzip: DNA -> Mutation (LLM) -> Selektion (Fitness) -> Replikation
Inspiriert von Bioinformatik: Punktmutation, Insertion, Deletion, Rekombination
"""

import ast
import random
import re
from dataclasses import dataclass, field
from typing import List, Callable, Dict, Tuple

@dataclass
class Strand:
    name: str
    code: str
    fitness: float = 0.0
    generation: int = 0
    lineage: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_prompt(self):
        return f"# Name: {self.name} (Gen {self.generation}, Fit {self.fitness:.3f})\n{self.code}"

# --- FITNESS FUNKTIONEN (Selektionsdruck) ---
class FitnessEvaluator:
    """Bewertet wie gut ein Code-Strang ist - wie natürliche Selektion"""
    
    @staticmethod
    def evaluate(code: str, tests: List[Tuple[Callable, float]]) -> float:
        """
        tests = [(test_fn, weight), ...]
        test_fn bekommt exec namespace und returned bool/score
        """
        score = 0.0
        total_weight = 0.0
        
        # 1. Syntax Fitness - kann es überhaupt leben?
        try:
            ast.parse(code)
            score += 1.0 * 0.2
        except Exception:
            return 0.0  # lethal mutation
        total_weight += 0.2
        
        # 2. Ausführungs-Fitness
        for test_fn, weight in tests:
            try:
                ns = {}
                exec(code, {}, ns)
                result = test_fn(ns)
                if isinstance(result, bool):
                    score += (1.0 if result else 0.0) * weight
                else:
                    score += float(result) * weight
            except Exception as e:
                # leichte Bestrafung, nicht lethal - ermöglicht Selbstheilung
                score += 0.0
            total_weight += weight
            
        # 3. Komplexitäts-Bonus - nicht zu aufgebläht (Parsimonie)
        lines = len(code.splitlines())
        complexity_penalty = max(0, (lines - 20) * 0.02)
        
        return max(0.0, (score / total_weight if total_weight>0 else 0) - complexity_penalty)


# --- LLM MUTATOR ---
class LLMMutator:
    """
    Echter LLM Mutator. Funktioniert mit:
    - Ollama lokal (kostenlos)
    - OpenAI API
    - Fallback: AST-basierte organische Mutation (wenn kein LLM)
    """
    
    MUTATION_PROMPTS = {
        "point": "Führe eine Punktmutation durch: Ändere eine einzelne Logikstelle, Variable oder Konstante. Erhalte die Funktionssignatur.",
        "insert": "Führe eine Insertion durch: Füge eine sinnvolle neue Fähigkeit, einen Check oder ein Feature hinzu. Max 3 neue Zeilen.",
        "delete": "Führe eine Deletion durch: Vereinfache den Code, entferne Redundanz, mache ihn eleganter.",
        "crossover": "Rekombiniere die Stärken beider Eltern. Nimm die beste Logik aus beiden.",
        "optimize": "Optimiere für Performance und Lesbarkeit. Nutze Pythonic Idioms aus Bioinformatics Programming (List Comprehensions, Generators).",
        "neo": "Erfinde eine völlig neue Variante mit gleicher Signatur aber anderem Ansatz (z.B. rekursiv statt iterativ)."
    }
    
    def __init__(self, llm_provider="fallback"):
        self.provider = llm_provider
        self._ollama = None
        if self.provider == "ollama":
            try:
                from ollama_integration import OllamaMutator
                self._ollama = OllamaMutator()
            except (ImportError, ConnectionError) as e:
                self.provider = "fallback"

    def _call_llm(self, system: str, user: str) -> str:
        """LLM call: Ollama wenn verfuegbar, sonst intelligenter AST-Fallback."""
        if self.provider == "ollama" and self._ollama is not None:
            try:
                return self._ollama.mutate(user, system)
            except ConnectionError as e:
                self.provider = "fallback"
                return self._fallback_mutate(system, user)
        if self.provider == "fallback":
            return self._fallback_mutate(system, user)
        return user.split("```python")[-1].split("```")[0] if "```" in user else user
    
    def _fallback_mutate(self, instruction: str, code_context: str) -> str:
        """Bio-inspirierte AST Mutation wenn kein LLM - trotzdem organisch!"""
        # Extrahiere reinen Code aus Kontext
        m = re.search(r"```python(.*?)```", code_context, re.DOTALL)
        if m:
            code = m.group(1).strip()
        else:
            # nimm letzten Codeblock
            parts = code_context.split("CODE:")
            code = parts[-1].strip() if len(parts)>1 else code_context
        
        try:
            tree = ast.parse(code)
            
            # Zufällige organische Operatoren
            mutations = []
            
            # 1. Konstanten mutieren
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                    if random.random() < 0.5:
                        node.value = node.value * random.uniform(0.8, 1.25)
                        mutations.append(f"const {node.value}")
            
            # 2. Operator tauschen
            for node in ast.walk(tree):
                if isinstance(node, ast.BinOp):
                    if random.random() < 0.3:
                        node.op = random.choice([ast.Add(), ast.Mult(), ast.Sub()])
            
            # Unparse zurück
            new_code = ast.unparse(tree)
            
            # Manchmal kleine Insertion
            if "insert" in instruction.lower() and random.random() < 0.5:
                lines = new_code.splitlines()
                insert_at = random.randint(0, len(lines)-1)
                lines.insert(insert_at, "    # [ORGANIC INSERT] adaptive check")
                new_code = "\n".join(lines)
            
            return new_code
        except Exception:
            # Wenn AST failt: einfache Textmutation
            lines = code.splitlines()
            if lines:
                idx = random.randrange(len(lines))
                if "return" in lines[idx]:
                    lines[idx] = lines[idx].replace("return", "return (  # mutated")
                return "\n".join(lines)
            return code
    
    def mutate(self, strand: Strand, strategy: str = None) -> Strand:
        strategy = strategy or random.choice(list(self.MUTATION_PROMPTS.keys()))
        instruction = self.MUTATION_PROMPTS[strategy]
        
        prompt = f"""
Du bist eine organische Mutations-Engine für Python Code.

AUFGABE: {instruction}

ORIGINAL STRAND:
```python
{strand.code}
```

REGELN:
- Erhalte Funktionsnamen und Signatur
- Code muss valides Python bleiben
- Keine Imports wenn nicht nötig
- Max 30 Zeilen
- Antworte NUR mit Python Codeblock

MUTIERTER CODE:
"""
        
        mutated_code = self._call_llm("Du bist ein Python Evolutionsexperte.", prompt)
        # Clean
        mutated_code = re.sub(r"^```python|^```|```$", "", mutated_code, flags=re.MULTILINE).strip()
        
        return Strand(
            name=f"{strand.name}_m{strand.generation+1}",
            code=mutated_code,
            generation=strand.generation+1,
            lineage=strand.lineage + [strand.name],
            metadata={"parent_fitness": strand.fitness, "mutation": strategy}
        )
    
    def crossover(self, a: Strand, b: Strand) -> Strand:
        prompt = f"""
CROSSOVER zweier Eltern:

ELTERN A (Fit {a.fitness:.2f}):
```python
{a.code}
```

ELTERN B (Fit {b.fitness:.2f}):
```python
{b.code}
```

Erzeuge ein Kind das beide Stärken kombiniert.
"""
        # Fallback Crossover: nimm Hälfte von A, Hälfte von B
        lines_a = a.code.splitlines()
        lines_b = b.code.splitlines()
        mid = len(lines_a)//2
        child_code = "\n".join(lines_a[:mid] + lines_b[mid:])
        fallback = child_code
        
        # Versuche LLM; bei Fehler bleibt der Merged-Fallback aktiv
        try:
            child_code = self._call_llm("Crossover Experte", prompt)
            child_code = re.sub(r"^```python|^```|```$", "", child_code, flags=re.MULTILINE).strip()
        except Exception:
            child_code = fallback
        
        return Strand(
            name=f"{a.name}x{b.name}_g{max(a.generation,b.generation)+1}",
            code=child_code,
            generation=max(a.generation,b.generation)+1,
            lineage=list(set(a.lineage + b.lineage + [a.name, b.name])),
            metadata={"crossover": f"{a.name}+{b.name}"}
        )


# --- EVOLUTIONS-ENGINE ---
class EvolutionEngine:
    def __init__(self, population_size=8, mutator=None, hall_of_fame_size=5):
        self.population: List[Strand] = []
        self.history: List[List[Strand]] = []
        self.mutator = mutator or LLMMutator("fallback")
        self.pop_size = population_size
        self.hall_of_fame: List[Strand] = []
        self.hall_of_fame_size = hall_of_fame_size

    def _update_hall_of_fame(self):
        candidates = self.population + self.hall_of_fame
        # Diversity Guard: verwerfe nahezu identischen Code, kuerzester gewinnt
        unique: List[Strand] = []
        seen_codes = set()
        for s in sorted(candidates, key=lambda x: (x.fitness, -len(x.code)), reverse=True):
            key = re.sub(r"\s+", "", s.code)[:200]
            if key in seen_codes:
                continue
            seen_codes.add(key)
            unique.append(s)
        self.hall_of_fame = unique[: self.hall_of_fame_size]

    def seed(self, initial_code: str, name="adam"):
        adam = Strand(name=name, code=initial_code, fitness=0.0, generation=0)
        self.population = [adam]
        # Initiale Diversifizierung
        for i in range(self.pop_size-1):
            child = self.mutator.mutate(adam, strategy=random.choice(["point","neo","insert"]))
            child.name = f"{name}_seed_{i}"
            self.population.append(child)
    
    def evolve(self, fitness_fn: FitnessEvaluator, tests, generations=10):
        print(f"\n🧬 EVOLUTION START - Pop {len(self.population)}, {generations} Generationen")
        
        for gen in range(generations):
            # 1. Fitness bewerten
            for s in self.population:
                s.fitness = fitness_fn.evaluate(s.code, tests)
            
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            best = self.population[0]
            print(f"Gen {gen}: Best {best.name} Fit={best.fitness:.3f} [{best.metadata.get('mutation','seed')}]")
            
            self.history.append(self.population.copy())
            self._update_hall_of_fame()
            
            if best.fitness >= 0.95:
                print(f"🎯 Perfekte Fitness erreicht in Gen {gen}!")
                break
            
            # 2. Selektion - Tournament
            next_gen = [best]  # Elitismus: Bestes überlebt
            
            while len(next_gen) < self.pop_size:
                # Tournament selection
                tournament = random.sample(self.population, k=3)
                tournament.sort(key=lambda x: x.fitness, reverse=True)
                parent = tournament[0]
                
                r = random.random()
                if r < 0.7:
                    # Mutation
                    child = self.mutator.mutate(parent)
                elif r < 0.9 and len(self.population) > 1:
                    # Crossover
                    parent2 = random.choice(self.population)
                    child = self.mutator.crossover(parent, parent2)
                else:
                    # Replikation mit leichter Drift
                    child = self.mutator.mutate(parent, strategy="point")
                
                next_gen.append(child)
            
            self.population = next_gen
        
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        return self.population[0]

# --- DEMO ---
if __name__ == "__main__":
    # Ziel: Evolviere eine bessere GC-Content Funktion (aus deinem Buch!)
    initial = """
def gc_content(seq):
    gc = seq.count("G") + seq.count("C")
    return gc / len(seq) if seq else 0
"""
    def test_correctness(ns):
        if "gc_content" not in ns: return False
        fn = ns["gc_content"]
        try:
            return abs(fn("GGCCAA") - 0.666) < 0.01
        except Exception:
            return False
    tests = [(test_correctness, 0.8)]
    engine = EvolutionEngine(population_size=6, mutator=LLMMutator("fallback"))
    engine.seed(initial, name="gc_adam")
    winner = engine.evolve(FitnessEvaluator, tests, generations=5)
    print(winner.code) 