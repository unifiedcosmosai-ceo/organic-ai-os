"""Tests für config.py (Konfigurations-Layer)."""

import os

os.environ.pop("ORGANIC_PORT", None)
os.environ.pop("ORGANIC_POPULATION_SIZE", None)

import config


def test_defaults_loaded():
    cfg = config.load_config(config_path=None)
    assert cfg["port"] == 8000
    assert cfg["hall_of_fame_size"] == 5
    assert cfg["llm_provider"] in ("fallback", "ollama")


def test_env_override(tmp_path):
    os.environ["ORGANIC_PORT"] = "9000"
    cfg = config.load_config(config_path=None)
    assert cfg["port"] == 9000
    os.environ.pop("ORGANIC_PORT", None)


def test_toml_wins_over_defaults(tmp_path):
    toml = tmp_path / "organic.toml"
    toml.write_text("# beispiel\nwatch_interval = 3.5\n")
    cfg = config.load_config(config_path=toml)
    assert cfg["watch_interval"] == 3.5


def test_bool_env(tmp_path):
    os.environ["ORGANIC_EVOLVE_ON_STARTUP"] = "true"
    cfg = config.load_config(config_path=None)
    assert cfg["evolve_on_startup"] is True
    os.environ.pop("ORGANIC_EVOLVE_ON_STARTUP", None)