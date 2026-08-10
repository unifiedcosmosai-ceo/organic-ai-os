"""
bio_formats.py - Multi-Format Bioinformatik Layer (03 Proteom).

Unterstuetzt selbst-evolvierende Parser fuer:
  - FASTA  (Sequenzen mit '>' Header, mehrere Records)
  - FASTQ   (Sequenzen mit '@' Header, Qualitaetszeile '+', Phred-Strings)

Format-Autodetektion anhand der ersten Non-Empty-Zeile.
Die Parser-Funktionen sind als Strings gehalten, damit die
Evolution ihre Mutationen direkt darauf anwenden kann.
"""

import re

WS = re.compile(r"\s+")

SEED_FASTA = """
import re
def parse_fasta(text):
    records={}
    curr=None
    buf=[]
    ws=re.compile(r"\\s+")
    for line in text.splitlines():
        s=line.strip()
        if not s: continue
        if s.startswith(">"):
            if curr: records[curr]="".join(buf)
            curr=s[1:].split()[0]
            buf=[]
        else:
            buf.append(ws.sub("", s).upper())
    if curr: records[curr]="".join(buf)
    return records
"""

SEED_FASTQ = """
def parse_fastq(text):
    records={}
    header=None
    lines=text.splitlines()
    i=0
    while i < len(lines):
        s=lines[i].strip()
        if not s:
            i+=1
            continue
        if s.startswith("@"):
            if header: records[header]={"seq":"".join(seq), "qual":"".join(qual)}
            header=s[1:].split()[0]
            seq=[]
            qual=[]
            i+=1
            # Sequenzzeile(n) bis "+"
            while i < len(lines) and not lines[i].startswith("+"):
                if lines[i].strip():
                    seq.append(lines[i].strip().upper())
                i+=1
            # "+" plus Qualitaetszeile ueberspringen
            if i < len(lines):
                i+=1
                if i < len(lines):
                    qual.append(lines[i].strip())
                    i+=1
        else:
            i+=1
    if header: records[header]={"seq":"".join(seq), "qual":"".join(qual)}
    return records
"""

FORMATS = {
    "fasta": {"marker": ">", "seed": SEED_FASTA, "func": "parse_fasta"},
    "fastq": {"marker": "@", "seed": SEED_FASTQ, "func": "parse_fastq"},
}


def detect_format(text: str) -> str:
    """Erkennt FASTA vs FASTQ anhand des ersten Non-Empty Zeichens."""
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith(">"):
            return "fasta"
        if s.startswith("@"):
            return "fastq"
        return "fasta"  # Default: FASTA
    return "fasta"


def seed_code(fmt: str) -> str:
    return FORMATS[fmt]["seed"]


def func_name(fmt: str) -> str:
    return FORMATS[fmt]["func"]


def parse_file(content: str) -> dict:
    """Parst eine Datei anhand der Autodetektion mit dem Seed-Parser (nicht evolviert)."""
    fmt = detect_format(content)
    code = seed_code(fmt)
    ns = {}
    exec(code, ns, ns)
    fn = ns[func_name(fmt)]
    return fmt, fn(content)