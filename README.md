# La Forja — Ecosistema de Agentes y Skills de IA para A2LT Soluciones

> **Sistema:** A2LT Soluciones | **Operador:** Argenis | **Versión:** 2.3.0

---

## 🎯 ¿Qué es La Forja?

La Forja es el **entorno de desarrollo modular para agentes y skills de IA** que potencia las soluciones de A2LT Soluciones. Transforma requisitos en componentes reutilizables, validados y escalables.

**Tres pilares:**
- 🔧 **Core (./.agent/)** — Infraestructura interna: herramientas para orquestar la forja
- 📦 **Catálogo (./catalogo/)** — Componentes productivos listos para reutilizar
- 🚀 **Empaquetado (./output/)** — Distribución a proyectos cliente

---

## 📚 Documentación Principal

| Documento | Propósito | Público |
|---|---|---|
| **[GEMINI.md](GEMINI.md)** | **Especificación completa.** Sistema operativo, estándares, flujos, reglas. Fuente de verdad. | Arquitecta, Operador |
| [CHANGELOG.md](CHANGELOG.md) | Historial de versiones y cambios | Arquitecta, Operador |
| `.agent/manifest.json` | Registro de herramientas internas (Core) | Sistema (lectura/escritura en despliegues) |
| `catalogo/manifest.json` | Registro de componentes productivos | Sistema |

---

## 🚀 Inicio Rápido

### 1. Entender la arquitectura (5 min)

Lee **§0 (MAPA)** y **§1 (ROL)** de [GEMINI.md](GEMINI.md) para entender:
- Dónde va cada cosa (estructura de directorios)
- Cómo funciona La Forja (flujos operativos)
- Qué se espera de ti como operador

### 2. Explorar componentes de ejemplo (10 min)

Ya hay 2 componentes en `./.agent/`:

**Skill: `yaml-validator`**
```bash
# Validar un archivo YAML
python .agent/skills/yaml-validator/scripts/yaml_validator.py \
  --filepath "./Modelos\ AGENTS/AGENTS\ \(Gemini\).txt" \
  --strict-mode
```

**Agente: `component-auditor`**
```bash
# Ver instrucciones del agente
cat .agent/agents/component-auditor/AGENT.md
```

### 3. Crear tu primer componente (30 min)

Sigue el flujo completo en **§7.2 (Forjar Skills)** o **§7.3 (Forjar Agentes)**.

Resumen:
1. Define qué quieres construir (Paso 0: Verificación en Catálogo)
2. Investiga referencias externas (Paso 1: Investigación)
3. Diseña con brainstorming (Paso 2: Ideación)
4. Construye (Paso 3: Construcción)
5. Revisa con modelo externo (Paso 4: Consulta Externa)
6. Integra feedback (Paso 5: Síntesis)
7. Valida (Paso 6: Auditoría de Valor)
8. Despliega (Paso 7: Validación Pre-Despliegue)

---

## 📋 Estructura de Directorios

```
La_Forja/
├── .agent/                    ← Core: infraestructura interna
│   ├── agents/               ← Agentes internos (ej: component-auditor)
│   ├── skills/               ← Skills internas (ej: yaml-validator)
│   └── manifest.json         ← Fuente de verdad del Core
│
├── catalogo/                 ← Catálogo: componentes de producción
│   ├── agentes/
│   ├── skills/
│   └── manifest.json
│
├── output/                   ← Paquetes empaquetados para clientes
│   └── [proyecto]/
│       ├── .agent/           ← Componentes copiados del catálogo
│       ├── GEMINI.md         ← Instrucciones del paquete
│       └── requirements.txt
│
├── quarantine_lab/           ← Área de cuarentena temporal (se limpia)
│
├── rag/                      ← RAG: infraestructura de búsqueda local
│   ├── index/                ← ChromaDB embeddings (generado)
│   ├── sources/              ← Documentos indexables
│   └── config.yaml           ← Configuración RAG
│
├── GEMINI.md                 ← Este archivo: especificación maestra
├── CHANGELOG.md
├── .gitignore
└── README.md                 ← Estás aquí
```

---

## 🔑 Conceptos Clave

### Flows (Flujos)

| Flujo | Qué pasa | Paso a paso |
|---|---|---|
| **Forjar Skill** | Crear skill nueva o mejorar existente | `[GEMINI.md §7.2]` |
| **Forjar Agente** | Diseñar agente nuevo o actualizar existente | `[GEMINI.md §7.3]` |
| **Empaquetar Proyecto** | Exportar componentes a `./output/` para cliente | `[GEMINI.md §7.4]` |

### Componentes

**Skill:** Herramienta específica. Ejecuta tarea puntual.
- Validar, transformar, integrar, buscar
- Tiene script + documentación YAML
- Ejemplo: `yaml-validator`

**Agente:** Orquestador inteligente. Coordina skills, toma decisiones.
- Con "identidad" y "misión" explícitas
- Usa límites de responsabilidad claros
- Depende de skills
- Ejemplo: `component-auditor`

### Manifiestos

`./.agent/manifest.json` y `./catalogo/manifest.json` son **fuentes de verdad**.
Registran qué componentes existen, sus versiones, dependencias.

---

## ⚙️ Reglas Operativas (CRÍTICAS)

