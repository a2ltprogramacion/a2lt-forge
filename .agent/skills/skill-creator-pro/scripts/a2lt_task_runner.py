#!/usr/bin/env python3
# a2lt_task_runner.py - Generador de telemetría simulada para evals
# Uso: python a2lt_task_runner.py --eval-set <ruta.json> --skill-path <ruta> --runs-per-query <int> --output-dir <directorio>

import argparse
import json
import sys
import os
import time
import random
from datetime import datetime

def generar_tokens_simulados(query, factor_aleatorio=True):
    """Simula conteo de tokens basado en la longitud de la consulta."""
    palabras = len(query.split())
    base = palabras * 2  # supuesto: cada palabra ~2 tokens
    if factor_aleatorio:
        base += random.randint(-5, 5)
    return max(1, base)

def ejecutar_simulacion(query, run_id):
    """Simula una ejecución de skill y devuelve métricas."""
    inicio = time.perf_counter()
    # Simular latencia de procesamiento (entre 0.1 y 0.8 segundos)
    time.sleep(random.uniform(0.1, 0.8))
    fin = time.perf_counter()
    duracion = fin - inicio

    # Generar tokens simulados
    prompt_tokens = generar_tokens_simulados(query)
    completion_tokens = random.randint(10, 50)
    total_tokens = prompt_tokens + completion_tokens

    return {
        "query": query,
        "run_id": run_id,
        "duration_seconds": duracion,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def main():
    parser = argparse.ArgumentParser(description="Lanza ejecuciones simuladas de una skill para telemetría.")
    parser.add_argument("--eval-set", required=True, help="Ruta al archivo JSON con el conjunto de evaluaciones.")
    parser.add_argument("--skill-path", required=True, help="Ruta a la skill (no utilizada en simulación pura, pero se valida existencia).")
    parser.add_argument("--runs-per-query", type=int, required=True, help="Número de ejecuciones por cada consulta.")
    parser.add_argument("--output-dir", required=True, help="Directorio donde se guardarán los logs generados.")
    args = parser.parse_args()

    # Validar existencia del archivo de evals
    if not os.path.isfile(args.eval_set):
        print(f"ERROR: No se encuentra el archivo de evals: {args.eval_set}", file=sys.stderr)
        sys.exit(1)

    # Validar que skill-path exista (aunque no se use activamente, se requiere por especificación)
    if not os.path.exists(args.skill_path):
        print(f"ERROR: La ruta de skill no existe: {args.skill_path}", file=sys.stderr)
        sys.exit(1)

    if args.runs_per_query <= 0:
        print("ERROR: runs-per-query debe ser un entero positivo.", file=sys.stderr)
        sys.exit(1)

    # Crear directorio de salida si no existe
    os.makedirs(args.output_dir, exist_ok=True)

    # Leer conjunto de evals
    try:
        with open(args.eval_set, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: No se pudo leer el archivo de evals: {e}", file=sys.stderr)
        sys.exit(1)

    # Se espera que el JSON contenga una clave "evals" con una lista de objetos que tengan al menos "query"
    if not isinstance(data, dict) or "evals" not in data or not isinstance(data["evals"], list):
        print("ERROR: El archivo de evals debe ser un objeto con una clave 'evals' que contenga una lista.", file=sys.stderr)
        sys.exit(1)

    queries = [item.get("query") for item in data["evals"] if isinstance(item, dict) and "query" in item]
    if not queries:
        print("ERROR: No se encontraron consultas válidas en el archivo de evals.", file=sys.stderr)
        sys.exit(1)

    # Nombre del archivo de log con timestamp
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"run_{timestamp_str}.log"
    log_path = os.path.join(args.output_dir, log_filename)

    try:
        run_counter = 0
        with open(log_path, "w", encoding="utf-8") as log_file:
            for query in queries:
                for run in range(1, int(args.runs_per_query) + 1):
                    run_counter += 1  # type: ignore
                    metricas = ejecutar_simulacion(query, run_counter)
                    log_file.write(json.dumps(metricas) + "\n")
                    log_file.flush()  # asegurar escritura inmediata
    except Exception as e:
        print(f"ERROR durante la generación de logs: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Ejecución completada. {run_counter} registros escritos en {log_path}")
    sys.exit(0)

if __name__ == "__main__":
    main()
