---
name: build-caching-and-speed
description: "Usar al acelerar builds Maven o CI: caché de dependencias, builds paralelos, build incremental, caché de capas Docker, sin perder reproducibilidad ni correctitud."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Caché y velocidad de build

## Cuándo aplicar y cuándo no
- Aplica cuando el feedback de CI supera lo razonable o el agente ejecuta builds repetidos en un mismo ciclo.
- No aplica como primera medida si el build es lento por tests inestables o por un módulo mal dividido: arregla eso antes.

## Reglas
- **MUST** medir antes de optimizar: registrar tiempo total y por fase (resolución, compilación, tests, empaquetado).
- **MUST** cachear el repositorio local de Maven (`~/.m2/repository`) en CI con clave derivada de los `pom.xml` (hash), nunca con clave fija.
- **MUST NOT** cachear `target/` entre ramas ni reutilizar resultados sin que la clave incluya código y versión de JDK.
- **SHOULD** usar `./mvnw -T 1C` (módulos en paralelo) solo si los módulos y tests son thread-safe; empezar por `-T 1`.
- **SHOULD** usar `-B` (batch) y `--no-transfer-progress` en CI para logs limpios.
- **SHOULD** separar tests rápidos (unit, `surefire`) de lentos (integración, `failsafe`) en etapas distintas.
- **MAY** evaluar la extensión Maven Build Cache; comprobar estado, versión y compatibilidad con los plugins usados.
- **MUST** ordenar el Dockerfile para cachear capas: dependencias antes del código (ver `container-images`).
- **MUST NOT** desactivar tests, enforcer o análisis (`-DskipTests`, `-Denforcer.skip`) para ir más rápido en la rama principal.

## Por qué
Un build lento hace que se agrupen cambios grandes y se evite ejecutar la verificación completa. Pero una caché mal invalidada produce builds verdes con código obsoleto, peor que uno lento. Por eso la clave de caché lleva el hash de entradas.

## Ejemplos
### Mal
```text
# Caché con clave fija, tests desactivados "para ir rápido"
cache key: maven-cache
./mvnw install -DskipTests -Denforcer.skip=true
```
### Bien
```yaml
# Esquema genérico de CI (adaptar al motor elegido)
cache:
  path: ~/.m2/repository
  key: "m2-${{ hashFiles('**/pom.xml') }}-jdk21"
  restore-keys: "m2-"
steps:
  - run: ./mvnw -B --no-transfer-progress verify
```
```dockerfile
# Capa de dependencias reutilizable antes de copiar el código
COPY pom.xml .
COPY .mvn .mvn
COPY mvnw .
RUN ./mvnw -B dependency:go-offline
COPY src src
RUN ./mvnw -B package -DskipTests
```
`dependency:go-offline` no resuelve siempre todos los plugins (comprobar al fijar la versión); alternativa: montar caché de BuildKit para `~/.m2`.

## Checklist de revisión
- [ ] Hay medición de tiempos por fase antes y después del cambio.
- [ ] La clave de caché incluye hash de POMs y JDK.
- [ ] No se omiten tests ni enforcer en la rama principal.
- [ ] El paralelismo se probó sin fallos intermitentes.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de pipeline (claves de caché, flags de skip) | 3 | agente `code-reviewer` |
| Búsqueda de `-DskipTests` / `enforcer.skip` en CI | 1 | pendiente (regla en `policies/`) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `reproducible-builds`, `container-images`, `maven-wrapper-and-toolchains`, `enforcer-rules`.
- Fuentes: maven.apache.org (Parallel builds in Maven 3, Build Cache extension) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
