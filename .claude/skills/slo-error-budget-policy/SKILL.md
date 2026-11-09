---
name: slo-error-budget-policy
description: "Usar al definir SLIs/SLOs y la política de presupuesto de error que decide cuándo congelar cambios y priorizar fiabilidad."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# SLO y política de presupuesto de error

## Cuándo aplicar y cuándo no
- Aplica a todo servicio con tier asignado; el SLO es el objetivo medible que sostiene el tier.
- No aplica a la implementación de dashboards/alertas (ver `dashboards-and-slos-as-code`).

## Reglas
- **MUST** definir por servicio SLIs desde la perspectiva del usuario (disponibilidad, latencia, frescura) con ventana móvil (p. ej. 28 días).
- **MUST** fijar el SLO por debajo del 100% y derivarlo del tier; el presupuesto de error es `1 - SLO`.
- **MUST** tener una política escrita y firmada por producto e ingeniería que diga qué ocurre al agotar el presupuesto.
- **MUST** definir como mínimo: congelar cambios no críticos (salvo P0 y correcciones de seguridad) hasta recuperar el SLO, prioridad a trabajo de fiabilidad y mecanismo de escalado para discrepancias.
- **MUST** alertar por velocidad de consumo (burn rate) en varias ventanas, no por umbral de error instantáneo.
- **SHOULD** exigir postmortem cuando un solo incidente consuma un porcentaje alto del presupuesto (el ejemplo de Google usa 20%; ajustar).
- **SHOULD** excluir del cómputo tráfico fuera de alcance (pruebas de carga, pentest) y documentarlo.
- **MUST NOT** usar el SLO como arma entre equipos ni cambiarlo tras un incumplimiento sin revisión formal.

## Por qué
Sin política, el SLO es un número decorativo. El presupuesto convierte la fiabilidad en una decisión de negocio compartida: si sobra presupuesto se innova; si no, se estabiliza. La política de ejemplo de Google SRE detiene cambios y lanzamientos salvo P0/seguridad cuando se supera el presupuesto en la ventana, y prevé excepciones (fallos de infraestructura global, otros equipos, tráfico fuera de alcance).

## Ejemplos
### Mal
```text
SLO: "99.99% siempre". Sin ventana, sin dueño, sin consecuencia.
```
### Bien
```yaml
service: orders-api
tier: 1
slis:
  - name: availability
    good: "http_requests{code!~'5..'}"
    total: "http_requests"
slo: {target: 99.9, window: 28d}
error_budget_policy:
  on_exhausted:
    - freeze: "releases salvo P0 y seguridad"
    - priority: "reliability backlog"
  burn_alerts:
    - {window: 1h, burn_rate: 14.4, action: page}
    - {window: 6h, burn_rate: 6, action: page}
  escalation: "head-of-engineering decide en discrepancias"
  signed_by: [product-owner, eng-lead]
```
Los valores de burn rate son un punto de partida.

## Criterios de decisión y trampas
### Cómo decidir
- Una política escrita de qué se hace al agotar el presupuesto (congelar cambios, priorizar fiabilidad) y quién decide; acordada con negocio y producto.
- Revisa los objetivos cuando cambia el uso.
### Trampas frecuentes
- Una política sin consecuencias reales.
- Objetivos irreales.
- Decidir caso por caso sin criterios.
- Presupuesto que se gasta sin que nadie lo vea.
- No distinguir fallos propios de los de dependencias.
### Evidencia
- Un registro de las veces que se activó la política y qué se hizo.

## Checklist de revisión
- [ ] SLIs orientados a usuario y ventana definida.
- [ ] SLO derivado del tier, no del 100%.
- [ ] Política firmada con congelación, prioridades y escalado.
- [ ] Alertas por burn rate.
- [ ] Exclusiones documentadas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Esquema/Conftest para `slo.yaml` (campos `slo`, `window`, `error_budget_policy`) | 1 | pendiente: `policies/opa-conftest/` |
| Gate de release que consulta el presupuesto restante | 2 | pendiente (`change-and-release-management`) |
| Revisión humana de la firma de la política | 4 | PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `tier-model-and-rpo-rto`, `dashboards-and-slos-as-code`, `change-and-release-management`, `incident-management-and-postmortems`.
- Fuentes (verificado 2026-11-07): https://sre.google/workbook/error-budget-policy/ .
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
