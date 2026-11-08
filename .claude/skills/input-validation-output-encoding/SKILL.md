---
name: input-validation-output-encoding
description: "Usar al recibir datos externos (API, formularios, ficheros, colas) y al renderizarlos: validación con Bean Validation, listas permitidas y codificación según contexto (XSS)."
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Validación de entrada y codificación de salida

## Cuándo aplicar y cuándo no
- Aplica a todo dato que cruce una frontera de confianza: HTTP, mensajes, ficheros, respuestas de terceros y datos leídos de BD que se muestran en HTML.
- No aplica como sustituto de consultas parametrizadas (ver `injection-families`): validar no previene inyección por sí solo.

## Reglas
- **MUST** validar en el servidor (sintaxis y semántica); la validación del cliente React es solo UX.
- **MUST** preferir listas permitidas (formato, longitud, rango, enum) frente a listas de bloqueo.
- **MUST** usar Bean Validation (`@Valid`, `@NotNull`, `@Size`, `@Pattern`) en DTOs de entrada y rechazar con 400 sin eco del valor.
- **MUST** limitar longitud de strings, tamaño de colecciones y profundidad de JSON.
- **MUST** normalizar (Unicode, trim) antes de validar y no re-decodificar tras validar.
- **MUST** codificar la salida según el contexto (HTML, atributo, JS, URL, CSS); usar el escapado por defecto del motor de plantillas.
- **MUST NOT** usar `dangerouslySetInnerHTML` ni `th:utext` con datos no confiables; si es inevitable, sanear con una librería mantenida y una política restrictiva.
- **MUST NOT** construir HTML por concatenación de strings.
- **SHOULD** usar tipos de dominio (`Email`, `OrderId`) que se validan al construirse.

## Por qué
Los datos no confiables llegan por rutas que el desarrollador no anticipa. Validar acota el espacio de entradas; codificar en la salida neutraliza lo que pase. Son controles complementarios: el escapado correcto es lo que previene XSS, no el filtro de entrada.

## Ejemplos
### Mal
```java
@PostMapping("/users")
public void create(@RequestBody Map<String, Object> body) {   // sin esquema ni límites
    service.create((String) body.get("name"));
}
```
```jsx
<div dangerouslySetInnerHTML={{ __html: comment.text }} />
```
### Bien
```java
public record CreateUserRequest(
        @NotBlank @Size(max = 80) String name,
        @NotBlank @Email @Size(max = 254) String email,
        @Pattern(regexp = "^[A-Z]{2}$") String countryCode) {}

@PostMapping("/users")
public ResponseEntity<Void> create(@Valid @RequestBody CreateUserRequest req) {
    service.create(req);
    return ResponseEntity.status(HttpStatus.CREATED).build();
}
```
```jsx
<p>{comment.text}</p>   {/* React escapa por defecto */}
```
Límites de tamaño (propiedades `spring.servlet.multipart.max-file-size` y `max-request-size`; verificado en el apéndice de propiedades de Spring Boot 4.x el 2026-11-08):
```yaml
server:
  tomcat:
    max-http-form-post-size: 1MB
spring:
  servlet:
    multipart:
      max-file-size: 5MB
```

## Checklist de revisión
- [ ] Los DTOs de entrada tienen restricciones y `@Valid`.
- [ ] Hay límites de longitud y tamaño.
- [ ] Ningún `dangerouslySetInnerHTML`/`th:utext` con datos de usuario.
- [ ] Errores de validación no reflejan el valor recibido.
- [ ] Salida codificada por contexto.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| ESLint `react/no-danger` | 1 | pendiente (`policies/frontend-boundaries/`) |
| Regla Semgrep: `@RequestBody Map<String, Object>` en controladores | 1 | pendiente (`policies/semgrep/`) |
| Regla ArchUnit: parámetros `@RequestBody` llevan `@Valid` | 2 | pendiente (`policies/archunit/`) |
| Revisión de sanitización de HTML | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `injection-families`, `security-headers-cors-csrf`, `file-upload-security`, `owasp-top10-and-api-top10`.
- Fuentes: OWASP Input Validation Cheat Sheet y XSS Prevention Cheat Sheet; documentación de Jakarta Bean Validation (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
