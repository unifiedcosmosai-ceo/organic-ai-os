"""
LAYER 12: REPORTER - Taeglicher Zustandsbericht
Erzeugt aus Memory, Hall of Fame und Symbiom-Schwarm:
  - reports/report.json  (maschinenlesbar)
  - reports/report.html  (humangelesbar, self-contained)
Usage: python -m 12_phenotype.reporter  (oder via app.py status --report)
"""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def collect_day_data() -> dict:
    """Sammelt alle Datenquellen zu einem Tagesreport."""
    memory_path = ROOT / "memory" / "organism_memory.json"
    hof_path = ROOT / "memory" / "hall_of_fame.json"
    symbiom_path = ROOT / "memory" / "symbiom_hall_of_fame.json"

    data = {}

    if memory_path.exists():
        mem = json.loads(memory_path.read_text())
        data.update({
            "evolution_count": mem.get("evolution_count", 0),
            "files_seen": len(mem.get("seen_files", {})),
            "failures": len(mem.get("failures", [])),
        })

    if hof_path.exists():
        hof = json.loads(hof_path.read_text())
        data["hall_of_fame"] = [
            {"name": h["name"], "fitness": round(h.get("fitness", 0), 3),
             "generation": h.get("generation", 0)}
            for h in hof
        ]
    else:
        data["hall_of_fame"] = []

    if symbiom_path.exists():
        sym = json.loads(symbiom_path.read_text())
        data["symbiom_hall_of_fame"] = [
            {"name": s["name"], "speciality": s.get("speciality", "?"),
             "fitness": round(s.get("fitness", 0), 3)}
            for s in sym
        ]
    else:
        data["symbiom_hall_of_fame"] = []

    data["generated_at"] = datetime.now().isoformat()
    return data


def _render_html(data: dict) -> str:
    best = data.get("hall_of_fame", [{}])[0] if data.get("hall_of_fame") else {}
    rows_hof = "".join(
        f"<tr><td>{h['name']}</td><td>{h['fitness']}</td><td>Gen {h['generation']}</td></tr>"
        for h in data.get("hall_of_fame", [])
    )
    rows_sym = "".join(
        f"<tr><td>{h['name']}</td><td>{h['speciality']}</td><td>{h['fitness']}</td></tr>"
        for h in data.get("symbiom_hall_of_fame", [])
    )
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Organic AI OS - Tagesreport</title>
<style>
  body {{ font-family: sans-serif; margin: 2em; background: #f7f9fb; }}
  h1 {{ color: #2d6a4f; }} h2 {{ color: #40916c; }}
  table {{ border-collapse: collapse; margin: 1em 0; }}
  td, th {{ border: 1px solid #ccc; padding: .4em .8em; }}
  th {{ background: #e9ecef; }}
  .kpi {{ display: inline-block; background: #fff; border: 1px solid #ddd;
          border-radius: 8px; padding: .8em 1.4em; margin: .4em; }}
  .kpi b {{ display: block; font-size: 1.6em; color: #2d6a4f; }}
</style>
</head>
<body>
<h1>🧬 Organic AI OS - Tagesreport</h1>
<p>Erstellt: {data['generated_at']}</p>

<div>
  <div class="kpi">Evolutionen <b>{data.get('evolution_count', 0)}</b></div>
  <div class="kpi">Dateien gesehen <b>{data.get('files_seen', 0)}</b></div>
  <div class="kpi">Fehler <b>{data.get('failures', 0)}</b></div>
  <div class="kpi">Champion <b>{best.get('name', '-')}</b></div>
</div>

<h2>🏆 Hall of Fame</h2>
<table><tr><th>Name</th><th>Fitness</th><th>Generation</th></tr>{rows_hof or '<tr><td colspan=3>-</td></tr>'}</table>

<h2>🐝 Symbiom Hall of Fame</h2>
<table><tr><th>Name</th><th>Spezialitaet</th><th>Fitness</th></tr>{rows_sym or '<tr><td colspan=3>-</td></tr>'}</table>

<p><small>Organic AI OS v4 Phase D - generiert vom Reporter (Layer 12)</small></p>
</body>
</html>"""


def generate_report(report_dir: Path = None):
    report_dir = report_dir or (ROOT / "reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    data = collect_day_data()

    json_path = report_dir / "report.json"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    html_path = report_dir / "report.html"
    html_path.write_text(_render_html(data), encoding="utf-8")
    return json_path, html_path


if __name__ == "__main__":
    jp, hp = generate_report()
    print(f"Report JSON: {jp}")
    print(f"Report HTML: {hp}")