---
name: jdk-distribution-and-upgrade-cadence
description: "Usar al elegir distribución y versión de JDK, o al planificar una subida de JDK LTS, parches trimestrales y compatibilidad con Spring Boot y librerías."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Distribución de JDK y cadencia de actualización

## Cuándo aplicar y cuándo no
- Aplica al elegir JDK para un proyecto nuevo, al fijar imagen base y al planificar migraciones o parches.
- No aplica a la elección de lenguaje (Java, decisión cerrada) ni a features concretas del lenguaje.

## Reglas
- **MUST** usar una versión LTS de JDK como objetivo; usar versiones no LTS solo en experimentos, nunca en producción.
- **MUST** elegir una distribución OpenJDK de licencia libre con actualizaciones de seguridad (p. ej. Eclipse Temurin); sin licencias de pago por defecto (D16). Cambiar de distribución requiere ADR.
- **MUST** usar la misma distribución y versión mayor en desarrollo, CI e imagen de runtime (`maven-wrapper-and-toolchains`, `container-images`).
- **MUST** documentar en `docs/` del proyecto el JDK objetivo, la fecha de fin de soporte y la fecha prevista de migración. Fechas: TODO-VERIFY en la hoja de ruta oficial de la distribución.
- **MUST** aplicar parches de seguridad (actualizaciones trimestrales del JDK) mediante PR automatizado de Renovate y pasar toda la suite.
- **SHOULD** planificar la subida al siguiente LTS cuando la versión actual entre en el último año de soporte, no cuando termine.
- **MUST** comprobar compatibilidad antes de subir: versión mínima de Java de Spring Boot, plugins Maven, agente de OpenTelemetry y librerías con bytecode manipulation (TODO-VERIFY en cada documentación).
- **SHOULD** compilar con `release` al nivel del JDK objetivo y ejecutar CI en la matriz [actual, siguiente LTS] como aviso temprano.
- **MUST NOT** activar `--enable-preview` en código de producción.

## Por qué
Un JDK sin parches acumula CVE; uno que se salta tres LTS produce una migración traumática (APIs eliminadas, módulos cerrados). Mantener una cadencia pequeña y continua es más barato que un gran salto.

## Ejemplos
### Mal
```xml
<properties>
  <java.version>22</java.version> <!-- no LTS, sin plan de soporte -->
</properties>
```
```dockerfile
FROM openjdk:latest
```
### Bien
```xml
<properties>
  <maven.compiler.release>21</maven.compiler.release> <!-- LTS; TODO-VERIFY LTS vigente a la fecha -->
</properties>
```
```yaml
# docs/jdk-policy.yaml (ejemplo)
target: 21
distribution: temurin
eol_review_date: "TODO-VERIFY"
next_lts_evaluation: "12 meses antes del fin de soporte"
ci_matrix: ["21", "next-lts-early-access"]
```
```json
{ "packageRules": [{ "matchPackageNames": ["eclipse-temurin"], "groupName": "jdk patch updates" }] }
```

## Checklist de revisión
- [ ] JDK objetivo es LTS y está documentado con fecha de revisión.
- [ ] Misma distribución en local, CI e imagen.
- [ ] Hay PR automático de parches del JDK.
- [ ] Compatibilidad con Spring Boot y agentes verificada antes de subir.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| `requireJavaVersion` en enforcer | 1 | `pom.xml` del proyecto generado (`enforcer-rules`) |
| PR automáticos de imagen base | 1 | configuración Renovate del proyecto generado |
| Revisión de la política de JDK | 4 | revisión humana en cada fase |

## Relacionados, fuentes y mantenimiento
- Relacionados: `maven-wrapper-and-toolchains`, `container-images`, `renovate-dependabot-policy`, `enforcer-rules`.
- Fuentes: openjdk.org (releases), adoptium.net (soporte de Temurin), documentación de Spring Boot (requisitos del sistema) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
