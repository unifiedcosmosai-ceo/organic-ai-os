# Organic AI Plattform - Chat Log
**Datum:** 2026-08-09 07:30:42
**Thema:** 12-Layer AI Plattform mit organischem Code in Python

---

## 1. User: Plane eine 12 layer ai plattform mit organischem code in python

**Assistant:**
- PDF "Bioinformatics Programming Using Python" analysiert (524 Seiten)
- 12-Layer Architektur entworfen, bio-inspiriert:

### Die 12 Layer (Zelle von innen nach außen):
1. **GENOM** - DNA Code Speicher (Python Code als String)
2. **TRANSKRIPTOM** - Transkription zu ausführbarem Code (ast.parse, compile)
3. **PROTEOM** - Worker Proteine (Funktionen/Klassen)
4. **METABOLOM** - State & Memory (ChromaDB, shelve)
5. **EPIGENOM** - Regulation & Lernen (Fitness, Methylierung)
6. **MEMBRAN** - API Boundary (FastAPI, selektive Permeabilität)
7. **MITOCHONDRIUM** - Energie/Compute (Async, Queue)
8. **IMMUNSYSTEM** - Selbst-Heilung & Security (try/except Autorepair)
9. **NEURO** - Inference Cortex (LLM/RAG)
10. **SYMBIOM** - Multi-Agent Kolonie
11. **EVOLUTION** - Mutation & Selektion (Genetische Algorithmen)
12. **PHÄNOTYP** - Emergenz UI

- Organische Prinzipien: Replikation, Mutation, Selektion, Symbiose, Homöostase
- Interaktives Diagramm erstellt: `12_layer_organische_ai_agentic_artifact_1_7f5bec45100d.html`
- Basis Struktur: `core/organic_base.py` mit `OrganicStrand` Klasse

---

## 2. User: Layer 11 (Evolution) mit echter Code-Mutation via LLM bauen

**Assistant:**
- Layer 11 Evolution Engine gebaut: `11_evolution/llm_evolver.py`
- **LLM Mutator** mit 6 Strategien:
  - point, insert, delete, crossover, optimize, neo
- **FitnessEvaluator**: Syntax (20%) + Ausführung + Komplexitäts-Penalty
- **EvolutionEngine**: Tournament Selection + Elitismus
- Fallback: AST-basierte Mutation wenn kein LLM
- Ollama Integration vorbereitet

---

## 3. User: Ja (parse_fasta evolvieren)

**Assistant:**
- Demo: `parse_fasta` aus Buch Kapitel 8 evolviert
- **Adam (schwach):** Fitness 0.649
  ```python
  def parse_fasta(text):
      records = {}
      header = ""
      for line in text.split("\n"):
          ...
  ```
- **Gen1 +strip+split:** Fitness 0.799
- **Gen2 +regex+upper:** Fitness 1.197
- **Gen3 WINNER +stream:** Fitness 1.199
  ```python
  def parse_fasta(text):
      import re
      records = {}
      ws = re.compile(r"\s+")
      for line in text.splitlines():
          s = line.strip()
          if not s: continue
          ...
          buf.append(ws.sub("", s).upper())
  ```
- Evolution Report gespeichert: `fasta_evolved_final.py`

---

## 4. User: Layer 11 jetzt direkt an deine 12-Layer Plattform andocken, sodass sich die anderen Layer (z.B. Layer 3 Proteom) selbst evolvieren

**Assistant:**
- EvolutionDock erstellt: dockt Layer 11 an alle Layer an
- **Flow:** Umgebung -> Membran erkennt Stress (Fitness <0.7) -> Evolution mutiert Proteom -> Selektion -> bestes Protein ersetzt altes
- File: `organic_ai_os_evolving.py`
- **OrganismMemory:** Speichert gesehene Files, Failures, atypische Muster
- Live Demo:
  ```
  [GENOM] 03_proteom/03_proteom_fasta Gen0
   EVOLVIERE 03_proteom
   Gen 0: best=03_proteom_fasta fit=0.750
   WINNER 03_proteom_fasta fit=0.750
  ```

