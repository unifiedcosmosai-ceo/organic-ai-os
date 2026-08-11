.PHONY: all test test-api test-regression test-mcts test-skills coverage run parse evolve-now report clean

# Automatische Unit- + Regressions-Tests (CI-Einstieg)
all: test

# Lokale Tests: pytest (inkl. Regressions-Suite)
test:
	python3 -m pytest tests/ -v

# Nur die Regressions-Suite (schnell)
test-regression:
	python3 -m pytest tests/test_regression.py -v

# Nur die MCTS-Suite (v5)
test-mcts:
	python3 -m pytest tests/test_mcts_evolver.py -v

# Nur die Skill-Library-Suite (v5)
test-skills:
	python3 -m pytest tests/test_skill_library.py -v

# Nur API-Tests
test-api:
	python3 -m pytest tests/test_api.py -v

# Coverage anzeigen
coverage:
	python3 -m pytest tests/ --cov=. --cov-report=term-missing

# Organismus starten (Watcher + API)
run:
	python3 app.py watch

# CLI: Datei parsen mit Auto-Detection
parse:
	python3 app.py parse $(FILE)

# Evolution sofort triggern
evolve-now:
	python3 app.py evolve-now

# Tagesreport erzeugen
report:
	python3 app.py report

# PyCache aufräumen
clean:
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; true