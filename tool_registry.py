"""
LAYER 12: TOOL-REGISTRY + AGENT-FASSADE + REPLAY (v5)
"Organic-Copilot": orchestriert alle Faehigkeiten ueber eine Tool-Registry,
loggt jeden Aufruf (FEV-Provenance) und erlaubt reproduzierbares Replay.

Forschung 2026 (BioMedAgent, KBase, MARWA, FEV):
- Tools als aufgerufene Funktionen mit Namen+Beschreibung (Tool-Abstraktion)
- Deterministisches Replay: geloggte Sequenz -> identischer Pfad (Seed-fix)
- Provenance-Bundle: Antwort + Aufrufliste + Version als reproduzierbares Paket
"""

import hashlib
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass
class ReplayEntry:
    ts: float
    tool: str
    args: dict
    result: object
    ok: bool
    seed: Optional[int]

    def to_dict(self) -> dict:
        return {"ts": self.ts, "tool": self.tool, "args": self.args,
                "result": self.result, "ok": self.ok, "seed": self.seed}


def _hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:12]


def _seed_parse_fasta(use_splitlines=False) -> str:
    """Standard parse_fasta Saatcode fuer MCTS/Skill/Budget Tools."""
    split = "text.splitlines()" if use_splitlines else 'text.split("\\n")'
    return f"""def parse_fasta(text):
    records = {{}}
    header = ""
    for line in {split}:
        if line.startswith(">"):
            header = line[1:].split()[0]
            records[header] = ""
        else:
            records[header] += line.strip().upper()
    return records
"""


def _t_basic_parser(ns) -> bool:
    """parse_fasta Basistest: 2 Records."""
    try:
        return len(ns["parse_fasta"](">a\nATGC\n>b\nGG\n")) == 2
    except Exception:
        return False


class ToolRegistry:
    """Registriert + ruft Faehigkeiten auf; fuehrt Replay-Log (FEV)."""

    def __init__(self, replay_path: Optional[Path] = None, seed: Optional[int] = None):
        self.tools: Dict[str, Callable] = {}
        self.tool_meta: Dict[str, dict] = {}
        self.replay: List[ReplayEntry] = []
        self.replay_path = replay_path
        self.seed = seed or 42

    # --- Registrierung ---
    def register(self, name: str, fn: Callable, description: str = ""):
        self.tools[name] = fn
        self.tool_meta[name] = {"description": description, "callable": fn.__name__}

    def register_all(self, bundle: Dict[str, Callable], descriptions: Optional[Dict[str, str]] = None):
        for name, fn in bundle.items():
            desc = (descriptions or {}).get(name, "")
            self.register(name, fn, desc)

    def list_tools(self) -> List[str]:
        return sorted(self.tools)

    # --- Ausfuehrung + Replay ---
    def run(self, tool: str, **kwargs) -> dict:
        """Fuehrt Tool aus und protokolliert (Replay-Log FEV). Result mit ok-Flag."""
        if tool not in self.tools:
            entry = self._log(tool, kwargs, {"error": f"unknown tool: {tool}"}, ok=False)
            return entry
        try:
            start = time.monotonic()
            result = self.tools[tool](**kwargs)
            entry = self._log(tool, kwargs, result, ok=True, ms=(time.monotonic() - start) * 1000)
        except Exception as e:
            entry = self._log(tool, kwargs, {"error": f"{type(e).__name__}: {e}"}, ok=False)
        return entry

    def _log(self, tool: str, args: dict, result, ok: bool, ms: float = 0.0) -> dict:
        entry = ReplayEntry(ts=time.time(), tool=tool, args=args, result=result, ok=ok, seed=self.seed)
        self.replay.append(entry)
        return {"ok": ok, "tool": tool, "args": args, "result": result,
                "ts": entry.ts, "ms": round(ms, 2), "replay_hash": _hash(entry.to_dict())}

    # --- Replay (FEV-treu) ---
    def save_replay(self, path: Optional[Path] = None) -> Path:
        path = path or self.replay_path
        if path is None:
            path = Path("memory") / "replay_log.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "seed": self.seed,
            "entries": [e.to_dict() for e in self.replay],
            "bundle_hash": _hash([e.to_dict() for e in self.replay]),
        }, indent=2, ensure_ascii=False))
        self.replay_path = path
        return path

    @classmethod
    def load_replay(cls, path: Path) -> dict:
        return json.loads(path.read_text())

    def verify_replay(self, path: Path) -> bool:
        """Prueft, dass das geloggte Bundle-Integritaet stimmt (Anti-Tamper)."""
        data = cls_load(path)
        entries = data["entries"]
        return data["bundle_hash"] == _hash(entries)

    @property
    def summary(self) -> dict:
        tools_used = {}
        for e in self.replay:
            tools_used[e.tool] = tools_used.get(e.tool, 0) + 1
        return {"tools_used": tools_used, "total_calls": len(self.replay),
                "failed": sum(1 for e in self.replay if not e.ok),
                "replay_hash": _hash([e.to_dict() for e in self.replay])}


def cls_load(path: Path) -> dict:
    return json.loads(path.read_text())


# --- Vordefinierte Tools (Bundles) ---
def parse_file_tool(filepath: str) -> dict:
    import bio_formats
    content = Path(filepath).read_text()
    fmt, records = bio_formats.parse_file(content)
    return {"format": fmt, "records": len(records), "sample": str(records)[:200]}


