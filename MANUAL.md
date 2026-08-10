# 📖 Benutzerhandbuch - Organic AI OS

## Für wen ist das?

- **Bioinformatiker:** FASTA, GFF, VCF Parser die sich selbst an eure Daten anpassen
- **AI Engineer:** Beispiel wie man Code + Prompts co-evolvieren lässt
- **Neugierige:** Lebender Code der nachts lernt

---

## 1. Schnellstart für Ungeduldige

```bash
# 1. Ins Repo wechseln (oder Ordner kopieren)
cd organic-ai-os

# 2. Starten
docker compose up --build -d

# 3. LLM laden (einmalig, ~4GB)
docker exec -it organic_ollama ollama pull codellama:7b

# 4. Eigene FASTA reinwerfen
cp ~/Downloads/*.fasta ./fasta_inbox/

# 5. Zuschauen
docker logs -f organic_ai_organism
# 👁️  SCAN ... ✅ example_clean.fasta: 2 records
# 🌙 NÄCHTLICHE EVOLUTION ... 🏆 WINNER Fit=1.0

# 6. Besten Parser holen
cat memory/best_parser.py
```

Fertig. Der Rest passiert automatisch.

---

## 2. Wie nutze ich den evolvierten Parser?

### 2.1 Direkt

```python
from pathlib import Path
code = Path("memory/best_parser.py").read_text()
ns = {}
exec(code, {}, ns)
parse_fasta = ns["parse_fasta"]

result = parse_fasta(">seq1\nATGC\n>seq2\nGGGG")
print(result)  # {'seq1': 'ATGC', 'seq2': 'GGGG'}
```

### 2.2 Als Modul

```python
# In deinem Projekt
import sys
sys.path.insert(0, "/opt/organic_ai_platform/memory")
from best_parser import parse_fasta
```

### 2.3 Über API

```bash
curl http://localhost:8000/best_parser | jq -r .code > my_parser.py
```

---

## 3. Der Live Watch Ordner

**Pfad:** `fasta_inbox/` (oder `/opt/organic_ai_platform/fasta_inbox/` bei Systemd)

### 3.1 Was passiert wenn ich ein File reinlege?

1. **Innerhalb ~1 Sekunde (event-getrieben):** watchdog meldet das neue File
2. **Versucht zu parsen** mit aktuellem besten Parser
3. **Wenn ok:** Merkt sich File (Hash, Size, parsed_ok=true)
4. **Wenn Fehler:** 
   - Speichert Failure + atypische Merkmale
   - **Sofortige Heilung:** Fügt strip(), upper(), re.sub hinzu
   - Testet Heilung sofort
   - Wenn erfolgreich: ersetzt best_parser.py sofort

> Falls `watchdog` nicht installiert ist, wechselt der Organismus automatisch auf Polling-Interval (alle 2s).

**Beispiel:**
```bash
echo -e ">sp|P69905|HBA_HUMAN\n  atgc atgc  " > fasta_inbox/tricky.fasta

# Log:
# 👁️  SCAN tricky.fasta: ok=False 'spaces'
# 🚨 Immunsystem triggert Schnell-Heilung
# 🩹 Heilung erfolgreich - neuer Parser gespeichert
```

### 3.2 Welche Files werden erkannt?

- `*.fasta`, `*.fa`, `*.fas`, `*.txt` in `fasta_inbox/`
- Unterordner werden nicht gescannt (einfach halten)
- Große Files (>100MB) werden trotzdem versucht, aber langsam

---

## 4. Die nächtliche Evolution (02:00 Uhr)

### 4.1 Was passiert nachts?

1. **Sammelt alle Failures** der letzten Tage aus `memory/organism_memory.json`
2. **Baut Tests** daraus:
   - File hatte lowercase? -> Test: `atgc` muss zu `ATGC`
   - File hatte spaces? -> Test: `AT GC` muss zu `ATGC`
   - File war Uniprot? -> Test: Header muss `sp|P69905|...` enthalten
