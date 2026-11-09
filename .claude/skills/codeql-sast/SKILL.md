---
name: codeql-sast
description: "Usar al decidir si añadir CodeQL como segunda capa de SAST junto a Semgrep, y al configurarlo en CI con su licencia, compilación y triaje de alertas."
metadata:
  block: "07-appsec"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# CodeQL como análisis estático de seguridad

## Cuándo aplicar y cuándo no
- Aplica cuando la organización ya dispone de una licencia que cubre CodeQL sobre código privado y se quiere una segunda capa de análisis, más profunda en flujo de datos, además de Semgrep.
- No aplica si no hay esa licencia: entonces el SAST es Semgrep OSS (`policies/semgrep/`), que no tiene restricciones de uso (D16).
- No sustituye a la revisión de código ni al modelado de amenazas.

## Reglas
- **MUST** decidir su uso en un ADR del proyecto antes de activarlo: el CLI de CodeQL es gratuito en repositorios públicos y para investigación y código abierto, pero para analizar código privado exige GitHub Code Security u otra licencia comercial (verificado el 2026-11-09 en la documentación de GitHub).
- **MUST NOT** activarlo por defecto en un repositorio privado sin esa licencia: choca con D16 (sin licencias de pago por defecto).
- **SHOULD** mantener Semgrep como SAST base y usar CodeQL como complemento: reglas propias rápidas y de patrón frente a análisis profundo y más lento.
- **MUST** ejecutarlo en cada PR hacia la rama principal y de forma programada (por ejemplo, semanal) sobre la rama principal, para detectar vulnerabilidades nuevas en código antiguo.
- **MUST** configurar la compilación para Java y Kotlin: el análisis de lenguajes compilados necesita observar el build (modo automático o un comando explícito de Maven sin tests).
- **MUST** tratar cada alerta con un dueño y un plazo según `vulnerability-sla-and-incident-response`; descartar una alerta exige un motivo registrado, nunca solo cerrarla.
- **SHOULD** empezar con el conjunto de consultas por defecto y ampliarlo cuando el ruido sea manejable.
- **MUST** dar al job el permiso mínimo de subida de resultados y fijar la acción por SHA completo (`github-actions`).

## Por qué
Una sola herramienta de SAST deja huecos: cada motor modela el código de una manera. CodeQL trata el código como una base de datos consultable y sigue flujos de datos entre funciones y ficheros, lo que encuentra clases de fallo que un patrón no ve. A cambio es más lento y tiene licencia: por eso se decide por ADR y se usa como segunda capa.

## Ejemplos
### Mal
```yaml
# Acción por tag mutable, permisos amplios y sin compilar el proyecto Java
permissions: write-all
steps:
  - uses: github/codeql-action/init@v3
    with: { languages: java-kotlin }
  - uses: github/codeql-action/analyze@v3
```
### Bien
```yaml
name: codeql
on:
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 3 * * 1"
permissions:
  contents: read
jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@<SHA-40-HEX>   # vX
      - uses: github/codeql-action/init@<SHA-40-HEX>   # vX
        with:
          languages: java-kotlin
          build-mode: manual
      - run: ./mvnw -B -DskipTests package
      - uses: github/codeql-action/analyze@<SHA-40-HEX>   # vX
```

## Criterios de decisión y trampas
### Cómo decidir
- ¿Hay licencia para código privado? Sin ella, no hay decisión que tomar: Semgrep. Con ella, CodeQL como segunda capa.
- Proyecto pequeño con pocas reglas propias: Semgrep suele bastar. Proyecto con mucha lógica de flujo de datos o requisitos de cumplimiento que piden análisis profundo: añade CodeQL.
- Si el tiempo del PR se dispara, deja el análisis completo en el job programado y en el PR solo lo rápido.
### Trampas frecuentes
- Activarlo en un repositorio privado y descubrir después que hace falta licencia.
- Analizar sin compilar y obtener un resultado vacío que parece «limpio».
- Duplicar alertas entre CodeQL y Semgrep sin triaje común, con dos listas de pendientes.
- Cerrar alertas «por ruido» sin registrar el motivo.
- Permisos de escritura amplios en el job.
### Evidencia
- Un ADR con la licencia comprobada y el plan de triaje, y resultados con dueño y plazo.

## Checklist de revisión
- [ ] Hay un ADR con la licencia y el motivo.
- [ ] El análisis se ejecuta en PR y de forma programada.
- [ ] El build de Java y Kotlin se ejecuta dentro del análisis.
- [ ] Acciones fijadas por SHA y permisos mínimos.
- [ ] Cada alerta abierta tiene dueño y plazo.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Fijado de acciones por SHA | 1 | `policies/opa-conftest/github-actions-pinning.rego` |
| Workflow de CodeQL en el proyecto | 2 | `.github/workflows/` del proyecto generado (pendiente) |
| Revisión de alertas y decisiones de descarte | 3 | agente `security-reviewer` |
| Aprobación de la licencia | 4 | persona responsable de seguridad (Gate 1) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `security-testing-sast-dast`, `security-gates`, `github-actions`, `vulnerability-sla-and-incident-response`, `injection-families`.
- Fuentes: documentación de GitHub sobre el CLI de CodeQL y sobre los lenguajes soportados, y términos de licencia de CodeQL (consultados el 2026-11-09); los nombres exactos de las entradas de la acción se contrastan con su versión fijada.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
