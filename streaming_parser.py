"""
LAYER 03 / DATA: STREAMING-PARSER (v6)
Zeilenweises Parsen grosser FASTA/FASTQ-Dateien - memory-sparsam:
es ist immer nur EIN Record im Speicher (Generator statt vollem Dict).

Beispiel:
    fmt, it = parse_stream("reads.fastq")
    for header, rec in it:
        print(header, rec["seq"][:10])
"""

from pathlib import Path
from typing import Dict, Iterator, Tuple, Union

Record = Union[str, Dict[str, str]]


def detect_format_handle(handle) -> str:
    """Peek: erste nicht-leere Zeile -> 'fasta' oder 'fastq' (default fasta)."""
    for line in handle:
        s = line.strip()
        if not s:
            continue
        if s.startswith("@"):
            return "fastq"
        return "fasta"
    return "fasta"


def iter_fasta(handle) -> Iterator[Tuple[str, str]]:
    """Streamender FASTA-Parser: liefert (header, seq) Record fuer Record."""
    header = None
    buf = []
    for line in handle:
        s = line.strip()
        if not s:
            continue
        if s.startswith(">"):
            if header:
                yield header, "".join(buf)
            header = s[1:].split()[0]
            buf = []
        else:
            buf.append(s.upper())
    if header:
        yield header, "".join(buf)


def iter_fastq(handle) -> Iterator[Tuple[str, Dict[str, str]]]:
    """Streamender FASTQ-Parser: liefert (header, {seq, qual})."""
    header = None
    seq = []
    state = "seek"
    for line in handle:
        s = line.strip()
        if not s:
            continue
        if state == "seek":
            if s.startswith("@"):
                header = s[1:].split()[0]
                seq = []
                state = "seq"
        elif state == "seq":
            if s.startswith("+"):
                state = "qual"
            else:
                seq.append(s.upper())
        elif state == "qual":
            yield header, {"seq": "".join(seq), "qual": s}
            header = None
            seq = []
            state = "seek"
    if header and state == "seq":
        yield header, {"seq": "".join(seq), "qual": ""}


def parse_stream(path: str, fmt: str = None) -> Tuple[str, Iterator]:
    """Oeffnet eine Sequenzdatei und liefert (format, Stream-Iterator)."""
    handle = Path(path).open(errors="ignore")
    if fmt is None:
        fmt = detect_format_handle(handle)
        handle.seek(0)
    if fmt == "fastq":
        return fmt, iter_fastq(handle)
    return fmt, iter_fasta(handle)


def count_records(path: str, fmt: str = None) -> int:
    """Streamt die gesamte Datei und zaehlt Records (kein Speicherbedarf)."""
    _, it = parse_stream(path, fmt=fmt)
    return sum(1 for _ in it)


def stream_head(path: str, n: int = 5, fmt: str = None) -> list:
    """Liefert die ersten n Records (bricht den Stream frueh ab)."""
    _, it = parse_stream(path, fmt=fmt)
    records = []
    for header, rec in it:
        if len(records) >= n:
            break
        records.append((header, rec))
    return records