"""Tests fuer Layer 13 (UI + Brainstorm) — MCTS 3x3 Forest, Mindmap, Responsive UI."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "13_ui"))

import mcts_idea_forest as mif
import mindmap as mm
from idea_seeds import seed_pool


def test_seed_pool_filter():
    core = seed_pool(axis="core")
    atom = seed_pool(scale="atomic")
    assert all(g.axis == "core" for g in core)
    assert all(g.scale == "atomic" for g in atom)
    assert len(seed_pool()) > 20


def test_idea_fitness_bounds():
    g = seed_pool()[0]
    for cat in mif.CATEGORIES:
        f = mif.idea_fitness(g, cat)
        assert 0.0 <= f <= 1.0


def test_forest_produces_400():
    ranked = mif.run_forest(seed=7, iterations_per_tree=50)
    assert set(ranked) == set(mif.CATEGORIES)
    for cat, items in ranked.items():
        assert len(items) >= 100


def test_forest_deterministic():
    r1 = mif.run_forest(seed=11, iterations_per_tree=30)
    r2 = mif.run_forest(seed=11, iterations_per_tree=30)
    for cat in r1:
        assert [i.title for i in r1[cat]] == [i.title for i in r2[cat]]


def test_forest_differs_across_categories():
    r = mif.run_forest(seed=5, iterations_per_tree=60)
    ups = {i for i in [x.title for x in r["upgrades"][:30]]}
    exts = {i for i in [x.title for x in r["extensions"][:30]]}
    assert ups != exts


def test_categories_diverge_by_scoring():
    r = mif.run_forest(seed=5, iterations_per_tree=60)
    for cat in ("upgrades", "optimisations", "extensions", "automatisation"):
        scores = [i.score for i in r[cat][:20]]
        assert all(a >= b for a, b in zip(scores, scores[1:])), "muss absteigend sortiert sein"


def test_build_forest_output_files(tmp_path):
    out = mif.build_forest_output(seed=3, iterations_per_tree=20, out_dir=str(tmp_path / "bf"))
    assert (out / "top100.json").exists()
    assert (out / "mindmap.md").exists()
    data = json.loads((out / "top100.json").read_text())
    assert sum(data["counts"].values()) == 400


def test_mindmap_tree_shape(tmp_path):
    out = mif.build_forest_output(seed=3, iterations_per_tree=20, out_dir=str(tmp_path / "bf"))
    files = mm.build_files(str(out), str(out))
    assert set(files) == {"mindmap.mmd", "mindmap.html", "mindmap.md", "mindmap_tree.json"}
    tree = json.loads((out / "mindmap_tree.json").read_text())
    assert tree["name"] == "Organic AI OS"
    assert len(tree["children"]) == 4
    for cat in tree["children"]:
        assert cat["children"], "jede Kategorie braucht Achsen-Zweige"


def test_mermaid_syntax():
    tree = {"name": "root", "children": [{"name": "c1", "children": [
        {"name": "axis/skale", "children": [{"name": "Idea (0.9)"}]}]}]}
    mmd = mm.to_mermaid(tree)
    assert mmd.startswith("mindmap")
    assert "root" in mmd and "Idea" in mmd


def test_ui_files_exist():
    ui = ROOT / "13_ui" / "static" / "index.html"
    assert ui.exists()
    html = ui.read_text()
    assert "horizontal" in html and "vertical" in html
    assert "clamp(" in html           # fluid auto-scale
    assert "100dvh" in html           # dynamische Viewport-Hoehe
    assert "orientation" in html      # Auto-Detect horizontal/vertikal


def test_api_ui_endpoints():
    sys.path.insert(0, str(ROOT))
    from fastapi.testclient import TestClient
    from api_server import app

    client = TestClient(app)
    assert client.get("/ui").status_code == 200
    top = client.get("/brainstorm/top100.json")
    assert top.status_code == 200
    assert all(len(v) >= 100 for v in top.json()["categories"].values())
    assert client.get("/brainstorm/mindmap_tree.json").status_code == 200
    assert client.get("/brainstorm/mindmap").status_code == 200