<p align="center">
  <img src="https://img.shields.io/badge/Bio-Inspired-Organic%20Code-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Layer-13%20Layer%20OS-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/v6-UI%20%2B%20Idea--Forest-brightgreen?style=for-the-badge" />
</p>

<h1 align="center">🧬 Organic AI OS</h1>

<p align="center">
  <strong>Code = DNA | Prompts = mRNA | LLM = Ribosom</strong><br>
  Eine selbst-evolvierende 13-Layer AI Plattform für Bioinformatik
</p>

<p align="center">
  <a href="https://github.com/unifiedcosmosai-ceo/organic-ai-os"><img src="https://img.shields.io/github/stars/unifiedcosmosai-ceo/organic-ai-os?style=social" /></a>
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" />
  <img src="https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/ollama-codellama%3A7b-orange" />
  <img src="https://img.shields.io/badge/evolution-autonomous%2002%3A00-red" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
  <img src="https://img.shields.io/badge/fitness-1.19-brightgreen" />
</p>

<p align="center">
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-architektur">Architektur</a> •
  <a href="MANUAL.md">Manual</a> •
  <a href="DOCS.md">Docs</a> •
  <a href="DEPLOY.md">Deploy</a>
</p>

---

## ⚡ Quickstart (30 Sekunden)

```bash
git clone https://github.com/unifiedcosmosai-ceo/organic-ai-os.git
cd organic-ai-os

# Starten
docker compose up --build -d
docker exec organic_ollama ollama pull codellama:7b

# Eigene FASTA reinwerfen - Organismus lernt live (SOFORT, event-getrieben)
cp ~/my_data/*.fasta ./fasta_inbox/
docker logs -f organic_ai_organism

# API
curl http://localhost:8000/memory | jq
```

**Fertig.** Watcher event-getrieben (≤1s), Evolution nachts um 02:00.

## 🚀 Was ist neu in v4 (Optimisations Phase)

- **⚡ Event-getriebener Watcher** — `watchdog`-Events statt 10s Polling; automatischer Polling-Fallback
- **💾 Robustes Memory** — atomare JSON-Writes (kein Korruptionsrisiko), relative Pfade + einmalige Migration alter `/mnt/data`-Pfade
- **📜 Strukturiertes Logging** — rotierende `logs/organism.log` mit SCAN/HEAL/EVOLUTION/BOOT Events
- **🏆 Hall of Fame** — die Top-5 Gen-Strands werden als Fossilien erhalten (`memory/hall_of_fame.json`), Diversity-Guard verhindert redundanten Code
- **🛡️ Bugfixes** — `emergency_heal` (war immer aktiv) + `detect_atypical` Präzedenz korrigiert

### v4 Phase B (Config + CLI + Multi-Format)

- **🔬 Multi-Format Parser** — `bio_formats.py` mit Auto-Detection für FASTA **und** FASTQ (`python app.py parse`)
- **⚙️ Konfiguration** — `config.py` mit Priorität *Defaults < Umgebungsvariablen (`ORGANIC_*`) < `organic.toml`*
- **🖥️ CLI-Subcommands** — `watch`, `serve`, `parse`, `evolve-now`, `status` (mit `--json`) unter `app.py`
- **📄 Beispieldateien** — `fasta_inbox/example_small.fastq` für sofortiges Testen

```bash
python app.py parse fasta_inbox/example_small.fastq   # FASTA/FASTQ Auto-Detection
python app.py status --json                           # Statusreport als JSON
python app.py evolve-now --show-hof                   # Evolution jetzt triggern
ORGANIC_PORT=9000 python app.py serve                 # Konfig per Environment
```

### v4 Phase C (API v2 + Tests)

- **🌐 API v2** — neue Endpoints: `POST /parse`, `GET /stats`, `GET /lineage`, `GET /fitness`, `GET /health` (Pydantic Request-Modelle)
- **🧪 19 Tests** — `tests/` für Parser, Konfiguration & API (`python3 -m pytest tests/ -v`)
- **🔧 Makefile** — `make test`, `make run`, `make parse FILE=...`, `make evolve-now`

```bash
make test                        # alle Tests
curl -X POST localhost:8000/parse -H 'Content-Type: application/json' \
     -d '{"content": "@r1\nACGT\n+\nIIII\n"}'
```

### v4 Phase D (Symbiom Swarm + Co-Evolution + Reporter)

