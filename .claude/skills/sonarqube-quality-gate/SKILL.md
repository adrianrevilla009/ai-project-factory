---
name: sonarqube-quality-gate
description: "Usar al plantear SonarQube como análisis de calidad en CI, conociendo los límites de la edición gratuita, y al definir su puerta de calidad sobre código nuevo."
metadata:
  block: "08-testing-quality"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# SonarQube: análisis de calidad y puerta de calidad

## Cuándo aplicar y cuándo no
- Aplica cuando el equipo quiere un tablero único de calidad (bugs, olores de código, cobertura, duplicación, puntos calientes de seguridad) y está dispuesto a autoalojar SonarQube.
- No aplica como puerta de PR si solo se dispone de la edición gratuita: no analiza ramas ni PR (ver Reglas).
- No sustituye a `static-analysis` (Checkstyle, PMD, SpotBugs) ni a `coverage-policy`; los complementa.

## Reglas
- **MUST** conocer los límites de SonarQube Community Build antes de decidir: es gratuito, pero solo analiza la rama principal y no ofrece análisis de PR ni comentarios en el PR; eso es de la edición Developer en adelante, de pago (verificado el 2026-11-09 en la documentación de Sonar).
- **MUST NOT** depender de funciones de pago por defecto (D16). Si se necesita análisis de PR, o se contrata con ADR, o se cubre con las herramientas del propio build.
- **SHOULD** compensar la falta de análisis de PR con la cobertura del diff, Checkstyle, PMD, SpotBugs y Semgrep en el pipeline (`quality-gates`).
- **MUST** definir la puerta de calidad sobre código nuevo («clean as you code»): condiciones de bugs y vulnerabilidades nuevos, cobertura y duplicación del código añadido; la deuda anterior se gestiona aparte.
- **MUST** pasar el token por variable de entorno o secreto del CI (`${SONAR_TOKEN}`), nunca en el `pom.xml` ni en el repositorio.
- **MUST NOT** ejecutar el análisis con secretos sobre código de forks.
- **SHOULD** importar el informe de cobertura de JaCoCo (XML) en lugar de recalcularlo.
- **SHOULD** autoalojarlo con copias de seguridad de su base de datos y actualizarlo de forma regular; lo que contiene es un mapa de los puntos débiles de tu código.
- **MUST** tratar un fallo de la puerta como bloqueo del pipeline en la rama principal, con el mismo régimen de excepciones que otras puertas.

## Por qué
Un tablero de calidad sirve cuando la puerta es sobre lo que cambia: exigir limpiar el pasado de golpe desmoraliza y acaba ignorándose. Y conviene saber desde el principio qué ofrece la edición gratuita, para no basar el proceso en una función (el análisis del PR) que no incluye.

## Ejemplos
### Mal
```xml
<!-- Token en el repositorio y expectativa de análisis por PR con la edición gratuita -->
<properties>
  <sonar.token>abc123-literal</sonar.token>
  <sonar.pullrequest.key>${env.PR_NUMBER}</sonar.pullrequest.key>
</properties>
```
### Bien
```yaml
# Análisis de la rama principal con el token del secreto del CI
sonar:
  if: github.ref == 'refs/heads/main'
  steps:
    - run: >-
        ./mvnw -B verify
        org.sonarsource.scanner.maven:sonar-maven-plugin:sonar
        -Dsonar.host.url=${SONAR_HOST_URL}
        -Dsonar.token=${SONAR_TOKEN}
        -Dsonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml
      env:
        SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

## Criterios de decisión y trampas
### Cómo decidir
- ¿Necesitas análisis de PR? Con la edición gratuita no: o se contrata la edición de pago por ADR, o se usa el conjunto de herramientas del build y se deja SonarQube como tablero de la rama principal.
- ¿Ya tienes Checkstyle, PMD, SpotBugs y Semgrep? SonarQube aporta el tablero y el histórico; si solo quieres puertas, quizá no compense operarlo.
- ¿Equipo grande con muchos proyectos? El tablero único tiene valor; en uno pequeño, el coste de operarlo suele superar el beneficio.
### Trampas frecuentes
- Basar el proceso de revisión en comentarios de PR que la edición gratuita no genera.
- Una puerta sobre todo el código que nadie puede cumplir y se desactiva.
- Token en el `pom.xml`.
- Ignorar los puntos calientes de seguridad porque «no son vulnerabilidades».
- Perfiles de calidad personalizados que no están versionados y divergen entre proyectos.
### Evidencia
- La puerta de calidad exportada o documentada, y el último informe de la rama principal con sus condiciones.

## Checklist de revisión
- [ ] Se ha comprobado qué incluye la edición elegida y no se asume análisis de PR en la gratuita.
- [ ] La puerta se define sobre código nuevo.
- [ ] El token viaja por secreto del CI.
- [ ] La cobertura se importa del informe de JaCoCo.
- [ ] Hay copias de seguridad y plan de actualización del servidor.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Puerta de calidad en el servidor y job de análisis en CI | 2 | pipeline del proyecto generado (pendiente) |
| Revisión de la configuración de la puerta y de excepciones | 3 | agente `code-reviewer` |
| Decisión de contratar una edición de pago | 4 | persona responsable de arquitectura, por ADR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `static-analysis`, `quality-gates`, `coverage-policy`, `code-review-guidelines`, `security-gates`.
- Fuentes: tabla de comparación de funciones de SonarQube Community Build y documentación de análisis de ramas y PR de Sonar (consultadas el 2026-11-09); el nombre del plugin de Maven existe en Maven Central.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
