import sys
import os
import json

# Agregar los directorios necesarios al path
base_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(os.path.join(base_dir, 'scripts'))
sys.path.append(os.path.join(base_dir, 'scripts', 'core'))

from core.client import GHLClient

def validate_structure():
    print("--- Validación de Estructura de Master Skill ---")
    files_to_check = [
        "SKILL.md",
        "scripts/main.py",
        "scripts/core/client.py",
        "scripts/modules/contacts.py",
        "scripts/modules/opportunities.py",
        "scripts/modules/calendars.py",
        "scripts/modules/conversations.py",
        "scripts/modules/custom_objects.py"
    ]
    
    for f in files_to_check:
        path = os.path.join("y:/Proyectos IA/a2lt-forge/quarantine_lab/ghl-master-skill", f)
        if os.path.exists(path):
            print(f"[OK] {f}")
        else:
            print(f"[ERROR] No se encuentra {f}")

if __name__ == "__main__":
    validate_structure()
