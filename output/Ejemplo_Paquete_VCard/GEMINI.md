# Paquete Ejemplo — VCard Minimalista

**Versión:** 1.0.0 | **Generado:** 2026-03-11 | **Compatible con:** La Forja v2.3.0+

---

## Propósito

Paquete de inicio rápido para crear un sitio VCard ligero. Incluye componentes mínimos para landing de presencia digital con formulario de contacto integrado con GoHighLevel.

**Casos de uso:**
- Freelancers (consultor, coach, fotógrafo)
- Pequeños negocios sin e-commerce aún
- Clínicas o servicios profesionales
- Portafolios personales

---

## Componentes Incluidos

| Nombre | Tipo | Versión | Descripción |
|---|---|---|---|
| `yaml-validator` | skill | 1.0.0 | Validación YAML para configuración del sitio |
| `component-auditor` | agent | 1.0.0 | Auditoría pre-despliegue de cambios |

**Total:** 2 componentes (1 skill + 1 agente)

---

## Instalación

### Requisitos previos
- Python 3.10+
- pip o poetry
- Acceso de escritura a directorio del proyecto

### Pasos de instalación

1. **Descomprimir paquete en raíz del proyecto:**
   ```bash
   cp -r .agent ./proyecto-destino/
   ```

2. **Instalar dependencias Python:**
   ```bash
   pip install -r requirements.txt
   # O con Poetry:
   poetry install
   ```

3. **Validar integración:**
   ```bash
   python .agent/skills/yaml-validator/scripts/yaml_validator.py --help
   ```

4. **Verificar disponibilidad de agentes:**
   ```bash
   # Consultar que component-auditor responde
   python .agent/agents/component-auditor/scripts/component_auditor.py --version
   ```

---

## Configuración

### Variables de entorno

Crear archivo `.env` en raíz con:

```env
# La Forja framework
FORJA_ENV=development  # development | staging | production
FORJA_LOG_LEVEL=INFO   # DEBUG | INFO | WARN | ERROR

# GoHighLevel (si se integra después)
GHL_API_KEY=<tu-api-key>
GHL_WORKSPACE_ID=<tu-workspace-id>
```

Referencia completa: `.env.example` dentro del paquete.

### Archivos de configuración

- `rag/config.yaml` — Configuración del índice RAG local (búsqueda)
- `catalogo/manifest.json` — Registro central de componentes disponibles

No modificar estos archivos directamente. Usar herramientas del Core.

---

## Dependencias Externas

| Paquete | Versión | Propósito |
|---|---|---|
| `pyyaml` | >=6.0 | Parsing YAML |
| `jsonschema` | >=4.17 | Validación contra esquema JSON |

**Instalación:**
```bash
pip install pyyaml>=6.0 jsonschema>=4.17
```

O directamente desde `requirements.txt` incluido.

---

## Notas de Integración

1. **Estructura de directorios:** Este paquete asume que el proyecto destino tiene una estructura similar a La Forja. Si tu proyecto usa otra estructura, adaptar las rutas en la configuración.

2. **Versionado:** Los componentes usan SemVer. Consultar CHANGELOG si hay breaking changes entre versiones.

3. **Dependencias transversales:** `yaml-validator` es dependencia de `component-auditor`. No remover ninguno.

4. **Primer uso:** Ejecutar `component-auditor` contra tu `.agent/` después de integrar para asegurar coherencia.

---

## Asunciones Documentadas

| ID | Asunción | Validación requerida |
|---|---|---|
| ASUNCIÓN-001 | Python 3.10+ disponible en servidor destino | Ejecutar `python --version` |
| ASUNCIÓN-002 | PyYAML y jsonschema pueden instalarse vía pip | Intentar instalación; si falla, proporcionar alternativas |
| ASUNCIÓN-003 | Proyecto destino tiene estructura `.agent/` disponible | Si no: copiar `.agent/` desde paquete |
| ASUNCIÓN-004 | No hay conflictos de nombres entre skills incluidas y las del destino | Ejecutar `component-auditor` como check |

---

## Notas de Compliance

**Regulaciones aplicables:** Ninguna para este paquete mínimo.

Si el proyecto destino incorpora más adelante manejo de datos personales (GDPR, LFPDPPP):
- Revisar documentación de privacidad en cada componente que agregues
- Usar componentes marcados con `tier: compliance` si es necesario

---

## Próximos pasos

Después de integrar este paquete:

1. Familiarizarse con GEMINI.md (este archivo) y AGENTS.md en el workspace
2. Explorar skills disponibles: `catalogo/skills/`
3. Crear primer componente personalizado usando `skill-creator-pro`
4. Registrarlo en `catalogo/manifest.json`

Documentación completa: consultar `./GEMINI.md` en la raíz.