Leer completo: **§4 (RULES)** de [GEMINI.md](GEMINI.md)

**Resumen:**
- ✅ Todo código debe ser **completo y funcional** (no fragmentos)
- ✅ **Presión quirúrgica:** no refactorices fuera del scope solicitado
- ✅ **Especificidad:** cada componente es específico a A2LT, no genérico
- ✅ **No orquestación con modelo base** si existe skill del Core para eso
- ✅ **Cuestionamiento estratégico:** si ves riesgo, pausas y notificas

---

## 🛡️ Auditoría y Validación

Todo componente antes de despliegue pasa por:

1. **Estructura:** ¿Directorio = nombre? ¿SKILL.md o AGENT.md presente?
2. **YAML:** ¿Frontmatter válido contra esquema?
3. **Dependencias:** ¿Todas existen? ¿Sin ciclos?
4. **Stack:** ¿Compatible con Python 3.10+, Django 4.2+, etc.?

Herramienta: `component-auditor` (agente)

```bash
# Auditar un componente
python scripts/audit.py --component "./catalogo/skills/ejemplo/"
```

---

## 📦 Ejemplo: Crear y Desplegar una Skill

### Escenario
Necesitas una skill que **valide correos electrónicos contra un whitelist**.

### Ejecución (30 minutos)

```
Paso 0: Verificación en Catálogo
  → ¿Existe algo similar? No. Continúa.

Paso 1: Investigación (skill-search)
  → Busca en GitHub: "email validation python"
  → 3 candidatos encontrados

Paso 2: Ideación (brainstorming)
  → Propuesta: usar regex + API de verificación Kickbox (opcional)

Paso 3: Construcción (skill-creator-pro)
  → Genera SKILL.md + script completo + tests

Paso 4: Consulta Externa
  → Envia SKILL.md a Claude/DeepSeek para validar seguridad

Paso 5: Síntesis
  → Integra feedback (agregar rate-limiting)

Paso 6: Auditoría de Valor
  → Tests demuestran 98% accuracy en email detection

Paso 7: Despliegue
  → Validación → Backup → Deploy a ./catalogo/skills/email-validator/
  → Actualizar manifest → Indexar en RAG
  → ✅ LISTO
```

---

## 🤝 Decisiones y Escalamiento

Si encuentras:
- ❓ **Ambigüedad técnica** → Pregunta antes de ejecutar
- ⚠️ **Riesgo crítico** → Pausa con formato `[ALTO]` (§2.4 GEMINI.md)
- 📈 **Decisión de negocio** → Escala al operador

Formato requerido para escalamiento:
```
[ALTO] <Tipo de riesgo>
• Problema:      <descripción precisa>
• Impacto:       <consequence si se ignora>
• Opciones:      (a) solución 1  (b) solución 2  (c) escalar
• Recomendación: <tu sugerencia fundamentada>
```

---

## 🔄 Flujo de Trabajo Típico del Operador

```
1. Define requisito → envía al Forja
2. Arquitecta busca si existe en catálogo
   SÍ → usa directamente
   NO → inicia flujo de forja
3. Arquitecta ejecuta Pasos 0-7
4. Al completar Paso 7:
   - Backup en quarantine_lab/
   - Deploy a .agent/ o ./catalogo/
   - Manifest actualizado
   - RAG re-indexado
   - quarantine_lab/ limpiado
5. Operador integra en proyecto cliente
```

---

## 📖 Lectura Recomendada por Rol

### 👩‍💻 Arquitecta (Tú)
1. **[GEMINI.md](GEMINI.md)** — Especificación completa
2. **§7 (DYNAMICS)** — Flujos paso a paso
3. **§3 (CONTEXT)** — Stack y modelado
4. **§4 (RULES)** — Restricciones operativas

### 👔 Operador (Argenis)
1. **§0 (MAPA)** — Estructura
2. **§1 (ROL)** — Postura y límites
3. **§7 (DYNAMICS)** — Qué esperar en cada flujo
4. **[CHANGELOG.md](CHANGELOG.md)** — Qué es nuevo

### 🔧 Desarrollador (Consumidor)
1. **README.md** en cada skill/agente
2. **SKILL.md** o **AGENT.md** para interfaz
3. **examples/** para casos de uso
4. **§3.4 (Metadatos)** para understanding triggers

---

## 🆘 Troubleshooting

### "El manifest dice que existe X, pero no lo encuentro"
→ Directorio `.agent/skills/X/` debe existir. Si no: rebuild o reindexar RAG.

### "La validación YAML falla pero el YAML se ve bien"
→ Chequea: ¿frontmatter entre `---`? ¿Indentación con espacios, no tabs?

### "Un componente depende de otro que aún no existe"
→ Pausa. Ese es un bloqueador. Ver **§8.5 (Política de Fallback)**.

---

## 📧 Soporte

Reportar issues o propuestas:
1. Describir problema + contexto
2. Incluir error/output completo
3. Citar sección de GEMINI.md si aplica
4. Sugerir solución si la tienes

---

## 📜 Licencia y Propiedad

La Forja es infraestructura interna de **A2LT Soluciones**.
Todos los componentes creados son propiedad de A2LT.

---

**Versión:** 2.3.0 | **Última actualización:** 11 de marzo de 2026
