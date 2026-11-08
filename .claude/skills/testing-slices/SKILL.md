---
name: testing-slices
description: Usar al escribir tests de Spring Boot para elegir el slice mínimo (@WebMvcTest, @DataJpaTest, @JsonTest) en lugar de @SpringBootTest completo.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Tests por slices en Spring Boot

## Cuándo aplicar y cuándo no
- Aplica a tests de capa web, persistencia, JSON y clientes HTTP dentro de un servicio Spring Boot.
- No aplica a tests unitarios puros (sin contexto Spring) ni a E2E de sistema (bloque 08).

## Reglas
- **MUST** preferir test unitario sin contexto; luego slice; `@SpringBootTest` solo para integración de extremo a extremo del servicio.
- **MUST** usar `@WebMvcTest(Controller.class)` para controladores (validación, serialización, códigos HTTP, Problem Details).
- **MUST** usar `@DataJpaTest` con una base real vía Testcontainers (misma BD que producción) para repositorios; **MUST NOT** probar queries nativas contra H2.
- **MUST** usar `@JsonTest` para contratos de serialización críticos.
- **MUST** sustituir colaboradores con `@MockitoBean` (Spring Framework 6.2+; en versiones anteriores `@MockBean`, TODO-VERIFY) y limitar su uso: muchos mocks indican un slice mal elegido.
- **SHOULD** reutilizar contenedores entre tests (singleton / `@ServiceConnection`, Boot 3.1+) para no multiplicar el tiempo.
- **MUST NOT** usar `@DirtiesContext` salvo causa documentada: destruye la caché de contextos.
- **MUST** que los tests no dependan del orden ni de datos de otros tests.

## Por qué
`@SpringBootTest` arranca todo y tarda; un slice carga solo lo necesario, falla más cerca de la causa y se ejecuta en segundos. Contextos distintos por test (por mocks o propiedades distintas) rompen la caché de contexto de Spring y multiplican el tiempo de la suite.

## Ejemplos
### Mal
```java
@SpringBootTest
@AutoConfigureMockMvc
class OrderControllerTest {
    @Autowired MockMvc mvc;      // arranca BD, Kafka, seguridad... para probar un 400

    @Test
    void rejectsEmptyBody() throws Exception {
        mvc.perform(post("/orders").contentType(APPLICATION_JSON).content("{}"))
           .andExpect(status().isBadRequest());
    }
}
```
### Bien
```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @Autowired MockMvc mvc;
    @MockitoBean OrderService orderService;

    @Test
    void rejectsEmptyBody() throws Exception {
        mvc.perform(post("/orders").contentType(APPLICATION_JSON).content("{}"))
           .andExpect(status().isBadRequest())
           .andExpect(content().contentType("application/problem+json"));
    }
}
```
```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class OrderRepositoryTest {
    @Container @ServiceConnection
    static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
    // tag de imagen ilustrativa: fijar la versión real en el proyecto
}
```

## Checklist de revisión
- [ ] Cada test usa el slice más pequeño posible.
- [ ] Repositorios probados contra el motor real (Testcontainers), no H2.
- [ ] Sin `@DirtiesContext` injustificado.
- [ ] Pocos `@MockitoBean`; configuraciones de contexto compartidas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `@SpringBootTest` + `@AutoConfigureMockMvc` sin justificación y `@DirtiesContext` | 1 | pendiente |
| Dependencia H2 prohibida en el POM (enforcer/OPA) | 1 | pendiente (`policies/opa-conftest/`) |
| Hook `require-green-tests` al parar | 2 | `.claude/hooks/stop/` (pendiente) |
| Revisión de tests nuevos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `n-plus-one`, `controllers-and-validation`, `integration-testing-testcontainers`, `unit-testing-java`.
- Fuentes: Spring Boot Reference (Testing, test slices, Testcontainers) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
