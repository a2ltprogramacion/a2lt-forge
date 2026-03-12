#!/usr/bin/env python3
# journal_query.py — La Forja / A2LT Soluciones
# Text-based search across journal entries. Complements RAG for exact-match queries.
# Usage: python journal_query.py --term <text> [--type <type>] [--journal-dir <path>]

import os
import sys
import re
import argparse
from collections import defaultdict


VALID_TYPES = {"forge", "problem", "adr", "pattern", "field"}


def find_project_root(start: str) -> str:
    current = os.path.abspath(start)
    for _ in range(10):
        if os.path.exists(os.path.join(current, "AGENTS.md")):
            return current
        if os.path.exists(os.path.join(current, "agent", "manifest.json")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(start)


def search_entries(
    entries_dir: str,
    term: str,
    entry_type: str | None = None,
    max_results: int = 20
) -> list[dict]:
    """
    Full-text search across journal entries.
    Returns list of matches with filename, type, title, and matched lines.
    """
    if not os.path.exists(entries_dir):
        return []

    results = []
    term_lower = term.lower()

    for fname in sorted(os.listdir(entries_dir), reverse=True):  # newest first
        if not fname.endswith(".md"):
            continue

        # Filter by type if specified
        if entry_type:
            type_match = re.match(r'^\d{8}-\d{6}_([a-z]+)_', fname)
            if not type_match or type_match.group(1) != entry_type:
                continue

        fpath = os.path.join(entries_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
        except Exception:
            continue

        if term_lower not in content.lower():
            continue

        # Extract title
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = h1_match.group(1).strip() if h1_match else fname

        # Extract type from comment
        type_tag_match = re.search(r'\[JOURNAL\] type:(\w+)', content)
        etype = type_tag_match.group(1) if type_tag_match else "unknown"

        # Find matching lines with context
        matched_lines = []
        for i, line in enumerate(lines):
            if term_lower in line.lower():
                matched_lines.append({
                    "line_number": i + 1,
                    "content": line.strip()[:120]
                })
                if len(matched_lines) >= 3:
                    break

        results.append({
            "filename":     fname,
            "type":         etype,
            "title":        title,
            "matched_lines": matched_lines,
        })

        if len(results) >= max_results:
            break

    return results


def format_results(results: list[dict], term: str) -> None:
    if not results:
        print(f"[Journal] Sin resultados para: '{term}'")
        return

    print(f"[Journal] {len(results)} entrada(s) encontrada(s) para: '{term}'\n")
    print("=" * 70)

    for r in results:
        print(f"\n[{r['type'].upper()}] {r['title']}")
        print(f"  Archivo: {r['filename']}")
        if r["matched_lines"]:
            print("  Coincidencias:")
            for ml in r["matched_lines"]:
                print(f"    L{ml['line_number']}: {ml['content']}")
        print("-" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="La Forja Journal — Búsqueda de texto en entradas del journal."
    )
    parser.add_argument(
        "--term",
        required=True,
        help="Término de búsqueda (case-insensitive)."
    )
    parser.add_argument(
        "--type",
        choices=list(VALID_TYPES),
        default=None,
        help="Filtrar por tipo de entrada."
    )
    parser.add_argument(
        "--journal-dir",
        default=None,
        help="Ruta al directorio del journal. Por defecto: ./.agent/memory/journal/ desde raíz."
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=20,
        help="Número máximo de resultados a mostrar (default: 20)."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output en formato JSON (para consumo programático)."
    )
    args = parser.parse_args()

    if args.journal_dir:
        journal_dir = os.path.abspath(args.journal_dir)
    else:
        root = find_project_root(os.getcwd())
        journal_dir = os.path.join(root, "agent", "memory", "journal")

    entries_dir = os.path.join(journal_dir, "entries")

    if not os.path.exists(entries_dir):
        print(f"ERROR: Directorio de entradas no encontrado: {entries_dir}", file=sys.stderr)
        sys.exit(2)

    results = search_entries(
        entries_dir=entries_dir,
        term=args.term,
        entry_type=args.type,
        max_results=args.max_results
    )

    if args.json:
        import json
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        format_results(results, args.term)

    sys.exit(0 if results else 1)


if __name__ == "__main__":
    main()
