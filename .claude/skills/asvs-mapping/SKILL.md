---
name: asvs-mapping
description: Usar al fijar el nivel OWASP ASVS de un servicio y trazar requisitos de seguridad a código y tests; para backlog de seguridad y revisiones de diseño.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "gate"
---

# Mapeo a OWASP ASVS

## Cuándo aplicar y cuándo no
- Aplica al arrancar un servicio (elegir nivel), al escribir historias con criterios de seguridad y al revisar cobertura.
- No aplica como sustituto de pruebas: ASVS lista requisitos verificables, no los verifica por sí mismo.

## Reglas
- **MUST** declarar el nivel ASVS objetivo por servicio (L1 mínimo; L2 por defecto si trata datos personales o autenticación; L3 solo con justificación de riesgo) en un ADR.
- **MUST** mantener una matriz capítulo -> requisito aplicable -> evidencia (test, config o ADR) -> estado.
- **MUST** marcar como "no aplica" cada requisito descartado, con motivo; no dejar celdas vacías.
- **MUST** convertir los requisitos aplicables en criterios de aceptación de las historias afectadas (login, sesión, validación, API).
- **SHOULD** priorizar capítulos de autenticación, control de acceso, validación, criptografía y registro.
- **MUST NOT** afirmar "cumple ASVS L2" sin evidencia por requisito; usar "cobertura ASVS L2: N de M requisitos con evidencia".
- **SHOULD** referenciar los identificadores con la versión explícita (p. ej. `v5.0.0-x.y.z`) para que no cambien de significado.

## Por qué
Sin un estándar de verificación, "es seguro" no es discutible. ASVS da una lista cerrada y numerada que permite medir avance y repartir trabajo. Los identificadores cambian entre versiones, por eso la versión va en la matriz (comprobar versión vigente de ASVS y formato de IDs).

## Ejemplos
### Mal
```markdown
- [x] Seguridad revisada
```
### Bien
```markdown
# docs/security/asvs-matrix.md  (objetivo: L2, ASVS versión comprobar al fijar la versión)
| Requisito (id ASVS) | Aplica | Evidencia | Estado |
|---|---|---|---|
| Sesión: invalidar en logout | sí | `SessionLogoutIT` | hecho |
| Contraseñas: almacenamiento con hash adaptativo | no (Keycloak gestiona credenciales) | ADR-0012 | n/a |
| Control de acceso: denegar por defecto | sí | `AuthorizationDefaultDenyArchTest` | pendiente |
```
Historia con criterio:
```gherkin
Scenario: acceso a un pedido de otro tenant
  Given un usuario autenticado del tenant "example-a"
  When pide GET /orders/{id} de un pedido del tenant "example-b"
  Then recibe 404
```

## Checklist de revisión
- [ ] Nivel objetivo documentado en ADR.
- [ ] Matriz con versión de ASVS y sin celdas vacías.
- [ ] Cada "aplica" tiene evidencia enlazada o estado pendiente.
- [ ] Las historias de login/sesión/acceso incluyen criterios de seguridad.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validador de matriz (sin celdas vacías, versión declarada) | 2 | pendiente |
| Tests nombrados en la matriz existen | 2 | pendiente |
| Revisión de la matriz en el gate de diseño | 3 | `gates/` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `secure-sdlc-nist-ssdf`, `owasp-top10-and-api-top10`, `authz-rbac-abac-rebac`, `input-validation-output-encoding`.
- Fuentes: proyecto OWASP ASVS (owasp.org/www-project-application-security-verification-standard) — comprobar versión y niveles vigentes.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
