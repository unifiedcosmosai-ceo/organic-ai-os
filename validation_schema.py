"""
LAYER 03 / DATA: VALIDIERUNGS-SCHEMA (v6)
Schemabasierte Validierung von geparsten Records (FASTA/FASTQ).

Statt hartkodierter Checks werden Regeln in Schemata gebuendelt -
neue Formate sind nur eine neue Schema-Definition (analog Format-Spec).
Forschung 2026: Validierung als Rueckgrat gegen Pseudo-Correctness,
bevor Daten weiter verarbeitet/promotet werden.

Records-Shape (bio_formats.parse_file):
  FASTA: {header: "SEQUENZ"}
  FASTQ: {header: {"seq": "...", "qual": "..."}}
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List

IUPAC = set("ACGTURYSWKMBDHVN")


@dataclass(frozen=True)
class ValidationRule:
    name: str
    check: Callable[[str, object], bool]
    detail: str = ""


@dataclass
class ValidationViolation:
    record: str
    rule: str
    detail: str


@dataclass
class ValidationReport:
    format: str
    schema: str
    total: int
    violations: List[ValidationViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations

    @property
    def violated(self) -> int:
        return len(self.violations)

    def to_dict(self) -> dict:
        return {
            "format": self.format,
            "schema": self.schema,
            "total": self.total,
            "ok": self.ok,
            "violated": self.violated,
            "violations": [
                {"record": v.record, "rule": v.rule, "detail": v.detail}
                for v in self.violations
            ],
        }


@dataclass
class RecordSchema:
    name: str
    format: str
    rules: List[ValidationRule]
    description: str = ""


def _seq_of(record: object) -> str:
    if isinstance(record, dict):
        return record.get("seq", "")
    return record or ""


def _rule_alphabet() -> ValidationRule:
    def check(rid, rec):
        seq = _seq_of(rec)
        if not seq:
            return True
        return all(c.upper() in IUPAC for c in seq)

    return ValidationRule("alphabet", check,
                          "Sequenz enthaelt Zeichen ausserhalb des IUPAC-Alphabets")


def _rule_nonempty() -> ValidationRule:
    def check(rid, rec):
        return bool(_seq_of(rec))

    return ValidationRule("nonempty", check, "Record hat leere Sequenz")


def _rule_unique_headers() -> ValidationRule:
    seen = set()

    def check(rid, rec):
        if rid in seen:
            return False
        seen.add(rid)
        return True

    return ValidationRule("unique_headers", check, "Doppelter Header/Record-Id")


def _rule_qual_length() -> ValidationRule:
    def check(rid, rec):
        seq = _seq_of(rec)
        qual = rec.get("qual", "") if isinstance(rec, dict) else ""
        return not qual or len(qual) == len(seq)

    return ValidationRule("qual_length", check,
                          "Qualitaetslaenge != Sequenzlaenge")


def _rule_max_seq_len(max_len: int) -> ValidationRule:
    def check(rid, rec):
        return len(_seq_of(rec)) <= max_len

    return ValidationRule("max_seq_len", check, f"Sequenz laenger als {max_len} bp")


def fasta_schema(max_seq_len: int = None) -> RecordSchema:
    rules = [_rule_alphabet(), _rule_nonempty(), _rule_unique_headers()]
    if max_seq_len:
        rules.append(_rule_max_seq_len(max_seq_len))
    return RecordSchema("fasta", "fasta", rules,
                        "FASTA: IUPAC-Alphabet, nicht-leer, eindeutige Header")


def fastq_schema(max_seq_len: int = None) -> RecordSchema:
    rules = [_rule_alphabet(), _rule_nonempty(), _rule_unique_headers(),
             _rule_qual_length()]
    if max_seq_len:
        rules.append(_rule_max_seq_len(max_seq_len))
    return RecordSchema("fastq", "fastq", rules,
                        "FASTQ: IUPAC-Alphabet + Qualitaetslaenge == Sequenzlaenge")


def default_schemas() -> Dict[str, RecordSchema]:
    return {"fasta": fasta_schema(), "fastq": fastq_schema()}


def list_schemas() -> List[str]:
    return sorted(default_schemas())


def detect_schema(content: str) -> str:
    import bio_formats
    return bio_formats.detect_format(content)


def validate_records(schema: RecordSchema, records: Dict[str, object]) -> ValidationReport:
    report = ValidationReport(format=schema.format, schema=schema.name, total=len(records))
    for rid, rec in records.items():
        for rule in schema.rules:
            try:
                ok = rule.check(rid, rec)
            except Exception:
                ok = False
            if not ok:
                report.violations.append(
                    ValidationViolation(str(rid), rule.name, rule.detail))
    return report


def validate_content(content: str, schema: str = "auto",
                     max_seq_len: int = None) -> ValidationReport:
    """Parst Inhalt (Auto-Detect) und validiert gegen ein Schema."""
    import bio_formats

    fmt = bio_formats.detect_format(content)
    if schema == "auto":
        sch = default_schemas()[fmt]
    else:
        sch = default_schemas().get(schema)
        if sch is None:
            raise ValueError(f"Unbekanntes Schema: {schema}")
    if max_seq_len:
        sch = RecordSchema(sch.name, sch.format, sch.rules + [_rule_max_seq_len(max_seq_len)])
    _, records = bio_formats.parse_file(content)
    return validate_records(sch, records)
