
"""
AUTONOMER ORGANISMUS - Live FASTA Watcher + Nächtliche Evolution
Beobachtet Ordner, lernt aus echten Daten, verbessert sich nachts

Run: python autonomous_organism.py
"""

import time, json, hashlib, ast, re, random
from pathlib import Path
from datetime import datetime, timedelta
import threading
from dataclasses import dataclass, field
from typing import List, Dict

# Import aus deinen Layern
import sys
sys.path.insert(0, str(Path(__file__).parent / "11_evolution"))
sys.path.insert(0, str(Path(__file__).parent / "09_neuro"))
try:
    from llm_evolver import Strand, FitnessEvaluator, LLMMutator, EvolutionEngine
    print("✅ Evolution Engine geladen")
except Exception as e:
    print(f"Fallback Evolution Engine: {e}")
    @dataclass
    class Strand:
        name: str; code: str; fitness: float=0.0; generation: int=0; lineage: List[str]=field(default_factory=list); metadata: Dict=field(default_factory=dict)
    class FitnessEvaluator:
        @staticmethod
        def evaluate(code, tests):
            import ast
            try: ast.parse(code)
            except: return 0.0
            score=0
            for fn,w in tests:
                try:
                    ns={}; exec(code, {}, ns)
                    score+=(1.0 if fn(ns) else 0.0)*w
                except: pass
            return score
    class LLMMutator:
        def __init__(self, provider="fallback"): self.provider=provider
        def mutate(self, strand, strategy=None):
            import random, re
            code=strand.code
            if "strip()" not in code:
                code=code.replace("line", "line.strip()")
            child=Strand(name=f"{strand.name}_m{strand.generation+1}", code=code, generation=strand.generation+1)
            return child
    class EvolutionEngine:
        def __init__(self, population_size=6, mutator=None):
            self.population=[]; self.mutator=mutator or LLMMutator(); self.pop_size=population_size
        def seed(self, code, name="adam"):
            self.population=[Strand(name=name, code=code)]
            for i in range(self.pop_size-1):
                child=self.mutator.mutate(self.population[0])
                child.name=f"{name}_seed_{i}"
                self.population.append(child)
        def evolve(self, fitness_fn, tests, generations=5):
            for gen in range(generations):
                for s in self.population:
                    s.fitness=fitness_fn.evaluate(s.code, tests)
                self.population.sort(key=lambda x: x.fitness, reverse=True)
                best=self.population[0]
                print(f" Gen {gen}: best={best.name} fit={best.fitness:.3f}")
                next_gen=[best]
                while len(next_gen)<self.pop_size:
                    parent=self.population[0]
                    child=self.mutator.mutate(parent)
                    next_gen.append(child)
                self.population=next_gen
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            return self.population[0]


WATCH_DIR = Path(__file__).parent / "fasta_inbox"
MEMORY_DIR = Path(__file__).parent / "memory"
WATCH_DIR.mkdir(exist_ok=True)
MEMORY_DIR.mkdir(exist_ok=True)

# --- MEMORY: Was hat der Organismus gelernt? ---
class OrganismMemory:
    def __init__(self):
        self.db_path = MEMORY_DIR / "organism_memory.json"
        self.data = self.load()
    
    def load(self):
        if self.db_path.exists():
            return json.loads(self.db_path.read_text())
        return {"seen_files": {}, "failures": [], "best_strands": {}, "prompt_history": [], "evolution_count": 0}
    
    def save(self):
        self.db_path.write_text(json.dumps(self.data, indent=2))
    
    def remember_file(self, filepath: Path, content: str, parsed_ok: bool, error=""):
        h = hashlib.md5(content.encode()).hexdigest()[:8]
        self.data["seen_files"][str(filepath)] = {
            "hash": h,
            "size": len(content),
            "parsed_ok": parsed_ok,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "atypical": self.detect_atypical(content)
        }
        if not parsed_ok:
            self.data["failures"].append({"file": str(filepath), "error": error, "atypical": self.detect_atypical(content)})
        self.save()
    
    def detect_atypical(self, content: str) -> Dict:
        """Erkennt ungewöhnliche FASTA Merkmale - das löst Evolution aus"""
        atypical = {}
        if " " in content.splitlines()[1] if len(content.splitlines())>1 else False:
            atypical["spaces_in_seq"] = True
        if any(c.islower() for c in content):
            atypical["lowercase"] = True
        if "\r" in content:
            atypical["crlf"] = True
        if content.count(">") > 1000:
            atypical["huge_file"] = True
        if "  " in content:
            atypical["double_spaces"] = True
        if re.search(r">.*\|.*\|", content):
            atypical["uniprot_format"] = True
        return atypical

