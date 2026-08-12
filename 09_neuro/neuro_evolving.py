import random, re, ast
from dataclasses import dataclass, field
from typing import List

try:
    from provenance import get_provenance as _get_prov
    from cortex_persist import snapshot_population as _snapshot_pop
    _NEURO_OBS = True
except Exception:
    _NEURO_OBS = False

@dataclass
class PromptStrand:
    name: str
    prompt_template: str
    fitness: float = 0.0
    generation: int = 0
    lineage: List[str] = field(default_factory=list)
    tokens: int = 0

class NeuroMutator:
    def mutate(self, strand, strategy=None):
        import random, re
        strategies=['point','insert','delete','role','cot','fewshot']
        strategy=strategy or random.choice(strategies)
        template=strand.prompt_template
        if strategy=='point':
            template=template.replace('mache','generiere präzise').replace('erstelle','konstruiere robusten')
        elif strategy=='insert':
            template+='\nRegel: Nur valider Python Code, max 15 Zeilen, nutze strip(), splitlines(), re.compile.'
        elif strategy=='delete':
            template=re.sub(r'\b(bitte|einfach|nur)\b','',template,flags=re.IGNORECASE)
            template=re.sub(r'\s+',' ',template).strip()
        elif strategy=='role':
            role=random.choice(['Du bist Senior Bioinformatics Engineer.','Du bist Python Core Developer.','Du bist Code-Chirurg.'])
            template=role+'\n\n'+template if 'Du bist' not in template else re.sub(r'Du bist.*?\.',role,template,count=1)
        elif strategy=='cot':
            if 'Schritt' not in template:
                template+='\nDenke Schritt für Schritt: 1) Parse 2) Handle Edges 3) Optimize.'
        elif strategy=='fewshot':
            if 'Beispiel' not in template:
                template+='\nBeispiel: Input ">a\\nATGC" -> Output {"a":"ATGC"}'
        child=PromptStrand(name=f"{strand.name}_g{strand.generation+1}", prompt_template=template.strip(), generation=strand.generation+1, lineage=strand.lineage+[strand.name])
        child.tokens=len(child.prompt_template.split())
        if _NEURO_OBS:
            _get_prov().record(parent=strand.name, child=child.name, strategy=strategy,
                               generation=strand.generation,
                               fitness_before=strand.fitness,
                               prompt_snippet=template[:80])
        return child

class NeuroCortex:
    def __init__(self):
        self.strands={}
        self.mutator=NeuroMutator()
        self.history=[]
    def seed(self):
        seeds=[
            PromptStrand(name='adam_simple', prompt_template='Schreibe Python Funktion parse_fasta.', generation=0),
            PromptStrand(name='adam_bio', prompt_template='Du bist Bioinformatics Experte. Schreibe parse_fasta(text) robust gegen Leerzeilen.', generation=0),
            PromptStrand(name='adam_engineer', prompt_template='Du bist Senior Python Engineer. Erstelle def parse_fasta(text: str) -> dict. Requirements: strip(), upper(), splitlines(), handle empty, max 15 lines. Return {header: seq}.', generation=0),
        ]
        for s in seeds:
            s.tokens=len(s.prompt_template.split())
            self.strands[s.name]=s
    def execute_prompt(self, strand):
        quality=len(strand.prompt_template)/100
        if 'Senior' in strand.prompt_template: quality+=0.3
        if 'strip()' in strand.prompt_template: quality+=0.3
        if 'Beispiel' in strand.prompt_template: quality+=0.2
        if 'Schritt' in strand.prompt_template: quality+=0.2
        if quality>0.8:
            return 'def parse_fasta(text):\n    import re\n    records={}\n    curr=None\n    buf=[]\n    ws=re.compile(r"\\s+")\n    for line in text.splitlines():\n        s=line.strip()\n        if not s: continue\n        if s.startswith(">"):\n            if curr: records[curr]="".join(buf)\n            curr=s[1:].split()[0]\n            buf=[]\n        else:\n            buf.append(ws.sub("",s).upper())\n    if curr: records[curr]="".join(buf)\n    return records\n'
        elif quality>0.5:
            return 'def parse_fasta(text):\n    records={}\n    header=None\n    parts=[]\n    for line in text.splitlines():\n        l=line.strip()\n        if not l: continue\n        if l.startswith(">"):\n            if header: records[header]="".join(parts)\n            header=l[1:].split()[0]\n            parts=[]\n        else:\n            parts.append(l.upper())\n    if header: records[header]="".join(parts)\n    return records\n'
        else:
            return 'def parse_fasta(text):\n    records={}\n    h=""\n    for line in text.split("\\n"):\n        if line.startswith(">"):\n            h=line[1:]\n            records[h]=""\n        else:\n            records[h]+=line\n    return records\n'
    def evaluate(self, strand, tests):
        code=self.execute_prompt(strand)
        try:
            ast.parse(code)
        except Exception:
            strand.fitness=0.0
            return 0.0
        score=0
        total=0
        for fn,w in tests:
            try:
                ns={}
                exec(code, {}, ns)
                score+=(1.0 if fn(ns) else 0.0)*w
                total+=w
            except Exception:
                total+=w
        eff=score/(strand.tokens+1)*5 if strand.tokens else 0
        strand.fitness=(score/total if total else 0)+min(0.1,eff)
        return strand.fitness
    def evolve(self, tests, generations=12, pop_size=8):
        print(f'\nNEURO EVOLUTION {generations} Gen')
        self.seed()
        pop=list(self.strands.values())
        while len(pop)<pop_size:
            parent=random.choice(pop)
            child=self.mutator.mutate(parent)
            self.strands[child.name]=child
            pop.append(child)
        for gen in range(generations):
            for p in pop:
                self.evaluate(p, tests)
            pop.sort(key=lambda x: x.fitness, reverse=True)
            best=pop[0]
            print(f' Gen {gen}: best={best.name} fit={best.fitness:.3f} tok={best.tokens}')
            print(f'   Prompt: {best.prompt_template[:90]}...')
            self.history.append([(p.name,p.fitness,p.generation) for p in pop])
            if _NEURO_OBS:
                _snapshot_pop(pop, gen)
            if best.fitness>=0.95:
                break
            next_gen=[best]
            while len(next_gen)<pop_size:
                parent=random.choice(pop[:3])
                child=self.mutator.mutate(parent)
                self.strands[child.name]=child
                next_gen.append(child)
            pop=next_gen
        winner=max(pop, key=lambda x: x.fitness)
        print(f'\nWINNER PROMPT Gen{winner.generation} Fit={winner.fitness:.3f}')
        print('='*70)
        print(winner.prompt_template)
        print('='*70)
        print('\nGENERIERTER CODE:')
        print(self.execute_prompt(winner))
        return winner

def test_basic(ns):
    if 'parse_fasta' not in ns: return False
    try:
        r=ns['parse_fasta']('>a\nATGC\n>b\nGG')
        return len(r)==2
    except Exception:
        return False

def test_robust(ns):
    if 'parse_fasta' not in ns: return False
    try:
        r=ns['parse_fasta']('>a messy\n  atgc  \n\n>b\nGG')
        return len(r)==2 and all(' ' not in v for v in r.values())
    except Exception:
        return False

if __name__=='__main__':
    c=NeuroCortex()
    w=c.evolve([(test_basic,0.6),(test_robust,0.4)], generations=12, pop_size=8)