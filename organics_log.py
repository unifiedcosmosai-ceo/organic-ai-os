"""
organics_log.py - Strukturiertes Logging fuer den Organic AI OS.
Layer 08 Homoeostase: protokolliert SCAN / HEAL / EVOLUTION / ERROR Events
in einer rotierenden Datei (logs/organism.log) und auf der Konsole.
"""

import logging
import logging.handlers
import sys
from pathlib import Path

_configured = False


def get_logger(name: str = "organism", level: int = logging.INFO) -> logging.Logger:
    """Liefert einen Logger mit einheitlichem Format und Rotating FileHandler."""
    global _configured
    logger = logging.getLogger(name)

    if _configured:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    logs_dir = Path(__file__).resolve().parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "organism.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _configured = True
    return logger


def event(logger: logging.Logger, kind: str, message: str, level: int = logging.INFO) -> None:
    """Loggt ein strukturiertes Event im Format 'EVENT_TYPE: message'."""
    logger.log(level, "%s | %s", kind, message)
