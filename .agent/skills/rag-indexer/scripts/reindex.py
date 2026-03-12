"""
RAG Indexer — ChromaDB Index Builder for La Forja
Builds and updates the vector index from ecosystem documents.

Usage (from project root, using venv):
    .venv/Scripts/python.exe .agent/skills/rag-indexer/scripts/reindex.py
    .venv/Scripts/python.exe .agent/skills/rag-indexer/scripts/reindex.py --force-rebuild
    .venv/Scripts/python.exe .agent/skills/rag-indexer/scripts/reindex.py --validate
    .venv/Scripts/python.exe .agent/skills/rag-indexer/scripts/reindex.py --collections proyecto-docs
"""

import argparse
import glob
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import chromadb
import yaml


# ─── Configuration ───────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[4]  # .agent/skills/rag-indexer/scripts → root
CONFIG_PATH = PROJECT_ROOT / "rag" / "config.yaml"
INDEX_DIR = PROJECT_ROOT / "rag" / "index"


def load_config() -> dict[str, Any]:
    """Loads RAG configuration from config.yaml."""
    if not CONFIG_PATH.exists():
        print(f"[ERROR] Config not found: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ─── Markdown Chunking ──────────────────────────────────────────────────────

def chunk_by_headers(content: str, source_file: str, max_tokens: int = 512) -> list[dict]:
    """
    Splits markdown content by H2/H3 headers.
    Each chunk includes: content, metadata (section_header, source_file).
    Approximation: 1 token ≈ 4 characters.
    """
    chunks = []
    max_chars = max_tokens * 4

    # Extract YAML frontmatter as first chunk
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if frontmatter_match:
        fm_text = frontmatter_match.group(0)
        # Parse component name from frontmatter
        name_match = re.search(r'^name:\s*(.+)$', fm_text, re.MULTILINE)
        component_name = name_match.group(1).strip().strip('"\'') if name_match else Path(source_file).parent.name
        version_match = re.search(r'^version:\s*(.+)$', fm_text, re.MULTILINE)
        version = version_match.group(1).strip().strip('"\'') if version_match else "unknown"

        chunks.append({
            "content": fm_text,
            "metadata": {
                "source_file": source_file,
                "component_name": component_name,
                "version": version,
                "section_header": "frontmatter",
                "type": "proyecto-docs"
            }
        })
        content = content[frontmatter_match.end():]
    else:
        component_name = Path(source_file).parent.name
        version = "unknown"

    # Split by H2/H3 headers
    sections = re.split(r'(?=^#{2,3}\s)', content, flags=re.MULTILINE)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract header
        header_match = re.match(r'^(#{2,3})\s+(.+)', section)
        header = header_match.group(2).strip() if header_match else "body"

        # Truncate if too long (simple approach)
        if len(section) > max_chars:
            section = section[:max_chars] + "\n[...truncated]"

        chunks.append({
            "content": section,
            "metadata": {
                "source_file": source_file,
                "component_name": component_name,
                "version": version,
                "section_header": header,
                "type": "proyecto-docs"
            }
        })

    return chunks


def chunk_full_document(content: str, source_file: str, max_tokens: int = 1024) -> list[dict]:
    """
    Indexes document as a single chunk (or splits by H2 if too large).
    Used for AUDITs, ADRs, session documents.
    """
    max_chars = max_tokens * 4
    filename = Path(source_file).name

    # Determine metadata from filename
    tipo = "adr" if filename.startswith("ADR-") else (
        "audit-failure" if "FAILURE" in filename else (
            "audit-success" if filename.startswith("AUDIT-") else "session"
        )
    )

    # Extract component name from filename pattern AUDIT-[name]-[date].md
    comp_match = re.match(r'AUDIT-(?:FAILURE-)?(?:OPTION-[A-Z]-)?(.+?)-(\d{8})\.md', filename)
    component_name = comp_match.group(1) if comp_match else filename.replace(".md", "")

    # Extract failure category from content if present
    failure_cat = None
    cat_match = re.search(r'Failure category:\s*(\S+)', content)
    if cat_match and cat_match.group(1) != "null":
        failure_cat = cat_match.group(1)

    # Extract status
    status = "exitoso"
    if "FAILURE" in filename:
        status = "fracaso"
    elif re.search(r'Status final:\s*(fracaso|parcial)', content):
        status_match = re.search(r'Status final:\s*(\S+)', content)
        status = status_match.group(1) if status_match else "exitoso"

    base_metadata = {
        "source_file": source_file,
        "component_name": component_name,
        "tipo": tipo,
        "status": status,
        "failure_category": failure_cat or "null",
        "type": "decisiones-arq"
    }

    # If fits in one chunk
    if len(content) <= max_chars:
        return [{
            "content": content,
            "metadata": base_metadata
        }]

    # Split by H2 if too large
    chunks = []
    sections = re.split(r'(?=^##\s)', content, flags=re.MULTILINE)
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if len(section) > max_chars:
            section = section[:max_chars] + "\n[...truncated]"

        header_match = re.match(r'^##\s+(.+)', section)
        header = header_match.group(1).strip() if header_match else "header"

        meta = {**base_metadata, "section_header": header}
        chunks.append({"content": section, "metadata": meta})

    return chunks


# ─── File Discovery ──────────────────────────────────────────────────────────

def discover_files(sources: list[str], root: Path) -> list[Path]:
    """Discovers all .md files from the configured sources."""
    files = []
    for source in sources:
        source_path = root / source.lstrip("./")
        if source_path.is_file():
            files.append(source_path)
        elif source_path.is_dir():
            for md_file in sorted(source_path.rglob("*.md")):
                files.append(md_file)
        else:
            # Treat as glob pattern
            for match in sorted(glob.glob(str(root / source.lstrip("./")), recursive=True)):
                p = Path(match)
                if p.is_file() and p.suffix == ".md":
                    files.append(p)
    return files


def file_hash(path: Path) -> str:
    """Calculates SHA-256 hash of a file for change detection."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ─── ChromaDB Operations ────────────────────────────────────────────────────

def get_client() -> chromadb.PersistentClient:
    """Creates or connects to the ChromaDB persistent client."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(INDEX_DIR))


def index_collection(
    client: chromadb.PersistentClient,
    collection_name: str,
    collection_config: dict,
    force_rebuild: bool = False
) -> int:
    """Indexes documents into a ChromaDB collection. Returns count of indexed docs."""

    if force_rebuild:
        try:
            client.delete_collection(collection_name)
            print(f"  [REBUILD] Deleted existing collection: {collection_name}")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": collection_config.get("description", "")}
    )

    sources = collection_config.get("sources", [])
    strategy = collection_config.get("extraction_strategy", "markdown_structure")
    chunk_size = collection_config.get("chunk_size", 512)

    files = discover_files(sources, PROJECT_ROOT)
    if not files:
        print(f"  [WARN] No files found for collection '{collection_name}'")
        return 0

    indexed = 0
    for filepath in files:
        rel_path = str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")
        content = filepath.read_text(encoding="utf-8", errors="replace")

        if not content.strip():
            continue

        # Chunk based on strategy
        if strategy == "markdown_structure":
            chunks = chunk_by_headers(content, rel_path, max_tokens=chunk_size)
        else:
            chunks = chunk_full_document(content, rel_path, max_tokens=chunk_size)

        for i, chunk in enumerate(chunks):
            doc_id = f"{rel_path}::chunk_{i}"
            # Check if already exists with same content hash
            content_hash = hashlib.md5(chunk["content"].encode()).hexdigest()
            chunk["metadata"]["content_hash"] = content_hash

            try:
                existing = collection.get(ids=[doc_id])
                if (existing["ids"]
                    and existing["metadatas"]
                    and existing["metadatas"][0].get("content_hash") == content_hash
                    and not force_rebuild):
                    continue  # Skip unchanged
            except Exception:
                pass

            collection.upsert(
                ids=[doc_id],
                documents=[chunk["content"]],
                metadatas=[chunk["metadata"]]
            )
            indexed += 1

    return indexed


