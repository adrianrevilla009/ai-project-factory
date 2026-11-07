---
name: cell-based-architecture
description: Usar al diseñar aislamiento de fallos por celdas (particiones independientes de la plataforma) para limitar el radio de impacto.
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Arquitectura basada en celdas

## Cuándo aplicar y cuándo no
- Aplica a sistemas con requisitos altos de disponibilidad o multi-tenant donde un fallo no debe afectar a todos los clientes.
- No aplica a sistemas pequeños o de disponibilidad moderada: el coste operativo (N copias, enrutado) no se justifica.

## Reglas
- **MUST** definir la celda como unidad completa e independiente (cómputo, datos, colas) que sirve a un subconjunto de clientes.
- **MUST** que no haya dependencias síncronas entre celdas ni estado compartido en la ruta crítica.
- **MUST** un enrutador de celdas muy simple y sin estado complejo, dueño de la asignación cliente -> celda.
- **MUST** dimensionar la celda con un tamaño máximo conocido y añadir celdas para crecer, no agrandarlas.
- **MUST** poder desplegar y revertir por celda (canary por celda).
- **SHOULD** observabilidad y alertas por celda con etiqueta `cell_id`.
- **SHOULD** definir qué datos son globales (catálogo, identidad) y cómo se replican de forma asíncrona.
- **MUST NOT** introducir doble escritura entre celdas; cada dato tiene una celda dueña.

## Por qué
Limita el radio de impacto: un despliegue defectuoso o un cliente ruidoso afecta a una celda, no a toda la plataforma. El precio es duplicar infraestructura y complejidad de enrutado y de datos globales.

## Ejemplos
### Mal
```text
Todas las celdas leen la misma tabla `tenants` en una BD central en cada petición.
Un fallo de esa BD tumba todas las celdas.
```
### Bien
```yaml
# Mapa de enrutado (ejemplo conceptual)
cells:
  cell-01: { tenants: ["acme", "globex"], max_tenants: 500 }
  cell-02: { tenants: ["initech"],        max_tenants: 500 }
router:
  lookup: tenant_id -> cell_id     # caché local, actualización asíncrona
  on_unknown_tenant: reject
deploy: "una celda cada vez; si el error rate de la celda canario > umbral, parar"
```

## Checklist de revisión
- [ ] La celda es autosuficiente en la ruta crítica.
- [ ] El enrutador es simple y su caída tiene plan.
- [ ] Datos globales definidos con replicación asíncrona.
- [ ] Despliegue y métricas por celda.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión humana de diseño; sin automatización (pendiente) | 4 | ADR del proyecto generado |

La fábrica no despliega (ADR-0004): el diseño queda "preparado para AWS, no verificado en real"; no se reproducen en local varias regiones/cuentas.

## Relacionados, fuentes y mantenimiento
- Relacionados: `multi-tenant-architecture`, `scalability-patterns`, `consistency-and-cap-tradeoffs`, `quality-attributes-atam`.
- Fuentes: AWS Well-Architected, guía de arquitectura basada en celdas — TODO-VERIFY URL (no consultada 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
