import asyncio
import json
import os
import subprocess
from typing import Dict, Any, Union, List

# Configuracion de prueba
LOCATION_ID = "Taooh0nQJLaaDDxbtG0L"
COMPANY_ID = "Taooh0nQJLaaDDxbtG0L" # Usaremos el mismo como fallback, pero sabemos que dar 422 si la API es estricta

async def run_skill(module: str, action: str, params: Dict[str, Any]) -> Any:
    cmd = [
        "python", "scripts/main.py",
        "--module", module,
        "--action", action,
        "--params", json.dumps(params)
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    stdout, stderr = await process.communicate()
    
    stdout_str = stdout.decode(errors='ignore').strip()
    stderr_str = stderr.decode(errors='ignore').strip()
    
    if stderr_str:
        print(f"Stderr en {module}/{action}: {stderr_str}")
    
    if not stdout_str:
        return {"error": "Empty output", "stderr": stderr_str}
        
    try:
        return json.loads(stdout_str)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response", "output": stdout_str, "stderr": stderr_str}

async def main():
    print("Iniciando Pruebas de Conexion GHL Master Skill...")
    
    tests = [
        ("contacts", "search_contacts", {"location_id": LOCATION_ID, "page_limit": 1}),
        ("opportunities", "list_opportunities", {"location_id": LOCATION_ID}),
        ("payments", "list_invoices", {"alt_id": LOCATION_ID}),
        ("ai", "list_ai_agents", {"location_id": LOCATION_ID}),
        ("social", "list_social_accounts", {"location_id": LOCATION_ID}),
        ("content", "list_funnels", {"location_id": LOCATION_ID}),
        ("system", "list_users", {"company_id": COMPANY_ID}), 
        ("saas", "list_snapshots", {"company_id": COMPANY_ID}),
    ]

    results = {}
    for module, action, params in tests:
        print(f"Testing {module}/{action}...")
        res = await run_skill(module, action, params)
        
        # Validacin
        if res is None:
            status = "FAILED (None)"
        elif isinstance(res, dict) and "error" in res:
            status = "FAILED"
        else:
            status = "OK"
            
        results[f"{module}/{action}"] = {"status": status, "resp": res}
        print(f"Result: {status}")

    print("\n--- RESUMEN DE PRUEBAS ---")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
