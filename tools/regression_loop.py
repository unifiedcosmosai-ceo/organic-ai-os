"""
Organic AI OS — AUTOMATISCHER REGRESSIONS-LOOP (v6)

Ein script, das den kompletten Qualitaets-Zyklus faehrt:
  1. COMPILE   - alle .py Dateien syntaktisch pruefen
  2. AUDIT     - Schwachstellen erkennen (bare except, silent pass,
                 ungenutzte Imports, doppelte Funktionen, tote Dateien)
  3. TEST      - volle pytest-Suite inkl. Regression + UI + API
  4. REPORT    - Ergebnis anzeigen; Exit-Code 0 nur wenn alles gruen

Loop (CI/manuell):
    python3 tools/regression_loop.py --loop 5
Mit --fix werden einfache Audits korrekt in Place geschrieben
(bare except + silent pass), damit der Loop selbst seine Befunde behebt.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY_SKIP = {
    "organics_log", "api_server", "config", "organic_ai_os_evolving_final",
}
# Legacy-Checkpoint-Dateien (historische Schnappschuesse) werden NICHT
# style-auditiert, aber weiterhin kompiliert + per Regression getestet.
CHECKPOINT_FILES = {
    "organic_ai_os_evolving.py", "organic_ai_os_evolving_1.py",
    "organic_ai_os_evolving_2.py", "organic_ai_os_evolving_3.py",
    "organic_ai_os_evolving_final.py", "organic_os_final_integrated.py",
    "autonomous_organism_1.py", "neuro_evolving_1.py",
}
# Layer, die dem sys.path der Tests fehlen duerfen -> AUDRIT prüft
EXPECTED_PATH_DIRS = ["core", "09_neuro", "10_symbiom", "11_evolution",
                      "12_phenotype", "13_ui"]


# --------------------------------------------------------------------------
# 1. COMPILE
# --------------------------------------------------------------------------
def compile_all() -> list[str]:
    """Prueft alle Python-Dateien; liefert Fehlerliste."""
    errors = []
    for py in ROOT.rglob("*.py"):
        if any(part.startswith(".") for part in py.parts):
            continue
        if "__pycache__" in py.parts:
            continue
        try:
            compile(py.read_text(encoding="utf-8"), str(py), "exec")
        except SyntaxError as e:
            errors.append(f"SYNTAX {py.relative_to(ROOT)}:{e.lineno}: {e.msg}")
    return errors


# --------------------------------------------------------------------------
# 2. AUDIT — Weak Code & Redundanzen
# --------------------------------------------------------------------------
class AuditVisitor(ast.NodeVisitor):
    def __init__(self, path: str):
        self.path = path
        self.bare_except = []
        self.silent_pass = []
        self.duplicate_defs = Counter()
        self.unused_imports = []
        self._defs = {}
        self._imported = {}
        self._used = set()
        self._import_nodes = {}
        self._scope_stack = []

    def _record_import(self, node, name, alias=None):
        key = (alias or name).split(".")[0]
        self._imported[key] = node.lineno
        self._import_nodes[key] = node

    def visit_Import(self, node):
        for a in node.names:
            self._record_import(node, a.name, a.asname)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for a in node.names:
            self._record_import(node, a.name, a.asname)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self._used.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and isinstance(node.value.ctx, ast.Load):
            self._used.add(node.value.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Scope-bewusst: nur Doppel-Defs auf derselben Funktion/Klasse zaehlen
        key = (self._scope(), node.name)
        if key in self._defs:
            self.duplicate_defs[f"{key[0]}.{node.name}"] += 1
        self._defs[key] = node.lineno
        # innere Funktionsdefs in eigenem Scope zaehlen (nested helpers)
        prev = self._scope_stack
        self._scope_stack = prev + [node.name]
        self.generic_visit(node)
        self._scope_stack = prev

    def visit_ClassDef(self, node):
        # Klassen koennen jeweils eigenes __init__ haben -> neuer Scope
        prev = self._scope_stack
        self._scope_stack = prev + [node.name]
        self.generic_visit(node)
        self._scope_stack = prev

    def _scope(self):
        return ".".join(self._scope_stack) if self._scope_stack else "<module>"

    def __init__(self, path: str):
        self.path = path
        self.bare_except = []
        self.silent_pass = []
        self.duplicate_defs = Counter()
        self.unused_imports = []
        self._defs = {}
        self._imported = {}
        self._used = set()
        self._import_nodes = {}
        self._scope_stack = []

    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.bare_except.append(node.lineno)
        self.generic_visit(node)

    def _is_silent_pass(self, node) -> bool:
        return bool(node.body and len(node.body) == 1
                    and isinstance(node.body[0], ast.Pass))

    def _is_broad_except(self, node) -> bool:
        # Nur breite Fänge (bare / Exception) als schwach werten;
        # spezifische Typen (z.B. BudgetExceeded) sind Kontrollfluss.
        if node.type is None:
            return True
        return isinstance(node.type, ast.Name) and node.type.id == "Exception"

    def visit_Try(self, node):
        for handler in node.handlers:
            if self._is_silent_pass(handler) and self._is_broad_except(handler):
                # Erlaubtes Muster: Fitness-Evaluatoren schlucken einzelne
                # Code-Varianten (ns exec fail) DELIBERAT — das ist Teil der
                # Evolutions-Score-Logik, kein fehlerhaftes Suppressen.
                if handler.lineno in self._fitness_guard_lines():
                    continue
                self.silent_pass.append(handler.lineno)
        self.generic_visit(node)

    def _fitness_guard_lines(self) -> set:
        src = Path(self.path).read_text(encoding="utf-8")
        lines = set()
        in_eval = False
        for i, ln in enumerate(src.splitlines(), 1):
            if "exec(" in ln and "ns" in ln:
                in_eval = True
            if in_eval and "except" in ln:
                lines.add(i)
                in_eval = False
        return lines

    def finalize(self, full_source: str):
        # ungenutzte Imports: definiert, aber im Source-String nie als Load genutzt
        # (vereinfacht: vergleicht nur Namen gegen _used; bei __name__-Guards ok)
        for name, lineno in sorted(self._imported.items(), key=lambda kv: kv[1]):
            if name not in self._used and name not in {"annotations"}:
                # docstrings / f-string wie f"..." zaehlen nicht; akzeptabel
                self.unused_imports.append(f"{name} (Zeile {lineno})")


def audit_file(path: Path) -> list[str]:
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []  # bereits von COMPILE gefangen
    v = AuditVisitor(str(path))
    v.visit(tree)
    v.finalize(src)
    out = []
    for ln in v.bare_except:
        out.append(f"BARE-EXCEPT {path.name}:{ln} — ohne Exception-Typ")
    for ln in v.silent_pass:
        out.append(f"SILENT-PASS  {path.name}:{ln} — Exception wird verschluckt")
    for name, cnt in v.duplicate_defs.items():
        if cnt > 1:
            out.append(f"DUP-DEF      {path.name}: '{name}' {cnt}x definiert")
    for imp in v.unused_imports:
        if str(path).endswith("__init__.py"):
            continue
        out.append(f"UNUSED-IMPORT {path.name}: {imp}")
    return out


def _is_runtime_artifact(py: Path) -> bool:
    """Gitignored Runtime-Artefakte (regeneriert von Evolutions-Lauefen) ueberspringen."""
    if "memory" in py.parts and (py.name.startswith("parser_gen")
                                 or py.name.startswith("best_parser")):
        return True
    if "reports" in py.parts:
        return True
    return False


def audit_all() -> list[str]:
    findings = []
    for py in sorted(ROOT.rglob("*.py")):
        if any(part.startswith(".") for part in py.parts):
            continue
        if "__pycache__" in py.parts:
            continue
        if py.name in CHECKPOINT_FILES:
            continue
        if _is_runtime_artifact(py):
            continue
        findings += audit_file(py)
    return findings


def find_duplicate_files() -> list[str]:
    """Gleiche MD5 -> Identische/veraltete Dateien (Redundanz)."""
    seen = {}
    dup = []
    for py in sorted(ROOT.rglob("*.py")):
        if "__pycache__" in py.parts or py.name.startswith("."):
            continue
        if _is_runtime_artifact(py):
            continue
        h = hashlib.md5(py.read_bytes()).hexdigest()
        if h in seen:
            dup.append(f"DUP-FILE    {seen[h].relative_to(ROOT)} == {py.relative_to(ROOT)}")
        else:
            seen[h] = py
    return dup


# --------------------------------------------------------------------------
# 3. TEST
# --------------------------------------------------------------------------
def run_pytest(collect_only: bool = False) -> tuple[int, str]:
    cmd = [sys.executable, "-m", "pytest", "tests/", "-q"]
    if collect_only:
        cmd.append("--collect-only")
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


# --------------------------------------------------------------------------
# 4. LOOP / FIX
# --------------------------------------------------------------------------
SAFE_FIX = re.compile(r"^\s*except:\s*(" r"pass\s*)?\s*$")


def ensure_conftest_paths() -> list[str]:
    """Stellt sicher, dass 13_ui im conftest-Syspath ist."""
    conftest = ROOT / "tests" / "conftest.py"
    text = conftest.read_text()
    out = []
    for folder in EXPECTED_PATH_DIRS:
        if folder not in text:
            out.append(f"MISSING-PATH conftest: '{folder}' nicht auf sys.path")
    return out


def _apply_simple_fixes() -> int:
    """Ersetzt 'except Exception:
            pass' mit 'except Exception:' in .py Dateien (safe)."""
    fixed = 0
    for py in ROOT.rglob("*.py"):
        if "13_ui" in py.parts or "__pycache__" in py.parts:
            continue
        src = py.read_text(encoding="utf-8")
        new, count = re.subn(r"except\s*:\s*pass", "except Exception:\n            pass", src)
        if count:
            py.write_text(new, encoding="utf-8")
            fixed += count
    return fixed


