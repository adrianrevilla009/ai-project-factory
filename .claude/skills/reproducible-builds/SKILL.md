---
name: reproducible-builds
description: "Usar al configurar el build Maven/Docker para que el mismo commit produzca artefactos idénticos bit a bit: timestamp, orden, versiones fijas."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Builds reproducibles

## Cuándo aplicar y cuándo no
- Aplica al parent POM, al empaquetado de JAR y a la construcción de imágenes de contenedor.
- No aplica a pruebas locales rápidas; es un requisito del pipeline de release.

## Reglas
- **MUST** definir `project.build.outputTimestamp` en el parent (valor fijo ISO-8601 o derivado del commit en release) para que los plugins de empaquetado normalicen fechas.
- **MUST** fijar versiones de todos los plugins y del propio Maven (wrapper, ver `maven-wrapper-and-toolchains`).
- **MUST** usar `project.build.sourceEncoding=UTF-8` y `maven.compiler.release` fijo.
- **MUST NOT** incrustar fecha/hora actual, hostname o usuario en el artefacto (`${maven.build.timestamp}` en recursos filtrados, `git.build.time` sin normalizar).
- **MUST NOT** usar rangos de versión, `LATEST` ni dependencias SNAPSHOT en release (ver `versioning-semver-snapshots`).
- **SHOULD** verificar la reproducibilidad en CI construyendo dos veces y comparando (`maven-artifact-plugin`, objetivo `artifact:compare`, que figura en la página del plugin; verificado el 2026-11-08).
- **SHOULD** que las imágenes usen base fijada por digest y capas ordenadas.
- **MUST** conservar la salida de la verificación como evidencia, sin afirmar nada sobre despliegues reales.

## Por qué
Si dos builds del mismo commit difieren, no se puede verificar que el binario desplegado viene del código revisado, y el SBOM/firma (ver `sbom-generation`) pierden valor. Reproducibilidad es la base para detectar manipulaciones de la cadena de suministro.

## Ejemplos
### Mal
```properties
# application.properties filtrado por Maven
build.time=${maven.build.timestamp}
```
### Bien
```xml
<properties>
  <project.build.outputTimestamp>2026-01-01T00:00:00Z</project.build.outputTimestamp>
</properties>
```
```text
# verificación (lectura/compilación local)
./mvnw -B clean verify
./mvnw -B artifact:compare
```
En release, `outputTimestamp` se fija al timestamp del commit de la etiqueta.

## Checklist de revisión
- [ ] `project.build.outputTimestamp` definido.
- [ ] Plugins y Maven con versión fija.
- [ ] Sin timestamps ni datos de máquina en el artefacto.
- [ ] Sin SNAPSHOT ni rangos en release.
- [ ] Doble build comparado en CI de release.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Enforcer `requirePluginVersions`, `requireReleaseDeps` | 1 | `policies/maven-enforcer/banned-dependencies.example.xml` |
| Job CI de doble build + `artifact:compare` | 1 | pendiente (proyecto generado, golden path en `catalog/golden-paths/`) |
| Revisión del parent al tocar empaquetado | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `parent-pom`, `maven-wrapper-and-toolchains`, `versioning-semver-snapshots`, `sbom-generation`, `container-images`.
- Fuentes: Apache Maven, "Configuring for Reproducible Builds" y reproducible-builds.org.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
