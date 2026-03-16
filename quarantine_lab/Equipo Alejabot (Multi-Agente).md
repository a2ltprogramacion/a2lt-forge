\# Skill: Equipo Alejabot (Multi-Agente)

Esta habilidad permite a Antigravity coordinar un equipo de agentes inteligentes trabajando en paralelo sobre el mismo proyecto, replicando la funcionalidad de "Agent Teams" de Claude Code.

\#\# Configuración del Entorno  
El equipo utiliza una carpeta oculta en la raíz del proyecto para comunicarse:  
\- \`.antigravity/team/tasks.json\` \-\> Lista maestra de tareas, estados y dependencias.  
\- \`.antigravity/team/mailbox/\` \-\> Mensajes individuales (.msg).  
\- \`.antigravity/team/broadcast.msg\` \-\> Mensajes globales para todo el equipo.  
\- \`.antigravity/team/locks/\` \-\> Semáforos para evitar edición simultánea de archivos.

\#\# Roles del Equipo  
1\. \*\*Director (Alejabot)\*\*: El líder. Divide el problema, asigna roles y aprueba planes.  
2\. \*\*Arquitecto\*\*: Define la estructura y patrones antes de codificar.  
3\. \*\*Especialista (Frontend/Backend/DB)\*\*: Ejecuta tareas técnicas específicas.  
4\. \*\*Marketer\*\*: Creación de marca, logos, copywriting y diseño de landing pages.  
5\. \*\*Investigador\*\*: Búsqueda de información, documentación y análisis de mercado.  
6\. \*\*Revisor (Devil's Advocate)\*\*: Busca fallos, bugs y problemas de seguridad.

\#\# Protocolo de Orquestación Avanzada

\#\#\# 1\. Modo de Planificación (Gatekeeping)  
Antes de realizar cambios significativos, cada agente debe enviar un \*\*Plan de Acción\*\* al buzón de Alejabot.  
\- El agente se mantiene en modo \`READ\_ONLY\` o \`PLANNING\` hasta que Alejabot responda con un mensaje de \`APPROVED\`.

\#\#\# 2\. Mensajería y Difusión (Broadcast)  
\- \*\*Mensaje Directo\*\*: Coordinación 1 a 1 entre especialistas.  
\- \*\*Broadcast\*\*: Alejabot puede escribir en \`broadcast.msg\` para dar nuevas directrices a todo el equipo simultáneamente.

\#\#\# 3\. Sincronización de Tareas y Dependencias  
\- Las tareas en \`tasks.json\` pueden tener una lista de \`dependencies\`. Una IA no debe reclamar una tarea si sus dependencias no están en estado \`COMPLETED\`.

\#\# Reglas Críticas  
\- NUNCA editar un archivo si existe un .lock activo en \`.antigravity/team/locks/\`.  
\- Al completar una tarea, el agente debe liberar sus "locks" y notificar a Alejabot.  
\`\`\`

\---

\#\# 3\. Script de Orquestación (team\_manager.py)  
\*Este script automatiza la gestión de las tareas y la comunicación. Guárdalo como \`team\_manager.py\`.\*

\`\`\`python  
import json  
import os  
import sys

TEAM\_DIR \= ".antigravity/team"

def init\_team():  
    """Inicializa la infraestructura del equipo."""  
    os.makedirs(f"{TEAM\_DIR}/mailbox", exist\_ok=True)  
    os.makedirs(f"{TEAM\_DIR}/locks", exist\_ok=True)  
    tasks\_path \= f"{TEAM\_DIR}/tasks.json"  
    if not os.path.exists(tasks\_path):  
        with open(tasks\_path, 'w') as f:  
            json.dump({"tasks": \[\], "members": \[\]}, f, indent=2)  
    if not os.path.exists(f"{TEAM\_DIR}/broadcast.msg"):  
        with open(f"{TEAM\_DIR}/broadcast.msg", 'w') as f: f.write("")  
    print("✓ Infraestructura 'Equipo Alejabot' lista.")

def assign\_task(title, assigned\_to, deps=\[\]):  
    """Asigna una nueva tarea con soporte para dependencias."""  
    path \= f"{TEAM\_DIR}/tasks.json"  
    with open(path, 'r+') as f:  
        data \= json.load(f)  
        task \= {  
            "id": len(data\["tasks"\]) \+ 1,  
            "title": title,  
            "status": "PENDING",  
            "plan\_approved": False,  
            "assigned\_to": assigned\_to,  
            "dependencies": deps  
        }  
        data\["tasks"\].append(task)  
        f.seek(0)  
        json.dump(data, f, indent=2)  
    print(f"✓ Tarea {task\['id'\]} ({title}) asignada a {assigned\_to}.")

def broadcast(sender, text):  
    """Envía un mensaje a todos los miembros del equipo."""  
    msg \= {"de": sender, "tipo": "BROADCAST", "mensaje": text}  
    with open(f"{TEAM\_DIR}/broadcast.msg", 'a') as f:  
        f.write(json.dumps(msg) \+ "\\n")  
    print(f"✓ Mensaje global enviado por {sender}.")

def send\_message(sender, receiver, text):  
    """Envía un mensaje al buzón de un agente específico."""  
    msg \= {"de": sender, "mensaje": text}  
    with open(f"{TEAM\_DIR}/mailbox/{receiver}.msg", 'a') as f:  
        f.write(json.dumps(msg) \+ "\\n")  
    print(f"✓ Mensaje enviado a {receiver}.")

if \_\_name\_\_ \== "\_\_main\_\_":  
    if len(sys.argv) \> 1:  
        cmd \= sys.argv\[1\]  
        if cmd \== "init": init\_team()  
\`\`\`

\---

\#\# 4\. Cómo usarlo  
1\. \*\*Activa el Líder\*\*: Pídele a Antigravity: \*"Usa la habilidad Equipo Alejabot para inicializar este proyecto"\*.  
2\. \*\*Reparte el trabajo\*\*: \*\*Alejabot\*\* dividirá el trabajo. Abre terminales nuevas para cada agente (Frontend, Marketer, etc.).  
3\. \*\*Flujo de Planificación\*\*: Los agentes envían sus planes a Alejabot antes de empezar. Un equipo bien coordinado es imparable.

\---  
\*Creado para la comunidad de Alejavi por academIArtificial.\*  
