import json
import sys
import argparse
from pathlib import Path

try:
    import yaml
    import jsonschema
except ImportError:
    print(json.dumps({
        "valid": False,
        "errors": [{"message": "Missing dependencies: pyyaml or jsonschema not installed"}]
    }))
    sys.exit(1)

# Default La Forja schema (§3.4)
DEFAULT_SCHEMA = {
    "type": "object",
    "required": ["name", "version", "type", "description"],
    "properties": {
        "name": {"type": "string", "pattern": "^[a-z0-9-]+$"},
        "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
        "type": {"enum": ["backend", "frontend", "integration", "utility"]},
        "subtype": {"enum": ["skill", "agent"]},
        "tier": {"enum": ["vcard", "authority", "enterprise", "all"]},
        "description": {"type": "string"},
        "triggers": {"type": "object"},
        "entrypoint": {"type": "object"},
        "inputs": {"type": "array"},
        "outputs": {"type": "array"},
        "dependencies": {"type": "array"},
        "framework_version": {"type": "string"}
    }
}

def validate_yaml(filepath, schema_path=None, strict_mode=False):
    """Valida un archivo YAML contra esquema."""
    result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "metadata": None
    }
    
    # Leer archivo
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        # Separar frontmatter YAML
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                yaml_content = parts[1]
            else:
                yaml_content = content
        else:
            yaml_content = content
        data = yaml.safe_load(yaml_content)
    except FileNotFoundError:
        result["errors"].append({"message": f"File not found: {filepath}"})
        return result
    except yaml.YAMLError as e:
        result["errors"].append({
            "message": f"YAML parsing error: {str(e)}",
            "line": getattr(e, 'start_mark').line + 1 if hasattr(e, 'start_mark') else "unknown"
        })
        return result
    
    # Cargar esquema
    schema = DEFAULT_SCHEMA
    if schema_path:
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
        except Exception as e:
            result["errors"].append({"message": f"Failed to load schema: {str(e)}"})
            return result
    
    # Validar contra esquema
    try:
        jsonschema.validate(instance=data, schema=schema)
        result["valid"] = True
        result["metadata"] = {k: v for k, v in data.items() if k in ["name", "version", "type", "description"]}
    except jsonschema.ValidationError as e:
        result["errors"].append({
            "field": e.path[-1] if e.path else e.schema_path[-1] if e.schema_path else "unknown",
            "message": e.message,
            "suggestion": f"Check AGENTS.md §3.4 for {e.schema_path[-1]} requirements" if e.schema_path else "Review YAML structure"
        })
    
    # Validaciones adicionales de La Forja
    if isinstance(data, dict):
        # Check SemVer
        if "version" in data:
            version = str(data["version"])
            if not all(part.isdigit() for part in version.split('.')):
                result["errors"].append({
                    "field": "version",
                    "message": f"Invalid SemVer format: {version}",
                    "suggestion": "Use format MAJOR.MINOR.PATCH (e.g., 1.0.0)"
                })
        
        # Missing optional fields (warnings)
        if "tier" not in data:
            result["warnings"].append({
                "line": "optional",
                "field": "tier",
                "message": "Optional field missing. Assumes tier=all if not specified."
            })
    
    if strict_mode and result["warnings"]:
        result["errors"].extend(result["warnings"])
        result["warnings"] = []
        result["valid"] = False
    
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate YAML files against La Forja schema (§3.4)")
    parser.add_argument("--filepath", required=True, help="Path to YAML file")
    parser.add_argument("--schema-path", help="Path to custom JSON Schema")
    parser.add_argument("--strict-mode", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--output-format", default="json", choices=["json", "text"], help="Output format")
    
    args = parser.parse_args()
    
    result = validate_yaml(args.filepath, args.schema_path, args.strict_mode)
    
    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Valid: {result['valid']}")
        if result["errors"]:
            print("\nErrors:")
            for err in result["errors"]:
                print(f"  - {err.get('field', '?')}: {err['message']}")
        if result["warnings"]:
            print("\nWarnings:")
            for warn in result["warnings"]:
                print(f"  - {warn.get('field', '?')}: {warn['message']}")
    
    sys.exit(0 if result["valid"] else 1)
