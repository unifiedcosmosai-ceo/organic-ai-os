"""Tests fuer den Streaming-Parser (v6, Layer 03 data)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from streaming_parser import (
    iter_fasta, iter_fastq, detect_format_handle, parse_stream,
    count_records, stream_head,
)

FASTA = ">a\nATGC\n>b\nGG\n"
FASTA_MULTI = ">a\naaaa\ncccc\n>b\nGG\n"


def _ff(txt):
    return txt.splitlines(True)


def test_iter_fasta_two_records():
    records = list(iter_fasta(_ff(FASTA)))
    assert [h for h, _ in records] == ["a", "b"]
    assert records[0][1] == "ATGC"
    assert records[1][1] == "GG"


def test_iter_fasta_multiline_concat():
    records = list(iter_fasta(_ff(FASTA_MULTI)))
    assert records[0][1] == "AAAACCCC"


def test_iter_fasta_uppercases_and_ignores_header_suffix():
    records = list(iter_fasta(_ff(">a desc\natgc\n>#\n\n")))
    assert records[0][0] == "a"
    assert records[0][1] == "ATGC"


def test_iter_fastq_basic():
    records = list(iter_fastq(_ff("@r1\nACGT\n+\nIIII\n@r2\nGG\n+\nHH\n")))
    assert len(records) == 2
    assert records[0][0] == "r1"
    assert records[0][1]["seq"] == "ACGT"
    assert records[0][1]["qual"] == "IIII"


def test_iter_fastq_seq_uppercased():
    records = list(iter_fastq(_ff("@r1\nacgt\n+\nIIII\n")))
    assert records[0][1]["seq"] == "ACGT"


def test_iter_fastq_without_qual_keeps_seq():
    records = list(iter_fastq(_ff("@r1\nACGT\n")))
    assert len(records) == 1
    assert records[0][1]["seq"] == "ACGT"
    assert records[0][1]["qual"] == ""


def test_detect_format_handle():
    assert detect_format_handle(_ff(FASTA)) == "fasta"
    assert detect_format_handle(_ff("@r1\nACGT\n+\nIIII\n")) == "fastq"
    assert detect_format_handle(_ff("\n\n")) == "fasta"


def test_parse_stream_returns_format_and_iterator(tmp_path):
    f = tmp_path / "reads.fasta"
    f.write_text(FASTA)
    fmt, it = parse_stream(str(f))
    assert fmt == "fasta"
    assert [h for h, _ in it] == ["a", "b"]


def test_parse_stream_fastq(tmp_path):
    f = tmp_path / "reads.fastq"
    f.write_text("@r1\nACGT\n+\nIIII\n")
    fmt, it = parse_stream(str(f))
    assert fmt == "fastq"
    assert list(it)[0][0] == "r1"


def test_count_records(tmp_path):
    f = tmp_path / "reads.fasta"
    f.write_text(FASTA)
    assert count_records(str(f)) == 2


def test_stream_head_limits(tmp_path):
    f = tmp_path / "reads.fasta"
    f.write_text(">a\nA\n>bb\nC\n>ccc\nG\n")
    head = stream_head(str(f), n=2)
    assert len(head) == 2
    assert [h for h, _ in head] == ["a", "bb"]