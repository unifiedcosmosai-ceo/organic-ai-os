"""Tests fuer den k-mer Index (v6, Layer 03 data)."""
from collections import Counter
import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kmer_index import compute_kmers, gc_content, KmerIndex, index_fasta


def test_compute_kmers_length_and_overlap():
    ks = compute_kmers("AAAA", 3)
    assert ks == Counter({"AAA": 2})


def test_compute_kmers_counts_each_position():
    ks = compute_kmers("ATGC", 2)
    assert ks["AT"] == 1 and ks["TG"] == 1 and ks["GC"] == 1


def test_compute_kmers_uppercases():
    ks = compute_kmers("atgc", 2)
    assert ks["AT"] == 1 and ks["GC"] == 1


def test_compute_kmers_k_larger_than_seq_is_empty():
    assert compute_kmers("AT", 5) == Counter()


def test_compute_kmers_k_zero_or_negative():
    assert compute_kmers("ATGC", 0) == Counter()
    assert compute_kmers("ATGC", -1) == Counter()


def test_gc_content():
    assert gc_content("GGCCAA") == pytest.approx(0.667, abs=0.01)
    assert gc_content("") == 0.0


def test_index_add_and_frequency():
    idx = KmerIndex(k=3)
    idx.add("a", "AAAATTTT")
    assert idx.frequency("AAA") == 2
    assert idx.total() == 6


def test_index_top_kmers_sorted():
    idx = KmerIndex(k=2)
    idx.add_many({"a": "AAAATT", "b": "AATTGG"})
    top = idx.top_kmers(3)
    assert top[0][0] == "AA"
    assert all(top[i][1] >= top[i + 1][1] for i in range(len(top) - 1))


def test_index_vocabulary():
    idx = KmerIndex(k=2)
    idx.add("a", "AAA")
    assert idx.vocabulary() == 1  # nur ein unique k-mer (AA)


def test_jaccard_identical_and_disjoint():
    idx = KmerIndex(k=3)
    assert idx.jaccard("AAAA", "AAAA") == 1.0
    assert idx.jaccard("AAAA", "CCCC") == 0.0
    assert idx.jaccard("AA", "CC") == 0.0  # keine k-mere


def test_index_fasta_file(tmp_path):
    f = tmp_path / "g.fasta"
    f.write_text(">a\nAAAATTTT\n>b\nAATTGG\n")
    idx = index_fasta(str(f), k=2)
    assert len(idx.per_record) == 2
    assert idx.top_kmers(1)[0][1] > 0