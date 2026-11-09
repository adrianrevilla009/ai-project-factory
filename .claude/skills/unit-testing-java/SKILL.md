---
name: unit-testing-java
description: "Usar al escribir o revisar tests unitarios Java con JUnit 5, AssertJ y Mockito: estructura, nombres, dobles y qué NO mockear."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Tests unitarios en Java

## Cuándo aplicar y cuándo no
- Aplica a clases de dominio y de aplicación testeables sin contexto Spring ni E2E.
- No aplica a verificar SQL, serialización real o configuración de Spring (usar `integration-testing-testcontainers` o `testing-slices`).

## Reglas
- **MUST** usar JUnit 5 (Jupiter) y AssertJ; estructura Arrange-Act-Assert con un solo comportamiento por test.
- **MUST** nombrar el test por comportamiento: `rejectsOrder_whenStockIsInsufficient`.
- **MUST** inyectar por constructor para poder instanciar la clase sin Spring.
- **MUST** inyectar `Clock` y generadores de ids; nunca depender de `LocalDateTime.now()` ni `UUID.randomUUID()` directos.
- **MUST NOT** usar `Thread.sleep`; usar latches o Awaitility (ver `concurrency-testing`).
- **MUST NOT** mockear tipos que no son tuyos (JDK, cliente HTTP, `JdbcTemplate`) ni value objects; usar instancias reales.
- **SHOULD** preferir fakes en memoria de puertos propios frente a Mockito cuando haya varias interacciones.
- **SHOULD** usar `@ParameterizedTest` para tablas de casos; `@Nested` para agrupar contextos.
- **SHOULD** limitar `verify(...)` a efectos de salida relevantes (evento publicado, correo enviado), no a cada llamada interna.
- **MUST NOT** usar Lombok en tests ni en producción (D27).

## Por qué
Un test unitario útil es rápido, determinista y falla por una sola razón. El exceso de mocks acopla los tests a la implementación y los rompe en cada refactor sin detectar defectos reales. Controlar tiempo y azar elimina la mayor fuente de flakiness (ver `flaky-test-management`).

## Ejemplos
### Mal
```java
@Test
void test1() throws Exception {
    when(repo.findById(1L)).thenReturn(Optional.of(new Order()));
    service.process(1L);
    Thread.sleep(500);
    verify(repo).findById(1L);          // solo prueba la implementación
    assertTrue(order.getDate().equals(LocalDate.now()));  // reloj real
}
```
### Bien
```java
class OrderServiceTest {
    private final Clock clock = Clock.fixed(Instant.parse("2026-01-15T10:00:00Z"), ZoneOffset.UTC);
    private final InMemoryOrderRepository orders = new InMemoryOrderRepository();
    private final OrderService service = new OrderService(orders, clock);

    @Test
    void confirmsOrder_stampingCurrentInstant() {
        var id = orders.save(Order.draft("SKU-1", 2));

        service.confirm(id);

        assertThat(orders.get(id).confirmedAt()).isEqualTo(Instant.parse("2026-01-15T10:00:00Z"));
    }

    @ParameterizedTest
    @CsvSource({"0", "-1"})
    void rejectsNonPositiveQuantity(int quantity) {
        assertThatThrownBy(() -> Order.draft("SKU-1", quantity))
            .isInstanceOf(IllegalArgumentException.class);
    }
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Dobles solo en las fronteras (puertos, reloj, red); fakes en memoria para repositorios del dominio; objetos reales para el resto.
- Mockito en modo estricto para detectar stubs sin usar.
- Un comportamiento por test; si necesitas tres `act`, son tres tests.
### Trampas frecuentes
- Verificar llamadas internas en vez del resultado observable.
- Mockear tipos de valor o el propio objeto bajo prueba.
- `any()` que oculta argumentos erróneos.
- Datos mutables compartidos entre tests o dependencia del orden.
- Probar getters y setters para subir cobertura.
### Evidencia
- Los unitarios corren en segundos, sin Spring, sin red y sin `sleep`.

## Checklist de revisión
- [ ] Un comportamiento por test, nombre descriptivo, AAA visible.
- [ ] Sin reloj, azar, red, disco ni `sleep` reales.
- [ ] Mocks solo en fronteras propias; value objects reales.
- [ ] Sin `@Disabled` sin ticket.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep: `Thread.sleep` en tests | 1 | `policies/semgrep/java-sleep-in-tests.yaml` |
| Semgrep: prohibido Lombok | 1 | `policies/semgrep/java-no-lombok.yaml` |
| Surefire en cada build | 1 | `pom.xml` del proyecto generado |
| Revisión de calidad de aserciones | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `tdd`, `time-and-money`, `concurrency-testing`, `mutation-testing`, `testing-slices`.
- Fuentes: guías de usuario de JUnit 5, AssertJ y Mockito.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
