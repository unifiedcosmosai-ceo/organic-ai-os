
"""
AUTONOMER ORGANISMUS - Live FASTA Watcher + Nächtliche Evolution
Beobachtet Ordner, lernt aus echten Daten, verbessert sich nachts

Run: python autonomous_organism.py
"""

import time, json, hashlib, ast, re, random, os, signal, sys
from pathlib import Path
from datetime import datetime, timedelta
import threading
from dataclasses import dataclass, field
from typing import List, Dict

from organics_log import get_logger, event

logger = get_logger("organism")

# Import aus deinen Layern
import sys
sys.path.insert(0, str(Path(__file__).parent / "11_evolution"))
sys.path.insert(0, str(Path(__file__).parent / "09_neuro"))
from organics_log import get_logger
logger = get_logger("organism")
try:
    from llm_evolver import Strand, FitnessEvaluator, LLMMutator, EvolutionEngine
    logger.info("Evolution Engine geladen")
except Exception as e:
    logger.warning("Fallback Evolution Engine: %s", e)
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
        self.migrate_stale_paths()

    def load(self):
        if self.db_path.exists():
            return json.loads(self.db_path.read_text())
        return {"seen_files": {}, "failures": [], "best_strands": {}, "prompt_history": [], "evolution_count": 0}

    def migrate_stale_paths(self):
        """Migriert absolute Alt-Pfade (z.B. /mnt/data/...) auf relative Pfade."""
        moved = False
        for key in list(self.data.get("seen_files", {})):
            if key.startswith("/"):
                # extrahiere den Teil ab fasta_inbox/ (oder ersten "inbox" Teil)
                for marker in ("organic_ai_platform/", "fasta_inbox/"):
                    if marker in key:
                        rel = key.split(marker, 1)[1]
                        break
                else:
                    rel = None
                if rel and rel not in self.data["seen_files"]:
                    self.data["seen_files"]["fasta_inbox/" + rel] = self.data["seen_files"].pop(key)
                    moved = True
        failures = self.data.get("failures", [])
        for f in failures:
            if isinstance(f.get("file"), str) and f["file"].startswith("/"):
                for marker in ("organic_ai_platform/", "fasta_inbox/"):
                    if marker in f["file"]:
                        f["file"] = "fasta_inbox/" + f["file"].split(marker, 1)[1]
                        moved = True
                        break
        if moved:
            self.save()
            logger.info("Memory Alt-Pfade (absolut) nach relativ migriert")

    def save(self):
        """Atomar schreiben: erst tmp-Datei, dann rename - kein Datenverlust bei Crash."""
        tmp_path = self.db_path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(self.data, indent=2))
        os.replace(tmp_path, self.db_path)
    
    def _relkey(self, filepath: Path) -> str:
        """Normiert einen Pfad zu relativem Schlüssel (portabel über Maschinen hinweg)."""
        try:
            return str(filepath.resolve().relative_to(Path(__file__).resolve().parent))
        except ValueError:
            return str(filepath)

    def remember_file(self, filepath: Path, content: str, parsed_ok: bool, error=""):
        h = hashlib.md5(content.encode()).hexdigest()[:8]
        self.data["seen_files"][self._relkey(filepath)] = {
            "hash": h,
            "size": len(content),
            "parsed_ok": parsed_ok,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "atypical": self.detect_atypical(content)
        }
        if not parsed_ok:
            self.data["failures"].append({"file": self._relkey(filepath), "error": error, "atypical": self.detect_atypical(content)})
        self.save()
    
    def detect_atypical(self, content: str) -> Dict:
        """Erkennt ungewöhnliche FASTA Merkmale - das löst Evolution aus"""
        atypical = {}
        lines = content.splitlines()
        second_line = lines[1] if len(lines) > 1 else ""
        if " " in second_line:
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
        event(logger, "SCAN", f"{WATCH_DIR} um {datetime.now().strftime('%H:%M:%S')}")
        for fasta_file in WATCH_DIR.glob("*.fa*"):
            if fasta_file.suffix in [".fasta",".fa",".txt",".fas"]:
                content = fasta_file.read_text(errors="ignore")
                ok, result, err = self.try_parse(content)
                is_new = str(fasta_file) not in self.memory.data["seen_files"]
                if is_new or not ok:
                    status = "ok" if ok else f"error {err[:60]}"
                    detail = f"{len(result)} records" if ok else ""
                    event(logger, "SCAN", f"{fasta_file.name}: ok={ok} {status} {detail}")
                    if not is_new and ok:
                        # schon gesehen und ok - skip
                        continue
                self.memory.remember_file(fasta_file, content, ok, err)
                
                # Wenn Fehler -> sofortige Notfall-Heilung (Layer 08 Immunsystem)
                if not ok:
                    event(logger, "IMMUN", f"Schnell-Heilung fuer {fasta_file.name}: {err[:80]}", level=logger.warning)
                    self.emergency_heal(err, content)
    
    def emergency_heal(self, error: str, content: str):
        # Einfache Heilung: füge strip(), upper() hinzu
        code = self.active_parser_code
        if "strip()" not in code:
            code = code.replace("line", "line.strip()")
            code = code.replace("s=line.strip()", "s=line.strip()")
        if "upper()" not in code:
            # generell upper hinzufügen
            code = code.replace('buf.append(s)', 'buf.append(s.upper())')
        
        # Teste Heilung
        try:
            ns={}
            exec(code, {}, ns)
            fn=ns["parse_fasta"]
            fn(content)
            event(logger, "IMMUN", "Heilung erfolgreich - neuer Parser gespeichert")
            (MEMORY_DIR / "best_parser.py").write_text(code)
            self.active_parser_code = code
            self.memory.data["best_strands"]["emergency_heal"] = {"code": code, "time": datetime.now().isoformat()}
            self.memory.save()
        except Exception as e:
            event(logger, "IMMUN", f"Heilung fehlgeschlagen: {e}", level=logger.error)

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
        event(logger, "EVOLUTION", f"Naechtliche Evolution {datetime.now()}")
        event(logger, "EVOLUTION", f"Failures in Memory: {len(self.memory.data['failures'])}")
        
        tests = self.build_tests_from_failures()
        event(logger, "EVOLUTION", f"Baue {len(tests)} Tests aus echten Daten")
        
        # Hole aktuellen besten Parser
        current_code = self.watcher.active_parser_code
        
        # Evolviere mit deiner Engine
        try:
            mutator = LLMMutator("fallback")
            engine = EvolutionEngine(population_size=8, mutator=mutator, hall_of_fame_size=5)
            engine.seed(current_code, name="nightly_adam")
            winner = engine.evolve(FitnessEvaluator, tests, generations=10)
            
            event(logger, "EVOLUTION", f"NACHT WINNER {winner.name} Fit={winner.fitness:.3f} Gen={winner.generation}")
            
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
            
            event(logger, "EVOLUTION", f"Old Score {old_score:.3f} vs New {new_score:.3f}")
            
            if new_score >= old_score:
                (MEMORY_DIR / "best_parser.py").write_text(winner.code)
                (MEMORY_DIR / f"parser_gen_{self.memory.data['evolution_count']}.py").write_text(winner.code)
                self.watcher.active_parser_code = winner.code
                self.memory.data["best_strands"][f"gen_{self.memory.data['evolution_count']}"] = {
                    "fitness": winner.fitness,
                    "code": winner.code[:1000],
                    "lineage": winner.lineage,
                    "time": datetime.now().isoformat()
                }
                self.memory.data["evolution_count"] += 1
                self._save_hall_of_fame(engine, tests)
                self.memory.save()
                event(logger, "EVOLUTION", f"Neuer Parser übernommen - Evolution {self.memory.data['evolution_count']}")
            else:
                event(logger, "EVOLUTION", "Neuer Parser schlechter - verworfen")
                self._save_hall_of_fame(engine, tests)
                
        except Exception as e:
            event(logger, "EVOLUTION", f"Evolution Fehler: {e}", level=logger.error)
            import traceback
            traceback.print_exc()

    def _save_hall_of_fame(self, engine, tests):
        """Persistiert die Top-N Strands der Evolution als fossile Gene.""" 
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
        hof = [
            {
                "name": s.name,
                "fitness": s.fitness,
                "score": eval_code(s.code),
                "generation": s.generation,
                "lineage": s.lineage,
                "code": s.code[:500],
            }
            for s in engine.hall_of_fame
        ]
        (MEMORY_DIR / "hall_of_fame.json").write_text(json.dumps(hof, indent=2))