- **🐝 Symbiom Schwarm** — `10_symbiom/symbiom_swarm.py`: spezialisierte Parser-Agenten (robust/fast/compact/strict) mit Knowledge-Sharing & eigener Hall of Fame
- **🌀 Co-Evolution** — `10_symbiom/co_evolution.py`: Neuro-Cortex-Prompts ↔ Code-Schwarm koppeln sich (Layer 09/10)
- **📊 Reporter** — `12_phenotype/reporter.py`: Tagesreport als JSON + HTML (`reports/`)
- **🧪 24 Tests gesamt** — inkl. Schwarm- & Co-Evolutions-Testsuite

```bash
python app.py coevolve --rounds 3 --save   # Co-Evolution starten
python app.py report                       # Tagesreport (JSON + HTML)
# → reports/report.html im Browser öffnen
```

### v4 Finale (Ollama-Anbindung + automatische Regression)

- **🔌 Tier-Ollama-Anbindung gefixt** — `LLMMutator("ollama")` nutzt jetzt `OllamaMutator` (lazy `import ollama`, kein Crash ohne Paket; bei fehlendem Ollama automatischer AST-Fallback)
- **🧪 Automatische Regressions-Suite** — `tests/test_regression.py` startet *alle* Einstiegspunkte (`organic_ai_os_evolving*.py`, CLI, API, LLM-Provider) und fängt Verbindungs-/Refactor-Fehler
- **⚙️ CI** — `.github/workflows/ci.yml` (compileall + Regression + Coverage), `make all` als Einstieg
- **✂️ Refactoring** — `tests/conftest.py` entfernt doppelte `sys.path`-Boilerplate

```bash
make test                 # Unit- + Regressions-Tests (37 pass)
make test-regression      # nur die schnelle Regressions-Suite
```

### v5 Phase 1 (MCTS-Evolutions-Kern)

- **🌳 MCTS-Suchkern** — `11_evolution/mcts_evolver.py`: Monte-Carlo-Tree-Search statt reinem GA-Tournament (UCB1-Selection, Process-Reward-Backprop, Bi-level wie BEAM)
- **🛡️ Adversarial-Testbank** — AdverMCTS-light: versteckte Grenzfaelle (Blankzeilen, Duplikat-Header, lowercase) verhindern Pseudo-Correctness
- **🚀 CLI** — `python app.py mcts-evolve --iterations N [--tests base|adversarial]`

```bash
python app.py mcts-evolve --iterations 150 --tests adversarial
make test      # 47 Tests (37 v4 + 10 v5)
```

### v5 Phase 2 (Skill / Tactic Library)

- **📚 Gated Library** — verifizierte MCTS-Rollouts werden permanent wiederverwendbar (`memory/skill_library.json`); Aufnahme nur bei Verifikation + Neuartigkeit (AST-normalisiert)
- **🩹 Failure-Library** — fehlgeschlagene Kandidaten tragen Fehlersignaturen zur Vermeidung im naechsten Run
- **🧭 Semantisches Retrieval** — `retrieve(specialty)` rankt spezialisierte Skills zuerst

```bash
python app.py skills --iterations 80 --min-visits 2 --list
make test      # 59 Tests (47 v5-P1 + 12 v5-P2)
```

### v5 Phase 3 (Budget-Guard)

- **⏱️ Mitochondrium** — globaler Kosten-Guard: Token-/Zeit-/Iterations-Budgets, adaptiv
- **🧭 Adaptive Suchtiefe** — REASON-CODE: Tiefe sinkt bei Budget-Erschöpfung (−45 %/−20 %)
- **🎯 Greedy-zuerst** — MCTS-Search nur wenn fallback-DNA schwach ist (spart Tokens)
- **📉 Pareto-Energie** — effiziente Lösungen (schnell + token-sparsam) werden belohnt

```bash
python app.py mcts-evolve --iterations 100 --budget
python app.py budget --token-budget 500 --iterations 60
make test      # 70 Tests (59 v5-P2 + 11 v5-P3)
```

### v5 Phase 4 (Format-Spec-Schema)

- **🧬 Schema-Metaparser** — Formate als DSL-Spec, Parser daraus automatisiert abgeleitet (GFF3 + VCF neu)
- **🗂️ GFF3** — 9 Spalten, `attributes`-Spalte wird in ein dict gemappt
- **🧬 VCF** — 8 Spalten, INFO als Rohstring; neue Formate = neue Spec, kein Parser-Neucode

```bash
python app.py parse-spec datei.gff         # Auto-Detect + parsen
python app.py specs                        # registrierte Specs
make test      # 83 Tests (70 v5-P3 + 13 v5-P4)
```

### v5 Phase 5 (Tool-Registry + Agent-Fassade)

