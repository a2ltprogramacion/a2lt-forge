"""
RAG Health Dashboard — La Forja
Reports index coverage, missing AUDITs, stale components, and overall health.

Usage (from project root, using venv):
    .venv/Scripts/python.exe .agent/skills/rag-indexer/scripts/rag_health.py
    .venv/Scripts/python.exe .agent/skills/rag-indexer/scripts/rag_health.py --json
"""

import json
import sys
from pathlib import Path
from typing import Any

import chromadb
import yaml


# ─── Configuration ───────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CONFIG_PATH = PROJECT_ROOT / "rag" / "config.yaml"
INDEX_DIR = PROJECT_ROOT / "rag" / "index"
AGENT_DIR = PROJECT_ROOT / ".agent"
CATALOGO_DIR = PROJECT_ROOT / "catalogo"
SESSIONS_DIR = PROJECT_ROOT / "rag" / "sources" / "sessions"


def load_config() -> dict[str, Any]:
    """Carga configuración RAG."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_manifest(path: Path) -> dict:
    """Carga un manifest.json."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def discover_components() -> list[dict]:
    """Descubre todos los componentes del ecosistema."""
    components = []

    # Core skills
    skills_dir = AGENT_DIR / "skills"
    if skills_dir.exists():
        for skill_dir in sorted(skills_dir.iterdir()):
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                components.append({
                    "name": skill_dir.name,
                    "type": "skill",
                    "plano": "core",
                    "path": str(skill_dir.relative_to(PROJECT_ROOT)),
                    "has_skill_md": skill_md.exists(),
                    "has_readme": (skill_dir / "README.md").exists(),
                    "has_scripts": (skill_dir / "scripts").exists()
                })

    # Core agents
    agents_dir = AGENT_DIR / "agents"
    if agents_dir.exists():
        for agent_dir in sorted(agents_dir.iterdir()):
            if agent_dir.is_dir():
                components.append({
                    "name": agent_dir.name,
                    "type": "agent",
                    "plano": "core",
                    "path": str(agent_dir.relative_to(PROJECT_ROOT)),
                    "has_skill_md": (agent_dir / "AGENT.md").exists(),
                    "has_readme": (agent_dir / "README.md").exists(),
                    "has_scripts": (agent_dir / "scripts").exists()
                })

    # Catálogo skills
    cat_skills = CATALOGO_DIR / "skills"
    if cat_skills.exists():
        for skill_dir in sorted(cat_skills.iterdir()):
            if skill_dir.is_dir():
                components.append({
                    "name": skill_dir.name,
                    "type": "skill",
                    "plano": "catalogo",
                    "path": str(skill_dir.relative_to(PROJECT_ROOT)),
                    "has_skill_md": (skill_dir / "SKILL.md").exists(),
                    "has_readme": (skill_dir / "README.md").exists(),
                    "has_scripts": (skill_dir / "scripts").exists()
                })

    # Catálogo agentes
    cat_agents = CATALOGO_DIR / "agentes"
    if cat_agents.exists():
        for agent_dir in sorted(cat_agents.iterdir()):
            if agent_dir.is_dir():
                components.append({
                    "name": agent_dir.name,
                    "type": "agent",
                    "plano": "catalogo",
                    "path": str(agent_dir.relative_to(PROJECT_ROOT)),
                    "has_skill_md": (agent_dir / "AGENT.md").exists(),
                    "has_readme": (agent_dir / "README.md").exists(),
                    "has_scripts": (agent_dir / "scripts").exists()
                })

    return components


def discover_audits() -> list[str]:
    """Descubre todos los AUDITs existentes."""
    if not SESSIONS_DIR.exists():
        return []
    return sorted([
        f.stem for f in SESSIONS_DIR.glob("AUDIT-*.md")
    ])


def check_index_health(client: chromadb.PersistentClient, config: dict) -> dict:
    """Verifica salud del índice ChromaDB."""
    collections = {}
    for col_config in config.get("collections", []):
        name = col_config["name"]
        try:
            col = client.get_collection(name)
            collections[name] = {
                "documents": col.count(),
                "status": "OK" if col.count() > 0 else "EMPTY"
            }
        except Exception:
            collections[name] = {"documents": 0, "status": "NOT_FOUND"}
    return collections


