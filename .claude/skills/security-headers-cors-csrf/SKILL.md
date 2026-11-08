---
name: security-headers-cors-csrf
description: Usar al configurar cabeceras HTTP de seguridad, CORS y protección CSRF en Spring Boot y SPA React, incluyendo CSP, HSTS y cookies SameSite.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Cabeceras de seguridad, CORS y CSRF

## Cuándo aplicar y cuándo no
- Aplica a toda app web/API accesible desde navegador y al gateway o ingress que añade cabeceras.
- No aplica a tráfico servicio a servicio sin navegador (CORS/CSRF no intervienen).

## Reglas
- **MUST** enviar `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` y una `Content-Security-Policy` restrictiva en el frontend.
- **MUST** CSP sin `unsafe-inline`/`unsafe-eval` en scripts; usar nonces o hashes; empezar en `Content-Security-Policy-Report-Only` si hay deuda.
- **MUST** definir `frame-ancestors` (o `X-Frame-Options`) para evitar clickjacking.
- **MUST** CORS con lista explícita de orígenes; **MUST NOT** `*` con credenciales ni reflejar el `Origin` recibido sin validarlo.
- **MUST** mantener CSRF activo en apps con sesión por cookie; usar token sincronizado o doble cookie más `SameSite`.
- **MAY** desactivar CSRF solo en APIs stateless con token Bearer en cabecera `Authorization`, dejándolo documentado.
- **MUST** respuestas con datos sensibles con `Cache-Control: no-store`.
- **SHOULD** terminar las cabeceras en un único punto (app o gateway) para no duplicarlas ni contradecirlas.
- **SHOULD** verificar con un escáner de cabeceras en CI.

## Por qué
Las cabeceras reducen el impacto de XSS y clickjacking; CORS permisivo permite que sitios ajenos lean respuestas autenticadas; CSRF explota cookies que el navegador envía solo. Valores concretos de cabeceras y API de Spring deben contrastarse con documentación vigente (comprobar al fijar la versión).

## Ejemplos
### Mal
```java
@Bean
CorsConfigurationSource cors() {
    var c = new CorsConfiguration();
    c.addAllowedOrigin("*");
    c.setAllowCredentials(true);
    c.addAllowedHeader("*");
    c.addAllowedMethod("*");
    var s = new UrlBasedCorsConfigurationSource();
    s.registerCorsConfiguration("/**", c);
    return s;
}
```
### Bien
```java
@Bean
CorsConfigurationSource cors() {
    var c = new CorsConfiguration();
    c.setAllowedOrigins(List.of("https://app.example.test"));
    c.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
    c.setAllowedHeaders(List.of("Authorization", "Content-Type"));
    c.setAllowCredentials(true);
    c.setMaxAge(Duration.ofMinutes(10));
    var s = new UrlBasedCorsConfigurationSource();
    s.registerCorsConfiguration("/api/**", c);
    return s;
}
```
```text
# Cabeceras objetivo del frontend (ajustar a la app)
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
```

## Checklist de revisión
- [ ] CSP sin `unsafe-inline` en scripts y con `frame-ancestors`.
- [ ] HSTS y `nosniff` presentes.
- [ ] CORS con orígenes explícitos; nunca `*` con credenciales.
- [ ] CSRF activo con sesión por cookie; desactivado solo con justificación escrita.
- [ ] `no-store` en respuestas sensibles.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: CORS con `*` y CSRF desactivado | 1 | `policies/semgrep/spring-security-misconfig.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| Test de integración que comprueba cabeceras | 2 | tests del proyecto generado |
| Política Conftest sobre ingress/gateway (cabeceras) | 2 | pendiente (`policies/opa-conftest/`) |
| Escáner DAST de cabeceras | 3 | `security-testing-sast-dast` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `jwt-and-sessions`, `input-validation-output-encoding`, `method-and-endpoint-security`.
- Fuentes: OWASP HTTP Headers Cheat Sheet, CSRF Prevention Cheat Sheet; MDN sobre CSP y CORS; Spring Security (CORS, CSRF) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