def parse_spec_tool(filepath: str) -> dict:
    from format_spec import default_specs, detect_spec, parse_file_spec
    content = Path(filepath).read_text()
    spec = detect_spec(content)
    if spec is None:
        return {"error": "no spec detected"}
    records = parse_file_spec(spec, content)
    return {"spec": spec.name, "records": len(records), "sample": str(records)[:200]}


def status_tool() -> dict:
    import autonomous_organism as ao
    memory = ao.OrganismMemory()
    hof = memory.data.get("hall_of_fame", [])
    return {"evolution_count": memory.data.get("evolution_count", 0),
            "files_seen": len(memory.data.get("seen_files", {})),
            "hall_of_fame": [{"name": h["name"], "fitness": h.get("fitness", 0)} for h in hof][:5]}


def mcts_evolve_tool(iterations: int = 60) -> dict:
    sys.path.insert(0, "11_evolution")
    from mcts_evolver import MCTSEvolution
    from llm_evolver import FitnessEvaluator, Strand

    seed = _seed_parse_fasta(use_splitlines=True)
    engine = MCTSEvolution(max_rollouts=iterations)
    tests = engine.adversarial_tests([(_t_basic_parser, 1.0)])
    best = engine.run_mcts(Strand(name="v5_adam", code=seed), FitnessEvaluator,
                           tests, iterations=iterations)
    return {"champion": best.strand.name, "fitness": round(best.strand.fitness, 4),
            "visits": best.visits}


def skill_library_tool(iterations: int = 60) -> dict:
    sys.path.insert(0, "11_evolution")
    from skill_library import SkillLibrary
    from mcts_evolver import MCTSEvolution
    from llm_evolver import FitnessEvaluator, Strand

    seed = _seed_parse_fasta(use_splitlines=True)
    engine = MCTSEvolution(max_rollouts=iterations)
    tests = engine.adversarial_tests([(_t_basic_parser, 1.0)])
    root = engine.run_mcts(Strand(name="adam", code=seed), FitnessEvaluator, tests,
                           iterations=iterations)
    lib = SkillLibrary.load(Path("memory") / "skill_library.json")
    added = 0
    for t in SkillLibrary.extract_from_mcts(root):
        t.verified, fit = lib.verify(t, FitnessEvaluator, tests)
        t.fitness = fit
        if lib.add(t):
            added += 1
    lib.save(Path("memory") / "skill_library.json")
    return {"skills_added": added, "total_skills": len(lib.skills)}


def budget_tool(iterations: int = 40, token_budget: float = 300.0) -> dict:
    sys.path.insert(0, "11_evolution")
    from budget_guard import BudgetGuard, budgeted_mcts
    from mcts_evolver import MCTSEvolution
    from llm_evolver import FitnessEvaluator, Strand

    seed = _seed_parse_fasta(use_splitlines=True)
    engine = MCTSEvolution(max_rollouts=iterations)
    tests = engine.adversarial_tests([(_t_basic_parser, 1.0)])
    with BudgetGuard(token_budget=token_budget, time_budget=30,
                     iteration_budget=iterations, soft=True) as guard:
        root, snap = budgeted_mcts(engine, Strand(name="adam", code=seed),
                                   FitnessEvaluator, tests, iterations, guard)
    best = engine._best_confirmed(root)
    return {"champion_fitness": round(best.strand.fitness, 4),
            "budget": snap.to_dict()}


def specs_tool() -> dict:
    from format_spec import default_specs, list_specs
    specs = default_specs()
    return {"specs": [{"name": n, "marker": specs[n].marker,
                       "columns": len(specs[n].columns)} for n in list_specs()]}


def make_agent(tools: Optional[Dict[str, Callable]] = None,
               replay_path: Optional[Path] = None, seed: Optional[int] = None) -> ToolRegistry:
    """Fabrik: Agent mit Standard-Tools + Replay-Log."""
    reg = ToolRegistry(replay_path=replay_path, seed=seed)
    default = {
        "parse_file": parse_file_tool,
        "parse_spec": parse_spec_tool,
        "status": status_tool,
        "mcts_evolve": mcts_evolve_tool,
        "skill_library": skill_library_tool,
        "budget": budget_tool,
        "specs": specs_tool,
    }
    if tools:
        default.update(tools)
    descriptions = {
        "parse_file": "Parst FASTA/FASTQ (Auto-Detect)",
        "parse_spec": "Parst GFF3/VCF ueber Format-Spec",
        "status": "Organismus-Status (Evolution, Hall of Fame)",
        "mcts_evolve": "MCTS-gesteuerte Evolution (Champion)",
        "skill_library": "MCTS-Rollouts -> verifizierte Skills",
        "budget": "Budget-begrenzter MCTS-Run",
        "specs": "Registrierte Format-Specs",
    }
    reg.register_all(default, descriptions)
    return reg


def run_agent_workflow(reg: ToolRegistry, steps: List[str]) -> dict:
    """Fuehrt eine Folge von Tool-Schritten aus (KBase-Narrative-Ansatz)."""
    results = {}
    for step in steps:
        if ":" in step:
            tool, arg = step.split(":", 1)
            results[step] = reg.run(tool, filepath=arg)
        else:
            results[step] = reg.run(step)
    return results


if __name__ == "__main__":
    agent = make_agent(replay_path=Path("memory") / "replay_demo.json", seed=7)
    out = run_agent_workflow(agent, ["status", "specs", "budget"])
    for k, v in out.items():
        print(f"  {k}: ok={v['ok']} result={v['result']}")
    bundle = agent.save_replay()
    print(f"\n📦 Replay-Bundle: {bundle}")
    print(f"Summary: {agent.summary}")
    print(f"Verify: {agent.verify_replay(bundle)}")