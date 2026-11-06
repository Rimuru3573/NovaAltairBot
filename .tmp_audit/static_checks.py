"""Static sanity checks for the bot package: duplicate handler names, star imports,
unused imports, shadowed names, and mutable/typo callback data cross-check."""

from __future__ import annotations

import ast
import pathlib
import re
from collections import Counter

ROOT = pathlib.Path("src/novaaltairbot")
files = sorted(ROOT.rglob("*.py"))

print("=" * 70)
print("DUPLICATE TOP-LEVEL FUNCTION NAMES (per file)")
print("=" * 70)
for f in files:
    tree = ast.parse(f.read_text(encoding="utf-8"))
    names = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    dupes = {k: v for k, v in Counter(names).items() if v > 1}
    if dupes:
        print(f"{f}: {dupes}")

print()
print("=" * 70)
print("HANDLER CALLBACK DATA vs KEYBOARD CALLBACK DATA")
print("=" * 70)
handler_data: set[str] = set()
for f in files:
    tree = ast.parse(f.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Attribute) and node.left.attr == "data":
            for comp in node.comparators:
                if isinstance(comp, ast.Constant) and isinstance(comp.value, str):
                    handler_data.add(comp.value)

kb_file = ROOT / "keyboards" / "inline.py"
kb_data: set[str] = set()
for m in re.finditer(r'callback_data="([^"]+)"', kb_file.read_text(encoding="utf-8")):
    kb_data.add(m.group(1))

print("handled  :", sorted(handler_data))
print("in kbd   :", sorted(kb_data))
print("DEAD BUTTONS (in keyboard, no handler):", sorted(kb_data - handler_data))
print("ORPHAN HANDLERS (no button):", sorted(handler_data - kb_data))

print()
print("=" * 70)
print("STAR IMPORTS / BROAD EXCEPTS / BARE EXCEPT")
print("=" * 70)
for f in files:
    tree = ast.parse(f.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and any(a.name == "*" for a in node.names):
            print(f"star import: {f}:{node.lineno} from {node.module}")
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            print(f"bare except: {f}:{node.lineno}")

print()
print("=" * 70)
print("UNUSED IMPORTED NAMES (rough, name-based)")
print("=" * 70)
for f in files:
    src = f.read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imported.append((a.asname or a.name.split(".")[0], node.lineno))
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                if a.name != "*":
                    imported.append((a.asname or a.name, node.lineno))
    used: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            pass
    # count textual occurrences beyond the import line
    lines = src.splitlines()
    for name, lineno in imported:
        occurrences = sum(
            1 for i, line in enumerate(lines, 1) if re.search(rf"\b{re.escape(name)}\b", line) and i != lineno
        )
        if occurrences == 0:
            print(f"unused import: {f}:{lineno} -> {name}")
