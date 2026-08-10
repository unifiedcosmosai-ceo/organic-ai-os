# Organic AI Organism - Deployment

## Schnellstart Docker (empfohlen)

```bash
cd /mnt/data/organic_ai_platform

# 1. Build & Start
docker compose up --build -d

# 2. Logs
docker logs -f organic_ai_organism

# 3. Ollama Modell laden (für echte LLM Mutation)
docker exec organic_ollama ollama pull codellama:7b
# oder
docker exec organic_ollama ollama pull mistral

# 4. In .env oder docker-compose.yml setzen:
# LLM_PROVIDER=ollama

# 5. FASTA Files reinwerfen
cp ~/my_data/*.fasta ./fasta_inbox/

# 6. Status API
curl http://localhost:8000/memory
curl http://localhost:8000/best_parser
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

## Monitoring

- API: http://localhost:8000
- Logs: ./logs/ oder docker logs
- Memory: ./memory/organism_memory.json
- Inbox: ./fasta_inbox/

## Autonomer Loop anpassen

In autonomous_organism.py:

WATCH_INTERVAL = 10  # Sekunden
NIGHTLY_HOUR = 2      # Uhrzeit
# Für Demo: alle 120 Sekunden
if (now - last_nightly).total_seconds() > 120:
