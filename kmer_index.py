"""
LAYER 03 / DATA: KMER-INDEX (v6)
k-mer Zaehlung + Index ueber Sequenzen. Basis fuer:
  - Stabilitaets-Monitoring (verteilte Sequenzen = grosse Cytoschwankung)
  - Bloom-filter-artige Verwandtschaft (Jaccard) zwischen Records/Populationen

Beispiel:
    idx = index_fasta("genome.fa", k=6)
    print(idx.top_kmers(10))
"""

from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


def compute_kmers(seq: str, k: int) -> Counter:
    """Alle k-mere einer Sequenz als Counter (Kanone: uppercase)."""
    s = seq.upper()
    if k <= 0 or len(s) < k:
        return Counter()
    return Counter(s[i:i + k] for i in range(len(s) - k + 1))


def gc_content(seq: str) -> float:
    """GC-Gehalt einer Sequenz (0..1)."""
    s = seq.upper()
    if not s:
        return 0.0
    return round((s.count("G") + s.count("C")) / len(s), 4)


class KmerIndex:
    """Inkrementeller k-mer Index: global + je Record."""

    def __init__(self, k: int = 5):
        self.k = k
        self.per_record: Dict[str, Counter] = {}
        self._global: Counter = Counter()

    def add(self, record_id: str, seq: str):
        kc = compute_kmers(seq, self.k)
        self.per_record[record_id] = kc
        self._global.update(kc)
        return self

    def add_many(self, records: dict):
        for rid, seq in records.items():
            self.add(rid, seq)
        return self

    def frequency(self, kmer: str) -> int:
        return self._global.get(kmer.upper(), 0)

    def top_kmers(self, n: int = 10) -> List[Tuple[str, int]]:
        return self._global.most_common(n)

    def vocabulary(self) -> int:
        return len(self._global)

    def total(self) -> int:
        return sum(self._global.values())

    def jaccard(self, a: str, b: str) -> float:
        """Jaccard-Index zwischen zwei Sequenzen (Stabilitaets/Aehnlichkeitsmass)."""
        ka = set(compute_kmers(a, self.k))
        kb = set(compute_kmers(b, self.k))
        union = ka | kb
        if not union:
            return 0.0
        return round(len(ka & kb) / len(union), 4)


def index_fasta(path: str, k: int = 5) -> KmerIndex:
    """Streamt eine FASTA-Datei und baut den k-mer Index auf."""
    import streaming_parser as sp

    idx = KmerIndex(k)
    fmt, it = sp.parse_stream(Path(path))
    for header, rec in it:
        seq = rec if isinstance(rec, str) else rec.get("seq", "")
        idx.add(header, seq)
    return idx