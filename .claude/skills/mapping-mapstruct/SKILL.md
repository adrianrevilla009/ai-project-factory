---
name: mapping-mapstruct
description: Usar al convertir entre entidades, DTOs y comandos en Java/Spring; MapStruct en tiempo de compilación, sin reflexión ni Lombok.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Mapeo con MapStruct

## Cuándo aplicar y cuándo no
- Aplica a conversiones entidad <-> DTO y comando <-> dominio con más de unos pocos campos.
- No aplica a conversiones triviales de 1-2 campos, donde un constructor o método estático es más claro.

## Reglas
- **MUST** usar MapStruct (generación en compilación) en lugar de mapeadores por reflexión (ModelMapper, Dozer).
- **MUST** declarar `@Mapper(componentModel = "spring")` para inyectar el mapper por constructor.
- **MUST** configurar `unmappedTargetPolicy = ReportingPolicy.ERROR` para que un campo nuevo sin mapear rompa la compilación.
- **MUST NOT** poner lógica de negocio, acceso a repositorios ni llamadas remotas en un mapper.
- **MUST** mapear a/desde `record` o clases con constructor; sin Lombok (D27). Si se usan ambos, requeriría `lombok-mapstruct-binding`; está fuera de política.
- **SHOULD** un mapper por módulo y por dirección clara (`toResponse`, `toEntity`); no mapeos bidireccionales genéricos.
- **SHOULD** mapear colecciones con el método generado y, para entidades JPA, evitar disparar cargas perezosas (mapear desde proyecciones o relaciones ya cargadas).
- **MUST** testear mappers con casos de campos sensibles (ocultar `passwordHash`, fechas, enums).

## Por qué
La reflexión falla en runtime y es lenta; MapStruct genera código plano, depurable y verificable al compilar. La política estricta de campos sin mapear evita que un campo sensible se omita o se filtre sin que nadie lo note. Mapear una entidad con relaciones perezosas puede reintroducir N+1.

## Ejemplos
### Mal
```java
CustomerResponse toResponse(Customer c) {
    var modelMapper = new ModelMapper();               // reflexión, sin control de campos
    return modelMapper.map(c, CustomerResponse.class);
}
```
### Bien
```java
@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.ERROR)
interface CustomerMapper {
    CustomerResponse toResponse(Customer customer);

    @Mapping(target = "id", ignore = true)
    Customer toEntity(CreateCustomerRequest request);
}
```
```xml
<!-- maven-compiler-plugin: annotationProcessorPaths con mapstruct-processor -->

```

## Criterios de decisión y trampas
### Cómo decidir
- Un generador de mapeos en tiempo de compilación para evitar código repetitivo y errores de campos; mapeos manuales para lo que tiene lógica.
- Falla la compilación si queda un campo sin mapear.
### Trampas frecuentes
- Mapeos que ocultan una conversión con efectos o consultas.
- Reglas de negocio dentro del mapeador.
- Campos sin mapear que se ignoran en silencio.
- Un mapeador por pares de clases sin necesidad.
- Sin pruebas de los mapeos con lógica.
### Evidencia
- El build falla ante campos sin mapear y hay pruebas de los mapeos no triviales.

## Checklist de revisión
- [ ] `componentModel = "spring"` y `unmappedTargetPolicy = ERROR`.
- [ ] Sin Lombok, sin ModelMapper/Dozer.
- [ ] Mappers sin lógica de negocio ni I/O.
- [ ] Test de mapeo para campos sensibles.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Compilación con `unmappedTargetPolicy=ERROR` | 1 | configuración del `@Mapper` en el proyecto generado |
| Regla Semgrep contra `new ModelMapper()` | 1 | pendiente (`policies/semgrep/`) |
| Revisión de mappers nuevos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `controllers-and-validation`, `n-plus-one`, `spring-data-rules`, `projections-and-dtos`.
- Fuentes oficiales: MapStruct Reference Guide (mapstruct.org).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
