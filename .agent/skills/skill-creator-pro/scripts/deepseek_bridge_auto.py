#!/usr/bin/env python3
# deepseek_bridge_auto.py — La Forja / A2LT Soluciones
# Delegates dense code generation to a local LM Studio instance (DeepSeek or equivalent).
# Reads deepseek_payload.md from quarantine_lab/, writes deepseek_response.md.
# Usage: python deepseek_bridge_auto.py [--quarantine-id <id>]

import requests
import json
import os
import re
import sys
import argparse

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore


# ---------------------------------------------------------------------------
# Project root and .env discovery
# ---------------------------------------------------------------------------

def find_project_root(start_path: str) -> str:
    """Walk up until we find AGENTS.md or agent/manifest.json."""
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


def load_env():
    """Load .env from project root. Auto-generates template if missing."""
    root = find_project_root(os.getcwd())
    env_path = os.path.join(root, ".env")

    if not os.path.exists(env_path):
        template = (
            "# La Forja — Environment Variables\n"
            "LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1\n"
            "LM_STUDIO_MODEL_ID=deepseek-coder-v2-lite-instruct\n"
        )
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(template)
        print(
            f"[BRIDGE] .env no encontrado. Template generado en: {env_path}\n"
            "         Completa LM_STUDIO_BASE_URL y LM_STUDIO_MODEL_ID antes de continuar.",
            file=sys.stderr
        )
        sys.exit(1)

    if load_dotenv:
        load_dotenv(env_path)
    else:
        # Manual fallback if python-dotenv not installed
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

    return root


# ---------------------------------------------------------------------------
# Payload chunker
# ---------------------------------------------------------------------------

def parse_payload(payload_content: str) -> list[tuple[str, str]]:
    """
    Splits payload by --- file: path --- delimiters.
    If no delimiters found, treats entire content as a single chunk.
    """
    file_chunks = re.split(r'--- file: (.*?) ---', payload_content)

    if len(file_chunks) <= 1:
        return [("full_payload.md", payload_content)]

    chunks = []
    global_context = file_chunks[0]

    for i in range(1, len(file_chunks), 2):
        file_path = file_chunks[i].strip()
        # Stop at next delimiter marker
        file_body = file_chunks[i + 1].split('---')[0]
        prompt = (
            f"{global_context}\n\n"
            f"### TASK: Generate complete, production-ready content for: {file_path}\n"
            f"{file_body}"
        )
        chunks.append((file_path, prompt))

    return chunks


# ---------------------------------------------------------------------------
# LM Studio API call
# ---------------------------------------------------------------------------

def call_lm_studio(prompt: str, base_url: str, model_id: str, max_tokens: int = 4096) -> str | None:
    payload = {
        "model": model_id,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a Senior Lead Developer. "
                    "Generate dense, functional, production-ready code. "
                    "No placeholders. No TODOs. No shortened logic. "
                    "High-density English only."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.ConnectionError:
        print(
            "[BRIDGE ERROR] No se puede conectar a LM Studio. "
            "Verifica que el servidor esté corriendo y que LM_STUDIO_BASE_URL sea correcto.",
            file=sys.stderr
        )
        return None
    except Exception as e:
        print(f"[BRIDGE ERROR] API call failed: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="La Forja Bridge — Delega generación densa a LM Studio (DeepSeek/local)."
    )
    parser.add_argument(
        "--quarantine-id",
        default=None,
        help="ID de sesión en quarantine_lab (ej: 20250311-143000_mi-skill). "
             "Si se omite, busca deepseek_payload.md directamente en ./quarantine_lab/."
    )
    args = parser.parse_args()

    root = load_env()
    base_url  = os.getenv("LM_STUDIO_BASE_URL",  "http://127.0.0.1:1234/v1")
    model_id  = os.getenv("LM_STUDIO_MODEL_ID",  "deepseek-coder-v2-lite-instruct")
    max_tokens = int(os.getenv("BRIDGE_MAX_TOKENS", "4096"))

    quarantine_base = os.path.join(root, "quarantine_lab")

    if args.quarantine_id:
        quarantine_dir = os.path.join(quarantine_base, args.quarantine_id)
    else:
        quarantine_dir = quarantine_base

    payload_path  = os.path.join(quarantine_dir, "deepseek_payload.md")
    response_path = os.path.join(quarantine_dir, "deepseek_response.md")

    if not os.path.exists(payload_path):
        print(
            f"[BRIDGE ERROR] Payload no encontrado en: {payload_path}\n"
            "               Genera el payload en el Paso 3.5 del flujo de forja.",
            file=sys.stderr
        )
        sys.exit(1)

    with open(payload_path, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"[BRIDGE] Analizando payload para chunking atómico...")
    chunks = parse_payload(content)
    print(f"[BRIDGE] {len(chunks)} tarea(s) identificada(s).")

    full_response = ""

    for filename, prompt in chunks:
        print(f"[BRIDGE] Procesando: {filename}...")
        response = call_lm_studio(prompt, base_url, model_id, max_tokens)
        if response:
            full_response += f"\n--- file: {filename} ---\n{response}\n---\n"
            print(f"[BRIDGE] [OK] Respuesta recibida para: {filename}")
        else:
            print(f"[BRIDGE] [ERROR] Sin respuesta para: {filename}", file=sys.stderr)
            sys.exit(1)

    os.makedirs(quarantine_dir, exist_ok=True)
    with open(response_path, "w", encoding="utf-8") as f:
        f.write(full_response)

    print(f"\n[BRIDGE] Handoff completado. Respuesta guardada en: {response_path}")
    print("         Revisa, sanitiza a estándares La Forja y continúa con el Paso 3.5.")
    sys.exit(0)


if __name__ == "__main__":
    main()
