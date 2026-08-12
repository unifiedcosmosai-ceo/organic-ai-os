"""
LAYER 13 UI / BRAINSTORM: MINDMAP GENERATOR (v6)
Baut aus den 400 Ideen (reports/brainstorm_v6/top100.json):
  - mermaid.js Mindmap (mindmap.mmd)
  - self-contained interaktives HTML-Mindmap (mindmap.html)

Aufbau: Wurzel "Organic AI OS" -> 4 Kategorien -> 3x3 Achsen/Skalen ->
Speakerfolge der TOP-100-Ideen je Kategorie.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

AXES = {"core": "Kern (Evolution/Memory)", "data": "Daten (Formate/IO)",
        "ops": "Ops (Runtime/API)"}
SCALES = {"atomic": "Atomar", "component": "Komponente", "system": "System"}
CAT_LABELS = {"upgrades": "Upgrades", "optimisations": "Optimisations",
              "extensions": "Extensions", "automatisation": "Automatisation"}


def _load(in_dir: str = "reports/brainstorm_v6"):
    p = Path(in_dir) / "top100.json"
    return json.loads(p.read_text())


def build_tree(data: dict) -> dict:
    """Baut einen verschachtelten JSON-Baum fuer das HTML-Mindmap."""
    root = {"name": "Organic AI OS", "children": []}
    for cat, label in CAT_LABELS.items():
        cat_node = {"name": label, "children": []}
        by_axis = defaultdict(list)
        for idea in data["categories"][cat]:
            by_axis[(idea["axis"], idea["scale"])].append(idea)
        for (axis, scale), ideas in sorted(by_axis.items()):
            ax_node = {"name": f"{AXES[axis]} / {SCALES[scale]}", "children": []}
            for idea in ideas[:12]:
                ax_node["children"].append({
                    "name": idea["title"],
                    "value": idea["score"],
                    "desc": idea["body"],
                    "impact": idea["impact"],
                    "feas": idea["feasibility"],
                })
            cat_node["children"].append(ax_node)
        root["children"].append(cat_node)
    return root


# --------------------------------------------------------------------------
# Mermaid
# --------------------------------------------------------------------------
def to_mermaid(tree: dict) -> str:
    lines = ["mindmap", "  root((Organic AI OS))"]
    for cat in tree["children"]:
        lines.append(f"    {cat['name']}")
        for ax in cat["children"]:
            lines.append(f"      {ax['name']}")
            for idea in ax["children"]:
                score = f"{idea.get('value', 0):.2f}"
                name = idea["name"].replace("(", "[").replace(")", "]")
                lines.append(f"        {name} ({score})")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Self-contained HTML Mindmap (inline SVG, pan/zoom, no CDN)
# --------------------------------------------------------------------------
_HTML_TPL = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Organic AI OS — MCTS 3x3 Mindmap (v6)</title>
<style>
:root{--bg:#0d1117;--fg:#e6edf3;--acc:#58a6ff;--line:#30363d;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
 font-family:ui-monospace,'Cascadia Code',Menlo,monospace;overflow:hidden}
#wrap{width:100vw;height:100vh;position:relative}
#svg{width:100%;height:100%;display:block}
.legend{position:fixed;top:12px;left:12px;z-index:5;font-size:12px;
 background:rgba(13,17,23,.85);border:1px solid var(--line);border-radius:8px;
 padding:8px 12px}
.legend b{color:var(--acc)}
.node text{fill:var(--fg);font-size:13px}
.node ellipse{stroke:var(--acc);fill:#1f2937}
.node.idea ellipse{stroke:#3fb950;fill:#16261c}
.edge{stroke:var(--line);stroke-width:1.2}
.node{cursor:pointer}
.tip{position:fixed;pointer-events:none;z-index:6;max-width:320px;font-size:12px;
 background:#161b22;border:1px solid var(--line);border-radius:8px;padding:10px 12px;
 display:none;line-height:1.5}
</style>
</head>
<body>
<div id="wrap"><svg id="svg"></svg></div>
<div class="legend"><b>Organic AI OS</b> — MCTS 3x3 · Pan/Zoom · Klick zum Fokussieren</div>
<div class="tip" id="tip"></div>
<script>
const TREE = __TREE__;
const SVGW = 2200, SVGH = 2200;
const LAYER=[{color:'#58a6ff'},{color:'#3fb950'},{color:'#d29922'},{color:'#bc8cff'}];
const svg=document.getElementById('svg');
const NS='http://www.w3.org/2000/svg';
let vx=0, vy=0, vs=1;

function makeEl(tag,attrs){const e=document.createElementNS(NS,tag);
 for(const k in attrs)e.setAttribute(k,attrs[k]);return e;}
function txt(s,x,y,size,cls){const t=makeEl('text',{x,y,class:cls,style:'font-size:'+size+'px'});
 t.textContent=s;return t;}

const coord=new Map();
function layout(node,x,y,d,c,idx){
  const id=node.name+'_'+idx; coord.set(id,{x,y,c,d,node});
  const kids=node.children||[];
  const span=Math.max(1,kids.length);
  for(let i=0;i<kids.length;i++){
    const nx=x+280*(d+1)*0.9, ny=y+(i-span/2)*60*Math.pow(1.15,d);
    layout(kids[i],nx,ny,d+1,c,i);
  }
}
layout(TREE,SVGW/2,SVGH/2,0);

const g=makeEl('g',{id:'main'}); svg.appendChild(g);

coord.forEach((v,id)=>{
  const depth=v.d;
  if(depth>0){
    const dy=v.y-vx, dx=v.x-vx;
    const col=LAYER[Math.min(depth-1,3)].color;
    const rx=44-depth*5, ry=16;
    const e=makeEl('ellipse',{cx:v.x,cy:v.y,rx,ry,fill:'#1f2937',stroke:col,'stroke-width':1.3});
    g.appendChild(e);
  }
});

coord.forEach((v,id)=>{
  const kids=Array.from(coord.values()).filter(o=>o.d===v.d+1);
  kids.forEach(k=>{
    const l=makeEl('line',{x1:v.x,y1:v.y,x2:k.x,y2:k.y,class:'edge'}); g.appendChild(l);
  });
});

coord.forEach((v,id)=>{
  const isIdea=!(v.node.children&&v.node.children.length);
  if(isIdea){
    let p=id;
    const x=52-(v.d)*1, y=15;
    const t=txt(v.node.name,v.x-x,v.y+y,x+0,y*1,'12px','idea');
    t.setAttribute('text-anchor','middle');
    t.style.fontSize=(14-v.d*0.5)+'px';
    g.appendChild(t);
  }
});

coord.forEach((v,id)=>{
  const d=v.d;
  if(d===0){g.appendChild(txt(TREE.name,SVGW/2,SVGH/2+6,20,'20px'));}
  else{
    const depth=d-1;
    const label=depth===0?'':null;
    if(!v.node.children||v.node.children.length<=0){} // Idee: Text bereits
    else{
      if(d===1){ g.appendChild(txt(v.node.name,v.x,v.y+6,16,'16px')); }
      else if(d===2){ g.appendChild(txt(v.node.name,v.x,v.y+6,12,'12px')); }
    }
  }
});

function apply(){ g.setAttribute('transform','translate('+vx+','+vy+') scale('+vs+')'); }
apply();

const tip=document.getElementById('tip');
coord.forEach((v,id)=>{
  const isIdea=!(v.node.children&&v.node.children.length);
  if(isIdea){
    // find text element: we re-add hover via rect
    const r=makeEl('rect',{x:v.x-70,y:v.y-14,width:140,height:28,fill:'transparent'});
    r.addEventListener('mouseenter',()=>{tip.style.display='block';
      tip.innerHTML='<b>'+v.node.name+'</b> · Score '+v.node.value+
      '<br>'+ (v.node.desc||'') +'<br>Impact '+v.node.impact+' · Machbar '+v.node.feas;});
    r.addEventListener('mousemove',e=>{tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY+14)+'px';});
    r.addEventListener('mouseleave',()=>{tip.style.display='none';});
    g.appendChild(r);
  }
});

let drag=null;
svg.addEventListener('mousedown',e=>{drag={x:e.clientX,y:e.clientY};
 svg.style.cursor='grabbing';e.preventDefault();});
window.addEventListener('mousemove',e=>{if(!drag)return;
 vx+= (e.clientX-drag.x); vy+=(e.clientY-drag.y); drag={x:e.clientX,y:e.clientY}; apply();});
window.addEventListener('mouseup',()=>{drag=null;svg.style.cursor='grab';});
svg.addEventListener('wheel',e=>{e.preventDefault();
 const f=e.deltaY<0?1.1:0.9; vs=Math.min(3,Math.max(0.2,vs*f)); apply();},{passive:false});
</script>
</body>
</html>"""


def build_files(in_dir: str = "reports/brainstorm_v6",
                out_dir: str = "reports/brainstorm_v6") -> list:
    data = _load(in_dir)
    tree = build_tree(data)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    (out / "mindmap.mmd").write_text(to_mermaid(tree))
    html = _HTML_TPL.replace("__TREE__", json.dumps(tree, ensure_ascii=False))
    (out / "mindmap.html").write_text(html)

    # JSON-Baum ebenfalls ablegen (fuer UI/API)
    (out / "mindmap_tree.json").write_text(
        json.dumps(tree, ensure_ascii=False, indent=2))
    return sorted(p.name for p in out.glob("mindmap*"))


if __name__ == "__main__":
    for f in build_files():
        print("generated:", f)