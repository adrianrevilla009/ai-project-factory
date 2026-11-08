---
name: consistency-and-cap-tradeoffs
description: "Usar al decidir niveles de consistencia, replicación o fronteras transaccionales en sistemas distribuidos; aplica CAP/PACELC de forma práctica."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "review"
---

# Consistencia y trade-offs CAP

## Cuándo aplicar y cuándo no
- Aplica al elegir entre transacción local y consistencia eventual, al usar réplicas de lectura, cachés o múltiples regiones.
- No aplica a un monolito con una sola BD y sin réplicas de lectura: ahí manda ACID local.

## Reglas
- **MUST** decidir la consistencia por caso de uso, no globalmente: qué operaciones requieren lectura fuerte (saldo, stock vendible) y cuáles toleran retraso (listados, contadores).
- **MUST** mantener ACID dentro de una frontera transaccional (un aggregate, una BD) y consistencia eventual entre fronteras.
- **MUST** documentar en el ADR el comportamiento ante partición: qué se sacrifica (disponibilidad o consistencia) en cada operación.
- **MUST** tratar la lectura desde réplica o caché como potencialmente obsoleta; si el flujo lee tras escribir, leer del primario o usar token de versión.
- **MUST NOT** presentar CAP como "elige 2 de 3": la partición no es opcional; la elección real es consistencia vs disponibilidad durante la partición, y latencia vs consistencia el resto del tiempo (PACELC).
- **MUST** usar claves de idempotencia en operaciones de escritura reintentables.
- **SHOULD** usar bloqueo optimista (`@Version`) para conflictos de escritura concurrente.
- **SHOULD** declarar la ventana máxima aceptable de obsolescencia (ej. proyecciones < 5 s) como requisito medible.
- **SHOULD** declarar qué no se reproduce en local (multi-AZ, replicación asíncrona real, latencias entre regiones); preparado para AWS, no verificado en real.

## Por qué
Las incoherencias en producción casi siempre vienen de suposiciones implícitas: "la réplica ya tendrá el dato", "el evento llegó una sola vez". Hacer explícita la consistencia por operación convierte el comportamiento en requisito comprobable.

## Ejemplos
### Mal
```text
Requisito: "el sistema debe ser consistente y siempre disponible".
Código: guarda en primario y lee inmediatamente de la réplica para mostrar el pedido recién creado.
```
### Bien
```text
| Operación           | Consistencia | En partición | Obsolescencia máx. |
|---------------------|--------------|--------------|--------------------|
| Reservar stock      | Fuerte (primario) | rechaza (503) | 0 s            |
| Listado de pedidos  | Eventual (proyección) | sirve lo último | 5 s        |
| Contador de visitas | Eventual     | sirve caché  | 60 s               |
```
```java
@Version private long version;   // conflicto -> OptimisticLockingFailureException -> 409
```

## Checklist de revisión
- [ ] Tabla de consistencia por operación en el ADR.
- [ ] Lecturas tras escritura leen del primario o usan versión.
- [ ] Escrituras reintentables con idempotency key.
- [ ] Ventana de obsolescencia definida y medible.
- [ ] Comportamiento ante partición explícito.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana del ADR de consistencia en el gate de arquitectura | 4 | `gates/` |
| Revisión de uso de réplicas/cachés | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `sagas-and-process-managers`, `cqrs`, `event-driven`, `scalability-patterns`.
- Fuentes: Brewer, "CAP Twelve Years Later" (2012); Abadi, "PACELC" (2012). (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
