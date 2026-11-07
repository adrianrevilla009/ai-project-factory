---
name: performance-testing
description: "Usar al planificar o ejecutar pruebas de rendimiento con JMeter: baseline, carga, soak y spike, con criterios de aceptación y entorno comparable."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Pruebas de rendimiento (JMeter)

## Cuándo aplicar y cuándo no
- Aplica a servicios con SLO de latencia/throughput, cambios en caminos calientes y antes de releases con riesgo de capacidad.
- No aplica a microbenchmarks (JMH) ni a pruebas de capacidad en AWS real: la fábrica no despliega (ADR-0004); los resultados locales son orientativos, no evidencia de capacidad en AWS.

## Reglas
- **MUST** definir antes de ejecutar los criterios de aceptación derivados del SLO (p95/p99, error rate, throughput) y la carga objetivo.
- **MUST** distinguir tipos: **baseline** (carga mínima de referencia), **load** (carga esperada), **soak** (carga sostenida horas: fugas, agotamiento de pool), **spike** (subida brusca y recuperación), **stress** (hasta romper).
- **MUST** ejecutar JMeter en modo no-GUI (`-n`) y guardar resultados `.jtl` y el informe HTML; el GUI solo para diseñar el plan.
- **MUST** correr con datos y volumen representativos y con calentamiento (warm-up) descartado del análisis.
- **MUST** comparar siempre contra el baseline anterior y registrar versión del código, entorno y configuración.
- **MUST NOT** apuntar la prueba a sistemas de terceros ni a entornos compartidos sin autorización.
- **MUST NOT** afirmar capacidad en AWS a partir de pruebas locales; indicar "preparado para AWS, no verificado en real".
- **SHOULD** medir también el cliente generador (CPU/red) para no confundir sus límites con los del servicio.
- **SHOULD** ejecutar un smoke de rendimiento en CI y las pruebas largas de forma programada.

## Por qué
Sin umbrales previos, cualquier resultado se racionaliza. El soak detecta lo que una prueba de 5 minutos nunca ve (fugas, pools, GC). La comparación con baseline detecta regresiones graduales.

## Ejemplos
### Mal
```text
Lancé JMeter con la GUI y 10 usuarios, iba rápido en mi portátil.
```
### Bien
```text
jmeter -n -t perf/orders-load.jmx -l target/perf/orders.jtl -e -o target/perf/report \
  -Jthreads=200 -Jrampup=120 -Jduration=900
```
```yaml
# perf/acceptance.yaml (criterios acordados antes de la prueba)
scenario: orders-load
slo:
  p95_ms: 300
  p99_ms: 800
  error_rate_pct: 0.5
  throughput_rps_min: 150
```

## Checklist de revisión
- [ ] Criterios de aceptación definidos antes de ejecutar.
- [ ] Tipo de prueba explícito (baseline/load/soak/spike/stress).
- [ ] Ejecución `-n`, warm-up descartado, resultados archivados.
- [ ] Comparación con baseline y entorno documentado.
- [ ] Sin afirmaciones de capacidad en AWS.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión del plan y resultados | 3 | agente `performance` (`.claude/agents/quality/performance.md`) |
| Smoke de rendimiento en CI con umbrales | 2 | pendiente (pipeline del proyecto generado) |
| Hook de honestidad AWS | 2 | `.claude/hooks/post-tool-use/maturity_label_check.py` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `slo-sli-error-budgets`, `profiling-and-leaks`, `connection-pooling`, `canary-analysis-and-synthetic-monitoring`.
- Fuentes: Apache JMeter, manual de ejecución en línea de comandos (https://jmeter.apache.org/usermanual/get-started.html, TODO-VERIFY flags a 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
