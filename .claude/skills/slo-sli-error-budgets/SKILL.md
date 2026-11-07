---
name: slo-sli-error-budgets
description: "Usar al definir SLIs, SLOs y presupuestos de error de un servicio, y al conectarlos con alertas, releases y el tier de resiliencia."
metadata:
  block: "10-observability-app"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# SLI, SLO y presupuestos de error

## Cuándo aplicar y cuándo no
- Aplica a todo servicio con usuarios o consumidores (internos o externos) y a la decisión de ritmo de cambios.
- No aplica a herramientas internas sin objetivo de disponibilidad ni a SLAs contractuales (esos requieren revisión legal/comercial).

## Reglas
- **MUST** definir SLIs como razón de eventos buenos sobre eventos válidos, medidos en el servidor o en el borde más cercano al usuario.
- **MUST** definir al menos: disponibilidad (peticiones no-5xx) y latencia (porcentaje bajo un umbral) por cada API crítica; **SHOULD** añadir frescura/corrección para pipelines de datos.
- **MUST** fijar el SLO como objetivo y ventana (p. ej. 30 días móviles) y derivar el presupuesto de error (`1 - SLO`); el SLO debe ser menor que lo que el diseño soporta (ver `ADR-0007` tier de resiliencia).
- **MUST** versionar SLOs como código (reglas de grabación Prometheus y/o definiciones SLO) junto al servicio, con dueño.
- **MUST** vincular las alertas paginables al consumo del presupuesto (burn rate, ver `alerting-symptom-based`).
- **SHOULD** definir una política de presupuesto agotado acordada con producto: congelar cambios no urgentes, priorizar fiabilidad.
- **MUST NOT** fijar el 100 %; **MUST NOT** copiar SLOs de otro servicio sin medir el comportamiento real.
- **MUST NOT** excluir del SLI las peticiones fallidas "por culpa del cliente" salvo que se definan por código de respuesta explícito.
- **SHOULD** revisar los SLOs trimestralmente con los datos reales.

## Por qué
El SLO convierte "que funcione bien" en un número discutible y permite equilibrar fiabilidad y velocidad: si sobra presupuesto se puede arriesgar más; si falta, se frena. Un SLO inalcanzable o trivial no informa decisiones.

## Ejemplos
### Mal
```text
"El servicio debe tener 99,999 % de disponibilidad." (sin SLI, ventana ni medición)
```
### Bien
```yaml
# slo/orders-api.yaml (formato propio ilustrativo; la herramienta concreta es TODO-VERIFY)
service: orders-api
owner: team-orders
slos:
  - name: availability
    objective: 99.9
    window: 30d
    sli:
      good:  'sum(rate(http_server_requests_seconds_count{application="orders-api",status!~"5.."}[5m]))'
      total: 'sum(rate(http_server_requests_seconds_count{application="orders-api"}[5m]))'
  - name: latency-p95-under-500ms
    objective: 99.0
    window: 30d
    sli:
      good:  'sum(rate(http_server_requests_seconds_bucket{application="orders-api",le="0.5"}[5m]))'
      total: 'sum(rate(http_server_requests_seconds_count{application="orders-api"}[5m]))'
```
Con 99,9 % en 30 días el presupuesto es unos 43 minutos de indisponibilidad total.

## Checklist de revisión
- [ ] SLIs como buenos/válidos con ventana y objetivo.
- [ ] SLO versionado con dueño.
- [ ] Alertas de burn rate enlazadas.
- [ ] Política de presupuesto agotado acordada.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de SLOs y política de presupuesto | 3 | agente `code-reviewer` + decisión humana de producto (4) |
| Validación de esquema de SLO (pendiente) | 1 | `factory/validators/` (pendiente) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `alerting-symptom-based`, `golden-signals-red-use`, `quality-attributes-atam`, `on-call-and-runbook-links`.
- Fuentes: Google SRE Book y Workbook (SLOs, error budgets), consultados 2026-11-07. Los SLAs contractuales son borrador por confirmar con fuente oficial y revisión legal. Los SLO son objetivos de diseño, no resultados medidos: preparado para AWS, no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
