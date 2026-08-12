"""pytest-Konfiguration: Projektroot + Layer auf sys.path legen."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
for folder in ("core", "09_neuro", "10_symbiom", "11_evolution", "12_phenotype", "13_ui"):
    sys.path.insert(0, str(ROOT / folder))