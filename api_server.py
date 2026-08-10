"""
Organic AI OS - API v2 (Layer 12 Phenotyp)

Endpoints:
  GET  /                    Healthcheck
  GET  /health              JDoeformatierter Healthcheck (uptime, memory, watcher)
  POST /parse               Sequenzdaten parsen (FASTA/FASTQ Auto-Detection)
  GET  /stats               Memory zahlen + Hall of Fame
  GET  /lineage             Best-Strand-Ahnengeschichte
  GET  /fitness             Fitness-Historie (nach Generation)
  GET  /memory              Roh-Memory JSON
  GET  /evolution_history   Evolution-Generationen
  GET  /inbox               Dateien im Watch-Ordner
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
import time
from datetime import datetime

import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import bio_formats

MEMORY_DIR = ROOT / "memory"
INBOX_DIR = ROOT / "fasta_inbox"

app = FastAPI(title="Organic Organism API", version="2.0.0")

_boot_time = time.time()


def _read_memory() -> dict:
    mem_file = MEMORY_DIR / "organism_memory.json"
    if mem_file.exists():
        return json.loads(mem_file.read_text())
    return {}


@app.get("/")
def root():
    return {"status": "alive", "organism": "organic_ai", "time": datetime.now().isoformat()}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_s": round(time.time() - _boot_time, 1),
        "memory_exists": (MEMORY_DIR / "organism_memory.json").exists(),
        "inbox_files": len(list(INBOX_DIR.glob("*.fa*"))),
        "time": datetime.now().isoformat(),
    }


class ParseRequest(BaseModel):
    content: str
    filename: str = "api_input"


@app.post("/parse")
def parse(req: ParseRequest):
    """Parst Sequenzdaten: body = rohe FASTA/FASTQ Text."""
    try:
        fmt, records = bio_formats.parse_file(req.content)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"parse failed: {e}")
    return {"format": fmt, "records": len(records), "filename": req.filename, "parsed": records}


@app.get("/stats")
def stats():
    data = _read_memory()
    hof_file = MEMORY_DIR / "hall_of_fame.json"
    hof = json.loads(hof_file.read_text()) if hof_file.exists() else []
    return {
        "evolution_count": data.get("evolution_count", 0),
        "files_seen": len(data.get("seen_files", {})),
        "failures": len(data.get("failures", [])),
        "best_strands": len(data.get("best_strands", {})),
        "hall_of_fame": [{"name": h["name"], "fitness": round(h.get("fitness", 0), 3), "generation": h.get("generation", 0)} for h in hof],
    }


@app.get("/lineage")
def lineage():
    data = _read_memory()
    return {"lineage": data.get("best_strands", {})}


@app.get("/fitness")
def fitness():
    hof_file = MEMORY_DIR / "hall_of_fame.json"
    if not hof_file.exists():
        return {"fitness_history": []}
    hof = json.loads(hof_file.read_text())
    return {
        "fitness_history": [
            {"name": h["name"], "fitness": round(h.get("fitness", 0), 4), "generation": h.get("generation", 0)}
            for h in hof
        ]
    }


@app.get("/memory")
def get_memory():
    return _read_memory() or {"error": "no memory yet"}


@app.get("/evolution_history")
def history():
    gens = sorted(MEMORY_DIR.glob("parser_gen_*.py"))
    return {"evolution_count": len(gens), "generations": [f.name for f in gens]}


@app.get("/inbox")
def inbox():
    files = sorted(INBOX_DIR.glob("*.fa*"))
    return {"count": len(files), "files": [f.name for f in files]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)