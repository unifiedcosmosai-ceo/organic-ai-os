"""Tests für die API v2 Endpoints (FastAPI TestClient)."""

from fastapi.testclient import TestClient

from api_server import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "alive"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "uptime_s" in r.json()


def test_parse_fasta():
    r = client.post("/parse", json={"content": ">s1\nATGC\n", "filename": "t.fasta"})
    assert r.status_code == 200
    body = r.json()
    assert body["format"] == "fasta"
    assert body["parsed"] == {"s1": "ATGC"}


def test_parse_fastq():
    r = client.post("/parse", json={"content": "@r1\nACGT\n+\nIIII\n"})
    assert r.status_code == 200
    body = r.json()
    assert body["format"] == "fastq"
    assert body["records"] == 1


def test_parse_invalid():
    r = client.post("/parse", json={"content": "keine sequenz\nnur text"})
    assert r.status_code in (200, 422)


def test_stats_shape():
    r = client.get("/stats")
    assert r.status_code == 200
    body = r.json()
    assert "evolution_count" in body
    assert "hall_of_fame" in body


def test_fitness_history():
    r = client.get("/fitness")
    assert r.status_code == 200
    assert "fitness_history" in r.json()


def test_memory():
    r = client.get("/memory")
    assert r.status_code == 200


def test_inbox():
    r = client.get("/inbox")
    assert r.status_code == 200
    assert "files" in r.json()