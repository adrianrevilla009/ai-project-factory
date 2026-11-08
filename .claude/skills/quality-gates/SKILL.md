---
name: quality-gates
description: "Usar al definir los gates de calidad bloqueantes del pipeline: tests, cobertura, mutación, arquitectura, estilo y análisis estático."
metadata:
  block: "16-ci-cd"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Quality gates del pipeline

## Cuándo aplicar y cuándo no
- Aplica a los jobs de PR y de rama principal que deciden si el código puede mezclarse.
- No aplica a gates de seguridad (`security-gates`), contrato (`contract-gate`) ni rendimiento (`performance-gate`).

## Reglas
- **MUST** ejecutar en CI `./mvnw verify` (unitarios + integración con Testcontainers, D19); el fallo bloquea el merge.
- **MUST** ejecutar las reglas ArchUnit como parte de los tests (`policies/archunit/`).
- **MUST** fallar el build si la cobertura de líneas/ramas en código nuevo baja del umbral acordado (umbral por proyecto; sugerido 80 % en código nuevo).
- **SHOULD** ejecutar PIT (mutación) sobre módulos de dominio con umbral explícito, en nightly si es lento.
- **MUST** aplicar formato y checkstyle/Spotless en modo `check`, no `apply`, en CI.
- **MUST NOT** desactivar tests (`@Disabled`, `-DskipTests`) para pasar el gate; un test inestable se arregla o se pone en cuarentena con issue y fecha.
- **MUST NOT** bajar umbrales para que pase un PR; cambiar un umbral requiere PR propio.
- **SHOULD** publicar informes (JaCoCo, Surefire) como artefacto del job.

## Por qué
Un gate que se puede saltar o relajar sin revisión deja de ser gate. El código nuevo es donde la deuda es más barata de evitar; medir cobertura solo global lo diluye.

## Ejemplos
### Mal
```yaml
- run: ./mvnw -B package -DskipTests
  continue-on-error: true
```
### Bien
```yaml
- run: ./mvnw -B verify
- run: ./mvnw -B spotless:check checkstyle:check
- run:./mvnw -B org.pitest:pitest-maven:mutationCoverage   # comprobar versión del plugin
- uses: actions/upload-artifact@<SHA-40-HEX> # vX comprobar al fijar la versión
  if: always()
  with: { name: reports, path: "**/target/site/jacoco/**" }
```

## Checklist de revisión
- [ ] Ningún `continue-on-error`/`-DskipTests` en el camino a main.
- [ ] ArchUnit, formato y estilo se ejecutan en modo check.
- [ ] Umbral de cobertura definido y versionado.
- [ ] Tests excluidos tienen issue y fecha.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep contra `Thread.sleep` en tests | 1 | `policies/semgrep/java-sleep-in-tests.yaml` |
| Reglas ArchUnit de ejemplo | 1 | `policies/archunit/` |
| Regla Rego: sin `continue-on-error` ni `-DskipTests` en workflows | 1 | pendiente |
| Hook de tests en verde al parar | 2 | `.claude/hooks/stop/` (según Oleada) |
| Branch protection con checks requeridos | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `pipeline-architecture`, `security-gates`, `contract-gate`, `evolutionary-architecture-fitness-functions`.
- Fuentes: ADR-0019 (`catalog/adr/0019-testing.md`); PIT/JaCoCo docs oficiales (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
