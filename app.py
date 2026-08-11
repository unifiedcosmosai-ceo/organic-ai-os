"""
ORGANIC AI OS - kombinierte Einzel-Anwendung (app.py)
Vereint alle Layer des Projekts in einem Einstiegspunkt:

  - core/organic_base.py          Layer 01   Genom / OrganicStrand
  - 09_neuro/neuro_evolving.py    Layer 09   Neuro / Prompt Cortex
  - 11_evolution/llm_evolver.py   Layer 11   Evolution / LLM Mutator
  - autonomous_organism.py        Layer 03/08 Watcher + Memory + Immunsystem
  - bio_formats.py                Layer 03   Multi-Format Parser (FASTA/FASTQ)
  - config.py                     Layer 05   Konfiguration (Defaults/env/organic.toml)
  - api_server.py                 Layer 12   FastAPI Status/API
  - 10_symbiom/                   Layer 09/10 Symbiom Schwarm + Co-Evolution
  - 12_phenotype/reporter.py      Layer 12   Tagesreport (JSON + HTML)

CLI-Subcommands:
  python app.py watch                Watcher + naechtliche Evolution + API (Threads)
  python app.py serve [--port N]     nur FastAPI
  python app.py parse <file>         Datei parsen (Auto-Detection FASTA/FASTQ)
  python app.py evolve-now           Evolution sofort triggern
  python app.py status               Statusreport aus Memory/Hall of Fame
  python app.py coevolve             Prompt<->Code Co-Evolution starten
  python app.py report               Tagesreport erzeugen (JSON + HTML)
  python app.py demo                 Code-Evolutions-Demo
  python app.py neuro-demo           Prompt-Evolutions-Demo
"""

import argparse
import json
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).parent
for folder in ("core", "09_neuro", "11_evolution"):
    sys.path.insert(0, str(ROOT / folder))


def _cfg(args):
    import config
    return config.load_config()


def build_app():
    from api_server import app
    return app


def run_demo():
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
    from neuro_evolving import NeuroCortex, test_basic, test_robust

    cortex = NeuroCortex()
    winner = cortex.evolve([(test_basic, 0.6), (test_robust, 0.4)], generations=8, pop_size=8)
    print("\nWINNER PROMPT:\n" + winner.prompt_template)


def cmd_parse(args):
    """Parst eine Datei mit Auto-Detection (FASTA/FASTQ)."""
    import bio_formats

    path = Path(args.file)
    content = path.read_text(errors="ignore")
    fmt, result = bio_formats.parse_file(content)
    print(f"Format: {fmt} | Records: {len(result)}")
    for header, rec in list(result.items())[:args.limit]:
        if isinstance(rec, dict):
            print(f"  {header}: seq={rec['seq'][:40]} qual={rec.get('qual','')[:20]}")
        else:
            print(f"  {header}: {rec[:60]}")


