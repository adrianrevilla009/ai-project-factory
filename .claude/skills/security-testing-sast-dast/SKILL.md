---
name: security-testing-sast-dast
description: "Usar al definir pruebas de seguridad en CI: SAST (Semgrep), DAST (ZAP), secretos, dependencias y gates con umbrales, triaje de falsos positivos."
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Pruebas de seguridad: SAST, DAST y tests de abuso

## Cuándo aplicar y cuándo no
- Aplica al diseñar el pipeline de CI de un proyecto generado y al decidir qué bloquea un merge.
- No aplica a pentests manuales (revisión humana periódica); estos complementan, no sustituyen, la automatización.

## Reglas
- **MUST** SAST en cada pull request (Semgrep OSS u otro de licencia abierta, D16) con reglas de `policies/semgrep/` más un conjunto base mantenido; salida SARIF.
- **MUST** escaneo de secretos en commits y en CI (`secrets-management`).
- **MUST** análisis de dependencias en CI (`dependency-security`).
- **MUST** DAST (p. ej. OWASP ZAP en modo baseline) contra un entorno efímero o local, nunca contra sistemas ajenos ni sin autorización.
- **MUST** tests de seguridad unitarios/integración para controles propios: acceso cruzado, token inválido, validación, límites.
- **MUST** definir umbral de bloqueo (p. ej. severidad alta/crítica bloquea merge) y proceso de excepción con caducidad.
- **MUST** triaje de falsos positivos con justificación versionada (fichero de supresiones con motivo y fecha), no desactivar la regla globalmente.
- **SHOULD** ejecutar SAST rápido en PR y DAST completo de forma nocturna o por release.
- **MUST NOT** tratar "0 hallazgos" como "seguro": indica solo que las reglas no detectaron nada.

## Por qué
Cada técnica cubre una clase distinta: SAST ve patrones en el código, DAST ve comportamiento en ejecución, los tests propios verifican reglas de negocio de seguridad. Un gate sin proceso de excepción acaba ignorado; uno sin umbral no bloquea nada.

## Ejemplos
### Mal
```yaml
- name: security
  run: semgrep scan || true        # nunca falla
```
### Bien
```yaml
# Fragmento de CI (sintaxis de ejemplo)
sast:
  script:
    - semgrep scan --config policies/semgrep/ --sarif --output semgrep.sarif --error
secrets:
  script:
    - gitleaks detect --redact
dast-baseline:
  script:
    - make local-up   # el servicio bajo prueba corre en el clúster kind del pipeline, no en Compose (ADR-0005)
    - zap-baseline.py -t http://localhost:8080 -r zap-report.html
```
```yaml
# security/suppressions.yaml
- rule: spring-csrf-disabled-globally
  path: src/main/java/com/example/ApiSecurity.java
  reason: "API stateless con Bearer; ver ADR-0031"
  expires: "2027-03-01"
```
```java
@Test
void tamperedToken_isRejected() throws Exception {
    mvc.perform(get("/api/orders").header("Authorization", "Bearer " + tamper(validToken)))
       .andExpect(status().isUnauthorized());
}
```

## Checklist de revisión
- [ ] SAST, secretos y dependencias corren en cada PR.
- [ ] Umbral de bloqueo definido y aplicado.
- [ ] DAST contra entorno propio y autorizado.
- [ ] Supresiones con motivo y caducidad.
- [ ] Tests de seguridad propios para controles críticos.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Reglas Semgrep propias de la fábrica | 1 | `policies/semgrep/` |
| Validador que exija jobs `sast`/`secrets` en el CI del proyecto generado | 2 | pendiente |
| Validación de caducidad de supresiones | 2 | pendiente |
| Pentest / revisión periódica | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `secure-sdlc-nist-ssdf`, `dependency-security`, `secrets-management`, `static-analysis`, `injection-families`.
- Fuentes: documentación de Semgrep OSS y OWASP ZAP; OWASP Web Security Testing Guide.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
