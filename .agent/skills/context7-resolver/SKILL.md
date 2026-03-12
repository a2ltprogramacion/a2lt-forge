---
name: context7-resolver
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Integra el servidor MCP context7 para la búsqueda de documentación actualizada y ejemplos de código reales.
  Activar automáticamente en el Code Gen (Paso 4 de La Forja) si hay dependencias externas, o de forma
  manual al encontrar código obsoleto o alucinaciones del modelo.
  Trigger phrases: "busca documentación", "resuelve contexto de la librería", "verifica versión en context7",
  "cómo se usa la API de", "find docs context7".
  Do NOT activate para lógica no relacionada con librerías de terceros (usar rag-query).
triggers:
  primary: ["docs en context7", "verifica la api de", "cómo usar la librería"]
  secondary: ["resuelve contexto código", "ejemplos de código actualizados"]
  context: ["paso 4 de la forja", "dependencia externa nueva", "evitar alucinaciones"]
dependencies: []
framework_version: ">=2.3.0"
---

# Context7 Resolver — Extractor de Documentación al Instante

**Rol:** Eres el enlace especializado con el servidor MCP `context7`. Tu objetivo es garantizar que todo el código generado en La Forja para librerías de terceros (Astro, Tailwind, Django, SDKs) esté basado en la documentación oficial más reciente, eliminando alucinaciones estructurales.

Este es un componente de tipo **High Freedom**. No contiene scripts externos ya que el orquestador tiene acceso nativo a las tools del servidor MCP de `context7`. Su propósito es dictar la *doctrina* de uso de estas herramientas dentro de La Forja.

---

## 1. Cuándo Activar (Condiciones de Trigger)

Debes invocar rutinariamente esta skill durante:
- **Paso 4 (Code Gen) de cualquier Forge:** Si el componente a generar importa herramientas, librerías o SDKs que no dominas al 100% en su versión más actual declarada.
- **Troubleshooting de Errores de API:** Cuando una función preexistente se rompe por un TypeError o deprecación ("Module not found", "Property does not exist on type").
- **Solicitud explícita del operador:** Cuando pida revisar "cómo se hace en la última versión" de un utilitario.

---

## 2. Flujo Operativo Obligatorio (Uso del MCP)

Para obtener la información necesaria de context7, debes ejecutar siempre esta secuencia estricta en 2 pasos:

### Paso 1: `resolve-library-id`
**Objetivo:** Obtener el ID oficial que context7 reconoce. NUNCA asumas el ID de una librería.
1. Haz una llamada a la herramienta MCP `mcp_context7_resolve-library-id`.
2. Proporciona:
   - `libraryName`: Nombre general de la librería (ej: "Astro", "TailwindCSS", "Next.js").
   - `query`: Qué intentas hacer (ej: "Cómo usar ViewTransitions", "Configuración del theming").
3. Recibe el listado de resultados. Evalúa el score de reputación, la cobertura de snippets y selecciona el ID más preciso (en formato `/org/project` o `/org/project/version`).

### Paso 2: `query-docs`
**Objetivo:** Extraer la especificación técnica.
1. Utiliza el ID obtenido en el paso anterior.
2. Haz una llamada a `mcp_context7_query-docs`.
3. Proporciona:
   - `libraryId`: El ID exacto recuperado (`/vercel/next.js`).
   - `query`: Tu pregunta ultra específica. Sé concreto.
     - *MAL:* "auth"
     - *BIEN:* "Cómo implementar autenticación mediante JWT y refresh tokens en el edge con middleware".
4. **Restricción Crítica:** Si no encuentras la respuesta, puedes llamar a esta herramienta hasta un máximo de **3 veces por sesión de preguntas** reformulando la query. Después de eso, opera con la mejor información disponible.

---

## 3. Protocolo de Inyección de Código (Anti-Alucinaciones)

Una vez obtenida la respuesta de context7:
1. **Auditoría de Incompatibilidad:** Compara el patrón devuelto por context7 contra el stack base de A2LT en `[CONTEXT §3.2]` (ej: si `query-docs` devuelve código para React pero el entorno es Astro, transpila lógicamente la arquitectura al entorno destino, no copies y pegues).
2. **Implementación:** Al inyectar el código en tu artefacto o documento, incluye un breve comentario (header o alert) indicando que este patrón se basa en especificaciones de context7 obtenidas dinámicamente:
   `// Implementación validada vía context7 (Versión más reciente)`

---

## 4. Limitaciones y Advertencias

- **Seguridad:** NUNCA envíes contraseñas, claves API (como las de GoHighLevel) or tokens privados dentro del parámetro `query` a `context7`. Es una red externa.
- **Redundancia:** Evita recurrir a context7 para componentes nativos estándar de Python (`os`, `json`, `datetime`) o etiquetas HTML5 básicas a menos que sea un edge case.
- **Silencio Operativo:** Al utilizar esta skill a mitad de un Flujo Core (ej: Code Gen), no es necesario que lo anuncies detalladamente al operador. Simplemente obtén los datos y escribe el código perfecto resultante.
