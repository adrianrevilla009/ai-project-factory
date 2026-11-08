---
name: method-and-endpoint-security
description: Usar al configurar Spring Security (SecurityFilterChain, method security, actuator) para exigir autenticación y permisos por endpoint y método con denegación por defecto.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Seguridad de endpoints y métodos en Spring

## Cuándo aplicar y cuándo no
- Aplica a toda configuración `SecurityFilterChain`, anotaciones `@PreAuthorize` y exposición de Actuator.
- No aplica al diseño del modelo de permisos (ver `authz-rbac-abac-rebac`).

## Reglas
- **MUST** terminar la cadena con `anyRequest().authenticated()` (o `denyAll()`); la lista de `permitAll` es corta, explícita y revisada.
- **MUST** habilitar method security (`@EnableMethodSecurity`) y proteger la capa de servicio, no solo los controladores.
- **MUST** ordenar matchers de lo específico a lo general.
- **MUST** exponer Actuator solo con `health` y `info` sin detalles; el resto detrás de rol y red de gestión.
- **MUST NOT** desactivar la seguridad con perfiles (`@Profile("dev")` con `permitAll`) sin que el arranque falle si el perfil llega a un entorno compartido.
- **MUST** devolver errores sin stack traces ni detalles internos (`server.error.include-stacktrace=never`, comprobar propiedad).
- **SHOULD** una cadena por tipo de cliente (API stateless vs. web con sesión).
- **SHOULD** probar la seguridad con `spring-security-test`, incluyendo caso anónimo.
- **MUST NOT** depender de ocultar rutas ("security by obscurity").

## Por qué
Un endpoint nuevo olvidado en una lista de excepciones queda público. Con denegación por defecto el error es visible (401/403) en vez de silencioso. Las anotaciones en servicios cubren también llamadas internas no HTTP (consumidores de mensajes, jobs).

## Ejemplos
### Mal
```java
http.csrf(c -> c.disable())
    .authorizeHttpRequests(a -> a.requestMatchers("/api/**").permitAll());   // todo público
```
### Bien
```java
@Configuration
@EnableMethodSecurity
class ApiSecurity {
    @Bean
    SecurityFilterChain api(HttpSecurity http) throws Exception {
        return http
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(a -> a
                .requestMatchers("/actuator/health/**").permitAll()
                .requestMatchers("/actuator/**").hasRole("OPS")
                .requestMatchers(HttpMethod.DELETE, "/api/**").hasAuthority("SCOPE_admin")
                .anyRequest().authenticated())
            .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
            .build();
    }
}
```
```java
@Test
void anonymousCannotListOrders() throws Exception {
    mvc.perform(get("/api/orders")).andExpect(status().isUnauthorized());
}
```

## Checklist de revisión
- [ ] Cadena acaba en `anyRequest().authenticated()`.
- [ ] `permitAll` limitado a lista justificada.
- [ ] Method security activa en servicios sensibles.
- [ ] Actuator restringido; sin stack traces en errores.
- [ ] Test anónimo -> 401 para rutas protegidas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: CSRF desactivado sin justificación | 1 | `policies/semgrep/spring-security-misconfig.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| Regla Semgrep para `anyRequest().permitAll()` | 1 | pendiente (`policies/semgrep/`) |
| Test anónimo por controlador | 2 | tests del proyecto generado |
| Revisión de la configuración de seguridad | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `authz-rbac-abac-rebac`, `authn-oidc-oauth2`, `security-headers-cors-csrf`, `audit-trail-and-security-logging`.
- Fuentes: documentación de Spring Security (authorize HTTP requests, method security) y de Spring Boot Actuator (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
