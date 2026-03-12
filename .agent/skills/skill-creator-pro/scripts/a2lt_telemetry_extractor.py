#!/usr/bin/env python3

# a2lt_telemetry_extractor.py - Agrega telemetría desde logs y genera timing.json

# Uso: python a2lt_telemetry_extractor.py --output-dir <directorio>

import argparse
import json
import sys
import os
import glob
from datetime import datetime

def procesar_archivos_log(directorio):
    """Lee todos los archivos .log del directorio y agrega métricas."""
    patron = os.path.join(directorio, "*.log")
    archivos = glob.glob(patron)

    total_duration = 0.0
    total_tokens = 0
    ejecuciones = 0
    archivos_procesados = 0

    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    try:
                        dato = json.loads(linea)
                        duracion = dato.get("duration_seconds", 0.0)
                        tokens = dato.get("total_tokens", 0)
                        total_duration += duracion
                        total_tokens += tokens
                        ejecuciones += 1
                    except json.JSONDecodeError:
                        # Ignorar líneas corruptas, pero contar error
                        print(f"Advertencia: línea JSON inválida en {archivo}", file=sys.stderr)
            archivos_procesados += 1
        except Exception as e:
            print(f"Error al leer {archivo}: {e}", file=sys.stderr)
            # Continuamos con otros archivos

    return {
        "total_duration_seconds": total_duration,
        "total_tokens": total_tokens,
        "total_ejecuciones": ejecuciones,
        "archivos_procesados": archivos_procesados,
        "fecha_procesamiento": datetime.utcnow().isoformat() + "Z"
    }

def main():
    parser = argparse.ArgumentParser(description="Extrae telemetría de logs y genera un resumen timing.json.")
    parser.add_argument("--output-dir", required=True, help="Directorio donde se encuentran los logs y donde se guardará timing.json.")
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        print(f"ERROR: El directorio {args.output_dir} no existe.", file=sys.stderr)
        sys.exit(1)

    resumen = procesar_archivos_log(args.output_dir)

    # Ruta de salida
    timing_path = os.path.join(args.output_dir, "timing.json")

    try:
        with open(timing_path, "w", encoding="utf-8") as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)
        print(f"Resumen guardado en {timing_path}")
    except Exception as e:
        print(f"ERROR al escribir timing.json: {e}", file=sys.stderr)
        sys.exit(1)

    if resumen["total_ejecuciones"] == 0:
        print("Advertencia: No se encontraron ejecuciones en los logs.", file=sys.stderr)
        # No es un error fatal, pero se notifica

    sys.exit(0)

if __name__ == "__main__":
    main()