# ─── Validation ──────────────────────────────────────────────────────────────

def validate_index(client: chromadb.PersistentClient, config: dict) -> str:
    """Validates index integrity. Returns OK | STALE | EMPTY."""
    collections = config.get("collections", [])
    results = {}

    for col_config in collections:
        name = col_config["name"]
        try:
            col = client.get_collection(name)
            count = col.count()
            results[name] = count
        except Exception:
            results[name] = 0

    if all(v == 0 for v in results.values()):
        return "EMPTY"

    # Check if source files have changed since last index
    for col_config in collections:
        name = col_config["name"]
        sources = col_config.get("sources", [])
        files = discover_files(sources, PROJECT_ROOT)
        col_count = results.get(name, 0)
        if len(files) > 0 and col_count == 0:
            return "STALE"

    return "OK"


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="RAG Indexer — La Forja")
    parser.add_argument("--force-rebuild", action="store_true",
                        help="Delete and rebuild index from scratch")
    parser.add_argument("--validate", action="store_true",
                        help="Validate index integrity without modifying")
    parser.add_argument("--collections", nargs="+", default=None,
                        help="Specific collections to index (default: all)")
    parser.add_argument("--help-json", action="store_true",
                        help="Output help in JSON format")
    args = parser.parse_args()

    if args.help_json:
        print(json.dumps({
            "description": "Builds and updates ChromaDB vector index for La Forja",
            "args": [
                {"name": "--force-rebuild", "type": "bool", "required": False,
                 "description": "Delete and rebuild from scratch"},
                {"name": "--validate", "type": "bool", "required": False,
                 "description": "Check index status without modifying"},
                {"name": "--collections", "type": "list", "required": False,
                 "description": "Collections to index: proyecto-docs, decisiones-arq"}
            ],
            "examples": [
                "python reindex.py",
                "python reindex.py --force-rebuild",
                "python reindex.py --validate",
                "python reindex.py --collections proyecto-docs"
            ]
        }, indent=2))
        return

    config = load_config()
    client = get_client()

    if args.validate:
        status = validate_index(client, config)
        print(f"Index status: {status}")
        for col_config in config.get("collections", []):
            name = col_config["name"]
            try:
                col = client.get_collection(name)
                print(f"  {name}: {col.count()} documents")
            except Exception:
                print(f"  {name}: NOT FOUND")
        sys.exit(0 if status == "OK" else 1)

    # Index collections
    print(f"RAG Indexer — La Forja")
    print(f"Mode: {'FORCE REBUILD' if args.force_rebuild else 'INCREMENTAL'}")
    print(f"Index directory: {INDEX_DIR}")
    print()

    start = time.time()
    total_indexed = 0

    for col_config in config.get("collections", []):
        name = col_config["name"]
        if args.collections and name not in args.collections:
            continue

        print(f"[{name}]")
        count = index_collection(client, name, col_config, args.force_rebuild)
        total_indexed += count
        try:
            col = client.get_collection(name)
            print(f"  Indexed: {count} new/updated | Total: {col.count()} documents")
        except Exception:
            print(f"  Indexed: {count} new/updated")

    elapsed = time.time() - start
    print(f"\nCompleted in {elapsed:.2f}s | Total indexed: {total_indexed}")
    print(json.dumps({
        "indexed_count": total_indexed,
        "index_status": "success",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")
    }))


if __name__ == "__main__":
    main()
