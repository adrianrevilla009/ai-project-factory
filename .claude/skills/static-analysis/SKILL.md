---
name: static-analysis
description: "Usar al configurar o revisar el análisis estático en Maven (Checkstyle, PMD, SpotBugs, Error Prone) y los quality gates que bloquean el build."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Análisis estático y quality gates

## Cuándo aplicar y cuándo no
- Aplica al `pom.xml` padre, a la configuración de reglas y a cualquier PR que suprima o relaje un aviso.
- No aplica a SAST de seguridad (ver `security-testing-sast-dast`) ni a la revisión de diseño (`code-review-guidelines`).

## Reglas
- **MUST** ejecutar en cada build, y fallar el build en el nivel acordado: Checkstyle (estilo), PMD (malas prácticas), SpotBugs (bugs de bytecode) y Error Prone (errores en compilación).
- **MUST** configurar los plugins una sola vez en el `pluginManagement` del parent POM (ver `parent-pom`) con ficheros de reglas versionados en el repo.
- **MUST** partir de reglas estrictas en código nuevo; la deuda previa se registra en un baseline explícito con plan, no con desactivación global.
- **MUST** que cada supresión (`@SuppressWarnings`, `@SuppressFBWarnings`, `// NOPMD`) lleve justificación en una línea y alcance mínimo.
- **MUST NOT** bajar la severidad o desactivar una regla para pasar un PR sin decisión registrada.
- **SHOULD** ejecutar las comprobaciones rápidas (Checkstyle, Error Prone) en cada compilación local y las pesadas (SpotBugs, PMD) en CI.
- **SHOULD** definir un quality gate: sin bugs nuevos, sin vulnerabilidades nuevas, cobertura sobre código nuevo según `coverage-policy`.
- **SHOULD** que la versión de cada herramienta quede fijada en el BOM/parent y actualizada por Renovate/Dependabot.

## Por qué
Los defectos de patrón (null, recursos sin cerrar, `equals` mal implementado, comparaciones erróneas) se detectan gratis y de forma consistente con herramientas; la revisión humana se reserva para diseño. Un gate que se puede saltear sin rastro deja de ser gate.

## Ejemplos
### Mal
```java
@SuppressWarnings("all")          // silencia todo, sin motivo
public class OrderService { /* ... */ }
```
### Bien
```java
@SuppressFBWarnings(value = "EI_EXPOSE_REP",
    justification = "Lista inmutable envuelta con List.copyOf en el constructor")  // alcance mínimo
public record OrderView(List<Line> lines) { }
```
```xml
<!-- parent pom: plugin configurado una vez; fallar en violaciones. Versiones: comprobar al fijar la versión -->
<plugin>
  <artifactId>maven-checkstyle-plugin</artifactId>
  <configuration>
    <configLocation>config/checkstyle.xml</configLocation>
    <failOnViolation>true</failOnViolation>
  </configuration>
</plugin>
```
Error Prone se integra vía `maven-compiler-plugin` con `-XDcompilePolicy=simple` y `-Xplugin:ErrorProne`; los flags exactos y la compatibilidad con la versión de JDK se confirman en la documentación oficial (comprobar al fijar la versión).

## Checklist de revisión
- [ ] Las cuatro herramientas están en el parent POM y fallan el build.
- [ ] Reglas y baseline versionados en el repo.
- [ ] Toda supresión tiene justificación y alcance mínimo.
- [ ] Ninguna regla desactivada sin registro.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Plugins con fallo de build en parent POM | 1 | `pom.xml` padre del proyecto generado (pendiente) |
| Semgrep sobre patrones de lenguaje | 1 | `policies/semgrep/java-language-pitfalls.yaml` |
| Revisión de supresiones nuevas | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `parent-pom`, `code-style-and-naming`, `coverage-policy`, `security-testing-sast-dast`, `no-lombok`.
- Fuentes: documentación oficial de Checkstyle, PMD, SpotBugs y Error Prone (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
