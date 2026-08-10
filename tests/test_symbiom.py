"""Tests für den Symbiom-Schwarm und Co-Evolution (Phase D)."""

from symbiom_swarm import SymbiomSwarm, _test_parse, _test_messy


SEED = """
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


def test_swarm_seed_population():
    swarm = SymbiomSwarm(population_per_species=3)
    swarm.seed(SEED)
    assert len(swarm.symbionts) == 4 * 3
    specs = {s.speciality for s in swarm.symbionts}
    assert specs == {"robust", "fast", "compact", "strict"}


def test_swarm_evaluate():
    swarm = SymbiomSwarm(population_per_species=2)
    swarm.seed(SEED)
    for s in swarm.symbionts:
        swarm.evaluate(s, [(_test_parse, 0.6), (_test_messy, 0.4)])
    assert all(s.fitness > 0 for s in swarm.symbionts)


def test_swarm_evolve_returns_winner():
    swarm = SymbiomSwarm(population_per_species=2)
    swarm.seed(SEED)
    winner = swarm.evolve([(_test_parse, 0.6), (_test_messy, 0.4)], generations=3)
    assert winner.fitness > 0
    assert winner.name


def test_swarm_hall_of_fame(tmp_path):
    swarm = SymbiomSwarm(population_per_species=2)
    swarm.seed(SEED)
    swarm.evolve([(_test_parse, 0.6), (_test_messy, 0.4)], generations=2)
    out = swarm.export_hall_of_fame(tmp_path / "symbiom.json")
    import json

    data = json.loads(out.read_text())
    assert isinstance(data, list)
    assert data


def test_coevolution_rounds():
    from co_evolution import evolve

    code, prompt, hist = evolve(rounds=2, swarm_generations=2, pop_per_species=2)
    assert code.fitness > 0
    assert prompt.fitness > 0
    assert len(hist) == 2