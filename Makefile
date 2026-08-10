.PHONY: test test-api coverage run make-migrate demo clean

# Lokale Tests: pytest
test:
	python3 -m pytest tests/ -v

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

# PyCache aufräumen
clean:
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; true