---

## 5. User: Layer 09 Neuro (LLM Cortex) auch evolvierbar mache, sodass sich die Prompts selbst optimieren

**Assistant:**
- Layer 09 Neuro Cortex evolvierbar gemacht: `09_neuro/neuro_evolving.py`
- **Bio-Metapher:**
  - Prompt = mRNA
  - LLM = Ribosom
  - Antwort = Protein
  - Fitness = funktioniert Protein?

- **NeuroMutator Strategien:**
  - point, insert, delete, role, cot (Chain-of-Thought), fewshot

- **Live Evolution Ergebnis:**
  ```
  NEURO EVOLUTION 12 Gen
   Gen 0: best=adam_bio fit=1.100 tok=9
     Prompt: Du bist Bioinformatics Experte. Schreibe parse_fasta...
  WINNER PROMPT Gen0 Fit=1.100
  ```

- Co-Evolution: Prompt-DNA + Code-DNA evolvieren gemeinsam
- File: `organic_os_final_integrated.py`

---

## 6. User: Weiter -> autonomen Loop bauen der live auf deine FASTA Files im Ordner reagiert und sich jede Nacht selbst verbessert

**Assistant:**
- Autonomer Organismus gebaut: `autonomous_organism.py`

### Architektur:
- **WATCH_DIR:** `fasta_inbox/` - alle 10 Sekunden gescannt
- **MEMORY_DIR:** `memory/` - organism_memory.json + best_parser.py + Fossilien
- **OrganismMemory.detect_atypical():**
  - spaces_in_seq, lowercase, crlf, huge_file, uniprot_format

- **FastaWatcher:**
  - Live Scan, try_parse, remember_file
  - Bei Fehler: emergency_heal (sofortige Heilung)

- **NightlyEvolution:**
  - Baut Tests aus echten Failures = echter Selektionsdruck
  - EvolutionEngine mutiert Parser
  - Nur wenn Score besser: ersetzt best_parser.py

- Live Demo:
  ```
  👁️  SCAN /fasta_inbox um 07:12:12
   ✅ example_clean.fasta: ok=True 2 records
   ✅ example_messy.fasta: ok=True 2 records

  🌙 NÄCHTLICHE EVOLUTION
   Gen 0: best=nightly_adam fit=1.000
   ✅ Neuer Parser übernommen - Evolution 1
  ```

---

## 7. User: Ja (als Systemd + Docker verpacken)

**Assistant:**
- Deployment Files erstellt:

### 1. Dockerfile
```dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install biopython fastapi uvicorn watchdog ollama
COPY . /app
CMD ["python", "autonomous_organism.py"]
```

### 2. docker-compose.yml
- organism (autonomer Loop)
- ollama (LLM für echte Mutation)
- api (FastAPI Monitoring)
- Volumes: fasta_inbox, memory, logs

