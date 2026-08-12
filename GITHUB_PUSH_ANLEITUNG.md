
# GitHub Push Anleitung

Dein Repo ist bereit: dieser Ordner (`organic-ai-os`).

## Option 1: GitHub Website (einfachste)

1. Gehe zu https://github.com/new
2. Repo Name: organic-ai-os
3. Description: 🧬 13-Layer Organic AI OS - Self-evolving FASTA parser with LLM mutation (v6: UI + MCTS-Idea-Forest)
4. Public, NICHT mit README initialisieren
5. Create

6. Dann lokal (auf deinem PC):

```bash
# Entpacke das tar.gz das du hier runterlädst
tar -xzf organic_ai_platform.tar.gz
cd organic_ai_platform

git init
git add .
git commit -m "🧬 Initial commit: 13-Layer Organic AI OS"

# Ersetze USERNAME
git remote add origin https://github.com/USERNAME/organic-ai-os.git
git branch -M main
git push -u origin main
```

## Option 2: GitHub CLI

```bash
cd organic_ai_platform
gh repo create organic-ai-os --public --source=. --remote=origin --push
```

## Was wird gepusht:

- README.md, DOCS.md, MANUAL.md, DEPLOY.md, CHAT_LOG.md
- autonomous_organism.py (Hauptloop)
- api_server.py
- 09_neuro/neuro_evolving.py
- 11_evolution/llm_evolver.py
- Dockerfile + docker-compose.yml
- organic-organism.service + install.sh
- fasta_inbox/examples
- memory/best_parser_example

Repository-Hinweise:
- `kali-linux-docker/` ist ein separates eingebettetes Repo und wird nicht gepusht
- `logs/` (rotierende organisms.log) ist per .gitignore ausgeschlossen

## Nach dem Push:

Füge in GitHub Repo Settings:
- Topics: bioinformatics, ai, evolution, llm, self-evolving, fasta, python
- Description: 🧬 Organic AI OS - Code as DNA, Prompts as mRNA, LLM as Ribosome. Autonomous FASTA parser that evolves nightly at 02:00. v6: 13 Layer, UI + MCTS-Idea-Forest.

Dein Tarball: /mnt/data/organic_ai_platform.tar.gz (54.9 KB)