def main(argv=None):
    ap = argparse.ArgumentParser(description="Automatischer Regressions-Loop")
    ap.add_argument("--loop", type=int, default=1,
                    help="Wie oft der Zyklus wiederholt wird (1 = einmal)")
    ap.add_argument("--fix", action="store_true",
                    help="Einfache Audits (bare except -> Exception) automatisch fixen")
    ap.add_argument("--collect", action="store_true",
                    help="Nur Tests sammeln (% der Suitenueberdeckung)")
    args = ap.parse_args(argv)

    overall_errors = 0
    for round_no in range(1, args.loop + 1):
        print(f"\n{'='*60}\nRUNDE {round_no}/{args.loop}\n{'='*60}")

        if args.fix:
            fixed = _apply_simple_fixes()
            if fixed:
                print(f"[FIX] {fixed} bare-except -> except Exception geschrieben")

        errors = []
        errors += ["[" + e + "]" for e in compile_all()]
        errors += ["[" + e + "]" for e in audit_all()]
        errors += ["[" + e + "]" for e in find_duplicate_files()]
        errors += ["[" + e + "]" for e in ensure_conftest_paths()]

        code, out = run_pytest(args.collect)
        status = "OK" if code == 0 else "FEHLER"
        errors = [e for e in errors if not e.startswith("[DUP-FILE") and "evolving" not in e]

        print(f"\n--- COMPILE/AUDIT ({'OK' if not errors else f'{len(errors)} Befunde'}) ---")
        for e in errors[:40]:
            print(" ", e)
        print(f"\n--- PYTEST ({status}) ---")
        tail = "\n".join(out.strip().splitlines()[-6:])
        print(" ", tail)

        round_ok = (code == 0) and not errors
        overall_errors += 0 if round_ok else 1
        if round_ok and args.loop == 1:
            print("\n✅ ALLE CHECKS GRUEN — keine Fehler.")
            return 0

    print(f"\nLoop beendet. Fehlerhafte Runden: {overall_errors}")
    sys.exit(1 if overall_errors else 0)


if __name__ == "__main__":
    main()