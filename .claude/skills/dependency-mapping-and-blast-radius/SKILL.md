---
name: dependency-mapping-and-blast-radius
description: "Usar al mapear dependencias de un servicio y estimar su radio de impacto antes de fijar tiers, DR o cambios; incluye dependencias duras, blandas y ocultas."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Mapa de dependencias y radio de impacto

## Cuándo aplicar y cuándo no
- Aplica al asignar tier/RPO/RTO, antes de un game day, al revisar un diseño multi-región y tras un incidente.
- No aplica a librerías internas sin I/O de red.

## Reglas
- **MUST** mantener por servicio un fichero `dependencies.yaml` versionado con dependencias de red, datos, identidad, DNS, secretos, CI/CD y terceros.
- **MUST** clasificar cada dependencia como dura (sin ella no hay servicio) o blanda (degradable), con el comportamiento degradado (`load-shedding-and-degradation`).
- **MUST** respetar la regla: un servicio de tier N no puede depender de forma dura de uno de tier inferior en criticidad.
- **MUST** incluir dependencias ocultas: control planes (Argo CD, Vault, Keycloak), emisión de certificados, resolución DNS, registro de imágenes.
- **MUST** estimar el radio de impacto como conjunto de servicios, usuarios y tenants afectados por el fallo de cada dependencia.
- **SHOULD** contrastar el mapa declarado con la telemetría real (trazas, service graph de Tempo) y registrar las diferencias.
- **SHOULD** revisar el mapa en cada cambio de arquitectura y tras cada postmortem.
- **MUST NOT** asumir que una dependencia "regional" de un tercero es independiente de la propia región sin comprobarlo (comprobar por proveedor).

## Por qué
Las caídas más largas vienen de dependencias que nadie listó: el plano de despliegue o el proveedor de identidad en la región caída. El mapa convierte el RTO en un cálculo: el RTO efectivo es el del peor eslabón duro. Sin mapa no hay forma de decidir qué probar en un game day ni qué aislar con celdas.

## Ejemplos
### Mal
```yaml
# dependencies.yaml
orders:
  depends_on: [postgres]   # sin tipo, sin tier, sin degradación
```
### Bien
```yaml
service: orders
tier: 1
dependencies:
  - name: orders-db
    kind: data
    coupling: hard
    tier: 1
    blast_radius: "todos los pedidos de la región"
  - name: recommendations
    kind: service
    coupling: soft
    tier: 3
    on_failure: "ocultar bloque de recomendaciones; respuesta 200 sin él"
  - name: keycloak
    kind: identity
    coupling: hard
    tier: 1
    on_failure: "tokens ya emitidos válidos hasta su exp; sin login nuevo"
```

## Checklist de revisión
- [ ] Todas las dependencias, incluidas las de plataforma, listadas.
- [ ] Cada una marcada dura/blanda con comportamiento degradado.
- [ ] Ninguna dependencia dura apunta a un tier inferior.
- [ ] Radio de impacto estimado y contrastado con trazas.
- [ ] Mapa actualizado desde el último postmortem.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Conftest sobre `dependencies.yaml` (tier y `coupling` obligatorios) | 1 | pendiente: `policies/opa-conftest/` |
| Revisión humana del mapa en el gate de arquitectura | 4 | PR / gate |

## Relacionados, fuentes y mantenimiento
- Relacionados: `tier-model-and-rpo-rto`, `static-stability-and-cell-architecture`, `fault-injection-and-game-days`, `cell-based-architecture`, `backpressure-and-bulkheads`.
- Fuentes: Well-Architected Reliability Pillar (https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html) — comprobar sección de dependencias.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