- **🤖 Organic-Copilot** — alle Fähigkeiten als registrierte Tools (parse, evolve, skills, budget, specs, status)
- **🎬 Workflow** — `python app.py agent status specs budget` führt eine Schrittfolge aus (KBase-Narrative-Stil)
- **📼 Replay-Log (FEV)** — jeder Aufruf wird mit Provenance geloggt; `verify_replay()` prüft Anti-Tamper-Integrität

```bash
python app.py agent status specs budget      # 3 Tools orchestrieren
python app.py agent --list-tools             # verfügbare Tools
make test      # 101 Tests (83 v5-P4 + 18 v5-P5)
```

### v5 Phase 6 (Practical Co-Evolution)

- **🌀 Praktische Co-Evolution** — die *nächtliche Evolution* koppelt jetzt echt an Layer 09/10: `NightlyEvolution.run_nightly(coevolve=True)` startet nach der Code-Evolution eine Prompt↔Code-Co-Evolution (`_run_coevolution`) und persistiert `prompt_hint` + `coevolution` im Memory
- **🔌 Externe Testsets** — `co_evolution.evolve(..., tests=None)` nimmt eigene Tests (z. B. aus echten Nightly-Failures) statt nur Defaults
- **🧬 Debug-Fixes** — `Symbiont.lineage`-Feld ergänzt; `--no-coevolve`-Flag korrekt verdrahtet

```bash
python app.py evolve-now                # Nightly + Co-Evolution
python app.py evolve-now --no-coevolve  # nur Code-Evolution
make test      # 109 Tests (101 v5-P5 + 8 v5-P6)
```

### v6 Layer 13 (UI + MCTS-Idea-Forest)

- **🌳 3×3 MCTS-Ideenwald** — `13_ui/mcts_idea_forest.py`: 9 Bäume (Achse core/data/ops × Skala atomic/component/system), UCB1-Selection und 4 Mutationsoperatoren (merge/specialize/cross/category) erzeugen **Top 100 × 4 Kategorien** (Upgrades · Optimisations · Extensions · Automatisation)
- **🧬 Codebase-groundete Seeds** — `13_ui/idea_seeds.py`: 26 Ideen-Gene mit Layer-Bezug (09..12, core, api), Impact & Machbarkeit
- **🗺️ Mindmap-Generator** — `13_ui/mindmap.py`: `mindmap.md`, `mindmap.mmd` (Mermaid), `mindmap.html` (self-contained, pan/zoom, Tooltips) + `mindmap_tree.json`
- **🖥️ Responsive UI** — `13_ui/static/index.html` unter `/ui`
- **🌐 API** — `/ui`, `/brainstorm/top100.json`, `/brainstorm/mindmap_tree.json`, `/brainstorm/mindmap`

```bash
python app.py brainstorm --iterations 400 --seed 42   # Ideenwald + Mindmap
python app.py serve                                   # dann: http://localhost:8000/ui
# → reports/brainstorm_v6/ (top100.json, mindmap.md/.mmd/.html, mindmap_tree.json)
make test      # 120 Tests (109 v5-P6 + 11 v6)
```

### v6 Code-Qualitaet (Regression-Loop)

- **🔁 Automatischer Qualitaets-Zyklus** — `tools/regression_loop.py`: COMPILE (alle `.py`) → AUDIT (bare `except`, silent `pass`, ungenutzte Imports, doppelte Funktionen/Dateien) → TEST (volle Suite) → REPORT; `--loop N` und `--fix` für Selbst-Heilung
- **🧹 Weak-Code-Audit** — alle bisherigen Befunde behoben: ~20 bare `except:` → `except Exception`, explizite LLM-Fallbacks, tote Duplikate entfernt (`llm_evolver_1/_2`, `fasta_evolved_final_1`)
- **⚙️ CI** — Weak-Code-Audit-Schritt in `.github/workflows/ci.yml`

```bash
make test-loop   # Regression-Loop (1 Runde)
make fix         # Audits automatisch reparieren
make test        # 122 Tests (alle Layer inkl. core + 13_ui)
```

### v6 Phase A (Top-Ideen: Validierung · Fruehwarnung · Dashboard)

Die drei Top-Ideen aus dem MCTS-Idea-Forest (upgrades/optimisations/extensions/automatisation) sind umgesetzt:

