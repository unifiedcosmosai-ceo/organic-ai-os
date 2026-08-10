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
