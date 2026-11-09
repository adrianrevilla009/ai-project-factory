---
name: flaky-test-management
description: "Usar cuando un test falla de forma intermitente, al diagnosticar tests inestables o antes de poner reintentos, @Disabled o quarantine."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Gestión de tests inestables (flaky)

## Cuándo aplicar y cuándo no
- Aplica a cualquier test que pasa y falla sin cambios de código, en local o en CI.
- No aplica a fallos deterministas: eso es un bug o un test roto, se arregla directamente.

## Reglas
- **MUST** tratar un test flaky como defecto con dueño y fecha: abrir incidencia, asignar y fijar plazo (sugerido: 7 días).
- **MUST NOT** "arreglar" con reintentos globales (`rerunFailingTestsCount` en todo el build) ni con `Thread.sleep`.
- **MUST** esperar condiciones, no tiempo: Awaitility o latches/`CountDownLatch`.
- **MUST** controlar las fuentes de no determinismo: reloj inyectado (`Clock`), semillas, orden de colecciones, zonas horarias, puertos aleatorios, orden de ejecución.
- **MUST** aislar estado: sin datos compartidos entre tests, BD limpia por test, sin dependencia del orden.
- **MUST** poner en cuarentena un flaky con `@Disabled("FLAKY-123: motivo, fecha límite")` solo si hay incidencia enlazada.
- **SHOULD** medir la tasa de flakiness por test en CI y listar los peores.
- **SHOULD** reproducir localmente repitiendo el test (`@RepeatedTest`) o en bucle antes de corregir.

## Por qué
Un test flaky enseña al equipo a ignorar el rojo; entonces un fallo real pasa desapercibido. Los reintentos esconden carreras reales de producción. Las causas habituales son tiempo, orden, estado compartido, concurrencia y recursos externos.

## Ejemplos
### Mal
```java
@Test
void publishesEvent() throws Exception {
    service.placeOrder(order);
    Thread.sleep(2000); // "suficiente"
    assertThat(listener.received()).hasSize(1);
}
```
### Bien
```java
@Test
void publishesEvent() {
    service.placeOrder(order);
    await().atMost(Duration.ofSeconds(5))
           .untilAsserted(() -> assertThat(listener.received()).hasSize(1));
}

@Disabled("FLAKY-123: carrera en el consumidor, dueño @team-orders, arreglar antes de 2026-12-01")
@Test
void legacyScenario() { /* ... */ }
```
Reloj controlado: `Clock.fixed(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC)` inyectado en el servicio.

## Criterios de decisión y trampas
### Cómo decidir
- Si un test inestable bloquea al equipo, ponlo en cuarentena con dueño y fecha y arregla la causa; no lo borres ni lo ignores.
- Las causas se repiten: tiempo, orden, estado compartido, concurrencia y red. Empieza por ahí.
### Trampas frecuentes
- Reintentos globales que esconden defectos reales.
- `sleep` para «esperar a que esté listo».
- Tests flaky sin dueño ni plazo.
- Medir solo la tasa global y no por test.
- Atribuirlo al «CI inestable» sin investigar.
### Evidencia
- Un panel con la tasa de fallos intermitentes por test y el tiempo que lleva en cuarentena.

## Checklist de revisión
- [ ] Sin `Thread.sleep` en tests.
- [ ] Reloj y aleatoriedad inyectados.
- [ ] Tests independientes del orden y sin estado compartido.
- [ ] Todo `@Disabled` tiene incidencia, dueño y fecha.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `Thread.sleep` en tests | 1 | `policies/semgrep/java-sleep-in-tests.yaml` |
| Regla Semgrep para `@Disabled` sin motivo | 1 | pendiente |
| Hook que exige tests en verde al parar | 2 | `.claude/hooks/stop/require_green_tests.py` |
| Revisión de cuarentenas | 3 | agente `qa-engineer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `concurrency-testing`, `integration-testing-testcontainers`, `test-data-management`, `e2e-testing`.
- Fuentes: Awaitility (https://github.com/awaitility/awaitility, comprobar versión y API a 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
