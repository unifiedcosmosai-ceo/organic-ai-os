"""Tests für bio_formats.py (Multi-Format Parser)."""

import bio_formats


def test_detect_fasta():
    assert bio_formats.detect_format(">seq1\nATGC\n") == "fasta"


def test_detect_fastq():
    assert bio_formats.detect_format("@r1\nACGT\n+\nIIII\n") == "fastq"


def test_parse_fasta_clean():
    fmt, records = bio_formats.parse_file(">seq1\nATGC\nATGC\n>seq2\nGGGG\n")
    assert fmt == "fasta"
    assert records == {"seq1": "ATGCATGC", "seq2": "GGGG"}


def test_parse_fasta_messy():
    fmt, records = bio_formats.parse_file(">a b c\n  atgc ATGC  \n\n>b\nGGGG\n")
    assert fmt == "fasta"
    assert records == {"a": "ATGCATGC", "b": "GGGG"}


def test_parse_fastq():
    fmt, records = bio_formats.parse_file("@r1\nACGTAC\n+\n!!!!!!\n@r2\nTTTT\n+\nIIII\n")
    assert fmt == "fastq"
    assert records["r1"] == {"seq": "ACGTAC", "qual": "!!!!!!"}
    assert records["r2"] == {"seq": "TTTT", "qual": "IIII"}


def test_parse_fastq_multiline_seq():
    fmt, records = bio_formats.parse_file("@r1\nACGT\nACGT\n+\nIIII\n")
    assert fmt == "fastq"
    assert records["r1"] == {"seq": "ACGTACGT", "qual": "IIII"}