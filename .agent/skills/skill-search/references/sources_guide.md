# Sources Guide — skill-search
# Load when navigating a specific source repository for the first time in a session.

## Fuente 1 — skills.sh (npx skills registry)

**URL:** https://skills.sh  
**CLI:** `npx skills find [query]`

### Comandos útiles

```bash
# Buscar por término
npx skills find [query]

# Ver detalle de una skill específica
npx skills info <owner/repo@skill-name>

# Clonar a cuarentena (SIEMPRE con --cwd apuntando a quarantine_lab)
npx skills add <owner/repo@skill-name> --cwd ./quarantine_lab/[id]/referencias/ -y
```

### Cómo leer los resultados
- El resultado muestra: `owner/repo@skill-name — description`
- El `@skill-name` es el identificador exacto para el comando `add`
- Prioriza skills con más estrellas o downloads si se muestra esa métrica

---

## Fuente 2 — sickn33/antigravity-awesome-skills

**URL:** https://github.com/sickn33/antigravity-awesome-skills  
**Tipo:** Colección curada de skills para Antigravity

### Estructura del repositorio
```
antigravity-awesome-skills/
├── README.md          ← índice con descripciones de cada skill
└── skills/
    └── [nombre]/
        ├── SKILL.md
        └── scripts/   (si aplica)
```

### Estrategia de navegación
1. Leer `README.md` primero — contiene el índice completo con descripciones breves
2. Si el README menciona algo relevante, navegar al subdirectorio específico
3. Clonar completo solo si hay múltiples candidatos a evaluar:
   ```bash
   git clone https://github.com/sickn33/antigravity-awesome-skills.git \
     ./quarantine_lab/[id]/referencias/awesome-skills --depth 1
   ```

### Fortalezas de esta fuente
- Skills diseñadas específicamente para el ecosistema Antigravity
- Alta probabilidad de compatibilidad estructural con La Forja
- Mantiene convenciones de frontmatter similares a las nuestras

---

## Fuente 3 — vudovn/antigravity-kit

**URL:** https://github.com/vudovn/antigravity-kit  
**Tipo:** Kit de herramientas y skills para Antigravity

### Estructura del repositorio
```
antigravity-kit/
├── README.md
├── skills/
│   └── [nombre]/
│       └── SKILL.md
└── workflows/         (si aplica)
```

### Estrategia de navegación
1. Revisar `README.md` para catálogo
2. Comparar con lo encontrado en Fuentes 1 y 2 — buscar diferencias de enfoque
3. Clonar solo si Fuentes 1 y 2 no cubrieron el requerimiento:
   ```bash
   git clone https://github.com/vudovn/antigravity-kit.git \
     ./quarantine_lab/[id]/referencias/antigravity-kit --depth 1
   ```

### Fortalezas de esta fuente
- Puede tener enfoques alternativos para problemas comunes
- Útil como segunda opinión cuando Fuente 2 tiene solo una implementación

---

## Notas Generales de Absorción

### Qué buscar en cualquier SKILL.md externo
1. **Frontmatter description** — cómo activan la skill (buenas frases de trigger)
2. **Pasos del workflow** — qué lógica secuencial usan
3. **Scripts en `scripts/`** — lógica determinista que resuelve algo específico
4. **Referencias** — qué documentación externa consultan
5. **Ejemplos** — casos de uso concretos que revelan el alcance real

### Señales de alta calidad
- Workflow de más de 3 pasos con criterios de salida explícitos
- Scripts con manejo de errores y exit codes documentados
- Descripción con frases negativas explícitas ("Do NOT activate when...")

### Señales de baja calidad (descartar)
- SKILL.md de menos de 30 líneas sin scripts
- Sin frontmatter o frontmatter incompleto
- Último commit hace más de 18 meses
- Solo contiene instrucciones en texto libre sin estructura
