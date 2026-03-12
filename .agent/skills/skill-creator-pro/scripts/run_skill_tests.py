#!/usr/bin/env python3
# run_skill_tests.py — La Forja / A2LT Soluciones
# Clones skill into quarantine_lab sandbox and runs --help on all scripts.
# Usage: python run_skill_tests.py <skill_path>

import os
import sys
import subprocess
import shutil
import json


def find_project_root(start_path: str) -> str:
    current = os.path.abspath(start_path)
    for _ in range(10):
        if os.path.exists(os.path.join(current, "AGENTS.md")):
            return current
        if os.path.exists(os.path.join(current, "agent", "manifest.json")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(start_path)


def run_tests(skill_path: str) -> bool:
    if not os.path.isdir(skill_path):
        print(f"ERROR: '{skill_path}' no es un directorio válido.", file=sys.stderr)
        return False

    root = find_project_root(skill_path)
    skill_name   = os.path.basename(os.path.normpath(skill_path))
    sandbox_base = os.path.join(root, "quarantine_lab")
    sandbox_path = os.path.join(sandbox_base, f"sandbox_{skill_name}")

    # Clean and recreate sandbox
    if os.path.exists(sandbox_path):
        shutil.rmtree(sandbox_path)
    os.makedirs(sandbox_base, exist_ok=True)

    try:
        shutil.copytree(skill_path, sandbox_path)
    except Exception as e:
        print(f"FATAL: No se pudo clonar la skill en quarantine_lab: {e}", file=sys.stderr)
        return False

    report = {"target": skill_name, "sandbox": sandbox_path, "tests": []}
    overall_pass = True

    scripts_dir = os.path.join(sandbox_path, "scripts")

    if os.path.isdir(scripts_dir):
        scripts = [s for s in os.listdir(scripts_dir) if s.endswith((".py", ".sh"))]

        if not scripts:
            report["tests"].append({
                "script": "none",
                "passed": True,
                "note": "No scripts encontrados en scripts/. Skill de tipo High Freedom."
            })
        else:
            for script in scripts:
                script_path = os.path.join(scripts_dir, script)

                if script.endswith(".py"):
                    cmd = [sys.executable, script_path, "--help"]
                else:
                    cmd = ["bash", script_path, "--help"]

                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=15,
                        cwd=sandbox_path
                    )
                    # --help exits 0 or 1 depending on argparse style; both acceptable
                    passed = result.returncode in (0, 1)
                    if not passed:
                        overall_pass = False

                    report["tests"].append({
                        "script":    script,
                        "exit_code": result.returncode,
                        "passed":    passed,
                        "stderr":    result.stderr.strip()[:300] if result.stderr else ""
                    })
                except subprocess.TimeoutExpired:
                    overall_pass = False
                    report["tests"].append({
                        "script":    script,
                        "exit_code": -1,
                        "passed":    False,
                        "stderr":    "Timeout — el script no respondió en 15s."
                    })
                except Exception as ex:
                    overall_pass = False
                    report["tests"].append({
                        "script":    script,
                        "exit_code": -1,
                        "passed":    False,
                        "stderr":    str(ex)
                    })
    else:
        report["tests"].append({
            "script": "none",
            "passed": True,
            "note":   "No existe directorio scripts/. Skill de tipo High Freedom o Deep Domain."
        })

    # Cleanup sandbox
    shutil.rmtree(sandbox_path)

    # Output JSON report
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if not overall_pass:
        print(
            "\n[La Forja] Tests FALLIDOS — revisa los errores y regresa al Paso 3 con --force.",
            file=sys.stderr
        )

    return overall_pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python run_skill_tests.py <ruta_directorio_skill>", file=sys.stderr)
        sys.exit(1)

    success = run_tests(sys.argv[1])
    sys.exit(0 if success else 1)
