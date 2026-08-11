"""
LAYER 03: FORMAT-SPEC-SCHEMA (v5)
Schema-basierter Metaparser: Formate werden als DSL-Spec beschrieben,
ein Parser wird aus der Spec ABGELEITET statt hartkodiert (Forschung: KBase,
Pfam/Stockholm-Stil, Ontologie-Mapping).

Design:
- `FormatSpec` = dataclass pro Format: marker, comment, columns, attrs.
- `derive_parser(spec)` = erzeugt eine Parser-Code-Funktion AUS der Spec
  (Code-Generator: strukturierter Text -> ausfuehrbares Python).
- Registry `SPECS` enthaelt GFF3 + VCF als neue Formate; FASTA/FASTQ bleiben
  in bio_formats, koennen aber ueber die Specs abgebildet werden.
- Schema-Tauglich: parse via JSON/TOML erweiterbar (Specs sind serialisierbar).
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


@dataclass
class FormatSpec:
    name: str
    marker: str                      # Zeilenpraefix der Records (z.B. "##gff-version")
    comment: str = "#"               # Kommentar-Marker
    sep: str = "\t"                  # Spaltentrenner
    columns: List[str] = field(default_factory=list)   # benannte Spaltenheader
    has_attributes: bool = False     # letzte Spalte = "attr=val;attr=val"
    skip_header_markers: List[str] = field(default_factory=list)
    seq_column: Optional[int] = None # bei Sequenzformaten: Spalte mit Sequenz

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "FormatSpec":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# --- Spec-Registry: neue Formate (GFF3, VCF) als wiederverwendbare Schemata ---
def default_specs() -> Dict[str, FormatSpec]:
    return {
        "gff3": FormatSpec(
            name="gff3",
            marker="##gff-version",
            comment="#",
            sep="\t",
            columns=["seqid", "source", "type", "start", "end",
                     "score", "strand", "phase", "attributes"],
            has_attributes=True,
            skip_header_markers=["##"],
        ),
        "vcf": FormatSpec(
            name="vcf",
            marker="##fileformat=VCF",
            comment="#",
            sep="\t",
            columns=["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO"],
            has_attributes=False,
            skip_header_markers=["##"],
        ),
    }


def _indent_attributes(col: int) -> str:
    """Erzeugt die Zeile, die die Attributes-Spalte in recs legt."""
    return (
        f'        attrs = {{}}\n'
        f'        for item in parts[{col}].split(";"):\n'
        f'            if "=" in item:\n'
        f'                k, v = item.split("=", 1)\n'
        f'                attrs[k] = v\n'
        f'        recs["attributes"] = attrs\n'
    )


def derive_parser(spec: FormatSpec) -> str:
    """
    Leitet aus einer FormatSpec eine ausfuehrbare Parser-Funktion als Code-String ab.
    Erzeugt getypte Records im FASTA/FASTQ-Stil (records dict) + optionale attrs-Map.
    """
    ncols = len(spec.columns)
    cols_repr = json.dumps(spec.columns, ensure_ascii=False)
    lines = [
        "def parse_" + spec.name + "(text):",
        f'    columns = {cols_repr}',
        "    records = {}",
        "    for line in text.splitlines():",
        "        s = line.strip()",
        "        if not s or s.startswith(" + repr(spec.comment) + "): continue",
        "        if any(s.startswith(m) for m in " + repr(spec.skip_header_markers) + "): continue",
        f'        parts = s.split({repr(spec.sep)})',
        "        if len(parts) != " + str(ncols) + ": continue",
    ]
    # Records-Schluessel
    if ncols >= 1:
        lines.append("        key = parts[0]")
    lines.append("        recs = records.setdefault(key, {})" if ncols >= 1 else "")
    # Spalten als dict (ohne den ersten als Key)
    lines.append(f"        for c, val in zip(columns[1:], parts[1:]):")
    lines.append('            recs[c] = val')
    if spec.has_attributes and "attributes" in spec.columns:
        attr_col = spec.columns.index("attributes")
        lines.append(_indent_attributes(attr_col))
    lines.append("    return records")
    code = "\n".join(l for l in lines if l != "")
    return code + "\n"


def build_parser_function(spec: FormatSpec) -> str:
    """Alias: vollstaendige Funktion mit import-loser Reinheit."""
    return derive_parser(spec)


def parse_file_spec(spec: FormatSpec, content: str) -> dict:
    """Fuehrt den abgeleiteten Parser AUS (kein exec-Caching)."""
    code = derive_parser(spec)
    ns = {}
    exec(code, ns, ns)
    fn = ns["parse_" + spec.name]
    return fn(content)


def detect_spec(text: str, specs: Optional[Dict[str, FormatSpec]] = None) -> Optional[FormatSpec]:
    """Erkennt ein Spec-Format anhand seines Marker-Praefixes."""
    specs = specs or default_specs()
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        for spec in specs.values():
            if s.startswith(spec.marker):
                return spec
        return None
    return None


def specs_to_json() -> str:
    return json.dumps({name: spec.to_dict() for name, spec in default_specs().items()},
                      indent=2, ensure_ascii=False)


def list_specs() -> list:
    """Fuer CLI/API: Namen der registrierten Specs."""
    return sorted(default_specs().keys())


if __name__ == "__main__":
    # Demo: GFF3 aus Spec ableiten und abspulen
    specs = default_specs()
    gff = specs["gff3"]
    print(f"🎯 Format-Spec: {gff.name} ({len(gff.columns)} Spalten)")
    code = derive_parser(gff)
    print(code)
    sample = (
        "##gff-version 3\n"
        "#Computational\n"
        "chr1\tsrc\tgene\t1000\t2000\t.\t+\t.\tID=gene1;Name=Foo\n"
        "chr1\tsrc\texon\t1000\t1500\t.\t+\t.\tID=exon1;Parent=gene1\n"
    )
    records = parse_file_spec(gff, sample)
    print("Records:", json.dumps(records, ensure_ascii=False))
    print("Detect:", detect_spec(sample).name if detect_spec(sample) else "?")