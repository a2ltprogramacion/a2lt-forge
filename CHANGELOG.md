# CHANGELOG — La Forja

Todos los cambios notables en este proyecto serán documentados aquí.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)
y este proyecto adhiere a [Semantic Versioning](https://semver.org/es/).

## [Unreleased] — En desarrollo

### Planeado
- Implementación del Core Toolkit mínimo (skill-search, validator)
- Ejemplos funcionales de skills y agentes
- Integración RAG con ChromaDB
- Dashboard de validación

---

## [2.4.0] — 2026-03-11

### Agregado
- **Mecanismos Duros (Hard Locks):** Implementación de barreras operativas estrictas para el Orquestador (evitar asunciones de diseño y despliegues fallidos).
- **Autoridad de Rutas (§0.4):** Regla de desempate vinculante y prohibición absoluta de la ruta legacy `./.agent/`.
- **Nuevo Schema de Manifest (v2.0.0):** Soporte para anidación de dependencias (`internal` / `external`) y estricta obligatoriedad de campos.

### Modificado
- `manifest_updater.py`: Lógica ajustada para soportar Schema v2.0.0, validaciones de ruta legacy y rechazo de asunciones en campos obligatorios.
- Reglas de escalamiento y auditoría reformateadas para mayor claridad estructural (tablas y listas).
- Tablas de integración RAG y eventos de indexación.

### Solucionado
- Subversión del protocolo de parada (Stop-Loss) durante despliegues con validación fallida.
- Falsas priorizaciones de velocidad sobre integridad arquitectónica en flujos de Forja.

---

## [2.3.0] — 2026-03-11

### Agregado
- GEMINI.md: especificación completa del ecosistema La Forja
- Estructura de directorios canónica (§0.1)
- Manifiestos iniciales para Core y Catálogo
- Configuración base de RAG (§9)
- Estándares de output y validación (§5)
- Gestión de dependencias y resolución (§8)

### Definido
- 3 flujos operativos: Forjar Core, Forjar Catálogo, Empaquetar Proyectos (§2, §7)
- Stack tecnológico base (§3.2)
- Reglas de comportamiento estricto (§4)
- Protocolo de escalamiento y auditoría (§1.5, §2.4)

### Notas
- Versión 2.3.0 marca la congelación de especificación arquitectónica
- Infraestructura física en construcción (v2.3.x)
- No hay versión en producción aún; todo componente es candidato

---

## [2.2.0] — 2026-02-28 (Draft)

### Cambio
- Revisión de ciclos operativos y dinámicas
- Refinamiento de límites de responsabilidad por componente

---

## [2.1.0] — 2026-02-15 (Concepto)

### Cambio
- Definición inicial de stack y módelo de negocios

---

## [2.0.0] — 2026-01-30 (Revisión completa)

### Cambio
- Migración a arquitectura modular por capas (Core → Catálogo → Empaquetado)
- Introducción de quarantine_lab para validación pre-despliegue
- Redefinición de SOPs y protocolos

---

## [1.x.x] — Pre-producción (Consultar historial Git)

Primeras iteraciones del framework. Archivado.
