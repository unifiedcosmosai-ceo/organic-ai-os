"""Tests fuer das Format-Spec-Schema (v5, Layer 03)."""
import json

import format_spec
from format_spec import (
    FormatSpec, default_specs, derive_parser, detect_spec, list_specs,
    parse_file_spec, specs_to_json,
)


GFF_SAMPLE = (
    "##gff-version 3\n"
    "#comment\n"
    "chr1\tsrc\tgene\t1000\t2000\t.\t+\t.\tID=gene1;Name=Foo\n"
    "chr1\tsrc\texon\t1000\t1500\t.\t+\t.\tID=exon1;Parent=gene1\n"
)

VCF_SAMPLE = (
    "##fileformat=VCFv4.2\n"
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
    "chr1\t1000\trs1\tA\tG\t50\tPASS\tDP=10;AF=0.5\n"
)


def test_default_specs_present():
    specs = default_specs()
    assert {"gff3", "vcf"} <= set(specs)


def test_derive_parser_compiles():
    for spec in default_specs().values():
        code = derive_parser(spec)
        compile(code, "<spec>", "exec")


def test_derive_parser_pure():
    code = derive_parser(default_specs()["gff3"])
    assert "import" not in code  # selbstenthalten, kein Import-Coupling


def test_detected_gff3():
    spec = detect_spec(GFF_SAMPLE)
    assert spec is not None
    assert spec.name == "gff3"


def test_detected_vcf():
    spec = detect_spec(VCF_SAMPLE)
    assert spec is not None
    assert spec.name == "vcf"


def test_detect_fasta_returns_none():
    assert detect_spec(">a\nATGC\n") is None


def test_parse_gff3_attributes_mapped():
    records = parse_file_spec(default_specs()["gff3"], GFF_SAMPLE)
    assert "chr1" in records
    # beide Zeilen laufen unter seqid chr1, letzte gewinnt pro Spalte (dict-Merge)
    assert records["chr1"]["attributes"]["ID"] == "exon1"
    assert records["chr1"]["attributes"]["Parent"] == "gene1"


def test_parse_vcf_columns():
    records = parse_file_spec(default_specs()["vcf"], VCF_SAMPLE)
    rec = records["chr1"]
    assert rec["POS"] == "1000"
    assert rec["REF"] == "A"
    assert rec["ALT"] == "G"
    assert rec["INFO"] == "DP=10;AF=0.5"


def test_parse_gff3_skips_comment_and_header():
    records = parse_file_spec(default_specs()["gff3"], GFF_SAMPLE)
    # beide Records gehen unter ein seqid (chr1)
    assert len(records["chr1"]) > 0


def test_malformed_line_skipped():
    spec = default_specs()["gff3"]
    records = parse_file_spec(spec, "##gff-version 3\nchr1\tsrc\n")
    assert "chr1" not in records  # unvollstaendige Zeile (keine 9 Spalten) wird uebersprungen


def test_specs_serializable_roundtrip():
    raw = specs_to_json()
    data = json.loads(raw)
    assert set(data.keys()) == {"gff3", "vcf"}
    spec = FormatSpec.from_dict(data["gff3"])
    assert spec.columns == default_specs()["gff3"].columns


def test_list_specs():
    assert list_specs() == sorted(["gff3", "vcf"])


def test_custom_spec_derives():
    custom = FormatSpec(name="bed", marker="track", sep="\t",
                        columns=["chrom", "start", "end"])
    code = derive_parser(custom)
    ns = {}
    exec(code, ns, ns)
    out = ns["parse_bed"]("track name=x\nchr1\t1\t10\n")
    assert out["chr1"] == {"start": "1", "end": "10"}