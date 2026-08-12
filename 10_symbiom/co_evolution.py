"""
LAYER 10/09: CO-EVOLUTION - Prompt <-> Code Symbiose
Der Neuro-Cortex evolviert Prompts, die besseren Code erzeugen.
Der Symbiom-Schwarm evolviert Code, dessen Fitness wiederum die Prompts trainiert.

Kreislauf: prompt -> code -> fitness -> prompt-Auswahl -> besserer prompt -> ...
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "09_neuro"))
sys.path.insert(0, str(ROOT / "10_symbiom"))
sys.path.insert(0, str(ROOT / "11_evolution"))

from neuro_evolving import NeuroCortex
from symbiom_swarm import SymbiomSwarm, _test_parse, _test_messy


def _seed_code() -> str:
    return """
def parse_fasta(text):
    records={}
    curr=None
    buf=[]
    for line in text.splitlines():
        s=line.strip()
        if not s: continue
        if s.startswith(">"):
            if curr: records[curr]="".join(buf)
            curr=s[1:].split()[0]
            buf=[]
        else:
            buf.append(s.upper())
    if curr: records[curr]="".join(buf)
    return records
"""


def evolve(rounds=4, swarm_generations=6, pop_per_species=3, tests=None):
    """
    Fuehrt die co-evolutionaere Schleife aus.
    `tests`: Liste von (fitness_fn, gewicht) — default: eingebaute parse-Tests.
    Returns: (best_code_strand, best_prompt, history)
    """
    if tests is None:
        tests = [(_test_parse, 0.6), (_test_messy, 0.4)]

    cortex = NeuroCortex()
    cortex.seed()
    swarm = SymbiomSwarm(population_per_species=pop_per_species)
    swarm.seed(_seed_code())

    history = []
    best_code = None
    best_prompt = None

    for rnd in range(rounds):
        print(f"\n🌀 CO-EVOLUTION ROUND {rnd + 1}/{rounds}")
        # 1. Code-Schwarm evolvieren
        code_winner = swarm.evolve(tests, generations=swarm_generations)
        best_code = code_winner

        # 2. Neuro-Cortex: Prompts anhand der erzielten Fitness mutieren
        pop = list(cortex.strands.values())
        for p in pop:
            # Prompt-Fitness = Code-Fitness des Gewinners (Symbiose) + Qualitaet
            p.fitness = code_winner.fitness * 0.6 + min(0.4, len(p.prompt_template) / 300)
        pop.sort(key=lambda x: x.fitness, reverse=True)
        best_prompt = pop[0]

        # 3. Naechste Runde: Schwarm mit bestem Prompt inspirieren
        hint = best_prompt.prompt_template
        for s in swarm.symbionts:
            if "[PROMPT-HINT]" not in s.code:
                s.code = f"# prompt-hint: {hint[:80]}\n{s.code}"

        history.append({
            "round": rnd + 1,
            "code_best": {"name": code_winner.name, "fitness": round(code_winner.fitness, 4)},
            "prompt_best": {"name": best_prompt.name, "fitness": round(best_prompt.fitness, 4)},
        })
        print(f" Round {rnd+1}: code={code_winner.name} fit={code_winner.fitness:.3f} | "
              f"prompt={best_prompt.name} fit={best_prompt.fitness:.3f}")

    return best_code, best_prompt, history


if __name__ == "__main__":
    code, prompt, hist = evolve(rounds=3)
    print("\n✅ CO-EVOLUTION FERTIG")
    print(f"Bester Code: {code.name} fit={code.fitness:.3f}")
    print(f"Bester Prompt: {prompt.name} fit={prompt.fitness:.3f}")