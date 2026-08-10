<p align="center">
  <img src="https://img.shields.io/badge/Bio-Inspired-Organic%20Code-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Layer-12%20Layer%20OS-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/v4-optimisations-brightgreen?style=for-the-badge" />
</p>

<h1 align="center">🧬 Organic AI OS</h1>

<p align="center">
  <strong>Code = DNA | Prompts = mRNA | LLM = Ribosom</strong><br>
  Eine selbst-evolvierende 12-Layer AI Plattform für Bioinformatik
</p>

<p align="center">
  <a href="https://github.com/oghighzenberg1982/organic-ai-os"><img src="https://img.shields.io/github/stars/oghighzenberg1982/organic-ai-os?style=social" /></a>
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
git clone https://github.com/oghighzenberg1982/organic-ai-os.git
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

## 🏗️ Architektur - 12 Layer wie eine Zelle

```
┌─────────────────────────────────┐
│ 12 PHÄNOTYP - UI / API           │ ← FastAPI
├─────────────────────────────────┤
│ 11 EVOLUTION - LLM Mutator       │ ← codellama:7b
├─────────────────────────────────┤
│ 10 SYMBIOM - Multi-Agent         │
│ 09 NEURO - Prompt Cortex ★       │ ← evolvierbar
├─────────────────────────────────┤
│ 08 IMMUNSYSTEM - Auto-Heal      │
│ 07 MITOCHONDRIUM - Compute      │
│ 06 MEMBRAN - API Boundary       │
├─────────────────────────────────┤
│ 05 EPIGENOM - Regulation        │
│ 04 METABOLOM - Memory           │
│ 03 PROTEOM - Worker ★           │ ← evolvierbar
│ 02 TRANSKRIPTOM - AST → Exec    │
│ 01 GENOM - Code als DNA         │
└─────────────────────────────────┘
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
