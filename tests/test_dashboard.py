"""Tests fuer das REST-Dashboard (v6, Layer 13)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "13_ui"))

import dashboard


def test_build_dashboard_data_keys():
    data = dashboard.build_dashboard_data(memory_dir=str(ROOT / "memory"))
    for k in ("evolution_count", "files_seen", "failures", "best_strands",
              "skills", "symbiom_hof", "hall_of_fame", "fitness_history", "guard"):
        assert k in data
    assert isinstance(data["fitness_history"], list)
    assert isinstance(data["guard"], dict)


def test_render_html_structure():
    data = dashboard.build_dashboard_data(memory_dir=str(ROOT / "memory"))
    html = dashboard.render_dashboard_html(data)
    assert "<html" in html
    assert 'id="tiles"' in html
    assert 'id="bars"' in html
    assert 'id="guard"' in html


def test_render_html_self_contained():
    data = dashboard.build_dashboard_data(memory_dir=str(ROOT / "memory"))
    html = dashboard.render_dashboard_html(data)
    assert "http://" not in html
    assert "https://" not in html


def test_build_files(tmp_path):
    files = dashboard.build_files(memory_dir=str(ROOT / "memory"),
                                  out_dir=str(tmp_path / "dash"))
    assert set(files) == {"dashboard.html", "dashboard.json"}
    assert (tmp_path / "dash" / "dashboard.html").exists()
    assert (tmp_path / "dash" / "dashboard.json").exists()


def test_dashboard_api_endpoints():
    from fastapi.testclient import TestClient
    from api_server import app

    client = TestClient(app)
    assert client.get("/dashboard").status_code == 200
    summary = client.get("/dashboard/summary")
    assert summary.status_code == 200
    assert "evolution_count" in summary.json()
    assert "fitness_history" in summary.json()
    guard = client.get("/dashboard/guard")
    assert guard.status_code == 200
    assert "guard" in guard.json()


def test_validate_api_endpoint_ok():
    from fastapi.testclient import TestClient
    from api_server import app

    client = TestClient(app)
    r = client.post("/validate", json={"content": ">a\nATGC\n", "schema": "auto"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["total"] == 1


def test_validate_api_endpoint_violation():
    from fastapi.testclient import TestClient
    from api_server import app

    client = TestClient(app)
    r = client.post("/validate", json={"content": ">a\nATXZ?\n"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert any(v["rule"] == "alphabet" for v in body["violations"])


def test_validate_api_endpoint_unknown_schema():
    from fastapi.testclient import TestClient
    from api_server import app

    client = TestClient(app)
    r = client.post("/validate", json={"content": ">a\nATGC\n", "schema": "nope"})
    assert r.status_code == 422
