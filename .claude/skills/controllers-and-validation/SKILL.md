---
name: controllers-and-validation
description: "Usar al escribir o revisar controladores REST Spring MVC: controladores finos, DTOs de entrada/salida y validación Jakarta en el borde."
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Controladores y validación

## Cuándo aplicar y cuándo no
- Aplica a `@RestController` y a cualquier DTO que cruce la frontera HTTP.
- No aplica al diseño del contrato (ver `rest-design-guidelines`, `openapi-contract-first`) ni a controladores reactivos (ver `reactive-vs-blocking`).

## Reglas
- **MUST** mantener el controlador fino: traduce HTTP a una llamada de servicio de aplicación; sin lógica de negocio ni acceso a repositorios.
- **MUST** usar DTOs (`record`) de entrada y salida; **MUST NOT** exponer entidades JPA en la API.
- **MUST** validar la entrada con `@Valid`/`@Validated` y restricciones Jakarta (`@NotBlank`, `@Size`, `@Positive`, `@Email`).
- **MUST** validar `@PathVariable` y `@RequestParam` anotando la clase con `@Validated`.
- **MUST** devolver códigos HTTP correctos (201 + `Location` al crear, 204 sin cuerpo, 404, 409) y delegar errores en el manejador global (`error-handling-problem-details`).
- **MUST NOT** aceptar `Map<String, Object>` ni campos desconocidos sin control como cuerpo; evitar mass assignment con DTOs específicos por caso de uso.
- **SHOULD** limitar tamaños (`@Size(max=...)`, `spring.servlet.multipart.max-file-size`) para prevenir abuso.
- **SHOULD** una validación de negocio (unicidad, estado) hacerla en el servicio, no con anotaciones.

## Por qué
Validar en el borde falla rápido con un 400 claro y protege el dominio. Exponer entidades acopla la API al esquema, filtra campos internos y habilita mass assignment. Un controlador fino es trivial de probar con `@WebMvcTest`.

## Ejemplos
### Mal
```java
@PostMapping("/customers")
Customer create(@RequestBody Customer entity) {   // entidad JPA como contrato
    return customerRepository.save(entity);
}
```
### Bien
```java
record CreateCustomerRequest(
        @NotBlank @Size(max = 120) String name,
        @NotBlank @Email String email) {}

record CustomerResponse(long id, String name) {}

@RestController
@Validated
@RequestMapping("/customers")
class CustomerController {
    private final CustomerService service;

    CustomerController(CustomerService service) { this.service = service; }

    @PostMapping
    ResponseEntity<CustomerResponse> create(@Valid @RequestBody CreateCustomerRequest request) {
        var created = service.create(request.name(), request.email());
        return ResponseEntity.created(URI.create("/customers/" + created.id())).body(created);
    }

    @GetMapping("/{id}")
    CustomerResponse get(@PathVariable @Positive long id) { return service.get(id); }
}
```

## Checklist de revisión
- [ ] Sin entidades JPA ni `Map` en firmas del controlador.
- [ ] `@Valid` en cada `@RequestBody`; restricciones en path/query.
- [ ] Sin lógica de negocio ni repositorios en el controlador.
- [ ] Códigos HTTP y `Location` correctos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla ArchUnit: controladores no dependen de repositorios ni entidades | 1 | `policies/archunit/` (pendiente) |
| Tests `@WebMvcTest` de validación | 1 | tests del proyecto generado |
| Revisión de contrato y DTOs | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `error-handling-problem-details`, `mapping-mapstruct`, `testing-slices`, `rest-design-guidelines`.
- Fuentes oficiales: Spring Framework Reference (Web MVC, Validation) y Jakarta Bean Validation (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