# --- LIVE WATCHER ---
class FastaWatcher:
    def __init__(self, memory: OrganismMemory):
        self.memory = memory
        self.active_parser_code = self.load_best_parser()
    
    def load_best_parser(self):
        best_path = MEMORY_DIR / "best_parser.py"
        if best_path.exists():
            return best_path.read_text()
        # Adam
        return """
def parse_fasta(text):
    records={}
    curr=None
    buf=[]
    for line in text.splitlines():
        s=line.strip()
        if not s: continue
        if s.startswith(">"):
            if curr: records[curr]="".join(buf)
            curr=s[1:].split()[0]
            buf=[]
        else:
            buf.append(s)
    if curr: records[curr]="".join(buf)
    return records
"""
    
    def try_parse(self, content: str):
        try:
            ns={}
            exec(self.active_parser_code, {}, ns)
            fn=ns["parse_fasta"]
            result=fn(content)
            return True, result, ""
        except Exception as e:
            return False, None, str(e)
    
    def scan_once(self):
        print(f"\n👁️  SCAN {WATCH_DIR} um {datetime.now().strftime('%H:%M:%S')}")
        for fasta_file in WATCH_DIR.glob("*.fa*"):
            if fasta_file.suffix in [".fasta",".fa",".txt",".fas"]:
                content = fasta_file.read_text(errors="ignore")
                ok, result, err = self.try_parse(content)
                is_new = str(fasta_file) not in self.memory.data["seen_files"]
                if is_new or not ok:
                    print(f" {'✅' if ok else '❌'} {fasta_file.name}: ok={ok} {err[:60] if err else f'{len(result)} records'}")
                    if not is_new and ok:
                        # schon gesehen und ok - skip
                        continue
                self.memory.remember_file(fasta_file, content, ok, err)
                
                # Wenn Fehler -> sofortige Notfall-Heilung (Layer 08 Immunsystem)
                if not ok:
                    print(f" 🚨 Immunsystem triggert Schnell-Heilung für {fasta_file.name}")
                    self.emergency_heal(err, content)
    
    def emergency_heal(self, error: str, content: str):
        # Einfache Heilung: füge strip(), upper() hinzu
        code = self.active_parser_code
        if "strip()" not in code:
            code = code.replace("line", "line.strip()")
            code = code.replace("s=line.strip()", "s=line.strip()")
        if "upper()" not in code and "lowercase" in error.lower() or True:
            # generell upper hinzufügen
            if "upper()" not in code:
                code = code.replace('buf.append(s)', 'buf.append(s.upper())')
        
        # Teste Heilung
        try:
            ns={}
            exec(code, {}, ns)
            fn=ns["parse_fasta"]
            fn(content)
            print(f" 🩹 Heilung erfolgreich - neuer Parser gespeichert")
            (MEMORY_DIR / "best_parser.py").write_text(code)
            self.active_parser_code = code
            self.memory.data["best_strands"]["emergency_heal"] = {"code": code, "time": datetime.now().isoformat()}
            self.memory.save()
        except Exception as e:
            print(f" Heilung fehlgeschlagen: {e}")

