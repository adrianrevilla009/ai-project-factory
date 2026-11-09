---
name: api-testing
description: "Usar al probar endpoints REST de un servicio Spring: estado, cuerpo, Problem Details, validación, seguridad y paginación, con MockMvc o RestAssured."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Testing de APIs REST

## Cuándo aplicar y cuándo no
- Aplica a controladores y a la API expuesta: códigos HTTP, JSON, errores, autenticación/autorización, paginación.
- No aplica a la lógica de dominio (unitario) ni al contrato entre servicios (ver `contract-testing`).

## Reglas
- **MUST** probar por endpoint: camino feliz, validación inválida (400/422), no encontrado (404), conflicto (409) y no autorizado/prohibido (401/403).
- **MUST** verificar el formato de error `application/problem+json` (ver `error-handling-problem-details`) y que no filtra trazas ni detalles internos.
- **MUST** probar autorización con usuarios/roles distintos, incluido acceso a recursos de otro tenant o usuario (BOLA/IDOR).
- **MUST** aserciones sobre el JSON con rutas concretas (`jsonPath`), no comparar cuerpos como cadenas enteras.
- **SHOULD** usar `@WebMvcTest` + MockMvc para capa web aislada y `@SpringBootTest(webEnvironment = RANDOM_PORT)` con RestAssured o `RestClient` para flujos completos.
- **SHOULD** validar las respuestas contra el esquema OpenAPI del contrato (ver `openapi-contract-first`).
- **SHOULD** cubrir paginación, orden y límites máximos de página.
- **MUST NOT** usar puertos fijos ni compartir estado entre tests.
- **MUST NOT** deshabilitar la seguridad en los tests de API para "simplificar".

## Por qué
La API es el contrato público: un cambio de estado o de forma de error rompe clientes. Los fallos de autorización entre usuarios son de las vulnerabilidades más frecuentes y solo se detectan probándolos explícitamente.

## Ejemplos
### Mal
```java
@Test
void getOrder() throws Exception {
    mvc.perform(get("/orders/1")).andExpect(status().isOk());   // solo camino feliz, sin auth
}
```
### Bien
```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @Autowired MockMvc mvc;
    @MockitoBean OrderQueryService orders;   // nombre de anotación según versión de Spring Boot

    @Test
    @WithMockUser(username = "alice", roles = "CUSTOMER")
    void returns404ProblemDetails_whenOrderDoesNotExist() throws Exception {
        when(orders.find("missing")).thenThrow(new OrderNotFoundException("missing"));

        mvc.perform(get("/orders/missing"))
           .andExpect(status().isNotFound())
           .andExpect(content().contentTypeCompatibleWith("application/problem+json"))
           .andExpect(jsonPath("$.title").value("Order not found"))
           .andExpect(jsonPath("$.stackTrace").doesNotExist());
    }

    @Test
    void returns401_whenNoCredentials() throws Exception {
        mvc.perform(get("/orders/1")).andExpect(status().isUnauthorized());
    }
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Slice web (`@WebMvcTest`) para validación, serialización y seguridad; `@SpringBootTest` con puerto aleatorio cuando intervienen filtros o transporte.
- Valida el contrato OpenAPI en CI además de las aserciones por endpoint.
### Trampas frecuentes
- Solo el camino feliz.
- Comparar cuerpos como texto en vez de rutas JSON.
- No probar la autorización cruzada (acceso al recurso de otro usuario o tenant).
- Respuestas de error con trazas o detalles internos.
- Depender de datos del entorno.
### Evidencia
- Una matriz endpoint × caso (200, 400, 401, 403, 404, 409) con cada celda cubierta o justificada.

## Checklist de revisión
- [ ] Cada endpoint cubre feliz, validación, 404/409 y 401/403.
- [ ] Errores en `problem+json` sin datos internos.
- [ ] Test de acceso a recurso ajeno.
- [ ] Seguridad activa en el test.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Surefire/Failsafe en CI | 1 | `pom.xml` del proyecto generado |
| Semgrep de seguridad Spring | 1 | `policies/semgrep/spring-security-misconfig.yaml` |
| Revisión de matriz de casos por endpoint | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `controllers-and-validation`, `error-handling-problem-details`, `testing-slices`, `openapi-contract-first`, `method-and-endpoint-security`.
- Fuentes: documentación de Spring Framework (MockMvc) y Spring Security Test.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
