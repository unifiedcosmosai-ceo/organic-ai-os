"""
Regressions-Suite: prueft ALLE Einstiegspunkte des Organic AI OS.
Laueft automatisch in CI (make test) - faengt Verbindungs-/Refactor-Regressionen.
"""

import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run_py(args, timeout=60):
    return subprocess.run(
        [sys.executable, *args], cwd=ROOT,
        capture_output=True, text=True, timeout=timeout,
    )


# ---- 1. Einstiegspunkte laufen ohne Traceback ----
def test_evolving_base_runs():
    r = _run_py(["organic_ai_os_evolving.py"])
    assert r.returncode == 0, r.stderr
    assert "WINNER" in r.stdout or "FINAL" in r.stdout


def test_evolving_1_runs():
    r = _run_py(["organic_ai_os_evolving_1.py"])
    assert r.returncode == 0, r.stderr
    assert "WINNER" in r.stdout or "FINAL" in r.stdout


def test_evolving_2_runs():
    r = _run_py(["organic_ai_os_evolving_2.py"])
    assert r.returncode == 0, r.stderr
    assert "WINNER" in r.stdout or "FINAL" in r.stdout


def test_evolving_3_runs():
    r = _run_py(["organic_ai_os_evolving_3.py"])
    assert r.returncode == 0, r.stderr
    assert "WINNER" in r.stdout or "FINAL" in r.stdout


# ---- 2. Ollama-Integration: Import darf nie crashen ----
def test_ollama_import_never_crashes():
    mod = importlib.import_module("ollama_integration")
    m = mod.OllamaMutator()
    assert m._client is not None  # lazy: kein ollama-Paket noetig


def test_ollama_missing_raises_clear_error():
    import ollama_integration as oi

    m = oi.OllamaMutator()
    try:
        m.mutate("code", "instruction")
        raised = False
    except ConnectionError:
        raised = True
    except ModuleNotFoundError:
        # ollama zufaellig doch installiert -> kein Fehler-Fall
        raised = False
    assert raised


# ---- 3. LLMMutator OLLAMA-Provider braucht kein Ollama ----
def test_llmmutator_fallback_default():
    import llm_evolver

    m = llm_evolver.LLMMutator("fallback")
    out = m._call_llm("sys", "~~~```python\ndef f():\n    return 0\n```")
    # AST-Fallback muss valides Python liefern (Konstanten koennen mutiert sein)
    import ast

    ast.parse(out)
    assert "def f" in out


def test_llmmutator_ollama_provider_silently_falls_back():
    import llm_evolver

    m = llm_evolver.LLMMutator("ollama")
    # Wenn ollama fehlt -> provider = fallback, kein Crash
    assert m.provider in ("fallback", "ollama")
    out = m._call_llm("sys", "text")
    assert isinstance(out, str)


# ---- 4. CLI-Subcommands (app.py) ----
def test_cli_parse():
    r = _run_py(["app.py", "parse", "fasta_inbox/example_clean.fasta"])
    assert r.returncode == 0, r.stderr
    assert "fasta" in r.stdout


def test_cli_status_json():
    r = _run_py(["app.py", "status", "--json"])
    assert r.returncode == 0, r.stderr
    import json

    json.loads(r.stdout)  # muss valides JSON sein


def test_cli_report():
    r = _run_py(["app.py", "report"])
    assert r.returncode == 0, r.stderr
    assert (ROOT / "reports" / "report.json").exists()


def test_cli_evolution_modules():
    import bio_formats
    import config

    assert callable(bio_formats.parse_file)
    assert "hall_of_fame_size" in config.load_config()


# ---- 5. Keine toten Ollama-Stubs mehr ----
def test_no_dead_ollama_stub():
    src = (ROOT / "11_evolution" / "llm_evolver.py").read_text()
    assert "pass  # import ollama" not in src
    assert "# import ollama; return" not in src