# --- NÄCHTLICHE EVOLUTION ---
class NightlyEvolution:
    def __init__(self, memory: OrganismMemory, watcher: FastaWatcher):
        self.memory = memory
        self.watcher = watcher
    
    def build_tests_from_failures(self):
        """Baut Tests aus echten fehlgeschlagenen Files - das ist der Selektionsdruck"""
        failures = self.memory.data["failures"][-10:]  # letzte 10
        if not failures:
            # Default Tests
            return [
                (lambda ns: self._test_basic(ns), 0.5),
                (lambda ns: self._test_robust(ns), 0.5),
            ]
        
        tests = []
        for fail in failures:
            # Für jedes Failure einen spezifischen Test generieren
            atyp = fail.get("atypical", {})
            if atyp.get("lowercase"):
                tests.append((lambda ns, f=fail: self._test_lowercase(ns), 0.3))
            if atyp.get("spaces_in_seq"):
                tests.append((lambda ns, f=fail: self._test_spaces(ns), 0.3))
            if atyp.get("uniprot_format"):
                tests.append((lambda ns, f=fail: self._test_uniprot(ns), 0.3))
        
        # immer Basis Tests
        tests.append((lambda ns: self._test_basic(ns), 0.4))
        tests.append((lambda ns: self._test_robust(ns), 0.3))
        return tests
    
    def _test_basic(self, ns):
        if "parse_fasta" not in ns: return False
        try:
            r=ns["parse_fasta"](">a\nATGC\n>b\nGG")
            return len(r)==2
        except: return False
    
    def _test_robust(self, ns):
        if "parse_fasta" not in ns: return False
        try:
            r=ns["parse_fasta"](">a messy\n  atgc  \n\n>b\nGG")
            return len(r)==2 and all(" " not in v for v in r.values())
        except: return False
    
    def _test_lowercase(self, ns):
        if "parse_fasta" not in ns: return False
        try:
            r=ns["parse_fasta"](">a\natgc\n")
            return "ATGC" in "".join(r.values()).upper()
        except: return False
    
    def _test_spaces(self, ns):
        if "parse_fasta" not in ns: return False
        try:
            r=ns["parse_fasta"](">a\nAT GC AT GC\n")
            return "ATGCATGC" in "".join(r.values()).replace(" ","")
        except: return False
    
    def _test_uniprot(self, ns):
        if "parse_fasta" not in ns: return False
        try:
            r=ns["parse_fasta"](">sp|P69905|HBA_HUMAN\nATGC\n")
            return len(r)==1 and "P69905" in list(r.keys())[0]
        except: return False
    
    def run_nightly(self):
        print(f"\n🌙 NÄCHTLICHE EVOLUTION {datetime.now()}")
        print(f" Failures in Memory: {len(self.memory.data['failures'])}")
        
        tests = self.build_tests_from_failures()
        print(f" Baue {len(tests)} Tests aus echten Daten")
        
        # Hole aktuellen besten Parser
        current_code = self.watcher.active_parser_code
        
        # Evolviere mit deiner Engine
        try:
            mutator = LLMMutator("fallback")
            engine = EvolutionEngine(population_size=8, mutator=mutator)
            engine.seed(current_code, name="nightly_adam")
            winner = engine.evolve(FitnessEvaluator, tests, generations=10)
            
            print(f"\n🏆 NACHT WINNER Fit={winner.fitness:.3f} Gen={winner.generation}")
            print(winner.code[:500])
            
            # Speichere wenn besser
            # Teste gegen alten
            def eval_code(code):
                score=0
                for fn,w in tests:
                    try:
                        ns={}
                        exec(code, {}, ns)
                        score+= (1.0 if fn(ns) else 0.0)*w
                    except:
                        pass
                return score
            
            old_score = eval_code(current_code)
            new_score = eval_code(winner.code)
            
            print(f" Old Score {old_score:.3f} vs New {new_score:.3f}")
            
            if new_score >= old_score:
                (MEMORY_DIR / "best_parser.py").write_text(winner.code)
                (MEMORY_DIR / f"parser_gen_{self.memory.data['evolution_count']}.py").write_text(winner.code)
                self.watcher.active_parser_code = winner.code
                self.memory.data["best_strands"][f"gen_{self.memory.data['evolution_count']}"] = {
                    "fitness": winner.fitness,
                    "code": winner.code[:1000],
                    "time": datetime.now().isoformat()
                }
                self.memory.data["evolution_count"] += 1
                self.memory.save()
                print(f" ✅ Neuer Parser übernommen - Evolution {self.memory.data['evolution_count']}")
            else:
                print(" ❌ Neuer Parser schlechter - verworfen")
                
        except Exception as e:
            print(f" Evolution Fehler: {e}")
            import traceback
            traceback.print_exc()

# --- MAIN LOOP ---
def main():
    memory = OrganismMemory()
    watcher = FastaWatcher(memory)
    nightly = NightlyEvolution(memory, watcher)
    
    print("🧬 ORGANISMUS STARTET")
    print(f" Watch Dir: {WATCH_DIR}")
    print(f" Memory: {MEMORY_DIR}")
    print(f" Lege FASTA Files in {WATCH_DIR} ab - ich lerne live")
    print(" Für nächtliche Evolution: läuft täglich um 02:00 oder jetzt mit Taste 'e'")
    
    # Initial scan
    watcher.scan_once()
    
    # Erstelle Beispiel FASTAs falls leer
    if not list(WATCH_DIR.glob("*.fa*")):
        print("\n📁 Erstelle Beispiel FASTAs...")
        (WATCH_DIR / "example_clean.fasta").write_text(">seq1\nATGCATGC\n>seq2\nGGGGCCCC\n")
        (WATCH_DIR / "example_messy.fasta").write_text(">sp|P69905|HBA_HUMAN messy\n  atgc atgc  \n\n>seq2 lower\natgcatgc\n")
        (WATCH_DIR / "example_huge.fasta").write_text((">s\nATGC\n"*100))
        watcher.scan_once()
    
    last_nightly = datetime.now() - timedelta(days=1)
    
    # Loop
    try:
        while True:
            # 1. Live Watch alle 10 Sekunden
            time.sleep(10)
            watcher.scan_once()
            
            # 2. Nächtliche Evolution um 02:00 oder alle 2 Minuten im Demo Modus
            now = datetime.now()
            # Demo: alle 2 Minuten evolvieren
            if (now - last_nightly).total_seconds() > 120:  # 120 Sek für Demo, in Prod: check hour==2
                nightly.run_nightly()
                last_nightly = now
            
            # Status
            print(f"\n💤 Organismus schläft... Evolutionen: {memory.data['evolution_count']} Files gesehen: {len(memory.data['seen_files'])} | Ctrl+C zum Stoppen")
            
    except KeyboardInterrupt:
        print("\n🛑 Organismus gestoppt")
        memory.save()

if __name__ == "__main__":
    main()