### 3. organic-organism.service (Systemd)
```ini
[Unit]
Description=Organic AI Organism
After=network.target docker.service

[Service]
ExecStart=/usr/bin/docker compose up --build
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. install.sh
- Installiert Docker falls nötig
- Kopiert nach /opt/organic_ai_platform
- Erstellt Systemd Service + Timer für 02:00 Uhr
- Startet Organismus

### 5. api_server.py
- GET / -> alive
- GET /memory -> organism_memory.json
- GET /best_parser -> aktueller Champion
- GET /inbox -> Files im Inbox
- GET /evolution_history

### Start:
```bash
docker compose up --build -d
docker exec organic_ollama ollama pull codellama:7b
cp *.fasta ./fasta_inbox/
docker logs -f organic_ai_organism
```

Oder:
```bash
chmod +x install.sh
./install.sh
sudo systemctl status organic-organism.service
```

---

## 8. User: Chat als markdown loggen

**Assistant:** Dieser Log wurde erstellt.

---

## 9. User (v4): Optimierungen, Erweiterungen, Upgrades, Erfindungen - Phase A (Optimizations)

**Assistant:**
- Repository initialisiert (git init, main) - Baseline-Kommit v3 + Frontfehler-Fixes
- README_1.md als Duplikat entfernt
- **A1 Event-getriebener Watcher** (`watcher.py`): watchdog Observer, Polling-Fallback, sauberes Shutdown (SIGINT/SIGTERM)
- **A2 Robustes Memory**: atomare JSON-Writes (tmp + os.replace), relative Pfade mit einmaliger `/mnt/data`-Migration
- **A3 Strukturiertes Logging** (`organics_log.py`): rotierende organisms.log, BOOT/SCAN/IMMUN/EVOLUTION/ERROR Events
  - Bugfix `emergency_heal` (war bedingt durch `or True` immer aktiv)
  - Bugfix `detect_atypical` (Operator-Präzedenz)
- **A4 Hall of Fame Evolution**: Top-5 Strands (`hall_of_fame.json`), Diversity-Guard gegen redundanten Code, Lineage-Tracking

### Demonstriert
```
EVENTS RECEIVED: [('live_event.fasta', 'created'), ('live_event.fasta', 'modified')]
🏆 HOF: 5 Einträge, top: nightly_adam fit=1.0
```

---

## 10. User (v4 Phase B): Multi-Format-Parser, Konfiguration & CLI

**Assistant:**
- **B5 Multi-Format Parser** (`bio_formats.py`): Auto-Detection FASTA/FASTQ, `parse_file()` liefert `(format, records)`
  - Bugfix: `exec(code, {}, ns)` → `exec(code, ns, ns)` (Namespaces)
  - Bugfix: FASTQ `qual` wurde als Liste statt String zurückgegeben → `"".join(qual)`
- **B6 Konfiguration** (`config.py`): Priorität *Defaults < `ORGANIC_*` env < `organic.toml`*, minimaler dependency-freier TOML-Parser
- **B6 CLI** (`app.py`): Subcommands `watch` / `serve` / `parse` / `evolve-now` / `status` (mit `--json`) / `demo` / `neuro-demo`
  - `status --json` von Logger-Output entkoppelt (redirect_stdout)
- **Docs**: README (Phase B Sektion), MANUAL §7, DOCS §8, CHAT_LOG
- **Branching**: `v4/phase-b` auf `v4/phase-a` rebased (Phase A-Files fehlten auf baseline-basiertem Branch)

### Demonstriert
```
Format: fastq | Records: 2   (example_small.fastq)
Format: fasta | Records: 2   (uniprot_tricky.fasta)
status --json → {"evolution_count": ..., "files_seen": ..., "hall_of_fame": [...]}
```

---

## Dateien Übersicht

```
/mnt/data/organic_ai_platform/
├── 01_genom/
├── 02_transkriptom/
├── 03_proteom/
├── 04_metabolom/
├── 05_epigenom/
├── 06_membran/
├── 07_mitochondrium/
├── 08_immunsystem/
├── 09_neuro/
│   └── neuro_evolving.py (evolvierender Prompt-Cortex)
├── 10_symbiom/
├── 11_evolution/
│   ├── llm_evolver.py (Evolution Engine)
│   ├── fasta_evolved_final.py (Winner 1.19 Fitness)
│   └── ollama_integration.py
├── 12_phaenotyp/
├── 13_ui/ (v6: UI + MCTS-Idea-Forest + Mindmap)
│   ├── idea_seeds.py (26 codebase-groundete Ideen-Gene)
│   ├── mcts_idea_forest.py (3x3 MCTS-Wald → Top 100 x 4)
│   ├── mindmap.py (mindmap.md/.mmd/.html/tree.json)
│   └── static/index.html (responsive UI)
├── tools/
│   └── regression_loop.py (v6: COMPILE → AUDIT → TEST → REPORT, --fix)
├── fasta_inbox/ (Live Watch Ordner)
│   ├── example_clean.fasta
│   ├── example_messy.fasta
│   └── uniprot_tricky.fasta
├── memory/ (Organismus Gedächtnis)
│   ├── organism_memory.json
│   ├── best_parser.py
│   └── parser_gen_*.py (Fossilien)
├── core/
│   └── organic_base.py (OrganicStrand)
├── autonomous_organism.py (Hauptloop)
├── organic_ai_os_evolving.py (integriertes OS)
├── Dockerfile
├── docker-compose.yml
├── organic-organism.service
├── install.sh
├── api_server.py
├── requirements.txt
├── DEPLOY.md
└── CHAT_LOG.md (dieser Log)
```

---

## Kernkonzepte (Organischer Code)

1. **Code = DNA:** Python Code als String gespeichert
2. **Selbst-Replikation mit Mutation:** `replicate()` + `mutate()`
3. **Selbst-Heilung:** try/except als Immunsystem
4. **Wachstum durch Umgebung:** Neue Strands bei Bedarf
5. **Selektion:** Fitness = funktioniert Code? Wie schnell? Wie robust?
6. **Co-Evolution:** Prompts evolvieren Code, Code evolviert Prompts

Inspiriert von: Bioinformatics Programming Using Python (O'Reilly) - Kapitel 3 Collections, 4 Control, 6 Utilities, 7 Pattern Matching, 8 Structured Text

---

*Log generiert: 2026-08-09T07:30:42.685100*

## 11. User (v4 Phase C): API v2 & Testsuite

**Assistant:**
- **C1 API v2** (`api_server.py`): Pydantic `ParseRequest`, Endpoints `/parse`, `/stats`, `/lineage`, `/fitness`, `/health`; ROOT-absolut Pfade
  - Fix: `/parse` mit Bare-Param lieferte 422 → Pydantic-Body-Modell
- **C2 Testsuite** (`tests/`): 19 Tests für Parser, Config, API (TestClient)
- **C3 Makefile**: `test`, `test-api`, `coverage`, `run`, `parse`, `evolve-now`, `clean`; `requirements-dev.txt`
- **Docs**: README (Phase C), MANUAL §8/§9, DOCS §9, CHAT_LOG

### Demonstriert
```
19 passed in 0.53s
GET /health → {"status":"ok","uptime_s":..., "inbox_files":4}
POST /parse (FASTQ) → {"format":"fastq","records":1, ...}
```

## 12. User (v4 Phase D): Symbiom Swarm, Co-Evolution & Reporter

**Assistant:**
- **D1 Layer 10 (`10_symbiom/symbiom_swarm.py`)**: Schwarm aus 4 Spezialisten-Nischen (robust/fast/compact/strict), Knowledge-Sharing, eigene Hall of Fame
  - Bugfix: `exec(code, {}, ns)` → `exec(code, ns, ns)` (Modulebene-import sichtbar)
  - Bugfix: robust-Mutat ohne `import re`; strict-Mutat erzeugte SyntaxError (continue außerhalb loop)
- **D2 Co-Evolution (Layer 09<->10)**: `co_evolution.py` koppelt NeuroCortex-Prompts mit Code-Schwarm
- **D3 Reporter (Layer 12)**: `12_phenotype/reporter.py` → `reports/report.json` + `reports/report.html`
- **CLI**: `app.py coevolve`, `app.py report`
- **Tests**: 24 gesamt (5 neue Schwarm/Co-Evolution)

### Demonstriert
```
24 passed in 0.51s
SYMBIOM SWARM → robust_0 fit=1.000
CO-EVOLUTION → code=robust_0 fit=1.000 | prompt=adam_engineer fit=1.000
Report JSON/HTML generiert
```

## 13. User (v4 Finale): Ollama-Anbindung, Regression, CI & Refactoring

**Assistant:**
- **Fix Verbindungsfehler**: `ollama_integration.py` hatte hartes `import ollama` (Crash ohne Paket) → lazy import + clear ConnectionError
- **Verdrahtung**: `LLMMutator("ollama")` ruft jetzt `OllamaMutator`; Fallback bei fehlendem Ollama (kein `pass`-Stub mehr)
- **Automatische Regressions-Suite** (`tests/test_regression.py`, 13 Tests): startet alle `organic_ai_os_evolving*.py`, CLI, API, LLM-Provider
- **CI**: `.github/workflows/ci.yml` (compileall + Regression + Coverage), `make all`/`test-regression`
- **Refactoring**: `tests/conftest.py` bündelt sys.path; Makefile erweitert (`report`, `test-regression`, `all`)
- **Tests gesamt**: 37 passed

### Demonstriert
```
37 passed in 1.08s
make all    → 37 passed
LLMMutator("ollama") ohne ollama → stdout, kein Traceback
```

## 14. v5 Phase 1: MCTS-Evolutions-Kern

**User:** (Fortsetzung der v5-Serie, Basis: `v4/finale`)

**Assistant:**
- **Branch**: `v5/mcts-core` (aus `v4/finale`); `.gitignore` um generierte Laufzeit-Artefakte erweitert
- **`11_evolution/mcts_evolver.py`**: Monte-Carlo-Tree-Search als Evolutions-Suchkern
  - `MCTNode` mit UCB1-Selection (Exploration/Exploitation, `c=1.4`)
  - Bi-level (BEAM-Stil): Struktur-Operatoren = alle MUTATION_PROMPTS; Funktionen per MCTS
  - Process-Reward-Backprop: `value += reward·0.9^depth`
  - `_best_confirmed`: Fitness + visits (anti-Pseudo-Correctness)
  - `adversarial_tests()`: AdverMCTS-light mit 3 versteckten Grenzfaellen
  - `BizFitness`: Korrektheit + Kompaktheits-Praemie (RPM-Idee)
- **CLI**: `app.py mcts-evolve --iterations N --tests base|adversarial [--seed-code]`
- **Bugfix (Escaping)**: CLI-Testdaten nutzten `\\n` (Literal-Backslash) waehrend der Seed auf echte Newlines splittete → Tests schlugen still fehl (fit 0.167); auf echte `\n` umgestellt → base fit=1.0, adversarial fit=0.864
- **Tests**: `tests/test_mcts_evolver.py`, 10 Tests; Gesamtstand `make test` → **47 passed**
- **Makefile**: `make test-mcts`-Ziel
- **Doku**: MANUAL §12, DOCS §12, README „v5 Phase 1", CHAT_LOG §14

### Demonstriert
```
47 passed in 1.20s
python app.py mcts-evolve --tests base        → Champion fit=1.000
python app.py mcts-evolve --tests adversarial → Champion fit=0.864 (Grenzfaelle aktiv)
```

## 15. v5 Phase 2: Skill / Tactic Library

**User:** (Fortsetzung v5, Basis: `main` mit gemergtem PR #6)

**Assistant:**
- **Branch**: `v5/skill-library` (aus `main`)
- **`11_evolution/skill_library.py`**: verifizierte, wiederverwendbare Parser-Tactics
  - `Tactic`: Typed-Skill mit applicability/precondition/postcondition/failure_signature
  - `SkillLibrary.add`: Gated Growth (verifiziert + AST-Dedup), Hall-of-Fame-Cap evictet schwaechste
  - `verify`: FitnessEvaluator-Run + Failure-Signature bei Misserfolg; 50 %-Test-Bar
  - `_register_failure`: Failure-Library (200er-Index) → `match_failure()` Recovery-Helfer
  - `retrieve(specialty)`: spezialisierte zuerst, dann generisch nach Fitness
  - `extract_from_mcts`: bestaetigte Rollouts (visits≥2, fit≥0.3) → Tactic-Kandidaten
  - `save`/`load`: JSON-Persistenz `memory/skill_library.json`
- **CLI**: `app.py skills --iterations N --min-visits N [--list] [--seed-code]`
  - Bugfix: Basis-Tests gaben fit=1.0 → frueher MCTS-Break (nur 1 Knoten) → jetzt Adversarial-Tests, Baum waechst
- **Tests**: `tests/test_skill_library.py` (12 Tests); Gesamtstand `make test` → **59 passed**
- **Makefile**: `make test-skills`
- **.gitignore**: `memory/skill_library.json`
- **Merge**: PR #6-Rebase-Konflikt (.gitignore reports/) geloest; main auf c0f058d

### Demonstriert
```
59 passed in 1.21s
python app.py skills --iterations 80 --list
# ➕ Skill: v5_adam fit=0.864 → memory/skill_library.json
```

## 16. v5 Phase 3: Budget-Guard

**User:** merge PR #7 → weiterechnen mit Budget-Guard

**Assistant:**
- **Branch**: `v5/budget-guard` (aus `main` nach Merge PR #7)
- **`11_evolution/budget_guard.py`**: globaler Kosten-Guard ("Mitochondrium")
  - `BudgetGuard` Kontextmanager: Zählwerk (Tokens/Zeit/Iterationen); `check()` wirft `BudgetExceeded` (hart) oder weicher Snapshot (soft)
  - `adapt_depth()`: adaptive Suchtiefe (REASON-CODE) −45 % >0.85, −20 % >0.6, min_depth-Floor
  - `beta_filter()`: Sub-Budget-Abschaltung (Vorsortierung ohne volle Bewertung)
  - `pareto_energy()`/`pareto_front()`: Effizienz-Bewertung (Speed+Tokens)
  - `budgeted_mcts()`: Batch-MCTS mit geteiltem Suchbaum (ARIADNE), weicher Abbruch
  - `greedy_or_search()`: Greedy zuerst, MCTS-Search nur bei Bedarf
- **mcts_evolver.py**: `run_mcts(..., root=None)` — optionaler Baum, damit Budget-Batches den Suchbaum teilen
- **CLI**: `app.py mcts-evolve --budget`; neu `app.py budget --token-budget N --iterations N` (Report + REASON-CODE-Entscheidung)
- **Bugfix (Escaping)**: Budget-Demo-Seed nutzte 4-fach-escaptes `\\n` (Literal-Backslash) vs echte Newlines in Tests → z. B. splitlines()
- **Tests**: `tests/test_budget_guard.py` (11 Tests); Gesamtstand `make test` → **70 passed**
- **Makefile**: `make test-budget`
- **Doku**: MANUAL §14, DOCS §14, README „v5 Phase 3", CHAT_LOG §16

### Demonstriert
```
70 passed in 1.32s
python app.py budget --token-budget 300 --iterations 40
⏱️ tokens 60/300 | iter 40/40 | depth 6 | searches 10
REASON-CODE: Greedy fit 0.864 < 0.9 -> MCTS-Search war noetig
```

## 17. v5 Phase 4: Format-Spec-Schema

**User:** merge PR #8 → weiter

**Assistant:**
- **Branch**: `v5/format-spec` (aus `main` nach Merge PR #8)
- **`format_spec.py`**: schema-basierter Metaparser (Forschung: KBase, Template-Parser)
  - `FormatSpec` DSL: name, marker, comment, sep, columns, has_attributes
  - `default_specs()`: GFF3 (9 Spalten, attrs-Map `ID=g1;Name=x` → dict) + VCF (8 Spalten, INFO roh)
  - `derive_parser()`: Spec → ausfuehrbaren `parse_<name>` Code (import-frei)
  - `parse_file_spec()`/`detect_spec()`: Runtime + Marker-Auto-Detektion
  - `specs_to_json()`/`list_specs()`: Serialisierung/CLI
- **CLI**: `app.py specs` + `app.py parse-spec <file> [--spec gff3|vcf|auto]`
- **Bugfix (generierter Code)**: attrs-Zeile referenzierte `rec` statt `recs` → auf `recs` umgestellt
- **Tests**: `tests/test_format_spec.py` (13 Tests inkl. Custom-BED-Spec-ableitung); `make test` → **83 passed**
- **Makefile**: `make test-spec`
- **Doku**: MANUAL §15, DOCS §15, README „v5 Phase 4", CHAT_LOG §17

### Demonstriert
```
83 passed in 1.36s
python app.py parse-spec sample.gff
# 🎯 Spec: gff3 | Records: 1 | {"chr1": {... "attributes": {"ID": "g1"}}}
```

## 18. v5 Phase 5: Tool-Registry + Agent-Fassade + Replay

**User:** merge PR #9 → weiter

**Assistant:**
- **Branch**: `v5/tool-registry` (aus `main` nach Merge PR #9)
- **`tool_registry.py`**: "Organic-Copilot" (Forschung: BioMedAgent, KBase, MARWA, FEV)
  - `ToolRegistry`: register/register_all/run, list_tools, tool_meta
  - `ReplayEntry` + `run()`: jeder Aufruf mit ts/tool/args/result/ok/seed
  - `save_replay`/`load_replay`/`verify_replay`: FEV-Bundle + Integrity-Hash (Anti-Tamper)
  - `summary`: Calls/Failed/Replay-Hash
  - Standard-Tools: parse_file, parse_spec, status, mcts_evolve, skill_library, budget, specs
  - `make_agent`/`run_agent_workflow`: Agent-Fabrik + Schrittfolge (`parse_file:/pfad` = Argument-Durchreiche)
- **CLI**: `app.py agent [steps...] [--list-tools] [--replay PATH] [--seed N]`
- **Tests**: `tests/test_tool_registry.py` (18 Tests inkl. Tamper-Detection); `make test` → **101 passed**
- **Makefile**: `make test-tools`
- **.gitignore**: `memory/replay_log.json`, `memory/replay_demo.json`
- **Doku**: MANUAL §16, DOCS §16, README „v5 Phase 5", CHAT_LOG §18

### Demonstriert
```
101 passed in 1.43s
python app.py agent status specs budget --seed 7
# ✅ status | ✅ specs | ✅ budget
# 📦 Replay-Bundle: memory/replay_log.json | Calls: 3 | Failed: 0 | Verify: True
```

## 19. v5 Phase 6: Practical Co-Evolution (Nightly ⇄ Layer 09/10)

**User:** merge PR #10 → Practical Co-Evolution an die naechtliche Evolution andocken

**Assistant:**
- **Branch**: `v5/practical-coevolve` (aus `main` nach Merge PR #10)
- **`autonomous_organism.py`**: `run_nightly(coevolve=True)` startet nach der
  Code-Evolution `_run_coevolution(tests, old_score, new_score)` → persistiert
  `prompt_hint` + `coevolution` (best_prompt, co_score) in `organism_memory.json`
- **`co_evolution.py`**: `evolve(..., tests=None)` durchreicht externe Testsets
  (echte nightly-Failures als Selektionsdruck)
- **`symbiom_swarm.py`**: `Symbiont.lineage`-Feld ergänzt (Provenienz)
- **`app.py`**: `--no-coevolve`-Flag korrekt verdrahtet
  (`coevolve=not getattr(args, "no_coevolve", False)`)
- **Tests**: `tests/test_practical_coevolution.py` (8 Tests); `make test` → **109 passed**
- **Doku**: README „v5 Phase 6", MANUAL §17, DOCS §17, CHAT_LOG §19

### Demonstriert
```
109 passed in ~4s
run_nightly(coevolve=True) → prompt_hint + coevolution im Memory
co_evolution.evolve(..., tests=[(_t_parse, 0.6), (_t_messy, 0.4)]) → code.fit>0.5
```

## 20. v6 Layer 13: UI + MCTS-Idea-Forest + Mindmap

**User:** (neue v6-Serie) Layer 13 UI + Brainstorm mit MCTS-Ideenwald

**Assistant:**
- **Branch**: `v5/practical-coevolve` (fortgesetzt)
- **`13_ui/idea_seeds.py`**: 26 codebase-groundete Ideen-Gene (layer 09..12/core/api,
  Achse core/data/ops, Skala atomic/component/system, impact/feasibility)
- **`13_ui/mcts_idea_forest.py`**: 3×3-MCTS-Wald (9 Bäume), UCB1, 4 Operatoren
  (merge/specialize/cross/category), `idea_fitness` mit kategoriespezifischen
  Gewichten → **Top 100 × 4** (Upgrades/Optimisations/Extensions/Automatisation)
- **`13_ui/mindmap.py`**: `mindmap.md` + `mindmap.mmd` (Mermaid) +
  `mindmap.html` (self-contained, inline-SVG, pan/zoom, Tooltips) +
  `mindmap_tree.json`
- **`13_ui/static/index.html`**: responsive, auto-skalierende UI (horiz/vertikal)
- **API**: `/ui`, `/brainstorm/top100.json`, `/brainstorm/mindmap_tree.json`,
  `/brainstorm/mindmap`; **CLI**: `app.py brainstorm --iterations N --seed N`
- **Artefakte**: `reports/brainstorm_v6/`
- **Tests**: `tests/test_ui_and_brainstorm.py` (11 Tests); `make test` → **120 passed**
- **conftest**: `13_ui` in sys.path
- **Doku**: README „v6 Layer 13", MANUAL §18, DOCS §18, CHAT_LOG §20

### Demonstriert
```
120 passed in ~5s
python app.py brainstorm --iterations 400 --seed 42
# upgrades: 100 | optimisations: 100 | extensions: 100 | automatisation: 100
# Artefakte -> reports/brainstorm_v6/ (top100.json, mindmap.md/.mmd/.html, mindmap_tree.json)
GET /ui → 200
```

## 21. v6 Code-Qualitaet: Regression-Loop & Weak-Code-Audit

**User:** Qualitaets-Loop bauen, der die ganze Plattform selbst testet + saeubert

**Assistant:**
- **Branch**: `v5/practical-coevolve` (fortgesetzt)
- **`tools/regression_loop.py`**: COMPILE (alle `.py`) → AUDIT (bare `except`,
  silent `pass`, ungenutzte Imports, doppelte Funktionen/Dateien) → TEST →
  REPORT; `--loop N`, `--fix`
- **Behoben**: ~20 bare `except:` → `except Exception` (inkl. `neuro_evolving.py`),
  explizite LLM-Fallbacks, tote Duplikate entfernt (`llm_evolver_1/_2`,
  `fasta_evolved_final_1`), Seed/Basis-Tests dedupliziert (`_seed_parse_fasta`,
  `_basic_tests`)
- **Makefile**: `test-loop`, `fix`; **CI**: Weak-Code-Audit-Schritt in
  `ci.yml` (compileall aller Layer inkl. core/13_ui)
- **Regression-Tests erweitert**: keine bare `except:`, kein toter Ollama-Stub,
  Regression-Loop-Tool phasengruen; Legacy-Checkpoints vom Style-Audit
  ausgenommen (CHECKPOINT_FILES)
- **Tests**: `make test` → **122 passed**
- **Doku**: README „v6 Code-Qualitaet", MANUAL §19, DOCS §19, CHAT_LOG §21

### Demonstriert
```
122 passed in ~5.3s
make test-loop  → COMPILE 0 | AUDIT 0 | TEST 122 passed
python3 tools/regression_loop.py --loop 3 → konvergiert mit 0 Fehlern
```