def generate_report(output_json: bool = False):
    """Genera reporte completo de salud RAG."""
    config = load_config()
    components = discover_components()
    audits = discover_audits()
    audit_names = {a.replace("AUDIT-", "").replace("AUDIT-FAILURE-", "")
                   for a in audits}

    # Index health
    try:
        client = chromadb.PersistentClient(path=str(INDEX_DIR))
        index_health = check_index_health(client, config)
        index_status = "OK"
    except Exception as e:
        index_health = {}
        index_status = f"ERROR: {e}"

    # Componentes sin AUDIT
    components_without_audit = []
    for comp in components:
        # Buscar si existe un AUDIT que contenga el nombre del componente
        has_audit = any(comp["name"] in audit_name for audit_name in audit_names)
        if not has_audit:
            components_without_audit.append(comp["name"])

    # Componentes sin README
    components_without_readme = [
        c["name"] for c in components if not c["has_readme"]
    ]

    # Componentes sin scripts funcionales
    components_without_scripts = [
        c["name"] for c in components if not c["has_scripts"]
    ]

    # Manifiestos
    core_manifest = load_manifest(AGENT_DIR / "manifest.json")
    cat_manifest = load_manifest(CATALOGO_DIR / "manifest.json")

    core_registered = set()
    for cat_key in ["skills", "agents"]:
        for item in core_manifest.get(cat_key, []):
            core_registered.add(item.get("name", ""))

    cat_registered = set()
    for cat_key in ["skills", "agentes"]:
        for item in cat_manifest.get(cat_key, []):
            cat_registered.add(item.get("name", ""))

    # Componentes no registrados en manifest
    unregistered = []
    for comp in components:
        if comp["plano"] == "core" and comp["name"] not in core_registered:
            unregistered.append(f"{comp['name']} (core)")
        elif comp["plano"] == "catalogo" and comp["name"] not in cat_registered:
            unregistered.append(f"{comp['name']} (catalogo)")

    # Calcular score de salud
    total_checks = len(components) * 3  # AUDIT + README + manifest
    passed_checks = (
        (len(components) - len(components_without_audit)) +
        (len(components) - len(components_without_readme)) +
        (len(components) - len(unregistered))
    )
    health_score = round((passed_checks / total_checks * 100) if total_checks > 0 else 0, 1)

    report = {
        "health_score": health_score,
        "index_status": index_status,
        "collections": index_health,
        "components": {
            "total": len(components),
            "core": len([c for c in components if c["plano"] == "core"]),
            "catalogo": len([c for c in components if c["plano"] == "catalogo"]),
        },
        "audits": {
            "total": len(audits),
            "components_without_audit": components_without_audit,
        },
        "documentation": {
            "components_without_readme": components_without_readme,
        },
        "manifest": {
            "unregistered_components": unregistered,
        },
        "issues": []
    }

    # Generar issues
    if index_status != "OK":
        report["issues"].append(f"[CRITICAL] Índice ChromaDB: {index_status}")
    for col_name, col_info in index_health.items():
        if col_info["status"] != "OK":
            report["issues"].append(f"[HIGH] Colección '{col_name}': {col_info['status']}")
    for comp in components_without_audit:
        report["issues"].append(f"[MEDIUM] Componente sin AUDIT: {comp}")
    for comp in unregistered:
        report["issues"].append(f"[MEDIUM] Componente no registrado en manifest: {comp}")
    for comp in components_without_readme:
        report["issues"].append(f"[LOW] Componente sin README: {comp}")

    if output_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    # Formato humano
    print("═══════════════════════════════════════════════════")
    print("  RAG Health Dashboard — La Forja")
    print("═══════════════════════════════════════════════════")
    print()
    print(f"  Health Score: {health_score}%")
    print(f"  Index Status: {index_status}")
    print()

    print("  ── Collections ──")
    for name, info in index_health.items():
        print(f"     {name}: {info['documents']} docs [{info['status']}]")
    print()

    print("  ── Components ──")
    print(f"     Total: {report['components']['total']} "
          f"(Core: {report['components']['core']}, "
          f"Catálogo: {report['components']['catalogo']})")
    print(f"     AUDITs: {report['audits']['total']}")
    print()

    if report["issues"]:
        print("  ── Issues ──")
        for issue in report["issues"]:
            print(f"     {issue}")
        print()

    if not report["issues"]:
        print("  ✅ No issues detected.")
        print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RAG Health Dashboard — La Forja")
    parser.add_argument("--json", action="store_true", help="Output in JSON")
    args = parser.parse_args()
    generate_report(output_json=args.json)
