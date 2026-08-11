# 📘 Technische Dokumentation - Organic AI OS

## 1. Kernkonzept: Organischer Code

### 1.1 Definition
Organischer Code behandelt Python Code nicht als statische Datei, sondern als **lebende DNA**:

```python
@dataclass
class Strand:
    name: str
    code: str          # Python Code als String = DNA Sequenz
    fitness: float     # Überlebensfähigkeit
    generation: int
    lineage: List[str] # Ahnenreihe
```

**Operationen:**
- `transcribe()` - DNA -> ausführbarer Code (ast.parse + compile)
- `mutate()` - Punktmutation, Insertion, Deletion
- `replicate()` - Selbst-Replikation mit Fehlern
- `evaluate()` - Fitness Test

### 1.2 Vergleich Biologie vs Code

| Biologie | Organischer Code |
|----------|------------------|
| DNA | `code: str` (Python Source) |
| mRNA | Prompt Template |
| Ribosom | LLM (codellama, gpt-4) |
| Protein | Ausführbare Funktion |
| Mutation | LLM ändert Code/Prompt |
| Selektion | Fitness Tests |
| Methylierung | Feature Flag / Fitness Score |
| Immunsystem | try/except Auto-Heal |

---

## 2. Layer 11: Evolution Engine

**File:** `11_evolution/llm_evolver.py`

### 2.1 Architektur

```
Population (8 Strands)
   ↓
FitnessEvaluator.evaluate() -> Fitness Score
   ↓
Sortierung (beste zuerst)
   ↓
Selektion:
  - Elitismus: Bester überlebt immer
  - Tournament: 3 zufällig, bester gewinnt
   ↓
Reproduktion:
  - 70% Mutation (LLM)
  - 20% Crossover (2 Eltern -> Kind)
  - 10% Drift (leichte Punktmutation)
   ↓
Nächste Generation
```

### 2.2 Fitness Funktion

```python
class FitnessEvaluator:
    @staticmethod
    def evaluate(code, tests):
        score = 0
        # 1. Syntax Fitness (20%)
        try: ast.parse(code); score+=0.2
        except: return 0.0 # lethal
        
        # 2. Funktionale Tests (80%)
        for test_fn, weight in tests:
            result = test_fn(exec(code))
            score += result * weight
        
        # 3. Parsimonie Penalty
        score -= max(0, (lines-20)*0.02)
        return score
```

**Beispiel Tests für FASTA:**
- `test_basic`: Parst >a\\nATGC ?
- `test_robust`: Leerzeilen, Spaces?
- `test_lowercase`: atgc -> ATGC ?
- `test_uniprot`: sp|P69905|... Format?
- `test_speed`: 2000 Records <0.3s ?

### 2.3 Mutator

**LLM Prompt für Mutation:**
```
Du bist eine organische Mutations-Engine für Python Code.

AUFGABE: {point|insert|delete|crossover|optimize|neo}

ORIGINAL STRAND:
```python
{strand.code}
```

REGELN:
- Erhalte Signatur
- Valides Python
- Max 30 Zeilen
- Nur Codeblock
```

