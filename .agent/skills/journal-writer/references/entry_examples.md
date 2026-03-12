# Entry Examples — La Forja Journal
# Load when generating entries to verify correct field population.

## Example: forge entry

```json
{
  "component_name": "rag-query",
  "component_type": "skill",
  "target_plane": "agent",
  "version": "1.0.0",
  "pattern_used": "Deterministic",
  "duration_minutes": 45,
  "external_audit": false,
  "rag_query_result": "No results — first instance of this component type",
  "notes": "ChromaDB collection must be initialized before first query. Added check in script."
}
```

## Example: problem entry

```json
{
  "title": "ChromaDB persist_directory not found on first run",
  "context": "Running rag-indexer for the first time on a fresh project",
  "root_cause": "ChromaDB expects the directory to exist before creating the collection",
  "solution": "Added os.makedirs(persist_directory, exist_ok=True) before ChromaDB client init",
  "mitigation": "All rag-* scripts now auto-create their required directories on startup",
  "affected_components": ["rag-indexer", "rag-query"],
  "severity": "medium",
  "recurrence_risk": "low"
}
```

## Example: adr entry

```json
{
  "title": "Use sentence-transformers/all-MiniLM-L6-v2 as default embedding model",
  "context": "Needed a local embedding model for ChromaDB without API key dependency",
  "decision": "all-MiniLM-L6-v2 via sentence-transformers library",
  "alternatives_considered": ["OpenAI text-embedding-ada-002", "Ollama nomic-embed-text", "Jina embeddings v2"],
  "reasoning": "all-MiniLM-L6-v2 runs locally with no API key, 384-dim vectors are fast and small, good semantic quality for technical documentation. OpenAI requires key. Ollama adds server dependency. Jina requires key at scale.",
  "consequences": "Model is English-optimized; Spanish content may have slightly lower retrieval quality. Acceptable given that technical body is in English per §4.6.",
  "status": "accepted",
  "supersedes": ""
}
```

## Example: pattern entry

```json
{
  "title": "Auto-create required directories on script startup",
  "description": "Scripts that depend on specific directory paths should create them with os.makedirs(exist_ok=True) before any file operation, rather than assuming they exist.",
  "evidence": ["20250311-150845_problem_chromadb-path-conflict.md", "20250309-112300_problem_quarantine-lab-missing.md"],
  "recommendation": "Add to all script templates: auto-create all required directories at startup. Add to quality_checklist.md.",
  "applies_to": "All Deterministic pattern skills with file I/O",
  "first_seen": "20250309"
}
```

## Example: field entry

```json
{
  "skill_or_agent": "skill-creator-pro",
  "project_context": "E-commerce automation backend — SMB client",
  "usage_description": "Used to forge a custom data-validation skill for product catalog imports",
  "outcome": "Skill generated correctly. Client used it successfully in 3 import cycles.",
  "client_friction": "Client was confused by the --force flag behavior — expected it to merge rather than backup+overwrite",
  "suggested_improvement": "Add --merge flag option or improve --force documentation with concrete example in SKILL.md",
  "operator_rating": 4
}
```