def cmd_stats(args):
    """Statusreport aus Memory + Hall of Fame."""
    import io
    import contextlib

    # stdout wegleiten, damit Logger-Output nicht die JSON-Ausgabe verschmutzt
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        import autonomous_organism as ao

    memory = ao.OrganismMemory()
    hof_path = Path(ao.MEMORY_DIR) / "hall_of_fame.json"
    hof = json.loads(hof_path.read_text()) if hof_path.exists() else []
    report = {
        "evolution_count": memory.data.get("evolution_count", 0),
        "files_seen": len(memory.data.get("seen_files", {})),
        "failures": len(memory.data.get("failures", [])),
        "best_strands": len(memory.data.get("best_strands", {})),
        "hall_of_fame": [{"name": h["name"], "fitness": round(h["fitness"], 3), "gen": h["generation"]} for h in hof],
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for k, v in report.items():
            print(f"{k}: {v}")
    return report


def cmd_evolve_now(args):
    """Trigger Evolution sofort und zeige den neuen Champion."""
    import autonomous_organism as ao

    memory = ao.OrganismMemory()
    watcher = ao.FastaWatcher(memory)
    ao.NightlyEvolution(memory, watcher).run_nightly()
    best = Path(ao.MEMORY_DIR) / "best_parser.py"
    if best.exists():
        print("\nAktueller Champion (best_parser.py):")
        print(best.read_text()[:600])
    if args.show_hof:
        hof_path = Path(ao.MEMORY_DIR) / "hall_of_fame.json"
        if hof_path.exists():
            print("\nHall of Fame:")
            print(hof_path.read_text()[:800])


def cmd_coevolve(args):
    """Startet die Prompt<->Code Co-Evolution (Layer 09/10)."""
    import importlib
    import json

    coevo = importlib.import_module("10_symbiom.co_evolution")
    code, prompt, hist = coevo.evolve(rounds=args.rounds, swarm_generations=args.swarm_gen)
    print("\n✅ CO-EVOLUTION FERTIG")
    print(f"Bester Code: {code.name} fit={code.fitness:.3f}")
    print(f"Bester Prompt: {prompt.name} fit={prompt.fitness:.3f}")
    if args.save:
        out = Path("memory") / "coevolution_report.json"
        out.write_text(json.dumps(hist, indent=2, ensure_ascii=False))
        print(f"Report: {out}")


def cmd_report(args):
    """Erzeugt den Tagesreport (JSON + HTML)."""
    import importlib

    reporter = importlib.import_module("12_phenotype.reporter")
    jp, hp = reporter.generate_report()
    print(f"Report JSON: {jp}")
    print(f"Report HTML: {hp}")


def cmd_mcts_evolve(args):
    """Startet die MCTS-gesteuerte Evolution (v5, Layer 11)."""
    sys.path.insert(0, "11_evolution")
    mcts = __import__("11_evolution.mcts_evolver", fromlist=["MCTSEvolution", "Strand"])
    evo_mod = __import__("11_evolution.llm_evolver", fromlist=["FitnessEvaluator"])

    seed = """def parse_fasta(text):
    records = {}
    header = ""
    for line in text.split("\\n"):
        if line.startswith(">"):
            header = line[1:].split()[0]
            records[header] = ""
        else:
            records[header] += line.strip().upper()
    return records
"""
    if args.seed_code:
        seed = Path(args.seed_code).read_text()

    def t_basic(ns):
        if "parse_fasta" not in ns:
            return False
        try:
            return len(ns["parse_fasta"](">a\nATGC\n>b\nGG\n")) == 2
        except Exception:
            return False

    def t_messy(ns):
        if "parse_fasta" not in ns:
            return False
        try:
            r = ns["parse_fasta"](">h x\n  atgc  \n\n>b\nGG\n")
            return len(r) == 2 and all(" " not in v for v in r.values())
        except Exception:
            return False

    tests = [(t_basic, 0.6), (t_messy, 0.4)]
    if args.tests == "adversarial":
        print("🌀 Verdrahtung: adversarial tests aktiviert")
        # invers: da default Pfad ohnehin adversarial ist, nur Info
    engine = mcts.MCTSEvolution(max_rollouts=args.iterations)
    root = mcts.Strand(name="v5_adam", code=seed)
    testset = engine.adversarial_tests(tests) if args.tests == "adversarial" else tests
    if args.budget:
        bg = __import__("11_evolution.budget_guard", fromlist=["BudgetGuard", "budgeted_mcts"])
        with bg.BudgetGuard(token_budget=max(100, args.iterations), time_budget=60,
                            iteration_budget=args.iterations, soft=True) as guard:
            best_root, snap = bg.budgeted_mcts(engine, root, evo_mod.FitnessEvaluator,
                                               testset, args.iterations, guard)
        best = engine._best_confirmed(best_root)
        print(f"\n⏱️  Budget-Guard: tokens {snap.tokens_used:.0f}/{snap.token_budget:.0f} | "
              f"iter {snap.iterations_used}/{snap.iteration_budget} | time {snap.time_used:.2f}s | "
              f"depth {snap.depth} | searches {snap.searches_run}")
    else:
        best = engine.run_mcts(root, evo_mod.FitnessEvaluator, testset, iterations=args.iterations)
    print(f"\n🏆 MCTS CHAMPION: {best.strand.name}  fit={best.strand.fitness:.3f}  visits={best.visits}")
    print("-" * 50)
    print(best.strand.code)
    if args.tests == "adversarial":
        print("-" * 50)
        print("Adversarial-Tests erhalten: Grenzfaelle (blank lines, Duplikat-Header, lowercase) sind Teil der Bewertung.")


def cmd_skills(args):
    """MCTS-Rollouts → verifizierte Skills (v5, Layer 11)."""
    sys.path.insert(0, "11_evolution")
    mcts = __import__("11_evolution.mcts_evolver", fromlist=["MCTSEvolution", "Strand"])
    evo_mod = __import__("11_evolution.llm_evolver", fromlist=["FitnessEvaluator"])
    skills_mod = __import__("11_evolution.skill_library", fromlist=["SkillLibrary"])

    seed = """def parse_fasta(text):
    records = {}
    header = ""
    for line in text.split("\\n"):
        if line.startswith(">"):
            header = line[1:].split()[0]
            records[header] = ""
        else:
            records[header] += line.strip().upper()
    return records
"""
    if args.seed_code:
        seed = Path(args.seed_code).read_text()

    def t_basic(ns):
        try:
            return len(ns["parse_fasta"](">a\nATGC\n>b\nGG\n")) == 2
        except Exception:
            return False

    def t_messy(ns):
        try:
            r = ns["parse_fasta"](">h x\n  atgc  \n\n>b\nGG\n")
            return len(r) == 2 and all(" " not in v for v in r.values())
        except Exception:
            return False

    tests = [(t_basic, 0.6), (t_messy, 0.4)]
    engine = mcts.MCTSEvolution(max_rollouts=args.iterations)
    testset = engine.adversarial_tests(tests)
    root = engine.run_mcts(mcts.Strand(name="v5_adam", code=seed),
                           evo_mod.FitnessEvaluator, testset, iterations=args.iterations)

    lib_path = Path("memory") / "skill_library.json"
    lib = skills_mod.SkillLibrary.load(lib_path)
    before = len(lib.skills)
    added = 0
    for t in skills_mod.SkillLibrary.extract_from_mcts(root, min_visits=args.min_visits):
        verified, fit = lib.verify(t, evo_mod.FitnessEvaluator, testset)
        t.verified = verified
        if lib.add(t):
            added += 1
            print(f"➕ Skill: {t.name} fit={fit:.3f}")
    lib.save(lib_path)
    print(f"\n📚 Bibliothek: {before} → {len(lib.skills)} Skills (neu: {added}) → {lib_path}")
    if args.list:
        print("\nTop-Skills:")
        for i, s in enumerate(lib.retrieve(limit=5), 1):
            print(f"  {i}. {s.name} fit={s.fitness:.3f} source={s.source} gen={s.generation}")


def cmd_budget(args):
    """Budget-Guard Demo: begrenzter MCTS-Run + Pareto-Report (v5)."""
    sys.path.insert(0, "11_evolution")
    mcts = __import__("11_evolution.mcts_evolver", fromlist=["MCTSEvolution", "Strand"])
    evo_mod = __import__("11_evolution.llm_evolver", fromlist=["FitnessEvaluator"])
    bg = __import__("11_evolution.budget_guard", fromlist=["BudgetGuard", "budgeted_mcts"])

    seed = """def parse_fasta(text):
    records = {}
    header = ""
    for line in text.splitlines():
        if line.startswith(">"):
            header = line[1:].split()[0]
            records[header] = ""
        else:
            records[header] += line.strip().upper()
    return records
"""

    def t_basic(ns):
        try:
            return len(ns["parse_fasta"](">a\nATGC\n>b\nGG\n")) == 2
        except Exception:
            return False

    def t_messy(ns):
        try:
            r = ns["parse_fasta"](">h x\n  atgc  \n\n>b\nGG\n")
            return len(r) == 2 and all(" " not in v for v in r.values())
        except Exception:
            return False

    tests = [(t_basic, 0.6), (t_messy, 0.4)]
    engine = mcts.MCTSEvolution(max_rollouts=args.iterations)
    testset = engine.adversarial_tests(tests)
    with bg.BudgetGuard(token_budget=args.token_budget, time_budget=30,
                        iteration_budget=args.iterations, soft=True) as guard:
        root, snap = bg.budgeted_mcts(engine, mcts.Strand(name="v5_adam", code=seed),
                                      evo_mod.FitnessEvaluator, testset, args.iterations, guard)
    best = engine._best_confirmed(root)
    print(f"\n⏱️  Budget-Guard Report")
    print(f"  Budget: {snap.to_dict()}")
    print(f"  Champion: {best.strand.name} fit={best.strand.fitness:.3f}")
    # REASON-CODE-Greedy: haette Search gespart?
    fit = evo_mod.FitnessEvaluator.evaluate(seed, testset)
    if fit >= 0.9:
        guard.record_greedy()
        print(f"  REASON-CODE: Greedy fit={fit:.3f} >= 0.9 -> MCTS-Search haette gespart werden koennen")
    else:
        print(f"  REASON-CODE: Greedy fit={fit:.3f} < 0.9 -> MCTS-Search war noetig")


def run_organism(port: int = 8000):
    """Startet Watcher + naechtliche Evolution + API parallel."""
    import autonomous_organism as ao
    import uvicorn
    from api_server import app

    organism_thread = threading.Thread(target=ao.main, daemon=True)
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
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("watch", help="Watcher + naechtliche Evolution + API (default)")
    sub.add_parser("demo", help="Code-Evolutions-Demo ausfuehren")
    sub.add_parser("neuro-demo", help="Prompt-Evolutions-Demo ausfuehren")

    serve_p = sub.add_parser("serve", help="nur FastAPI starten")
    serve_p.add_argument("--port", type=int, default=None, help="API Port")

    parse_p = sub.add_parser("parse", help="Datei parsen (FASTA/FASTQ Auto-Detection)")
    parse_p.add_argument("file", help="Pfad zur Sequenzdatei")
    parse_p.add_argument("--limit", type=int, default=10, help="Max. Records anzeigen")

    stats_p = sub.add_parser("status", help="Statusreport aus Memory/Hall of Fame")
    stats_p.add_argument("--json", action="store_true", help="Ausgabe als JSON")

    evolve_p = sub.add_parser("evolve-now", help="Evolution sofort triggern")
    evolve_p.add_argument("--show-hof", action="store_true", help="Hall of Fame anzeigen")

    coev_p = sub.add_parser("coevolve", help="Prompt<->Code Co-Evolution starten")
    coev_p.add_argument("--rounds", type=int, default=3, help="Co-Evolutions-Runden")
    coev_p.add_argument("--swarm-gen", type=int, default=6, help="Schwarm-Generationen pro Runde")
    coev_p.add_argument("--save", action="store_true", help="Report nach memory/coevolution_report.json")

    sub.add_parser("report", help="Tagesreport erzeugen (JSON + HTML)")

    mcts_p = sub.add_parser("mcts-evolve", help="MCTS-gesteuerte Evolution (v5) starten")
    mcts_p.add_argument("--iterations", type=int, default=150, help="MCTS-Rollouts")
    mcts_p.add_argument("--tests", choices=["base", "adversarial"], default="adversarial",
                        help="Testbasis (base = nur Kern-Tests, adversarial = + Grenzfaelle)")
    mcts_p.add_argument("--seed-code", default=None, help="Pfad zu Startcode (default: eingebauter parse_fasta-Saatcode)")
    mcts_p.add_argument("--budget", action="store_true",
                        help="Budget-Guard aktivieren (Tokens/Zeit/Iterationen begrenzen, adaptive Tiefe)")

    budget_p = sub.add_parser("budget", help="Budget-Guard Check & Status (v5)")
    budget_p.add_argument("--token-budget", type=float, default=500.0, help="Token-Budget")
    budget_p.add_argument("--iterations", type=int, default=60, help="Iterations-Budget")
    budget_p.add_argument("--list", action="store_true", help="Budget-Run reporten")

    skills_p = sub.add_parser("skills", help="MCTS-Rollouts → Skill/Tactic-Bibliothek (v5)")
    skills_p.add_argument("--iterations", type=int, default=80, help="MCTS-Rollouts")
    skills_p.add_argument("--min-visits", type=int, default=2, help="Minimum an Rollout-Bestaetigungen")
    skills_p.add_argument("--list", action="store_true", help="Top-Skills nach dem Lauf anzeigen")
    skills_p.add_argument("--seed-code", default=None, help="Pfad zu Startcode")

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    elif args.command == "neuro-demo":
        run_neuro_demo()
    elif args.command == "parse":
        cmd_parse(args)
    elif args.command == "status":
        cmd_stats(args)
    elif args.command == "evolve-now":
        cmd_evolve_now(args)
    elif args.command == "coevolve":
        cmd_coevolve(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "skills":
        cmd_skills(args)
    elif args.command == "mcts-evolve":
        cmd_mcts_evolve(args)
    elif args.command == "budget":
        cmd_budget(args)
    elif args.command == "serve":
        import uvicorn
        from api_server import app

        port = args.port or _cfg(args)["port"]
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
    else:  # default: watch
        run_organism(port=_cfg(args)["port"])


if __name__ == "__main__":
    main()