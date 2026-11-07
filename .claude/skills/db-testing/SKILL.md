---
name: db-testing
description: Usar al escribir tests de repositorios, migraciones y consultas contra PostgreSQL real con Testcontainers y @DataJpaTest.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Tests de base de datos

## Cuándo aplicar y cuándo no
- Aplica a repositorios, consultas nativas/JPQL, mapeos, migraciones, locking, RLS y cualquier lógica que dependa del motor.
- No aplica a tests unitarios de dominio sin I/O (ver `unit-testing-java`). El marco general de contenedores está en `integration-testing-testcontainers`.

## Reglas
- **MUST** probar contra el mismo motor y versión mayor que producción (PostgreSQL con Testcontainers); **MUST NOT** usar H2 "en modo PostgreSQL" para validar SQL, locking, JSON o RLS.
- **MUST** crear el esquema con las migraciones reales (Flyway) en los tests de persistencia, no con `ddl-auto=create` (ver `schema-migrations`).
- **MUST** reutilizar el contenedor entre tests de la suite (singleton / `@ServiceConnection`, TODO-VERIFY versión de Spring Boot) para tiempos razonables.
- **MUST** aislar los tests: datos únicos por test o limpieza explícita; no depender del orden. Tener en cuenta que `@Transactional` + rollback no prueba el commit real ni el locking entre transacciones.
- **MUST** tener tests de concurrencia reales (dos transacciones, hilos) para `optimistic-locking` y `pessimistic-locking`, y tests de conteo de sentencias en consultas críticas (ver `n-plus-one`).
- **MUST** incluir en tests los casos de aislamiento multi-tenant y RLS cuando aplique (ver `multi-tenancy`).
- **SHOULD** usar `@DataJpaTest` con `@AutoConfigureTestDatabase(replace = NONE)` para slices de persistencia.
- **SHOULD** usar builders de datos de prueba, no volcados SQL opacos; nunca datos reales de producción ni PII (ver `test-data-management`).
- **SHOULD** ejecutar `flush()` + `clear()` antes de verificar para forzar lectura real desde la BD.

## Por qué
Los bugs de persistencia viven en el comportamiento del motor: tipos, índices únicos, collation, bloqueos, JSON, RLS. Una BD en memoria distinta da falsa confianza. Un test con rollback automático oculta fallos de constraints diferidos y problemas de commit. Las versiones exactas de Testcontainers y Spring Boot deben verificarse en su documentación (TODO-VERIFY).

## Ejemplos
### Mal
```java
@DataJpaTest                       // sustituye la BD por H2 embebida
class OrderRepositoryTest {
    @Test
    void savesOrder() {
        repo.save(new Order());     // sin flush: no llega a ejecutarse el SQL real
    }
}
```
### Bien
```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class OrderRepositoryTest {

    @Container @ServiceConnection
    static PostgreSQLContainer<?> pg = new PostgreSQLContainer<>("postgres:16-alpine"); // TODO-VERIFY tag igual a produccion

    @Autowired OrderRepository repo;
    @Autowired EntityManager em;

    @Test
    void uniqueSku_isEnforcedByDatabase() {
        repo.saveAndFlush(new Order("sku-1"));
        assertThatThrownBy(() -> repo.saveAndFlush(new Order("sku-1")))
            .isInstanceOf(DataIntegrityViolationException.class);
    }
}
```
```yaml
# application-test.yml: el esquema lo crea Flyway
spring:
  jpa.hibernate.ddl-auto: validate
  flyway.enabled: true
```

## Checklist de revisión
- [ ] Motor y versión mayor iguales a producción; sin H2.
- [ ] Esquema creado por Flyway.
- [ ] Contenedor compartido; tests independientes entre sí.
- [ ] Hay tests de commit/concurrencia y de conteo de queries donde importa.
- [ ] Sin datos reales ni PII.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep/dependencias: prohibir H2 en el `pom.xml` de módulos con persistencia | 1 | pendiente (`policies/semgrep/`) |
| Hook `require-green-tests` al parar | 2 | `.claude/hooks/stop/` (Oleada 1, pendiente) |
| Revisión de cobertura de persistencia | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `integration-testing-testcontainers`, `schema-migrations`, `n-plus-one`, `test-data-management`, `testing-slices`.
- Fuentes: documentación de Testcontainers y de Spring Boot (Testing) — TODO-VERIFY URL y versión; no verificado 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