3. **Startet Evolution:** 8 Parser konkurrieren, 10 Generationen
4. **Vergleicht:** Alter Parser Score vs Neuer Score
5. **Nur wenn besser:** Ersetzt `best_parser.py`, speichert Fossil `parser_gen_N.py`

### 4.2 Manuell triggern

```bash
# Docker
docker exec organic_ai_organism python -c "
from autonomous_organism import OrganismMemory, FastaWatcher, NightlyEvolution
m=OrganismMemory(); w=FastaWatcher(m); NightlyEvolution(m,w).run_nightly()
"

# Oder einfach File ändern - Demo Modus evolviert alle 2 Minuten
```

### 4.3 Zeit ändern

In `autonomous_organism.py`:
```python
# Zeile ~280
if (now - last_nightly).total_seconds() > 120:  # Demo: 120 Sek
# Für Prod:
if now.hour == 2 and now.minute == 0:
```

Und in Systemd Timer:
```bash
sudo nano /etc/systemd/system/organic-organism-nightly.timer
# OnCalendar=02:00 -> OnCalendar=04:30
sudo systemctl daemon-reload
```

---

## 5. Monitoring & Logs

### 5.1 API (http://localhost:8000)

| Endpoint | Was |
|----------|-----|
| `/` | Alive Check |
| `/memory` | Alle gesehenen Files + Failures |
| `/best_parser` | Aktueller Champion Code |
| `/inbox` | Files im Inbox |
| `/evolution_history` | Alle Generationen |

```bash
curl http://localhost:8000/memory | jq .evolution_count
# 17

curl http://localhost:8000/best_parser | jq -r .code
```

### 5.2 Logs

```bash
# Docker
docker logs -f organic_ai_organism
docker logs -f organic_ollama

# Systemd
sudo journalctl -u organic-organism.service -f
sudo journalctl -u organic-organism-nightly.service -f

# Files
tail -f /opt/organic_ai_platform/logs/organism.log
cat /opt/organic_ai_platform/memory/organism_memory.json | jq
```

### 5.3 Memory verstehen

`memory/organism_memory.json`:
```json
{
  "seen_files": {
    "/.../example_clean.fasta": {
      "hash": "a1b2c3d4",
      "parsed_ok": true,
      "atypical": {}
    },
    "/.../tricky.fasta": {
      "parsed_ok": false,
      "error": "spaces_in_seq",
      "atypical": {"spaces_in_seq": true, "lowercase": true}
    }
  },
  "failures": [...],
  "best_strands": {...},
  "evolution_count": 17
}
```

---

## 6. Anpassen für eigene Daten

### 6.1 Anderen Parser evolvieren (z.B. GFF)

In `autonomous_organism.py`:

```python
# Ersetze active_parser_code
self.active_parser_code = 
---

## 7. CLI & Konfiguration (v4 Phase B)

### 7.1 Subcommands

```bash
python app.py watch                # default: Watcher + Evolution + API
python app.py serve --port 9000    # nur FastAPI
python app.py parse datei.fastq    # FASTA/FASTQ Auto-Detection
python app.py evolve-now           # Evolution jetzt ausführen
python app.py status --json        # Memory + Hall of Fame als JSON
python app.py demo                 # Code-Evolutions-Demo
python app.py neuro-demo           # Prompt-Evolutions-Demo
```

### 7.2 Konfigurations-Priorität

Werte werden in dieser Reihenfolge übernommen (höher überschreibt):

1. `organic.toml` (falls vorhanden)
2. Umgebungsvariablen `ORGANIC_*`
3. Defaults in `config.py`

```bash
ORGANIC_POPULATION_SIZE=12 ORGANIC_LLM_PROVIDER=ollama python app.py watch
```

Alle unterstützten Schlüssel stehen kommentiert in `organic.toml`.

### 7.3 Beispieldaten

`fasta_inbox/` enthält neben FASTA-Dateien nun auch `example_small.fastq`
zum Testen des Multi-Format-Parsers.

---

## 8. API v2 Endpoints (Phase C)

| Method | Endpoint | Funktion |
|--------|----------|----------|
| GET | `/health` | Healthcheck inkl. Uptime |
| POST | `/parse` | Sequenzen parsen (FASTA/FASTQ Auto-Detection, JSON-Body) |
| GET | `/stats` | Memory zahlen + Hall of Fame |
| GET | `/lineage` | Best-Strand-Ahnenreihe |
| GET | `/fitness` | Fitness-Historie |
| GET | `/memory` | Roh-Memory |
| GET | `/evolution_history` | Evolution-Generationen |
| GET | `/inbox` | Dateien im Watch-Ordner |

Beispiel:
```bash
curl -X POST localhost:8000/parse -H 'Content-Type: application/json' \
     -d '{"content": ">s1\nATGC\n", "filename": "t.fasta"}'
