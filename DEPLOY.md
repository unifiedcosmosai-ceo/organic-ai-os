# Organic AI Organism - Deployment

## Schnellstart Docker (empfohlen)

```bash
# Im Repo-Ordner (z.B. ./organic-ai-os)
docker compose up --build -d

# 2. Logs
docker logs -f organic_ai_organism

# 3. Ollama Modell laden (für echte LLM Mutation)
docker exec organic_ollama ollama pull codellama:7b
# oder
docker exec organic_ollama ollama pull mistral

# 4. In .env oder docker-compose.yml setzen:
# LLM_PROVIDER=ollama
# Hinweis: Fehlt das ollama-Paket, faellt der Mutator automatisch auf AST-Philosophie zurück (kein Crash).

# 5. FASTA Files reinwerfen
cp ~/my_data/*.fasta ./fasta_inbox/

# 6. Status API
curl http://localhost:8000/memory
curl http://localhost:8000/best_parser

# 7. Regression lokal (optional, auf dem Host)
python3 -m pytest tests/ -v
```

## Systemd auf Bare Metal Server

```bash
chmod +x install.sh
./install.sh

# Status
sudo systemctl status organic-organism.service
sudo journalctl -u organic-organism.service -f

# Nightly Timer
sudo systemctl status organic-organism-nightly.timer
```

## Was passiert um 02:00 Uhr?

1. Watcher hat tagsüber atypische FASTA Muster gesammelt (lowercase, spaces, uniprot, huge)
2. NightlyEvolution baut daraus Tests = Selektionsdruck
3. EvolutionEngine mutiert Parser mit LLM (codellama:7b)
4. Bester Parser ersetzt alten nur wenn Score besser
5. Fossil wird gespeichert: memory/parser_gen_N.py
6. Memory wird aktualisiert
7. Optional danach Co-Evolution (Prompt↔Code, Layer 09/10): persistiert
   `prompt_hint` + `coevolution` im Memory

## v6: UI, Brainstorm & Qualitaets-Loop

```bash
# Brainstorm (Layer 13): 400 Ideen (Top 100 x 4) + Mindmap
python app.py brainstorm --iterations 400 --seed 42
# → reports/brainstorm_v6/ (top100.json, mindmap.md/.mmd/.html, mindmap_tree.json)

# UI + Brainstorm-API über FastAPI
python app.py serve
# http://localhost:8000/ui               (responsive UI)
# http://localhost:8000/brainstorm/top100.json

# Qualitaets-Loop (COMPILE → AUDIT → TEST → REPORT)
make test-loop          # 1 Runde
make fix                # einfache Audits automatisch reparieren
python3 tools/regression_loop.py --loop 5
```

## Monitoring

- API: http://localhost:8000
- Logs: ./logs/organism.log (rotierend, strukturiert: SCAN/HEAL/EVOLUTION/BOOT)
- Memory: ./memory/organism_memory.json (atomare Writes, relative Pfade)
- Hall of Fame: ./memory/hall_of_fame.json (Top-5 Gen-Fossilien)
- Inbox: ./fasta_inbox/ (event-getrieben via watchdog, Polling-Fallback)

## Autonomer Loop anpassen

In autonomous_organism.py:

WATCH_INTERVAL = 10  # Sekunden
NIGHTLY_HOUR = 2      # Uhrzeit
# Für Demo: alle 120 Sekunden
if (now - last_nightly).total_seconds() > 120:
