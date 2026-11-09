---
name: dast-and-attack-simulation
description: "Usar al integrar DAST (OWASP ZAP) o simulación de ataques en CI o staging propios, con alcance acotado y autorizado; nunca contra terceros."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# DAST y simulación de ataques (ZAP)

## Cuándo aplicar y cuándo no
- Aplica a escaneo dinámico de aplicaciones propias desplegadas en un entorno efímero o de staging, y a ejercicios de simulación acordados (purple team) con alcance escrito.
- No aplica a objetivos de terceros, a producción con datos reales sin autorización, ni a escaneos lanzados libremente por un agente. El objetivo lo fija un fichero de configuración revisado, no el agente.

## Reglas
- **MUST** definir el objetivo solo en un plan versionado (`zap-plan.yaml`) con `includePaths` y exclusiones; nunca aceptar la URL por parámetro libre.
- **MUST** ejecutar el escaneo activo únicamente contra entornos propios con datos sintéticos; en producción solo el escaneo pasivo/baseline.
- **MUST** autenticar el escaneo con una cuenta de prueba dedicada y de privilegio mínimo, cuyas credenciales vengan del gestor de secretos del CI.
- **MUST** importar la definición OpenAPI para cubrir endpoints de API además del spider.
- **MUST** tratar el informe como entrada del registro de vulnerabilidades: hallazgos nuevos de severidad alta rompen el pipeline de la rama principal; el resto se registra.
- **SHOULD** usar el Automation Framework de ZAP (`-autorun` con YAML) en lugar de scripts ad hoc; ver jobs `openapi`, `spider`, `activeScan`, `report`.
- **SHOULD** limitar la tasa de peticiones y la duración para no degradar el entorno compartido.
- **SHOULD** mantener alertas de falsos positivos con filtros (`alertFilter`) justificados y con caducidad.
- **MUST NOT** ejecutar fuzzing o escaneo activo contra dependencias SaaS ni contra el IdP compartido.

## Por qué
SAST y SCA no ven fallos de configuración, cabeceras, flujos de autenticación ni problemas de despliegue. Pero un escáner activo es, en la práctica, tráfico de ataque: sin alcance fijado puede dañar datos o salirse del perímetro. Fijar el objetivo en un fichero revisado hace que la autorización sea auditable.

## Ejemplos
### Mal
```text
zap.sh -cmd -quickurl $TARGET_FROM_PROMPT -quickprogress
```
(el objetivo lo decide quien invoca, sin autorización ni exclusiones).
### Bien
```yaml
# zap-plan.example.yaml (ejecutar: ./zap.sh -cmd -autorun zap-plan.example.yaml)
env:
  contexts:
    - name: staging
      urls: ["https://staging.example.com"]
      includePaths: ["https://staging.example.com/.*"]
      excludePaths: [".*/logout.*"]
jobs:
  - type: openapi
    parameters: {apiUrl: "https://staging.example.com/v3/api-docs"}
  - type: spider
  - type: passiveScan-wait
  - type: activeScan
  - type: report
    parameters: {template: "traditional-json", reportDir: "reports"}
```
Nombres de jobs verificados en la documentación del Automation Framework (zaproxy.org/docs/automate/automation-framework/, 2026-11-07); los parámetros exactos de cada job.

## Checklist de revisión
- [ ] El objetivo está en un plan versionado con exclusiones.
- [ ] El escaneo activo solo apunta a entornos propios y sintéticos.
- [ ] Cuenta de prueba de mínimo privilegio y secreto en gestor.
- [ ] Hallazgos alta/crítica bloquean o se registran con SLA.
- [ ] Filtros de falsos positivos con justificación y caducidad.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Policy Rego: el plan ZAP solo puede listar dominios de una allowlist de entornos propios | 1 | pendiente (`policies/opa-conftest/`) |
| Revisión del plan y de excepciones | 3 | agente `code-reviewer` |
| Autorización de simulaciones con RoE | 4 | ver `penetration-testing-program` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `penetration-testing-program`, `vulnerability-management-program`, `ephemeral-environments`, `asvs-mapping`.
- Fuentes: ZAP Automation Framework (zaproxy.org/docs/automate/automation-framework/, 2026-11-07).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
