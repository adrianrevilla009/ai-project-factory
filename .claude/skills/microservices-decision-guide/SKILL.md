---
name: microservices-decision-guide
description: Usar al decidir si extraer un servicio o partir un monolito en microservicios; da criterios y un registro de decisión.
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Guía de decisión: microservicios

## Cuándo aplicar y cuándo no
- Aplica antes de crear un servicio nuevo, extraer un módulo o aprobar una propuesta de "pasar a microservicios".
- No aplica a decisiones ya tomadas con ADR vigente; en ese caso revisar solo la frontera.

## Reglas
- **MUST** partir de `modular-monolith` salvo que haya un motivo medible documentado.
- **MUST** justificar cada servicio con al menos un motivo: escalado distinto, cadencia de despliegue independiente, aislamiento de fallos/seguridad, o autonomía de un equipo.
- **MUST** que el servicio sea dueño de sus datos; sin base de datos compartida entre servicios y sin doble escritura Postgres+NoSQL.
- **MUST** registrar la decisión en un ADR con alternativas y coste operativo asumido (observabilidad, CI/CD, contratos, consistencia eventual).
- **MUST NOT** crear servicios por capa técnica ni "nano-servicios" que siempre se despliegan juntos.
- **MUST NOT** introducir llamadas síncronas en cadena sin timeouts, reintentos acotados y circuit breaker.
- **SHOULD** exigir contratos versionados (OpenAPI/AsyncAPI) y contract tests antes de la primera integración.
- **SHOULD** que un servicio sea operable por un único equipo.

## Por qué
Los microservicios cambian complejidad de código por complejidad distribuida: latencia, fallos parciales, consistencia eventual, coste operativo. Solo compensan cuando el beneficio (autonomía, escala selectiva) supera ese precio. Un monolito modular mantiene la opción abierta.

## Ejemplos
### Mal
```text
ADR: "Usaremos microservicios porque es la tendencia."
Servicios: user-crud, order-crud, db-service (todos escriben en la misma BD).
```
### Bien
```text
ADR-0123: Extraer `pricing` como servicio
Motivo: carga 40x superior al resto en campañas; escala independiente (medido en pruebas de carga).
Datos: pricing es dueño de su esquema; los demás consumen su API o eventos.
Coste asumido: contrato OpenAPI versionado, trazas distribuidas, despliegue propio.
Alternativas descartadas: caché en el monolito; réplica de lectura.
```

## Checklist de revisión
- [ ] Existe motivo medible y ADR.
- [ ] El servicio es dueño exclusivo de sus datos.
- [ ] Hay contrato versionado y contract tests.
- [ ] Se ha asumido el coste operativo (observabilidad, pipeline, on-call).
- [ ] Se descartó el monolito modular con argumentos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión humana del ADR de creación/extracción de servicio | 4 | `catalog/adr/` del proyecto generado; sin automatización (pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `modular-monolith`, `strangler-fig-migration`, `bff-and-api-gateway`, `consistency-and-cap-tradeoffs`, `sagas-and-process-managers`.
- Fuentes: Martin Fowler, "MonolithFirst" y "Microservice Premium" (martinfowler.com).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