- **🧬 Validierungs-Schema** — `validation_schema.py`: schemabasierte Records-Validierung (IUPAC-Alphabet, nicht-leer, eindeutige Header, FASTQ-Qualitaetslaenge, `max_seq_len`); `python app.py validate <file> [--schema fasta|fastq|auto]`, `POST /validate`
- **🚨 Fitness-Fruehwarnung** — `11_evolution/fitness_guard.py`: Score-Drop-Alarm **vor** Promotion (promote/hold/reject), persistente Baseline `memory/fitness_guard.json`; in `run_nightly()` integriert; `python app.py fitness-guard [--check F --baseline B]`
- **📊 REST-Dashboard** — `13_ui/dashboard.py`: self-contained KPI-Dashboard (HTML + JSON) aus Memory/HoF/Skills/Guard; `GET /dashboard`, `/dashboard/summary`, `/dashboard/guard`; `python app.py dashboard`

```bash
python app.py validate fasta_inbox/example_messy.fasta
python app.py fitness-guard --check 0.9
python app.py dashboard
make test        # 150 Tests (122 v6 + 28 v6-A)
```

### v6 Phase B (Alle Top-Ideen-Buendel: Daten · Ops · Traceability)

Die drei Top-Ideen-Buendel aus dem Idea-Forest sind umgesetzt - streaming
Pipe, Push-Monitoring und volle Rueckverfolgbarkeit:

- **💾 Streaming-Parser** — `streaming_parser.py`: zeilenweises FASTA/FASTQ-Lesen (ein Record im Speicher), `python app.py stream <file> [--count|--head N]`; `kmer_index.py` (`compute_kmers`, `KmerIndex.top_kmers/jaccard`, `index_fasta`), `python app.py kmers <file>`
- **📡 Webhook-Out** — `webhook_out.py`: HTTP-Push bei Events (`evolution`, `alarm`) via urllib, Konfig `memory/webhooks.json`; in `run_nightly()` nach dem Fitness-Guard-Verdikt feuert; `python app.py webhook [--url U --event E --test]`
- **🩺 Observability** — `observability.py`: Latenz/Fehler je API-Endpoint (FastAPI-Middleware); `GET /metrics`, `python app.py metrics`
- **🧬 mRNA-Provenienz** — `09_neuro/provenance.py`: Mutations-Traceback (`NeuroMutator.mutate` protokolliert jede Mutation: Strategie/Parent/Generation), `GET /provenance`, `python app.py provenance [--name X --strategy S]`
- **🧠 Neuro-Cortex-Persistenz** — `09_neuro/cortex_persist.py`: Gen-Snapshots der Prompt-Population (`memory/cortex_snapshots.json`) je Generation in `NeuroCortex.evolve`
- **🐝 Schwarm-Voting** — `10_symbiom/voting.py`: Majority-Ensemble + gewichtete Fitness, `SymbiomSwarm.ensemble_score`; `python app.py vote`

```bash
python app.py stream reads.fastq --count
python app.py kmers genome.fa --k 5 --top 10
python app.py provenance
python app.py vote
make test        # 223 Tests (150 v6-A + 73 v6-B)
```

---

## 🧪 Live Demo - Was er gelernt hat

### FASTA Parser Evolution (echt gelaufen)

| Generation | Fitness | Mutation |
|------------|---------|----------|
| Adam schwach | 0.649 | `split("\n")`, keine strip |
| Gen1 +strip+split | 0.799 | `strip()`, `split()[0]` |
| Gen2 +regex+upper | 1.197 | `re.compile(r"\s+")`, `upper()` |
| **Gen3 WINNER** | **1.199** | Generator + robust + schnell |

```python
# WINNER - evolviert aus messy real-world FASTA
def parse_fasta(text):
    import re
    records={}
    curr=None
    buf=[]
    ws=re.compile(r"\s+")
    for line in text.splitlines():
        s=line.strip()
        if not s: continue
        if s.startswith(">"):
            if curr: records[curr]="".join(buf)
            curr=s[1:].split()[0]
            buf=[]
        else:
            buf.append(ws.sub("",s).upper())
    if curr: records[curr]="".join(buf)
    return records
```

### Prompt Evolution (Layer 09)

| Prompt | Fitness | Tokens |
|--------|---------|--------|
| "Schreibe parse_fasta" | 0.45 | 3 |
| **"Du bist Bioinformatics Experte..."** | **1.10** | **9** |

**Co-Evolution:** Bessere Prompts → besserer Code → bessere Prompts.

---

## 🏗️ Architektur - 13 Layer wie eine Zelle