# --- MAIN LOOP ---
def main(nightly_interval: float = 120.0, enable_watcher: bool = True):
    memory = OrganismMemory()
    watcher = FastaWatcher(memory)
    nightly = NightlyEvolution(memory, watcher)
    
    event(logger, "BOOT", "ORGANISMUS STARTET")
    event(logger, "BOOT", f"Watch Dir: {WATCH_DIR}")
    event(logger, "BOOT", f"Memory: {MEMORY_DIR}")
    event(logger, "BOOT", f"Lege FASTA Files in {WATCH_DIR} ab - ich lerne live")
    
    # Initial scan
    watcher.scan_once()
    
    # Erstelle Beispiel FASTAs falls leer
    if not list(WATCH_DIR.glob("*.fa*")):
        event(logger, "BOOT", "Erstelle Beispiel FASTAs...")
        (WATCH_DIR / "example_clean.fasta").write_text(">seq1\nATGCATGC\n>seq2\nGGGGCCCC\n")
        (WATCH_DIR / "example_messy.fasta").write_text(">sp|P69905|HBA_HUMAN messy\n  atgc atgc  \n\n>seq2 lower\natgcatgc\n")
        (WATCH_DIR / "example_huge.fasta").write_text((">s\nATGC\n"*100))
        watcher.scan_once()
    
    # Event-getriebener Watcher (Layer 08) mit Polling-Fallback
    from watcher import DirectoryWatcher
    dir_watcher = DirectoryWatcher(WATCH_DIR, on_file=lambda p, k: watcher.scan_once(), interval=2.0)
    if enable_watcher:
        dir_watcher.start()
    
    last_nightly = datetime.now() - timedelta(days=1)
    
    def shutdown(signum=None, frame=None):
        event(logger, "BOOT", "Organismus gestoppt")
        dir_watcher.stop()
        memory.save()
        if signum is not None:
            sys.exit(0)
    
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    
    # Loop
    try:
        while True:
            time.sleep(1)
            now = datetime.now()
            # Nächtliche Evolution: alle N Sekunden (Demo) oder um 02:00 (Prod)
            if (now - last_nightly).total_seconds() > nightly_interval:
                nightly.run_nightly()
                last_nightly = now

    except KeyboardInterrupt:
        shutdown()

if __name__ == "__main__":
    main()
