---
name: authn-oidc-oauth2
description: "Usar al integrar autenticación con Keycloak/OIDC y OAuth2 en Spring Boot y React: flujos, PKCE, validación de tokens, resource server y logout."
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Autenticación con OIDC y OAuth2 (Keycloak)

## Cuándo aplicar y cuándo no
- Aplica a login de usuarios, protección de APIs con tokens y comunicación servicio a servicio.
- No aplica a autorización fina (ver `authz-rbac-abac-rebac`) ni al detalle de formato de token (ver `jwt-and-sessions`).

## Reglas
- **MUST** delegar la autenticación en el IdP (Keycloak, D-cerrada); los servicios no almacenan ni verifican contraseñas.
- **MUST** usar Authorization Code con PKCE para SPA y clientes públicos; **MUST NOT** usar Implicit ni Resource Owner Password.
- **MUST** usar Client Credentials para servicio a servicio, con cliente y secreto propios por servicio (`secrets-management`).
- **MUST** configurar las APIs como OAuth2 Resource Server y validar firma (JWKS del emisor), `iss`, `aud` y `exp`.
- **MUST** registrar redirect URIs exactas en el IdP; sin comodines.
- **MUST NOT** guardar tokens de acceso en `localStorage`; en SPA preferir patrón BFF con cookie de sesión `HttpOnly`/`Secure`/`SameSite`.
- **SHOULD** access tokens de vida corta y refresh tokens con rotación.
- **MUST** implementar logout que cierre sesión en el IdP (RP-initiated logout) además de local.
- **SHOULD** exigir MFA en el IdP para roles administrativos.

## Por qué
Reimplementar autenticación multiplica errores. Con PKCE se evita la interceptación del código en clientes públicos; validar `aud` impide que un token emitido para otra API sea aceptado. Detalles de propiedades de Spring Security y Keycloak a contrastar con la versión usada (TODO-VERIFY).

## Ejemplos
### Mal
```java
// Aceptar cualquier JWT decodificado sin validar emisor ni audiencia
Claims c = Jwts.parser().setSigningKey("changeme-example").parseClaimsJws(token).getBody();
```
### Bien
```yaml
# application.yml (propiedades de Spring Security resource server; TODO-VERIFY según versión)
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://idp.example.test/realms/example
```
```java
@Bean
SecurityFilterChain api(HttpSecurity http) throws Exception {
    return http
        .authorizeHttpRequests(a -> a.requestMatchers("/actuator/health/**").permitAll()
                                     .anyRequest().authenticated())
        .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
        .build();
}

@Bean
JwtDecoder jwtDecoder(OAuth2TokenValidator<Jwt> audienceValidator, @Value("${spring.security.oauth2.resourceserver.jwt.issuer-uri}") String issuer) {
    NimbusJwtDecoder d = JwtDecoders.fromIssuerLocation(issuer);
    d.setJwtValidator(new DelegatingOAuth2TokenValidator<>(JwtValidators.createDefaultWithIssuer(issuer), audienceValidator));
    return d;
}
```
En local Keycloak se ejecuta en contenedor; en AWS no se reproduce el IdP gestionado (Cognito u otro): preparado para AWS, no verificado en real.

## Checklist de revisión
- [ ] Flujo Authorization Code + PKCE; sin Implicit ni password grant.
- [ ] Resource server valida `iss`, `aud`, `exp` y firma.
- [ ] Redirect URIs exactas; sin tokens en `localStorage`.
- [ ] Logout cierra sesión en el IdP.
- [ ] Un cliente por servicio con secreto propio.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: JWT parseado sin verificación | 1 | `policies/semgrep/spring-security-misconfig.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| Test: token con `aud` incorrecto -> 401 | 2 | tests del proyecto generado |
| Linter de realm export (redirect URIs sin `*`) | 2 | pendiente (`policies/opa-conftest/`) |
| Revisión de flujos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `jwt-and-sessions`, `authz-rbac-abac-rebac`, `secrets-management`, `zero-trust`.
- Fuentes: RFC 6749, RFC 7636 (PKCE), OpenID Connect Core; documentación de Spring Security (OAuth2 Resource Server) y de Keycloak (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
