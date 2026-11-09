---
name: lazy-vs-eager
description: Usar al definir FetchType de asociaciones JPA y al tratar LazyInitializationException.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Carga perezosa frente a ansiosa

## Cuándo aplicar y cuándo no
- Aplica a toda asociación `@ManyToOne`, `@OneToOne`, `@OneToMany`, `@ManyToMany` y a atributos pesados (LOB).
- No aplica a consultas con proyección a DTO, que no cargan entidades.

## Reglas
- **MUST** declarar `fetch = FetchType.LAZY` en toda asociación; el mapeo es perezoso y la carga se decide por caso de uso.
- **MUST NOT** usar `FetchType.EAGER` en el mapeo; si un caso de uso necesita datos relacionados, usar `JOIN FETCH`, `@EntityGraph` o DTO.
- **MUST NOT** resolver `LazyInitializationException` con `EAGER`, con `open-in-view` ni alargando transacciones.
- **MUST** mantener `spring.jpa.open-in-view=false`.
- **MUST** devolver desde la capa de servicio datos ya cargados (DTO o entidad inicializada), no proxies sin inicializar.
- **SHOULD** modelar `@OneToOne` desde el lado propietario o con `@MapsId`; el lado inverso no puede ser perezoso de forma fiable.
- **SHOULD** usar `Hibernate.initialize` solo dentro de la transacción y de forma excepcional.

## Por qué
EAGER es global: penaliza todas las consultas, incluidas las que no necesitan la relación, y es origen habitual de N+1 (ver `n-plus-one`). LAZY obliga a explicitar la carga, que es donde se decide el coste.

## Ejemplos
### Mal
```java
@ManyToOne(fetch = FetchType.EAGER)
private Customer customer;
```
```properties
# "arreglo" de LazyInitializationException
spring.jpa.open-in-view=true
```
### Bien
```java
@ManyToOne(fetch = FetchType.LAZY, optional = false)
private Customer customer;

@EntityGraph(attributePaths = "customer")
Optional<Order> findWithCustomerById(Long id);
```
```properties
spring.jpa.open-in-view=false
```

## Checklist de revisión
- [ ] Ninguna asociación EAGER.
- [ ] Cada caso de uso carga explícitamente lo que necesita.
- [ ] `open-in-view=false`.
- [ ] Los servicios no devuelven proxies sin inicializar fuera de la transacción.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `ToOne` sin LAZY | 1 | `policies/semgrep/jpa-eager-toone.yaml` |
| Comprobación de `open-in-view` en propiedades | 1 | pendiente (policy sobre `application*.yml`) |
| Revisión de mapeos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `n-plus-one`, `joins-and-fetch-joins`, `projections-and-dtos`, `persistence-context-and-flush`.
- Fuentes: guía de usuario de Hibernate ORM (fetching) y referencia de Spring Boot (`spring.jpa.open-in-view`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
