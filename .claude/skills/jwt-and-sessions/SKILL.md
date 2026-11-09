---
name: jwt-and-sessions
description: "Usar al emitir, validar o almacenar JWT, cookies de sesión y refresh tokens: algoritmos, claims, caducidad, revocación y flags de cookie."
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# JWT y gestión de sesiones

## Cuándo aplicar y cuándo no
- Aplica a APIs que reciben JWT, a BFF con cookie de sesión y a cualquier almacenamiento de tokens en cliente.
- No aplica al flujo de obtención del token (ver `authn-oidc-oauth2`).

## Reglas
- **MUST** verificar firma con las claves públicas del emisor (JWKS); **MUST NOT** aceptar `alg: none` ni permitir que el token elija el algoritmo.
- **MUST** fijar la lista de algoritmos aceptados (p. ej. RS256/ES256) en el decoder.
- **MUST** validar `iss`, `aud`, `exp`, `nbf`; tolerancia de reloj pequeña y explícita.
- **MUST NOT** poner datos sensibles en el payload: un JWT firmado está codificado, no cifrado.
- **MUST** access tokens de vida corta (minutos); refresh tokens con rotación y detección de reutilización.
- **MUST** cookies de sesión con `HttpOnly`, `Secure` y `SameSite` (Lax o Strict), prefijo `__Host-` si es posible.
- **MUST** regenerar el identificador de sesión tras login y destruir la sesión en logout.
- **SHOULD** definir estrategia de revocación (lista de `jti` denegados con TTL, o introspección) para tokens de alto riesgo.
- **MUST NOT** guardar tokens en `localStorage`/`sessionStorage`.
- **MUST NOT** loguear tokens completos.

## Por qué
Los ataques típicos son aceptar tokens sin verificar, confusión de algoritmo, tokens para otra audiencia y robo desde almacenamiento accesible por JavaScript (XSS). Los flags de cookie y la vida corta limitan el daño. Los nombres de propiedades de cookie en Spring dependen de la versión.

## Ejemplos
### Mal
```java
String payload = new String(Base64.getUrlDecoder().decode(token.split("\\.")[1]));
// se confía en el contenido sin verificar firma
```
```javascript
localStorage.setItem("access_token", token);   // legible por cualquier XSS
```
### Bien
```java
NimbusJwtDecoder decoder = NimbusJwtDecoder.withJwkSetUri(jwksUri)
        .jwsAlgorithm(SignatureAlgorithm.RS256)          // algoritmo fijado
        .build();
decoder.setJwtValidator(new DelegatingOAuth2TokenValidator<>(
        JwtValidators.createDefaultWithIssuer(issuer), audienceValidator));
```
```yaml
# Cookie de sesión (propiedades `server.servlet.session.cookie.*`; verificado en el apéndice de propiedades de Spring Boot 4.x el 2026-11-08)
server:
  servlet:
    session:
      cookie:
        http-only: true
        secure: true
        same-site: lax
```

## Criterios de decisión y trampas
### Cómo decidir
- Sesión en el servidor con cookie `HttpOnly` cuando hay navegador; tokens firmados para servicio a servicio, con vida corta.
- Un token no se puede revocar a menos que tengas un mecanismo para ello: diseña la revocación.
### Trampas frecuentes
- Tokens de larga vida sin revocación.
- Datos sensibles dentro del token.
- Aceptar algoritmos «none» o cambiar el algoritmo.
- Almacenar el token en `localStorage`.
- Cookies sin `Secure` ni `SameSite`.
### Evidencia
- Pruebas de caducidad, manipulación de firma y revocación.

## Checklist de revisión
- [ ] Decoder con firma, algoritmo fijado, `iss`, `aud`, `exp`.
- [ ] Sin datos sensibles en claims.
- [ ] Cookies `HttpOnly`/`Secure`/`SameSite`.
- [ ] Sin tokens en storage del navegador ni en logs.
- [ ] Refresh con rotación; logout invalida la sesión.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: parseo de JWT sin verificar | 1 | `policies/semgrep/spring-security-misconfig.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| ESLint: prohibir `localStorage.setItem` con claves `token` | 1 | pendiente (`policies/frontend-boundaries/`) |
| Test: token expirado / `aud` incorrecto -> 401 | 2 | tests del proyecto generado |
| Revisión de gestión de sesión | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `authn-oidc-oauth2`, `security-headers-cors-csrf`, `secrets-management`.
- Fuentes: RFC 7519 (JWT), RFC 8725 (JWT Best Current Practices), OWASP Session Management Cheat Sheet.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
