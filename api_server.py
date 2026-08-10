
from fastapi import FastAPI
from pathlib import Path
import json
from datetime import datetime

app = FastAPI(title="Organic Organism API")

MEMORY_DIR = Path("memory")
INBOX_DIR = Path("fasta_inbox")

@app.get("/")
def root():
    return {"status": "alive", "organism": "organic_ai", "time": datetime.now().isoformat()}

@app.get("/memory")
def get_memory():
    mem_file = MEMORY_DIR / "organism_memory.json"
    if mem_file.exists():
        return json.loads(mem_file.read_text())
    return {"error": "no memory yet"}

@app.get("/best_parser")
def best_parser():
    p = MEMORY_DIR / "best_parser.py"
    if p.exists():
        return {"code": p.read_text(), "fitness": "unknown"}
    return {"error": "no parser yet"}

@app.get("/inbox")
def inbox():
    files = list(INBOX_DIR.glob("*.fa*"))
    return {"count": len(files), "files": [f.name for f in files]}

@app.get("/evolution_history")
def history():
    return {
        "evolution_count": len(list(MEMORY_DIR.glob("parser_gen_*.py"))),
        "generations": [f.name for f in sorted(MEMORY_DIR.glob("parser_gen_*.py"))]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