**Fallback (ohne LLM):**
- AST Walk: Konstanten * 0.8-1.25
- Operator Tausch: + -> *
- Insertion: "# [ORGANIC INSERT] adaptive check"
- Text Mutation: return -> return ( # mutated

### 2.4 Ollama Integration

```python
# llm_evolver.py
def _call_llm(self, system, user):
    if self.provider == "ollama":
        import ollama
        res = ollama.chat(model="codellama:7b",
              messages=[{"role":"system","content":system},
                        {"role":"user","content":user}])
        return res['message']['content']

# Nutzung:
mutator = LLMMutator("ollama")
engine = EvolutionEngine(mutator=mutator)
```

---

## 3. Layer 09: Neuro Cortex (Prompt Evolution)

**File:** `09_neuro/neuro_evolving.py`

### 3.1 Prompt als DNA

```python
@dataclass
class PromptStrand:
    name: str
    prompt_template: str  # DNA
    fitness: float
    tokens: int           # Länge = Kosten
```

**Fitness = Code Fitness + Effizienz Bonus**

Effizienz = `code_fitness / tokens * 5` - Kurze Prompts die guten Code erzeugen gewinnen.

### 3.2 Prompt Mutationen

| Strategie | Beispiel |
|-----------|----------|
| point | "mache" -> "generiere präzise" |
| insert | + "Regel: Nur valider Python, max 15 Zeilen" |
| delete | Entferne "bitte, einfach, nur" |
| role | "Du bist Senior Bioinformatics Engineer." |
| cot | + "Denke Schritt für Schritt: 1) Parse 2) Edges 3) Optimize" |
| fewshot | + 'Beispiel: ">a\\nATGC" -> {"a":"ATGC"}' |

### 3.3 Co-Evolution

**Loop:**
1. Prompt-DNA -> LLM -> Code-Protein
2. Teste Code -> Code Fitness
3. Prompt Fitness = Code Fitness / Tokens
4. Mutatiere Prompt
5. Wiederhole

**Ergebnis:** Prompts werden kürzer UND besser.

```
Gen0: "Schreibe parse_fasta" (3 Tok) -> Code Fitness 0.4 -> Gesamt 0.45
Gen3: "Du bist Senior... Requirements: strip(), splitlines()... Beispiel: ..." (22 Tok) -> Code Fitness 0.95 -> Gesamt 1.35
```

---

## 4. Autonomer Organismus

**File:** `autonomous_organism.py`

### 4.1 Komponenten

```
OrganismMemory
  - seen_files: {path: {hash, size, parsed_ok, atypical}}  (relative Pfade)
  - failures: [{file, error, atypical}]
  - best_strands: {gen: {fitness, code, lineage}}
  - evolution_count: int
  - atomare Writes (tmp + os.replace), einmalige /mnt/data-Pfad-Migration

FastaWatcher (Live, event-getrieben)
  - scan_once(): liest neue/changed Files
  - try_parse(): exec(best_parser.py)
  - remember_file(): in Memory
  - emergency_heal(): sofortige Heilung bei Fehler

NightlyEvolution (02:00 Uhr)
  - build_tests_from_failures(): aus echten Daten
  - run_nightly(): EvolutionEngine + Tests
  - Vergleicht alt vs neu Score
  - Übernimmt nur wenn besser
  - Hall of Fame: speichert Top-5 Strands (hall_of_fame.json, Diversity-Guard)

Watcher (watcher.py)
  - watchdog.Observer Event-Stream (created/modified/moved)
  - automatischer Polling-Fallback wenn watchdog fehlt
  - daemonisiert, stop() für sauberes Herunterfahren

Logging (organics_log.py)
  - RotatingFileHandler logs/organism.log (1MB x 3)
  - strukturierte Events: BOOT/SCAN/IMMUN/EVOLUTION/ERROR
```

### 4.2 Atypische Erkennung

```python
def detect_atypical(content):
    return {
      "spaces_in_seq": " " in seq_line,
      "lowercase": any(c.islower() for c in content),
      "crlf": "\\r" in content,
      "huge_file": content.count(">") > 1000,
      "uniprot_format": re.search(r">.*\\|.*\\|", content),
    }
```

Jedes atypische Merkmal generiert einen spezifischen Test -> Selektionsdruck.

### 4.3 Notfall Heilung

Wenn `try_parse` fehlschlägt:

```python
def emergency_heal(error, content):
    code = active_parser
    if "strip()" not in code:
        code = code.replace("line", "line.strip()")
    if "upper()" not in code:
        code = code.replace("buf.append(s)", "buf.append(s.upper())")
    # Teste sofort
    exec(code) -> fn(content) -> ok? -> speichere
```

Das ist Layer 08 Immunsystem live.

---

## 5. Deployment Architektur

### 5.1 Docker Compose

```
organism (autonomous_organism.py)
  volumes: fasta_inbox, memory, logs
  depends_on: ollama

ollama (ollama/ollama:latest)
  ports: 11434
  volume: ollama_data
  GPU optional

api (api_server.py)
  ports: 8000
  volumes: memory:ro, inbox:ro
```

### 5.2 Systemd

```
organic-organism.service (Type=simple, Restart=always)
  ExecStart: docker compose up

organic-organism-nightly.service (Type=oneshot)
  ExecStart: docker exec ... run_nightly()

organic-organism-nightly.timer
  OnCalendar=02:00
  Persistent=true
```

---

## 6. Performance & Grenzen

- **Population 8, Gen 10:** ~5 Sekunden (Fallback), ~2 Minuten (mit Ollama codellama:7b)
- **Fitness Evaluation:** exec() in isoliertem Namespace - sicher, aber langsam bei vielen Tests
- **Memory:** organism_memory.json wächst linear mit Files - ab 10k Files aufräumen
- **Best Parser:** Nur 1 aktiver Parser - für Multi-Parser: Genom als Dict erweitern

---

## 7. Erweiterung

### Neuen Layer evolvierbar machen:

```python
# In autonomous_organism.py
seeds = {
  "06_membran_filter": "def filter_input(s): return s.strip()[:1000]"
}
genom.add(Strand(layer="06_membran", name="filter", code=seeds["06_membran_filter"]))

# Test
def test_membran(ns):
    return len(ns["filter_input"]("  a"*2000)) <= 1000

# Evolution
evolution.evolve_layer("06_membran", [(test_membran, 1.0)])
```

### Eigenen Datentyp:

Ersetze `parse_fasta` durch `parse_gff`, `parse_vcf`, etc. - Tests anpassen, Rest bleibt gleich.

---

*Technische Doku v1.0 - 2026-08-09*

---

## 8. v4 Phase B: Multi-Format Parser, Config & CLI

### 8.1 `bio_formats.py` — Multi-Format Parser

- `FORMATS`: `fasta`, `fastq`
- `detect_format(content)` → Format-Name (Heuristik: `>`, `@`-Header)
- `parse_file(content)` → `(format, records)`; FASTQ liefert `{header: {"seq": ..., "qual": ...}}`
- Seeds werden per `exec` isoliert in einem eigenen Namespace ausgeführt (Bugfix: `exec(code, ns, ns)` statt `exec(code, {}, ns)`; FASTQ-`qual` wird als String gejoint)

```python
import bio_formats
fmt, rec = bio_formats.parse_file(open("x.fastq").read())
```

### 8.2 `config.py` — Konfigurations-Layer

Priorität: **Defaults < `ORGANIC_*` env < `organic.toml`**

- `DEFAULTS`: watch_dir, memory_dir, logs_dir, port, intervals, population/generation/hoF-Größe, LLM-Provider, Ollama-Host/Model, Timeout
- `load_config()` behandelt bool/int/float-Ena und liest `organic.toml` mit einem minimalen, dependency-freien TOML-Parser

### 8.3 `app.py` CLI

| Subcommand | Funktion |
|---|---|
| `watch` | Watcher + nächtliche Evolution + API (default) |
| `serve --port` | nur FastAPI |
| `parse <file>` | FASTA/FASTQ Auto-Detection |
| `evolve-now` | Evolution sofort ausführen |
| `status --json` | Memory + Hall of Fame als Report |
| `demo` / `neuro-demo` | Evolutions-Demos |

Die `status --json`-Ausgabe wird per `contextlib.redirect_stdout` von Logger-Output entkoppelt.

---

*Technische Doku v1.1 - 2026-08-11 (v4 Phase B)*

---

## 9. v4 Phase C: API v2 & Testsuite

### 9.1 API v2 (`api_server.py`)

- `ParseRequest` Pydantic-Modell für `POST /parse`
- Neue Endpoints: `/health`, `/parse`, `/stats`, `/lineage`, `/fitness`
- Bestehende `/memory`, `/evolution_history`, `/inbox` beibehalten
- `ROOT`-Pfade (`Path(__file__)`) statt CWD-relative Pfade → Start von überall

### 9.2 Testsuite (`tests/`)

| Datei | Deckt ab |
|-------|----------|
| `test_bio_formats.py` | FASTA/FASTQ Detection + Parsing inkl. messy Daten |
| `test_config.py` | Defaults, `ORGANIC_*` env-Override, `organic.toml`, bool-Ena |
| `test_api.py` | Alle API v2 Endpoints via `fastapi.testclient.TestClient` |

### 9.3 Makefile

`make test` / `make test-api` / `make coverage` / `make run` / `make parse FILE=...` / `make evolve-now` / `make clean`

---

*Technische Doku v1.2 - 2026-08-11 (v4 Phase C)*

---

## 10. v4 Phase D: Symbiom Swarm, Co-Evolution & Reporter

### 10.1 `10_symbiom/symbiom_swarm.py`

- `Symbiont` (name, speciality, code, fitness, discoveries)
- `SymbiomSwarm`: population_per_species je Nische, `seed(base_code)`, `evaluate()`,
  `_share_knowledge()` (besten Fund in den Schwarm impfen), `evolve(tests, generations)`,
  `export_hall_of_fame()` → `memory/symbiom_hall_of_fame.json`
- Nischen-Mutatoren: robust (import re + ws-compile), fast, compact (Leerzeilen),
  strict (Filter via List-Comprehension)
- Bugfix: `exec(code, ns, ns)` damit Modulebene-`import` im Funktion-Body sichtbar ist

### 10.2 `10_symbiom/co_evolution.py`

- `evolve(rounds, swarm_generations, pop_per_species)` → `(best_code, best_prompt, history)`
- Prompt-Fitness = Code-Fitness*0.6 + Prompt-Qualitaet*0.4
- Prompt-Hint wird in den Schwarm-Code eingewoben (Inspiration)

### 10.3 `12_phenotype/reporter.py`

- `collect_day_data()`: Memory + Hall of Fame + Symbiom-Pool
- `generate_report()`: `reports/report.json` (maschinell) + `reports/report.html` (self-contained, KPI-Kacheln)

### 10.4 CLI Integration

`python app.py coevolve --rounds N --swarm-gen M [--save]`, `python app.py report`

---

*Technische Doku v1.3 - 2026-08-11 (v4 Phase D)*

---

## 11. v4 Finale: Ollama-Anbindung, Regression & CI

### 11.1 Llama-Provider (`llm_evolver.py`)

`LLMMutator("ollama")` verdrahtet jetzt `OllamaMutator` aus `ollama_integration.py`:
- lazy `import ollama` → Import des Moduls crasht nie
- `except ConnectionError` → Fallback auf `_fallback_mutate` (AST-basiert)
- toter Stub entfernt

### 11.2 Regressions-Suite (`tests/test_regression.py`)

| Gruppe | Deckt ab |
|---|---|
| Einstiegspunkte | `organic_ai_os_evolving*.py` werfen keine Tracebacks |
| Ollama | Import crasht nie; fehlend → clear `ConnectionError` |
| LLMMutator | `fallback` und `ollama`-Provider (Silent-Fallback) |
| CLI | `parse`, `status --json` (valides JSON), `report` |
| Stub-Check | kein toter `# import ollama`-Code mehr |

### 11.3 CI + Makefile

- `.github/workflows/ci.yml`: compileall → Regressions-Suite → Coverage
- `make all` / `make test` / `make test-regression` / `make report`
- `tests/conftest.py`: zentrales sys.path-Setup (keine Boilerplate je Datei)

---

## 12. v5 Phase 1: MCTS-Evolutions-Kern

### 12.1 `11_evolution/mcts_evolver.py`

Bi-level GA+MCTS (Forschung 2026: BEAM, ARIADNE, AdverMCTS, RPM):

| Klasse/Funktion | Verantwortung |
|---|---|
| `MCTNode` | Suchbaum-Knoten; UCB1 über `value/visits + c·√(ln(parent)/visits)` |
| `MCTSEvolution.selection/expansion` | UCB1-Descent; Fächerauf je Strategie (alle MUTATION_PROMPTS) |
| `MCTSEvolution.simulation` | Rollout: vollständige Fitnessbewertung |
| `MCTSEvolution.backpropagation` | Process-Reward: `value += reward·0.9^depth` |
| `MCTSEvolution.run_mcts` | Iterationen mit Fokus-Zufallsauswahl; Terminal-Check bei fit≥0.95 |
| `_best_confirmed` | anti-Pseudo-Correctness: Fitness + visits + −depth |
| `adversarial_tests` | AdverMCTS-light: +3 Grenzfall-Tests (Blankzeilen, Duplikat-Header, lowercase) |
| `BizFitness` | Korrektheit + Kompaktheits-Prämie, ohne FitnessEvaluator-Abhängigkeit |

### 12.2 CLI

`python app.py mcts-evolve --iterations N --tests base|adversarial [--seed-code PATH]`

Champion-Auswahl gewichtet bestätigte Züge (visits) - keine Pseudo-Correctness.

### 12.3 Testabdeckung

- `tests/test_mcts_evolver.py`: 10 Tests (UCB1, best_child, Fitness-Runge,
  Adversarial-Deckung, BizFitness)
- Gesamtstand: `make test` → **47 Tests** (37 v4 + 10 v5)

---

## 13. v5 Phase 2: Skill / Tactic Library

### 13.1 `11_evolution/skill_library.py`

| Funktion | Verantwortung |
|---|---|
| `Tactic` | Typed-Skill: name, code, fitness, specialty, applicability, precondition, postcondition, failure_signature, source, lineage |
| `SkillLibrary.add` | Gated Growth: nur verifiziert + AST-normalisiert duplikatfrei; Hall-of-Fame-Cap evictet schwächste |
| `SkillLibrary.verify` | FitnessEvaluator-Run; setzt verified + Failure-Signature bei Misserfolg |
| `_register_failure` | Failure-Library (max 200 Einträge, code_hash) |
| `retrieve(specialty)` | Semantisches Retrieval: spezialisierte zuerst, dann generisch nach Fitness |
| `find_duplicate` / `match_failure` | Dedup bzw. Recovery-Helfer gegen bekannte Fehlersignaturen |
| `extract_from_mcts` | MCTS-Knoten (visits≥2, fit≥0.3) → Tactic-Kandidaten (Transfer) |
| `save`/`load` | JSON-Persistenz (`memory/skill_library.json`) |
| `_flatten_tree` | iterativer Flatten (kein Rekursionslimit) |

Design-Entscheidungen (Forschung 2026):
- **Gated Library Growth** (ARIADNE-geteilter Zustand): Aufnahme nur bei
  Verifikation + Neuartigkeit → keine Pseudo-Correctness-Skills.
- **Failure-Library** (FEV-ähnlich): fehlgeschlagene Codes merken sich ihre
  Signatur zur spaeteren Vermeidung/Wiederherstellung.
- **MCTS-Transfer**: bestaetigte Rollouts als Seed fuer den naechsten Run.

### 13.2 CLI

`python app.py skills --iterations N --min-visits N [--list] [--seed-code PATH]`
→ verifizierte Skills nach `memory/skill_library.json`.

### 13.3 Testabdeckung

- `tests/test_skill_library.py`: 12 Tests (Gates, Dedup, Verify, Failure-Index,
  Retrieval, Cap, Persistenz, Flatten, Normalize)
- Gesamtstand: `make test` → **59 Tests** (47 v5-P1 + 12 v5-P2)

---

## 14. v5 Phase 3: Budget-Guard

### 14.1 `11_evolution/budget_guard.py`

| Baustein | Verantwortung |
|---|---|
| `BudgetSnapshot` | momentane Kostenlage: Tokens/Zeit/Iterationen, ratios, depth |
| `BudgetGuard` | Kontextmanager + Zählwerk; `check()` wirft `BudgetExceeded` (hart) oder liefert Snapshot (soft) |
| `guard.adapt_depth` | REASON-CODE: Tiefe um −45 %/−20 % je Erschöpfungsstufe (min_depth-Floor) |
| `guard.beta_filter` | Sub-Budget-Abschaltung: billige Vorsortierung ohne volle Bewertung |
| `guard.pareto_energy` | Effizienz-Score: Fitness·(0.5+0.25·Speed+0.25·Token-Saving) |
| `pareto_front` | dominante Punkte über die Pareto-Front |
| `budgeted_mcts` | MCTS in Batches, geteilter Suchbaum (ARIADNE), adaptive Tiefe, weicher Abbruch |
| `greedy_or_search` | Greedy zuerst, MCTS-Search nur bei Bedarf (Budgetersparnis) |

Zusätzliche Änderung: `mcts_evolver.run_mcts(..., root=None)` — optionaler
bestehender Baum, damit Budget-Batches sind nicht mehr zurücksetzen.

### 14.2 CLI

- `python app.py mcts-evolve --iterations N --budget`
- `python app.py budget --token-budget N --iterations N`

### 14.3 Testabdeckung

- `tests/test_budget_guard.py`: 11 Tests (hart/soft, Iterations/Zeit-Break,
  adaptive Tiefe, beta_filter, Pareto-Energie/-Front, budgeted_mcts-Caps, Greedy)
- Gesamtstand: `make test` → **70 Tests** (59 v5-P2 + 11 v5-P3)

---

## 15. v5 Phase 4: Format-Spec-Schema

### 15.1 `format_spec.py`

| Baustein | Verantwortung |
|---|---|
| `FormatSpec` | DSL-dataclass: name, marker, comment, sep, columns, has_attributes, skip_header_markers |
| `default_specs()` | Registry: GFF3 (9 Spalten + attrs-Map) + VCF (8 Spalten, INFO roh) |
| `derive_parser(spec)` | Code-Generator: Spec → ausfuehrbare `parse_<name>` Funktion (JSON-Spalten, attrs-Ableitung) |
| `parse_file_spec` | faehrt den abgeleiteten Parser aus (Schema-Runtime) |
| `detect_spec` | Marker-basierte Auto-Detektion (GFF3/VCF), FASTA/FASTQ → None |
| `specs_to_json`/`list_specs` | Serialisierung / CLI-Ansicht |
| `FormatSpec.from_dict` | Specs aus JSON/TOML laden (erweiterbar) |

Design-Entscheidungen (Forschung: KBase, Template-Parser):
- **Schema als Code-Quelle**: Parser werden generiert, nicht gewartet —
  neue Formate = neue Spec-Zeile, kein Parser-Neucode.
- **Attributes-Map nur wenn `has_attributes`**: GFF3 bekommt Struktur,
  VCF bleibt roh (kein Pseudo-Typisieren).
- **`import`-frei** (`test_derive_parser_pure`): generierter Code ist selbstenthalten.

### 15.2 CLI

- `python app.py specs` — Liste der Specs
- `python app.py parse-spec <file> [--spec gff3|vcf|auto]`

### 15.3 Testabdeckung

- `tests/test_format_spec.py`: 13 Tests (Registry, Compile, Pure, Detect,
  GFF3-attrs, VCF-Spalten, Kommentar-Skip, malformed-Skip, JSON-Roundtrip,
  Custom-BED-Spec)
- Gesamtstand: `make test` → **83 Tests** (70 v5-P3 + 13 v5-P4)

---

## 16. v5 Phase 5: Tool-Registry + Agent-Fassade + Replay

### 16.1 `tool_registry.py`

| Baustein | Verantwortung |
|---|---|
| `ReplayEntry` | Provenance pro Aufruf: ts/tool/args/result/ok/seed |
| `ToolRegistry.register/register_all` | Tool-Abstraktion (Name + Beschreibung) |
| `ToolRegistry.run` | führt Tool aus, fängt Exceptions, loggt Replay (FEV) |
| `save_replay`/`load_replay`/`verify_replay` | Bundle + Integrity-Hash (Anti-Tamper) |
| `summary` | Calls/Failed/Replay-Hash für CLI/API |
| `parse_file_tool` | FASTA/FASTQ-Parse (bio_formats) |
| `parse_spec_tool` | GFF3/VCF via Format-Spec |
| `status_tool` | Organismus-Status (Memory + Hall of Fame) |
| `mcts_evolve_tool` | MCTS-Evolutions-Champion |
| `skill_library_tool` | MCTS-Rollouts → verifizierte Skills |
| `budget_tool` | budget-begrenzter MCTS-Run (BudgetGuard) |
| `specs_tool` | registrierte Format-Specs |
| `make_agent` | Fabrik: Agent mit Standard-Tools + Replay-Pfad + Seed |
| `run_agent_workflow` | führt Schrittfolge aus (`parse_file:/pfad` = Argument-Durchreiche) |

Design (Forschung 2026):
- **FEV-Provenance**: Korrektheit wird am Aufruf-Verlauf gemessen, nicht an
  einer End-Antwort → Replay + Verifikation sind die Währung.
- **Deterministischer Seed**: Replay-Reproduzierbarkeit (Gen0→GenN).
- **Workflow-Narrative** (KBase): Schrittfolge = reproduzierbares Bundle.

### 16.2 CLI

- `python app.py agent [steps...] [--list-tools] [--replay PATH] [--seed N]`

### 16.3 Testabdeckung

- `tests/test_tool_registry.py`: 18 Tests (Registry, run ok/error, Replay-
  Roundtrip, Tamper-Detection, Summary, Standard-Tools, Workflow, je Tool-Smoke)
- Gesamtstand: `make test` → **101 Tests** (83 v5-P4 + 18 v5-P5)

---

## 17. v5 Phase 6: Practical Co-Evolution

### 17.1 `autonomous_organism.py` (Nightly ⇄ Co-Evolution)

| Baustein | Verantwortung |
|---|---|
| `NightlyEvolution.run_nightly(coevolve=True)` | nach der Code-Evolution optional die Prompt↔Code-Co-Evolution starten |
| `NightlyEvolution._run_coevolution(tests, ...)` | `co_evolution.evolve` mit denselben (Failure-)Tests; persistiert `prompt_hint` + `coevolution` (best_prompt, co_score) im Memory |
| `cmd_evolve_now` / CLI `--no-coevolve` | `run_nightly(coevolve=not args.no_coevolve)` — Flag sauber verdrahtet |

### 17.2 `10_symbiom/co_evolution.py`

`evolve(rounds, swarm_generations, pop_per_species, tests=None)`:
- `tests=None` → Basis-Tests des Organs; sonst externe Testsets durchreichen
  (echter Selektionsdruck aus nightly-Failures).
- Bugfix: `Symbiont.lineage`-Feld in `10_symbiom/symbiom_swarm.py` ergänzt
  (Provenienz je Spezialist).

### 17.3 Testabdeckung

- `tests/test_practical_coevolution.py`: 8 Tests (Seed parst, Default-/
  externe Tests, History-Form, Prompt-Hint, Nightly-Integration,
  `coevolve=False`-Pfad, kaputte Tests crashen nicht)
- Gesamtstand: `make test` → **109 Tests** (101 v5-P5 + 8 v5-P6)

---

## 18. v6 Layer 13: UI + MCTS-Idea-Forest + Mindmap

Neuer Phenotyp-Layer: 400 Ideen (Top 100 × 4 Kategorien) aus einem
**3×3-Monte-Carlo-Tree-Wald** über der Codebase.

### 18.1 `13_ui/idea_seeds.py`

| Baustein | Verantwortung |
|---|---|
| `Gene` | Codebase-groundetes Ideen-Gen: name, desc, layer (09..12/core/api), axis (core/data/ops), scale (atomic/component/system), impact, feasibility, tags |
| `SEEDS` / `seed_pool(axis=, scale=)` | 26 Seeds mit Layer-Bezug; Filter-Fabrik für den Wald |

### 18.2 `13_ui/mcts_idea_forest.py`

| Baustein | Verantwortung |
|---|---|
| `MCTSNode.ucb1` | Exploration/Exploitation (`c=1.4`) |
| `op_merge` / `op_specialize` / `op_cross` / `op_category` | 4 Mutationsoperatoren: hybridisieren, konkretisieren, Cross-Pollination auf andere Layer, Kategorie-Framing |
| `IdeaMCTS` | selection → expansion → simulation → backpropagation (visits/value) |
| `idea_fitness` | kategorienspezifische Gewichtung (Upgrades=Tiefe, Optimisations=Machbarkeit, Extensions=Neuheit, Automatisation=Automatisierbarkeit) |
| `run_forest` | 3×3 Wald (9 Bäume, `iterations_per_tree`), Dedup, Top-100-Ranking je Kategorie |
| `build_forest_output` | Artefakte → `reports/brainstorm_v6/top100.json` |

### 18.3 `13_ui/mindmap.py`

`build_tree` → verschachtelter JSON-Baum; `to_mermaid` → `mindmap.mmd`;
self-contained HTML (inline SVG, pan/zoom, Tooltips, kein CDN) → `mindmap.html` +
`mindmap_tree.json`.

### 18.4 API + CLI

| Endpoint / CLI | Funktion |
|---|---|
| `python app.py brainstorm --iterations N --seed N` | Wald + Mindmap generieren |
| `GET /ui` | responsive UI (`13_ui/static/index.html`) |
| `GET /brainstorm/top100.json` | Top 100 × 4 Kategorien |
| `GET /brainstorm/mindmap_tree.json` | JSON-Baum |
| `GET /brainstorm/mindmap` | Mermaid/HTML-Ansicht |

### 18.5 Testabdeckung

- `tests/test_ui_and_brainstorm.py`: 11 Tests (Seeds, UCB1, Operatoren, Wald-
  Ränge, Mindmap-Artefakte, API-Endpoints, UI-Template)
- Gesamtstand: `make test` → **120 Tests** (109 v5-P6 + 11 v6)

---

## 19. v6 Regression-Loop & Code-Qualitaet

### 19.1 `tools/regression_loop.py`

| Phase | Verantwortung |
|---|---|
| `compile_all` | alle `.py` syntaktisch pruefen |
| `AuditVisitor` | bare `except:`, silent `pass`, ungenutzte Imports, doppelte Funktionen, tote Dateien |
| `audit_duplicates` | Duplikat-Dateien erkennen (normalisierte Hashes) |
| `run_pytest` | volle Suite inkl. Regression + UI + API |
| `--loop N` / `--fix` | N Runden bis Konvergenz; einfache Audits in-place reparieren |
| `PY_SKIP` / `CHECKPOINT_FILES` | Legacy-Checkpoints (`organic_ai_os_evolving*.py`, `neuro_evolving_1.py`, …) werden kompiliert/getestet, aber nicht style-auditiert |

### 19.2 Behandelte Befunde

- ~20 bare `except:` → `except Exception` (u. a. `09_neuro/neuro_evolving.py`)
- explizite LLM-Fallbacks (`11_evolution/llm_evolver.py`, `skill_library.py`)
- tote Duplikate entfernt: `11_evolution/llm_evolver_1.py`, `llm_evolver_2.py`,
  `fasta_evolved_final_1.py`
- Dedup Seed/Basis-Tests via `_seed_parse_fasta()`/`_basic_tests()` in
  `app.py` + `tool_registry.py`

### 19.3 Tooling

- Makefile: `test-loop`, `fix`
- CI: `.github/workflows/ci.yml` — compileall aller Layer (inkl. core/13_ui)
  + Weak-Code-Audit-Schritt
- Gesamtstand: `make test` → **122 Tests** (alle Layer inkl. core + 13_ui)

---

*Technische Doku v2.0 - 2026-08-11 (v5 Phase 6 + v6 Layer 13 + Regression-Loop)*
