---
name: integration-testing-testcontainers
description: "Usar al escribir tests de integración que necesitan PostgreSQL, Kafka, Redis u otro servicio real, con Testcontainers y Spring Boot."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Tests de integración con Testcontainers

## Cuándo aplicar y cuándo no
- Aplica a repositorios, migraciones, consumidores/productores Kafka, caché y cualquier código cuyo riesgo está en la dependencia real.
- No aplica a lógica de dominio pura (unitario) ni a emular servicios AWS (ver `localstack-aws`) ni HTTP de terceros (ver `wiremock-and-stubbing`).

## Reglas
- **MUST** probar contra la misma tecnología y versión mayor que producción (PostgreSQL real, no H2 como sustituto).
- **MUST** fijar la imagen con tag explícito, nunca `latest`; versión: comprobar según el estándar del proyecto.
- **MUST** que cada IT sea independiente: limpiar datos o usar transacciones/esquemas por test.
- **MUST** aplicar las migraciones reales (Flyway/Liquibase) en el contenedor; no `ddl-auto=create`.
- **SHOULD** usar `@ServiceConnection` (Spring Boot 3.1+) o `@DynamicPropertySource` para enlazar propiedades.
- **SHOULD** compartir un contenedor por suite (campo `static` o clase base) para no pagar el arranque por clase.
- **SHOULD** esperar con Awaitility, no con `sleep`, a efectos asíncronos (mensajes Kafka).
- **MUST NOT** depender de un servicio levantado a mano o de `docker compose` previo para pasar el IT.
- **MUST NOT** activar `reuse` en CI; solo como comodidad local opcional.

## Por qué
H2 y los mocks de repositorio ocultan diferencias de dialecto, tipos, índices y bloqueos que solo aparecen en la base real. Testcontainers da dependencias reales, efímeras y reproducibles sin infraestructura compartida. Requiere un runtime de contenedores disponible en CI: documentarlo.

## Ejemplos
### Mal
```java
@SpringBootTest   // usa H2 y ddl-auto=create: no valida las migraciones ni el SQL real
@AutoConfigureTestDatabase
class OrderRepositoryIT { }
```
### Bien
```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class OrderRepositoryIT {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @Autowired OrderRepository repository;

    @Test
    void findsOrdersByStatus() {
        repository.save(Order.draft("SKU-1", 1));
        assertThat(repository.findByStatus(OrderStatus.DRAFT)).hasSize(1);
    }
}
```
El tag `postgres:16-alpine` es ilustrativo: alinear con la versión del entorno (comprobar al fijar la versión).

## Criterios de decisión y trampas
### Cómo decidir
- Reutiliza el contenedor entre clases (singleton) por velocidad y aísla con esquema o limpieza por test.
- Mismo motor y misma versión mayor que producción; H2 nunca sustituye a PostgreSQL.
- Aplica las migraciones reales; el esquema generado por el ORM no prueba lo que se despliega.
### Trampas frecuentes
- Un contenedor nuevo por test: la suite tarda horas.
- Estado residual entre tests y dependencia del orden.
- Puertos fijos que chocan en paralelo.
- `@Disabled` cuando no hay Docker: el CI queda en verde sin probar nada.
- Imágenes `latest` o datos de producción.
### Evidencia
- Las migraciones se ejecutan en el IT y el tiempo de arranque del contenedor está medido.

## Checklist de revisión
- [ ] Imagen con tag fijo y misma tecnología que producción.
- [ ] Migraciones reales aplicadas en el test.
- [ ] Sin dependencia de servicios externos preexistentes.
- [ ] Sin `sleep`; esperas con Awaitility.
- [ ] Nombre `*IT`, ejecutado por Failsafe.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep: `Thread.sleep` en tests | 1 | `policies/semgrep/java-sleep-in-tests.yaml` |
| Failsafe ejecuta `*IT` en `verify` | 1 | `pom.xml` del proyecto generado |
| Prohibición de `latest` en imágenes de test | 3 | pendiente (regla Semgrep por escribir); hoy revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `db-testing`, `testing-slices`, `schema-migrations`, `kafka-producers-consumers`, `test-data-management`.
- Fuentes: documentación de Testcontainers for Java y de Spring Boot (Testcontainers support) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
