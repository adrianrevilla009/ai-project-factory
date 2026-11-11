---
name: skill-name
description: Una frase corta y precisa: cuándo cargar este skill (qué tarea lo activa).
metadata:
  block: "00-example"
  tier: T1            # T1 núcleo · T2 módulo · T3 referencia
  owner: "equipo/persona responsable"
  last_reviewed: "YYYY-MM-DD"
  enforcement: "policy | hook | reviewer | human"   # mínimo uno; ver sección Enforcement
---

# Título del skill

## Cuándo aplicar y cuándo no
- Aplica cuando…
- No aplica cuando…

## Reglas
- **MUST** …
- **SHOULD** …
- **MUST NOT** …

## Por qué
Razonamiento detrás de cada regla, para poder discutirla.

## Ejemplos
### Mal
```java
// código real que viola la regla
```
### Bien
```java
// código real que la cumple
```

## Criterios de decisión y trampas
### Cómo decidir
- Cuándo elegir una opción frente a otra y con qué criterio medible.
### Trampas frecuentes
- Los fallos habituales al aplicar la regla y cómo se detectan.
### Evidencia
- Qué prueba, medición o registro demuestra que se aplicó bien.

## Checklist de revisión
- [ ] …

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| … | … | ruta al artefacto |

Si no hay mecanismo automático, indicarlo explícitamente: *revisión humana*.

## Relacionados, fuentes y mantenimiento
- Skills relacionados: …
- Fuentes oficiales (con fecha de verificación): …
- Dueño: … · Última revisión: … · Nivel: T1/T2/T3
