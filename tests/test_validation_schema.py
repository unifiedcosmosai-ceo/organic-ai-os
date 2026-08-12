"""Tests fuer das Validierungs-Schema (v6, Layer 03)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from validation_schema import (
    fasta_schema, default_schemas, list_schemas,
    detect_schema, validate_records, validate_content, _rule_unique_headers,
)

FASTA_OK = ">a\nATGC\n>b\nGG\n"
FASTA_BAD_ALPHABET = ">a\nATXZ?\n"
FASTA_EMPTY = ">a\n\n"
FASTQ_OK = "@r1\nACGT\n+\nIIII\n"
FASTQ_BAD_QUAL = "@r1\nACGT\n+\nII\n"


def test_default_schemas_and_list():
    assert set(default_schemas()) == {"fasta", "fastq"}
    assert list_schemas() == ["fasta", "fastq"]


def test_detect_schema():
    assert detect_schema(FASTA_OK) == "fasta"
    assert detect_schema(FASTQ_OK) == "fastq"


def test_valid_fasta_passes():
    report = validate_content(FASTA_OK)
    assert report.ok
    assert report.total == 2


def test_invalid_alphabet_detected():
    report = validate_content(FASTA_BAD_ALPHABET)
    assert not report.ok
    assert any(v.rule == "alphabet" for v in report.violations)


def test_empty_sequence_detected():
    report = validate_content(FASTA_EMPTY)
    assert any(v.rule == "nonempty" for v in report.violations)


def test_unique_headers_rule():
    rule = _rule_unique_headers()
    assert rule.check("h1", "ATGC") is True
    assert rule.check("h1", "ATGC") is False
    assert rule.check("h2", "GG") is True


def test_fastq_ok():
    report = validate_content(FASTQ_OK, schema="fastq")
    assert report.ok


def test_fastq_qual_length_detected():
    report = validate_content(FASTQ_BAD_QUAL, schema="fastq")
    assert any(v.rule == "qual_length" for v in report.violations)


def test_max_seq_len():
    report = validate_content(FASTA_OK, max_seq_len=2)
    assert not report.ok
    assert any(v.rule == "max_seq_len" for v in report.violations)


def test_unknown_schema_raises():
    import pytest

    with pytest.raises(ValueError):
        validate_content(FASTA_OK, schema="nope")


def test_validate_records_direct():
    report = validate_records(fasta_schema(), {"a": "ATGC", "b": "N"})
    assert report.ok
    assert report.schema == "fasta"
    assert report.format == "fasta"


def test_report_shape():
    d = validate_content(FASTA_BAD_ALPHABET).to_dict()
    assert d["format"] == "fasta"
    assert d["ok"] is False
    assert d["violated"] >= 1
    assert "violations" in d