```
┌─────────────────────────────────────┐
│ 13 UI / BRAINSTORM - Idea-Forest    │ ← MCTS 3x3 + Mindmap
├─────────────────────────────────────┤
│ 12 PHÄNOTYP - UI / API              │ ← FastAPI
├─────────────────────────────────────┤
│ 11 EVOLUTION - LLM Mutator          │ ← codellama:7b
├─────────────────────────────────────┤
│ 10 SYMBIOM - Multi-Agent            │
│ 09 NEURO - Prompt Cortex ★          │ ← evolvierbar
├─────────────────────────────────────┤
│ 08 IMMUNSYSTEM - Auto-Heal          │
│ 07 MITOCHONDRIUM - Compute          │
│ 06 MEMBRAN - API Boundary           │
├─────────────────────────────────────┤
│ 05 EPIGENOM - Regulation            │
│ 04 METABOLOM - Memory               │
│ 03 PROTEOM - Worker ★               │ ← evolvierbar
│ 02 TRANSKRIPTOM - AST → Exec        │
│ 01 GENOM - Code als DNA             │
└─────────────────────────────────────┘
  ★ = selbst-evolvierend
```

**Organische Prinzipien:**
- 🧬 **Replikation:** `strand.replicate()`
- 🦠 **Mutation:** LLM ändert Code/Prompt (point/insert/delete/crossover)
- 🎯 **Selektion:** Fitness = funktioniert? robust? schnell?
- 🤝 **Symbiose:** Prompts + Code co-evolvieren
- 🛡️ **Homöostase:** Immunsystem heilt Fehler sofort

---

## 🤖 Autonomer Loop

```
📁 fasta_inbox/ (du wirfst Files rein)
   ↓ SOFORT (watchdog Event, ≤1s)
👁️ FastaWatcher.scan_once()
   ├─ ✅ ok → remember_file()
   └─ ❌ fail → emergency_heal() sofort
           ↓
🗒️ logs/organism.log (rotierend, strukturiert)
💾 memory/organism_memory.json (atomare Writes, relative Pfade)
   ↓ sammelt atypische Muster
🌙 NightlyEvolution 02:00 Uhr
   ├─ baut Tests aus echten Failures
   ├─ EvolutionEngine: 8 Parser, 10 Gen
   ├─ vergleicht alt vs neu
   └─ nur wenn besser → best_parser.py
   └─ Hall of Fame → memory/hall_of_fame.json (Top-5 Fossilien)
```

**Beispiel:**
```bash
echo -e ">sp|P69905|HBA_HUMAN\n  atgc atgc  " > fasta_inbox/tricky.fasta

# Log:
# 👁️  SCAN tricky.fasta: ok=False 'spaces'
# 🚨 Immunsystem triggert Schnell-Heilung
# 🩹 Heilung erfolgreich - neuer Parser gespeichert
# 🌙 NÄCHTLICHE EVOLUTION Fit 1.19 → neuer Champion
```

---

## 📦 Installation

| Methode | Befehl | Zeit |
|---------|--------|------|
| **Docker** | `docker compose up -d` | 30s |
| **Systemd** | `./install.sh` | 2min |
| **Dev** | `python autonomous_organism.py` | 5s |

Details: [DEPLOY.md](./DEPLOY.md)

---

## 📚 Doku

| Doc | Für wen |
|-----|---------|
| [MANUAL.md](./MANUAL.md) | User: Wie nutze ich den Organismus? |
| [DOCS.md](./DOCS.md) | Dev: Wie funktioniert Evolution? |
| [DEPLOY.md](./DEPLOY.md) | Ops: Docker + Systemd + Monitoring |
| [CHAT_LOG.md](./CHAT_LOG.md) | Historie: Wie ist er entstanden? |

---

## 🔬 API

```bash
curl http://localhost:8000/          # alive
curl http://localhost:8000/memory    # alle Files + Failures
curl http://localhost:8000/best_parser
curl http://localhost:8000/evolution_history
```

---

## 🧬 Inspiriert von

- **Bioinformatics Programming Using Python** - Mitchell Model (O'Reilly, 524 Seiten)
  - Kap 3: Collections & Generators → `yield` Symbiont
  - Kap 6: shelve → Metabolom
  - Kap 7: regex → `re.compile`
  - Kap 8: FASTA → Selektionsdruck
- Echte Biologie: DNA→RNA→Protein, Mutation, Selektion

---

## 🤝 Contribute

```bash
# Neuen Parser evolvieren
# 1. In autonomous_organism.py parse_fasta durch parse_gff ersetzen
# 2. Tests anpassen
# 3. PR mit memory/parser_gen_*.py Fossil

# Neuen Layer evolvierbar machen
genom.add(Strand(layer="06_membran", code="def filter(s): ..."))
evolution.evolve_layer("06_membran", tests)
```

---

## 📜 Lizenz

MIT - Mach damit was du willst. Lass Code leben.

---

<p align="center">
  <i>Built with 🧬 by <a href="https://github.com/oghighzenberg1982">Matthias Alexander Böhm</a> - Code that evolves while you sleep.</i>
</p>