```

## 9. Tests (Phase C)

```bash
python3 -m pytest tests/ -v     # oder
make test
```

---

## 10. Symbiom Schwarm & Co-Evolution (Phase D)

### Symbiom Schwarm
```bash
python -m 10_symbiom.symbiom_swarm
```
4 Spezialisten-Nischen (robust/fast/compact/strict) evolvieren parallel;
der Koordinator teilt Erkenntnisse (Knowledge-Sharing) und speichert
`memory/symbiom_hall_of_fame.json`.

### Co-Evolution (Prompt <-> Code)
```bash
python app.py coevolve --rounds 3 --swarm-gen 6 --save
```
Der Neuro-Cortex (Layer 09) evolviert Prompts, die Code erzeugen; der Schwarm
(Layer 10) optimiert den Code, dessen Fitness wiederum die Prompts bewertet.

### Reporter
```bash
python app.py report
# erzeugt reports/report.json + reports/report.html
```

---

## 11. Ollama-Anbindung & Regression (v4 Finale)

### LLM-Provider korrekt verdrahten

```python
from llm_evolver import LLMMutator
m = LLMMutator("ollama")   # lazy import: crasht NICHT ohne ollama-Paket
```

- Ohne `pip install ollama` → automatischer Fallback auf AST-Mutation
- Ohne laufendes `ollama run` → gleicher Fallback (klare ConnectionError-Meldung intern)

### Regressions-Suite

```bash
make test                 # 47 Tests (alle Layer + Einstiegspunkte)
make test-regression      # nur Einstiegspunkte (schnell, ~1s)
```

Die Suite startet `organic_ai_os_evolving*.py`, CLI-Subcommands, API und
LLM-Provider und sammelt jeden Traceback als fehlgeschlagenen Test.

## 12. MCTS-Evolutions-Kern (v5)

### Was ist neu?

Ein **Monte-Carlo-Tree-Search (MCTS)** ersetzt das reine GA-Tournament als
Such-Kern der Evolution (Forschung 2026: BEAM, ARIADNE, AdverMCTS, RPM):

- **Bi-level Evolution**: aeusserer Layer waehlt Struktur-Operatoren
  (Alle MUTATION_PROMPTS), innerer Layer sucht funktional mit MCTS.
- **UCB1 Selection**: Exploration/Exploitation-Ausgleich in O(log n).
- **Process-Reward Backprop**: Rollout-Fitness wird mit Tiefe diskontiert
  (0.9^depth) - naehere/bestaetigte Zuege wiegen mehr.
- **Adversarial-Testbank (AdverMCTS-light)**: verteidigt gegen
  Pseudo-Correctness durch versteckte Grenzfaelle:
  - mehrere Blankzeilen in FASTA (`_t_embedded_newline`)
  - doppelte Header (`_t_duplicate_headers`)
  - Nur-Kleinbuchstaben-Sequenzen (`_t_lowercase_only`)

### CLI

```bash
python app.py mcts-evolve --iterations 150 --tests adversarial
python app.py mcts-evolve --iterations 100 --tests base
python app.py mcts-evolve --seed-code /pfad/zu/start.py
```

Der Champion wird nach Fitness + Bestaetigungs-Zahl (visits) gewaehlt -
anti-Pseudo-Correctness.

### Tests

```bash
python -m pytest tests/test_mcts_evolver.py -v   # 10 Tests
make test                                        # 47 Tests (alle Layer)
```
