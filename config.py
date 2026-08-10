"""
config.py - Konfigurations-Layer fuer den Organic AI OS (05 Epigenom).

Prioritaet (niedrig -> hoch):
  1. Defaults
  2. Umgebungsvariablen (ORGANIC_*)
  3. organic.toml (falls vorhanden)
  4. CLI-Argumente (werden im App-Code uebergeben)
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

DEFAULTS = {
    "watch_dir": str(ROOT / "fasta_inbox"),
    "memory_dir": str(ROOT / "memory"),
    "logs_dir": str(ROOT / "logs"),
    "port": 8000,
    "watch_interval": 2.0,
    "nightly_interval": 120.0,
    "nightly_hour": 2,
    "population_size": 8,
    "generations": 10,
    "hall_of_fame_size": 5,
    "llm_provider": "fallback",
    "ollama_host": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
    "ollama_model": "codellama:7b",
    "llm_timeout": 30,
    "evolve_on_startup": False,
}


def _load_toml(path: Path) -> dict:
    """Minimaler TOML-Parser (Python <3.11 ohne tomllib): nur key = value Zeilen."""
    cfg = {}
    if not path.exists():
        return cfg
    import ast

    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("["):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        try:
            cfg[key] = ast.literal_eval(val)
        except (ValueError, SyntaxError):
            cfg[key] = val
    return cfg


def _env_override(name: str, default):
    env = os.environ.get(f"ORGANIC_{name.upper()}")
    if env is None:
        return default
    if isinstance(default, bool):
        return env.lower() in ("1", "true", "yes", "on")
    if isinstance(default, int):
        try:
            return int(env)
        except ValueError:
            return default
    if isinstance(default, float):
        try:
            return float(env)
        except ValueError:
            return default
    return env


def load_config(config_path: Path = None) -> dict:
    """Liest die Konfiguration nach Prioritaet defaults < .env < organic.toml."""
    cfg = dict(DEFAULTS)
    toml = _load_toml(config_path or (ROOT / "organic.toml"))
    cfg.update(toml)
    for key in list(DEFAULTS.keys()):
        cfg[key] = _env_override(key, cfg[key])
    return cfg