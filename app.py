"""
ORGANIC AI OS - kombinierte Einzel-Anwendung (app.py)
Vereint alle Layer des Projekts in einem Einstiegspunkt:

  - core/organic_base.py          Layer 01   Genom / OrganicStrand
  - 09_neuro/neuro_evolving.py    Layer 09   Neuro / Prompt Cortex
  - 11_evolution/llm_evolver.py   Layer 11   Evolution / LLM Mutator
  - autonomous_organism.py        Layer 03/08 Watcher + Memory + Immunsystem
  - api_server.py                 Layer 12   FastAPI Status/API

Start:
  python app.py                 Watcher + naechtliche Evolution + API (Threads)
  python app.py --api-only      nur FastAPI auf Port 8000
  python app.py --demo          ein schneller Code-Evolutions-Durchlauf
  python app.py --neuro-demo    ein schneller Prompt-Evolutions-Durchlauf
"""

import argparse
import threading
from pathlib import Path

import sys

ROOT = Path(__file__).parent
for folder in ("core", "09_neuro", "11_evolution"):
    sys.path.insert(0, str(ROOT / folder))


def build_app():
    """Erzeugt das FastAPI-App-Objekt aus api_server.py."""
    from api_server import app
    return app


def run_demo():
    """Schneller Code-Evolutions-Durchlauf (LLM-Evolver Demo)."""
    from llm_evolver import LLMMutator, FitnessEvaluator, EvolutionEngine

    initial = """
def gc_content(seq):
    gc = seq.count("G") + seq.count("C")
    return gc / len(seq) if seq else 0
"""

    def test_correctness(ns):
        if "gc_content" not in ns:
            return False
        try:
            return abs(ns["gc_content"]("GGCCAA") - 0.666) < 0.01
        except Exception:
            return False

    engine = EvolutionEngine(population_size=6, mutator=LLMMutator("fallback"))
    engine.seed(initial, name="gc_adam")
    winner = engine.evolve(FitnessEvaluator, [(test_correctness, 0.8)], generations=5)
    print("\nWINNER CODE:\n" + winner.code)


def run_neuro_demo():
    """Schneller Prompt-Evolutions-Durchlauf (Neuro Cortex Demo)."""
    from neuro_evolving import NeuroCortex, test_basic, test_robust

    cortex = NeuroCortex()
    winner = cortex.evolve([(test_basic, 0.6), (test_robust, 0.4)], generations=8, pop_size=8)
    print("\nWINNER PROMPT:\n" + winner.prompt_template)


def run_organism(port: int = 8000):
    """Startet Watcher + naechtliche Evolution + API parallel."""
    from autonomous_organism import main as organism_main
    import uvicorn
    from api_server import app

    organism_thread = threading.Thread(target=organism_main, daemon=True)
    organism_thread.start()

    def serve():
        print(f"\n🛰️  API auf http://0.0.0.0:{port}")
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

    api_thread = threading.Thread(target=serve, daemon=True)
    api_thread.start()

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\n🛑 Organismus gestoppt")


def main():
    parser = argparse.ArgumentParser(description="Organic AI OS - kombiniert alle Layer")
    parser.add_argument("--api-only", action="store_true", help="nur FastAPI starten (Port 8000)")
    parser.add_argument("--demo", action="store_true", help="Code-Evolutions-Demo ausfuehren")
    parser.add_argument("--neuro-demo", action="store_true", help="Prompt-Evolutions-Demo ausfuehren")
    parser.add_argument("--port", type=int, default=8000, help="API Port (default 8000)")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.neuro_demo:
        run_neuro_demo()
    elif args.api_only:
        import uvicorn
        from api_server import app

        uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="warning")
    else:
        run_organism(port=args.port)


if __name__ == "__main__":
    main()