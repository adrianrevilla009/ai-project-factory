---
name: testing-event-sourced-systems
description: "Usar al escribir tests de aggregates, upcasters y proyecciones en sistemas event-sourced (given-when-then sobre eventos, replay, concurrencia)."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Testing de sistemas event-sourced

Subskill de `event-sourcing`.

## Cuándo aplicar y cuándo no
- Aplica a aggregates cuyo estado se deriva de eventos, a upcasters, a proyecciones y al almacén de eventos.
- No aplica a CRUD ni a publicación simple de eventos de integración (ver `testing-slices`, `contract-testing-pact`).

## Reglas
- **MUST** testear aggregates con el patrón given (eventos pasados) - when (comando) - then (eventos nuevos o excepción); sin mocks de repositorio ni base de datos.
- **MUST** que el aggregate sea puro: sin reloj ni UUID internos; inyectar `Clock` e identificadores desde el comando.
- **MUST** tener un test por cada upcaster con un evento histórico real guardado como fixture (JSON versionado en `src/test/resources`).
- **MUST** tener un test de concurrencia optimista: dos comandos con la misma versión esperada, uno debe fallar con conflicto.
- **MUST** tener un test de reconstrucción: proyección viva == proyección reconstruida desde cero (ver `rebuilds-and-replays`).
- **SHOULD** usar property-based testing para invariantes ("el saldo nunca es negativo para cualquier secuencia válida"; ver `property-based-testing`).
- **SHOULD** probar el event store contra el motor real (Testcontainers para Postgres; para DynamoDB ver `local-vs-aws-dynamodb-testing`).
- **MUST NOT** comparar eventos por `toString()` o timestamps reales; comparar records por igualdad con reloj fijo.

## Por qué
Los eventos son el contrato permanente: un cambio que rompe la lectura de eventos antiguos solo se detecta con fixtures históricos. Un aggregate puro hace los tests rápidos y deterministas; la concurrencia y el rebuild son los dos fallos típicos que ningún test unitario de happy path ve.

## Ejemplos
### Mal
```java
@Test
void placeOrder() {
    Order o = new Order();
    o.place("c1", 100);                  // reloj y UUID internos
    assertEquals(o.getStatus(), "PLACED"); // asserts sobre estado mutable, no sobre eventos
}
```
### Bien
```java
@Test
void cannotShipTwice() {
    var fixture = new AggregateFixture<>(OrderAggregate::new, Clock.fixed(T0, UTC));
    fixture.given(new OrderPlaced("o1", "c1", 100L), new OrderShipped("o1", T0))
           .when(new ShipOrder("o1"))
           .thenThrows(IllegalStateException.class);
}

@Test
void upcastsLegacyOrderPlacedV1() throws Exception {
    var v1 = read("events/order-placed-v1.json");
    assertThat(upcaster.upcast(v1)).isEqualTo(new OrderPlacedV2("o1", "c1", 100L, "EUR"));
}
```
`AggregateFixture` es un helper del proyecto generado (no una librería concreta); si se usa Axon u otra, ver su documentación.

## Checklist de revisión
- [ ] Tests given-when-then sin base de datos.
- [ ] Reloj e identificadores inyectados.
- [ ] Fixture histórico por cada versión de evento.
- [ ] Test de conflicto de versión esperada.
- [ ] Test de rebuild contra vista viva.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Tests en CI del proyecto generado | 1 | pipeline del proyecto (la fábrica no los ejecuta) |
| Hook `require-green-tests` al parar | 2 | `.claude/hooks/stop/require_green_tests.py` |
| Revisión de cobertura de upcasters y concurrencia | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `event-sourcing`, `event-versioning-and-upcasting`, `optimistic-locking`, `property-based-testing`, `db-testing`.
- Fuentes: sin fuente oficial única; patrón given-when-then estándar.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
