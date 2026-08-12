.PHONY: all test test-loop test-regression test-mcts test-skills test-budget test-spec test-tools test-ui test-validate test-guard test-dashboard coverage run parse evolve-now report clean

# Automatische Unit- + Regressions-Tests (CI-Einstieg)
all: test

# Lokale Tests: pytest (inkl. Regressions-Suite)
test:
	python3 -m pytest tests/ -v

# Automatischer Regressions-Loop: Compile + Weak-Code-Audit + volle Suite
test-loop:
	python3 tools/regression_loop.py --loop 3

# Automatischer Regressions-Loop mit auto-fix (bare except -> Exception)
fix:
	python3 tools/regression_loop.py --fix --loop 3

# Nur die Regressions-Suite (schnell)
test-regression:
	python3 -m pytest tests/test_regression.py -v

# Nur die MCTS-Suite (v5)
test-mcts:
	python3 -m pytest tests/test_mcts_evolver.py -v

# Nur die Skill-Library-Suite (v5)
test-skills:
	python3 -m pytest tests/test_skill_library.py -v

# Nur die Budget-Guard-Suite (v5)
test-budget:
	python3 -m pytest tests/test_budget_guard.py -v

# Nur die Format-Spec-Suite (v5)
test-spec:
	python3 -m pytest tests/test_format_spec.py -v

# Nur die Tool-Registry-Suite (v5)
test-tools:
	python3 -m pytest tests/test_tool_registry.py -v

# Nur API-Tests
test-api:
	python3 -m pytest tests/test_api.py -v

# Nur UI + Brainstorm-Suite (v6)
test-ui:
	python3 -m pytest tests/test_ui_and_brainstorm.py -v

# Nur Validierungs-Schema-Suite (v6)
test-validate:
	python3 -m pytest tests/test_validation_schema.py -v

# Nur Fitness-Fruehwarnungs-Suite (v6)
test-guard:
	python3 -m pytest tests/test_fitness_guard.py -v

# Nur Dashboard-Suite (v6)
test-dashboard:
	python3 -m pytest tests/test_dashboard.py -v

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