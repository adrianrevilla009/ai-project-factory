---
name: capacity-and-load-modeling
description: "Usar al dimensionar capacidad, modelar carga o planificar pruebas de carga y headroom, incluido el pico que provoca un failover regional."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Capacidad y modelado de carga

## Cuándo aplicar y cuándo no
- Aplica al lanzar un servicio, antes de campañas/picos, al elegir N+1 / N+2 por AZ o región y al revisar un diseño de DR.
- No aplica a micro-optimización de código (ver `profiling-and-leaks`).
- Las pruebas de carga se diseñan aquí; su ejecución contra AWS no se hace desde la fábrica.

## Reglas
- **MUST** documentar el modelo de carga: peticiones/s por operación, mezcla de operaciones, tamaño de datos, concurrencia y crecimiento esperado a 6 y 12 meses.
- **MUST** basar los números en telemetría real o en supuestos marcados como tales; nunca en intuición sin etiqueta.
- **MUST** calcular el headroom para el peor caso de fallo soportado: si una AZ cae, las restantes absorben su carga (con 3 AZ cada una dimensionada para 50% del pico, no 33%).
- **MUST** modelar el failover regional: la región superviviente recibe el 100%; si no es capaz, el diseño es un pilot light con degradación explícita (`load-shedding-and-degradation`).
- **MUST** identificar el recurso limitante (CPU, conexiones de BD, IOPS, cuotas de servicio) y la cuota de AWS que se alcanzaría.
- **SHOULD** aplicar la ley de Little (concurrencia = tasa x latencia) para dimensionar pools y hilos (`connection-pooling`, `threads-executors-and-pools`).
- **SHOULD** probar carga en entorno aislado con perfil realista (rampa, pico, soak) y criterios de aceptación ligados al SLO.
- **MUST NOT** autoescalar sin límites máximos ni sin considerar las dependencias duras que no escalan (BD).

## Por qué
El failover es el momento de mayor carga y menor capacidad a la vez. Si el cálculo de headroom no lo contempla, el DR existe en el papel pero la región superviviente se satura y la caída se amplifica. El recurso limitante casi nunca es el cómputo.

## Ejemplos
### Mal
```text
"Con 3 réplicas va sobrado." (sin tasa, sin pico, sin fallo de AZ)
```
### Bien
```yaml
service: orders-api
peak_rps: 900            # fuente: telemetría 30d, TODO actualizar
growth_12m: 1.6
latency_p95_ms: 120
concurrency_needed: 172  # 900*1.6*0.120 (ley de Little)
az_count: 3
headroom_rule: "pérdida de 1 AZ => 2 AZ sirven el 100%"
pods_per_az: 6           # 172/2 => 86 conc., con 15 por pod
limiting_resource: "orders-db max_connections"
failover_region_target: "100% del pico, degradación nivel 1 permitida"
load_test:
  profile: [ramp 10m, peak 30m, soak 4h]
  pass_if: "p95 < 300ms y error rate < 0.1%"
```

## Checklist de revisión
- [ ] Modelo de carga con fuente y crecimiento.
- [ ] Headroom ante pérdida de AZ y de región.
- [ ] Recurso limitante y cuotas identificados.
- [ ] Prueba de carga diseñada con criterios de aceptación.
- [ ] Autoescalado con máximos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Kyverno/Conftest: HPA con `maxReplicas` y `PodDisruptionBudget` | 1 | pendiente: `policies/kyverno/` |
| Revisión humana del modelo de carga | 4 | PR / gate |

## Relacionados, fuentes y mantenimiento
- Relacionados: `tier-model-and-rpo-rto`, `scalability-patterns`, `multi-az-patterns`, `finops-of-resilience`, `load-shedding-and-degradation`.
- Fuentes: Well-Architected Reliability Pillar (cuotas y escalado).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
