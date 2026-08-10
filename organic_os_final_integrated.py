
"""
ORGANIC AI OS v3 - VOLLSTÄNDIG EVOLVIEREND
Layer 09 Neuro (Prompt Cortex) + Layer 11 Evolution + Layer 03 Proteom
Alles evolviert alles.

FLOW:
Prompt-DNA (Layer09) --LLM--> Code-DNA (Layer03) --Fitness--> Selektion
   ^                                                        |
   |<----------- Evolution (Layer11) mutiert beide ---------|
"""

import random, re, ast, json, time
from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path

# ---- PROMPT + CODE CO-EVOLUTION ----

@dataclass
class Organism:
    prompt: str
    code: str
    prompt_fit: float = 0.0
    code_fit: float = 0.0
    generation: int = 0
    name: str = ""

class IntegratedEvolution:
    def __init__(self):
        self.population: List[Organism] = []
    
    def seed(self):
        seeds = [
            ("Schreibe parse_fasta", "def parse_fasta(text):\n    records={}\n    h=''\n    for l in text.split('\\n'):\n        if l.startswith('>'): h=l[1:]; records[h]=''\n        else: records[h]+=l\n    return records"),
            ("Du bist Bioinformatics Experte. Schreibe parse_fasta robust mit strip(), splitlines()", "def parse_fasta(text):\n    records={}\n    curr=None\n    buf=[]\n    for line in text.splitlines():\n        s=line.strip()\n        if not s: continue\n        if s.startswith('>'):\n            if curr: records[curr]=''.join(buf)\n            curr=s[1:].split()[0]\n            buf=[]\n        else:\n            buf.append(s.upper())\n    if curr: records[curr]=''.join(buf)\n    return records"),
        ]
        for i,(p,c) in enumerate(seeds):
            self.population.append(Organism(prompt=p, code=c, generation=0, name=f"adam_{i}"))
    
    def evaluate(self, org: Organism) -> float:
        # Teste Code
        def test1(ns): 
            try: return len(ns['parse_fasta'](">a\nATGC\n>b\nGG"))==2
            except: return False
        def test2(ns):
            try: 
                r=ns['parse_fasta'](">a messy\n  atgc  \n\n>b\nGG")
                return all(" " not in v for v in r.values())
            except: return False
        try:
            ast.parse(org.code)
        except:
            org.code_fit=0
            return 0
        ns={}
        try:
            exec(org.code, {}, ns)
            s1=1.0 if test1(ns) else 0.0
            s2=1.0 if test2(ns) else 0.0
            org.code_fit = (s1*0.6 + s2*0.4)
        except:
            org.code_fit=0
        
        # Prompt Fitness = Code Fitness / Tokens (Effizienz)
        tokens=len(org.prompt.split())
        org.prompt_fit = org.code_fit + min(0.2, 1.0/tokens)
        return org.code_fit + org.prompt_fit
    
    def mutate_prompt(self, prompt: str) -> str:
        ops = [
            lambda p: p + "\nRegel: Nutze re.compile(r'\\s+') für Speed.",
            lambda p: p.replace("Schreibe", "Konstruiere robusten, produktionsreifen"),
            lambda p: "Du bist Senior Bioinformatics Engineer.\n" + p if "Du bist" not in p else p,
            lambda p: p + '\nBeispiel: ">a\\nATGC" -> {"a":"ATGC"}',
            lambda p: p + "\nDenke Schritt für Schritt.",
        ]
        return random.choice(ops)(prompt)
    
    def mutate_code_via_prompt(self, prompt: str) -> str:
        # Simuliere LLM das Prompt -> Code macht
        # Je besser Prompt, desto besser Code
        quality = 0
        if "Senior" in prompt: quality+=1
        if "strip()" in prompt: quality+=1
        if "re.compile" in prompt: quality+=1
        if "Beispiel" in prompt: quality+=1
        
        if quality>=3:
            return "def parse_fasta(text):\n    import re\n    records={}\n    curr=None\n    buf=[]\n    ws=re.compile(r'\\s+')\n    for line in text.splitlines():\n        s=line.strip()\n        if not s: continue\n        if s.startswith('>'):\n            if curr: records[curr]=''.join(buf)\n            curr=s[1:].split()[0]\n            buf=[]\n        else:\n            buf.append(ws.sub('',s).upper())\n    if curr: records[curr]=''.join(buf)\n    return records"
        elif quality>=1:
            return "def parse_fasta(text):\n    records={}\n    header=None\n    parts=[]\n    for line in text.splitlines():\n        l=line.strip()\n        if not l: continue\n        if l.startswith('>'):\n            if header: records[header]=''.join(parts)\n            header=l[1:].split()[0]\n            parts=[]\n        else:\n            parts.append(l.upper())\n    if header: records[header]=''.join(parts)\n    return records"
        else:
            return "def parse_fasta(text):\n    records={}\n    h=''\n    for line in text.split('\n'):\n        if line.startswith('>'): h=line[1:]; records[h]=''\n        else: records[h]+=line\n    return records"
    
    def evolve(self, generations=15, pop_size=10):
        self.seed()
        print(f"\n🧬 CO-EVOLUTION Neuro+Proteom {generations} Gen")
        # Initial pop
        while len(self.population)<pop_size:
            p=random.choice(self.population)
            new_prompt=self.mutate_prompt(p.prompt)
            new_code=self.mutate_code_via_prompt(new_prompt)
            self.population.append(Organism(prompt=new_prompt, code=new_code, generation=1, name=f"{p.name}_m1"))
        
        for gen in range(generations):
            for org in self.population:
                self.evaluate(org)
            self.population.sort(key=lambda x: x.code_fit, reverse=True)
            best=self.population[0]
            print(f" Gen {gen}: best={best.name} code_fit={best.code_fit:.3f} prompt_fit={best.prompt_fit:.3f} Gen={best.generation}")
            print(f"   Prompt: {best.prompt[:70]}...")
            if best.code_fit>=0.95:
                # versuche noch effizienteren Prompt
                if gen>5:
                    break
            next_gen=[best]
            while len(next_gen)<pop_size:
                parent=random.choice(self.population[:3])
                child_prompt=self.mutate_prompt(parent.prompt)
                child_code=self.mutate_code_via_prompt(child_prompt)
                next_gen.append(Organism(prompt=child_prompt, code=child_code, generation=parent.generation+1, name=f"{parent.name}_g{parent.generation+1}"))
            self.population=next_gen
        
        winner=max(self.population, key=lambda x: x.code_fit)
        print("\n🏆 CO-EVOLUTION WINNER")
        print(f"Prompt: {winner.prompt}")
        print(f"\nCode:\n{winner.code}")
        print(f"\nFitness Code={winner.code_fit} Prompt={winner.prompt_fit}")
        return winner

if __name__=="__main__":
    evo=IntegratedEvolution()
    winner=evo.evolve(generations=15, pop_size=10)
    
    # Speichere
    Path("winner_coevolved.py").write_text(winner.code)
    Path("winner_prompt.txt").write_text(winner.prompt)
    print("\n✅ Gespeichert: winner_coevolved.py + winner_prompt.txt")
