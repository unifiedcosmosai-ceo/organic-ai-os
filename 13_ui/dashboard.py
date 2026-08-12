"""
LAYER 13 UI: REST-DASHBOARD (v6)
Self-contained Dashboard: KPI-Tiles + JSON-Summary aus allen
Organismus-Gedaechtnissen (Memory, Hall of Fame, Skills, Symbiom, Guard).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_json(path: Path, default=None):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return default
    return default


def _fitness_series(hof) -> list:
    return [
        {"name": h.get("name", "?"), "fitness": round(float(h.get("fitness", 0)), 4),
         "generation": h.get("generation", 0)}
        for h in hof if isinstance(h, dict)
    ]


def build_dashboard_data(memory_dir: str = "memory") -> dict:
    mem = Path(memory_dir)
    memory = _load_json(mem / "organism_memory.json", {}) or {}
    hof = _load_json(mem / "hall_of_fame.json", []) or []
    skills = _load_json(mem / "skill_library.json", {}) or {}
    guard = _load_json(mem / "fitness_guard.json", {}) or {}
    symbiom = _load_json(mem / "symbiom_hall_of_fame.json", []) or []

    series = _fitness_series(hof)
    return {
        "evolution_count": memory.get("evolution_count", 0),
        "files_seen": len(memory.get("seen_files", {})),
        "failures": len(memory.get("failures", [])),
        "best_strands": len(memory.get("best_strands", {})),
        "coevolution": memory.get("coevolution"),
        "prompt_hint": bool(memory.get("prompt_hint")),
        "skills": len(skills.get("skills", [])) if isinstance(skills, dict) else 0,
        "symbiom_hof": len(symbiom),
        "hall_of_fame": series,
        "fitness_history": series,
        "guard": guard,
    }


_HTML_TPL = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Organic AI OS — Dashboard (v6)</title>
<style>
:root{--bg:#0d1117;--fg:#e6edf3;--acc:#58a6ff;--ok:#3fb950;--warn:#d29922;--bad:#f85149;--line:#30363d;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
 font-family:ui-monospace,'Cascadia Code',Menlo,monospace}
.wrap{max-width:1080px;margin:0 auto;padding:24px}
h1{font-size:20px;margin:0 0 4px}h1 b{color:var(--acc)}
.sub{color:#8b949e;font-size:12px;margin-bottom:20px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:22px}
.tile{background:#161b22;border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.tile .k{color:#8b949e;font-size:11px;text-transform:uppercase;letter-spacing:.08em}
.tile .v{font-size:26px;font-weight:700;margin-top:4px}
.tile.warn .v{color:var(--warn)}.tile.bad .v{color:var(--bad)}.tile.ok .v{color:var(--ok)}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:720px){.cards{grid-template-columns:1fr}}
.card{background:#161b22;border:1px solid var(--line);border-radius:10px;padding:16px}
.card h2{font-size:13px;margin:0 0 12px;color:var(--acc);text-transform:uppercase;letter-spacing:.06em}
.bars{display:flex;align-items:flex-end;gap:4px;height:120px;padding-top:8px}
.bar{flex:1;background:var(--acc);border-radius:3px 3px 0 0;min-height:2px;position:relative}
.bar:hover{outline:1px solid var(--fg)}
.bar span{position:absolute;bottom:calc(100% + 4px);left:50%;transform:translateX(-50%);
 font-size:10px;color:#8b949e;white-space:nowrap;display:none}
.bar:hover span{display:block}
.guard{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px}
.pill{border:1px solid var(--line);border-radius:999px;padding:4px 12px;font-size:12px}
.pill.ok{color:var(--ok)}.pill.warn{color:var(--warn)}.pill.bad{color:var(--bad)}
ul.log{list-style:none;margin:0;padding:0;font-size:12px;color:#8b949e}
ul.log li{padding:3px 0;border-bottom:1px dashed var(--line)}
.reject{color:var(--bad)}.hold{color:var(--warn)}.promote{color:var(--ok)}
</style>
</head>
<body>
<div class="wrap">
  <h1>Organic AI OS <b>· Live Dashboard</b></h1>
  <div class="sub">KPI-Tiles + Fitness-Historie + Fruehwarnung — self-contained (kein CDN)</div>
  <div class="tiles" id="tiles"></div>
  <div class="cards">
    <div class="card"><h2>Fitness-Historie (Hall of Fame)</h2><div class="bars" id="bars"></div></div>
    <div class="card"><h2>Fruehwarnung (Fitness-Guard)</h2><div class="guard" id="guard"></div>
      <ul class="log" id="log"></ul></div>
  </div>
</div>
<script>
const D = __DATA__;
const TILES = [
  {k:"Evolutionen", v:D.evolution_count},
  {k:"Files gesehen", v:D.files_seen},
  {k:"Failures", v:D.failures, cls:D.failures>0?"warn":""},
  {k:"Best Strands", v:D.best_strands},
  {k:"Skills", v:D.skills},
  {k:"Symbiom HoF", v:D.symbiom_hof},
  {k:"Prompt-Hint", v:D.prompt_hint?"ja":"nein", cls:D.prompt_hint?"ok":""},
  {k:"Co-Evo Score", v:D.coevolution?D.coevolution.co_score:"-"},
];
const tiles=document.getElementById('tiles');
TILES.forEach(t=>{const d=document.createElement('div');d.className='tile '+(t.cls||'');
 d.innerHTML='<div class="k">'+t.k+'</div><div class="v">'+t.v+'</div>';tiles.appendChild(d);});
const hf=D.fitness_history||[];
const bars=document.getElementById('bars');
const max=Math.max(1,...hf.map(h=>h.fitness));
hf.forEach(h=>{const b=document.createElement('div');b.className='bar';
 b.style.height=Math.max(4,(h.fitness/max)*100)+'%';
 b.innerHTML='<span>'+h.name+' '+h.fitness+'</span>';bars.appendChild(b);});
if(!hf.length){bars.innerHTML='<div style="font-size:12px;color:#8b949e">noch keine Hall of Fame</div>';}
const g=D.guard||{};
const guard=document.getElementById('guard');
const gcls = g.alarms>0?'bad':(g.best>0?'ok':'');
guard.innerHTML='<span class="pill '+gcls+'">best '+g.best+'</span>'+
 '<span class="pill '+(g.alarms>0?'bad':'ok')+'">Alarme '+g.alarms+'</span>'+
 '<span class="pill">Checks '+(g.checks||0)+'</span>';
const log=document.getElementById('log');
(g.history||[]).slice(-8).reverse().forEach(e=>{
 const li=document.createElement('li');
 li.innerHTML='<span class="'+e.decision+'">'+e.decision+'</span> '+
   e.name+' · '+e.fitness+' (Base '+e.baseline+') · '+e.reason;
 log.appendChild(li);});
if(!(g.history||[]).length){log.innerHTML='<li>noch keine Guard-Checks</li>';}
</script>
</body>
</html>"""


def render_dashboard_html(data: dict) -> str:
    return _HTML_TPL.replace("__DATA__", json.dumps(data, ensure_ascii=False))


def build_files(memory_dir: str = "memory", out_dir: str = "reports/dashboard") -> list:
    data = build_dashboard_data(memory_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "dashboard.html").write_text(render_dashboard_html(data))
    (out / "dashboard.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return ["dashboard.html", "dashboard.json"]


if __name__ == "__main__":
    for f in build_files():
        print("generated:", f)
