"""
RAG Query — ChromaDB Query Interface for La Forja
Queries the vector index for existing components, patterns, and decisions.

Usage (from project root, using venv):
    .venv/Scripts/python.exe .agent/skills/rag-query/scripts/query.py "búsqueda"
    .venv/Scripts/python.exe .agent/skills/rag-query/scripts/query.py "error 403 GHL" --collection decisiones-arq
    .venv/Scripts/python.exe .agent/skills/rag-query/scripts/query.py "validación YAML" --top-k 3 --min-score 0.8
    .venv/Scripts/python.exe .agent/skills/rag-query/scripts/query.py --help-json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import chromadb
import yaml


# ─── Configuration ───────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[4]  # .agent/skills/rag-query/scripts → root
CONFIG_PATH = PROJECT_ROOT / "rag" / "config.yaml"
INDEX_DIR = PROJECT_ROOT / "rag" / "index"

# Keywords que activan prioridad de decisiones-arq sobre proyecto-docs
PROBLEM_KEYWORDS = [
    "error", "falla", "fallo", "problema", "no funciona", "bloqueador",
    "403", "404", "500", "timeout", "exception", "traceback", "crash",
    "bug", "broken", "failed", "failure", "missing", "incompatible"
]


def load_config() -> dict[str, Any]:
    """Carga configuración RAG desde config.yaml."""
    if not CONFIG_PATH.exists():
        print(f"[ERROR] Config no encontrada: {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_client() -> chromadb.PersistentClient:
    """Conecta al cliente ChromaDB persistente."""
    if not INDEX_DIR.exists():
        print("[ERROR] Índice no inicializado. Ejecuta reindex.py primero.", file=sys.stderr)
        sys.exit(1)
    return chromadb.PersistentClient(path=str(INDEX_DIR))


def is_problem_query(query: str) -> bool:
    """Determina si la consulta es sobre un problema (priorizar decisiones-arq)."""
    query_lower = query.lower()
    return any(kw in query_lower for kw in PROBLEM_KEYWORDS)


def query_collection(
    client: chromadb.PersistentClient,
    collection_name: str,
    query_text: str,
    top_k: int = 5,
    min_score: float = 0.7
) -> list[dict]:
    """
    Consulta una colección ChromaDB.
    Retorna lista de resultados con score, source y excerpt.
    """
    try:
        collection = client.get_collection(collection_name)
    except Exception:
        return []

    if collection.count() == 0:
        return []

    # ChromaDB retorna distancias (menor = más similar)
    # Convertimos a score (1 - distancia normalizada)
    results = collection.query(
        query_texts=[query_text],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    formatted = []
    if results and results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i] if results["distances"] else 1.0
            # ChromaDB usa distancia coseno: score = 1 - (distance / 2)
            score = round(1 - (distance / 2), 4)

            if score < min_score:
                continue

            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            document = results["documents"][0][i] if results["documents"] else ""

            # Truncar excerpt para legibilidad
            excerpt = document[:300].strip()
            if len(document) > 300:
                excerpt += "..."

            formatted.append({
                "id": doc_id,
                "score": score,
                "source": metadata.get("source_file", "unknown"),
                "component": metadata.get("component_name", "unknown"),
                "section": metadata.get("section_header", ""),
                "type": metadata.get("type", ""),
                "failure_category": metadata.get("failure_category", "null"),
                "excerpt": excerpt
            })

    return sorted(formatted, key=lambda x: x["score"], reverse=True)


def query_all(
    client: chromadb.PersistentClient,
    query_text: str,
    collection: str | None = None,
    top_k: int = 5,
    min_score: float = 0.7
) -> dict:
    """
    Consulta principal. Retorna resultados de una o ambas colecciones.
    Aplica preferencia de colección según tipo de consulta.
    """
    config = load_config()
    collections = [c["name"] for c in config.get("collections", [])]
    problem_query = is_problem_query(query_text)

    # Filtrar colecciones según parámetro
    if collection and collection != "all":
        target_collections = [collection] if collection in collections else []
    else:
        target_collections = collections

    all_results = []
    for col_name in target_collections:
        results = query_collection(client, col_name, query_text, top_k * 2, min_score)
        all_results.extend(results)

    # Aplicar preferencia: si es consulta de problema, boostar decisiones-arq
    if problem_query and not collection:
        for r in all_results:
            if r["type"] == "decisiones-arq":
                r["score"] = min(r["score"] * 1.15, 1.0)  # 15% boost
                r["boosted"] = True

    # Re-ordenar y truncar
    all_results.sort(key=lambda x: x["score"], reverse=True)
    all_results = all_results[:top_k]

    return {
        "query": query_text,
        "problem_detected": problem_query,
        "results": all_results,
        "no_results": len(all_results) == 0,
        "collections_searched": target_collections,
        "total_found": len(all_results)
    }


# ─── Output Formatting ──────────────────────────────────────────────────────

def format_human(result: dict) -> str:
    """Formato legible para humanos."""
    lines = []
    lines.append(f"Query: \"{result['query']}\"")
    if result["problem_detected"]:
        lines.append("⚠ Consulta de problema detectada → prioridad a decisiones-arq")
    lines.append(f"Colecciones: {', '.join(result['collections_searched'])}")
    lines.append(f"Resultados: {result['total_found']}")
    lines.append("")

    if result["no_results"]:
        lines.append("[SIN RESULTADOS] Score mínimo no alcanzado en ninguna colección.")
        lines.append("Acción sugerida: activar skill-search o web-search.")
        return "\n".join(lines)

    for i, r in enumerate(result["results"], 1):
        boost_tag = " [BOOSTED]" if r.get("boosted") else ""
        fail_tag = f" [failure: {r['failure_category']}]" if r["failure_category"] != "null" else ""
        lines.append(f"  {i}. [{r['score']:.2f}]{boost_tag}{fail_tag}")
        lines.append(f"     Source: {r['source']}")
        lines.append(f"     Component: {r['component']} | Section: {r['section']}")
        lines.append(f"     Excerpt: {r['excerpt'][:200]}")
        lines.append("")

    return "\n".join(lines)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="RAG Query — La Forja")
    parser.add_argument("query", nargs="?", default=None,
                        help="Natural language query to search")
    parser.add_argument("--collection", "-c", default=None,
                        help="Collection: proyecto-docs | decisiones-arq | all (default)")
    parser.add_argument("--top-k", "-k", type=int, default=5,
                        help="Number of results (default: 5, max: 10)")
    parser.add_argument("--min-score", "-s", type=float, default=0.7,
                        help="Minimum relevance score (default: 0.7)")
    parser.add_argument("--json", action="store_true",
                        help="Output in JSON format (for programmatic use)")
    parser.add_argument("--help-json", action="store_true",
                        help="Output help in JSON format")
    args = parser.parse_args()

    if args.help_json:
        print(json.dumps({
            "description": "Queries ChromaDB index for La Forja ecosystem",
            "args": [
                {"name": "query", "type": "string", "required": True,
                 "description": "Natural language query"},
                {"name": "--collection", "type": "string", "required": False,
                 "description": "proyecto-docs | decisiones-arq | all"},
                {"name": "--top-k", "type": "int", "required": False,
                 "description": "Number of results (1-10)"},
                {"name": "--min-score", "type": "float", "required": False,
                 "description": "Minimum score threshold (0.0-1.0)"},
                {"name": "--json", "type": "bool", "required": False,
                 "description": "Output as JSON"}
            ],
            "examples": [
                'python query.py "validación YAML"',
                'python query.py "error 403 GHL" -c decisiones-arq',
                'python query.py "email validation" --json'
            ]
        }, indent=2))
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    top_k = min(max(args.top_k, 1), 10)
    min_score = max(min(args.min_score, 1.0), 0.0)

    client = get_client()
    result = query_all(client, args.query, args.collection, top_k, min_score)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_human(result))

    # Exit code: 0 = results found, 1 = no results
    sys.exit(0 if not result["no_results"] else 1)


if __name__ == "__main__":
    main()
