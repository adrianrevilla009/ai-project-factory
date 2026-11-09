---
name: performance-gate
description: "Usar al añadir pruebas de rendimiento con JMeter al pipeline: umbrales, entorno comparable y detección de regresiones."
metadata:
  block: "16-ci-cd"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Performance gate

## Cuándo aplicar y cuándo no
- Aplica a servicios con SLO de latencia/throughput antes de promover a staging o producción.
- No aplica a PRs de documentación ni a cambios sin efecto en el camino caliente (se corre en main/nightly, no en cada PR).

## Reglas
- **MUST** definir umbrales como código (p95/p99 de latencia, tasa de error, throughput mínimo) derivados del SLO, versionados con el servicio.
- **MUST** ejecutar JMeter (D19) en modo no-GUI (`-n`) contra el entorno efímero o staging, nunca contra producción.
- **MUST** fallar el job si se superan los umbrales o si la regresión frente a la línea base supera el margen acordado.
- **MUST** calentar la JVM (warm-up) y descartar ese tramo de las métricas.
- **SHOULD** comparar contra el último resultado de `main` (línea base almacenada como artefacto) y no solo contra umbrales absolutos.
- **SHOULD** ejecutar la prueba larga (soak) en nightly y una prueba corta (smoke de carga) en cada merge.
- **MUST NOT** interpretar resultados de runners compartidos como capacidad real: son tendencia relativa; la capacidad se modela aparte (`capacity-and-load-modeling`).

## Por qué
Las regresiones de rendimiento llegan por acumulación de cambios pequeños. Runners compartidos son ruidosos, por eso se compara contra línea base del mismo tipo de runner y no se extrapola a AWS.

## Ejemplos
### Mal
```yaml
- run: jmeter -t plan.jmx   # GUI/sin umbral; el job siempre pasa
```
### Bien
```yaml
- run: >
    jmeter -n -t perf/orders.jmx -l results.jtl -e -o report
    -Jhost=$PREVIEW_HOST -Jthreads=50 -Jduration=300
- name: assert thresholds
  run: python3 perf/assert_thresholds.py results.jtl --p95-ms 300 --error-rate 0.01
- uses: actions/upload-artifact@<SHA-40-HEX> # vX
  with: { name: perf-report, path: report }
```
`assert_thresholds.py` es un script del proyecto generado (pendiente en la fábrica). Flags de JMeter.

## Criterios de decisión y trampas
### Cómo decidir
- Umbrales derivados de los SLO y comparados con la línea base; una puerta de rendimiento en cada commit solo si es corta y estable.
- Contra un entorno efímero o de pruebas estable, nunca contra producción.
- Resultados con ruido: ejecuta varias veces o usa márgenes estadísticos.
### Trampas frecuentes
- Entornos con recursos variables que dan resultados incomparables.
- Umbrales absolutos copiados de otro servicio.
- No descartar el calentamiento de la JVM.
- Bloquear por una desviación dentro del ruido.
- Medir solo medias.
### Evidencia
- Los resultados quedan versionados y se comparan con la ejecución anterior en cada promoción.

## Checklist de revisión
- [ ] Umbrales derivados del SLO y versionados.
- [ ] JMeter en modo `-n`, con warm-up.
- [ ] Job falla ante incumplimiento o regresión.
- [ ] Nunca apunta a producción.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Script de aserción de umbrales en el proyecto generado | 1 | pendiente (proyecto generado) |
| Revisión de umbrales vs SLO | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `ephemeral-preview-environments`, `capacity-and-load-modeling`, `slo-error-budget-policy`, `quality-gates`.
- Fuentes: ADR-0019; manual de JMeter (https://jmeter.apache.org/usermanual/).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
