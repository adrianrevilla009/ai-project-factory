---
name: versioning-semver-snapshots
description: "Usar al versionar artefactos y servicios: SemVer, SNAPSHOT vs release, CI-friendly versions (revision) y reglas de inmutabilidad."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Versionado: SemVer y SNAPSHOT

## Cuándo aplicar y cuándo no
- Aplica a la versión de módulos Maven, imágenes, BOM y librerías internas publicadas.
- No aplica a la versión de APIs HTTP expuestas (ver `api-versioning-deprecation`).

## Reglas
- **MUST** seguir SemVer `MAJOR.MINOR.PATCH`: MAJOR rompe compatibilidad, MINOR añade compatible, PATCH corrige.
- **MUST** que las versiones release sean inmutables: una versión publicada nunca se re-sube ni se sobrescribe; se corrige con una nueva.
- **MUST** que `-SNAPSHOT` exista solo en ramas de desarrollo; **MUST NOT** desplegar ni referenciar SNAPSHOT en un release ni en una imagen de producción.
- **MUST NOT** depender de un SNAPSHOT de terceros en `main`.
- **SHOULD** usar CI-friendly versions (`${revision}`) con `flatten-maven-plugin` para que el POM publicado lleve la versión resuelta.
- **SHOULD** derivar la versión de un tag git `vX.Y.Z` en el pipeline de release (ver `release-automation`).
- **SHOULD** que todos los módulos de un reactor compartan la misma versión.
- **MUST NOT** usar `versions:set` manual con commits "bump version" a mano si hay automatización.

## Por qué
Un SNAPSHOT cambia bajo los pies: el mismo `1.2.0-SNAPSHOT` compilado hoy y mañana difiere, rompiendo reproducibilidad (`reproducible-builds`) y trazabilidad de incidentes. SemVer da a Renovate/Dependabot y a los consumidores una señal fiable del riesgo de actualizar.

## Ejemplos
### Mal
```xml
<dependency>
  <groupId>com.example</groupId>
  <artifactId>billing-client</artifactId>
  <version>1.4.0-SNAPSHOT</version> <!-- en rama release -->
</dependency>
```
### Bien
```xml
<version>${revision}</version>
<properties>
  <revision>1.4.0-SNAPSHOT</revision>
</properties>
```
```text
# en CI de release (tag v1.4.0), sin SNAPSHOT
./mvnw -B -Drevision=1.4.0 verify
```

## Checklist de revisión
- [ ] Versión release sin `-SNAPSHOT`.
- [ ] Ninguna dependencia SNAPSHOT en `main`/release.
- [ ] Cambio incompatible implica MAJOR.
- [ ] El tag git coincide con la versión publicada.
- [ ] El repositorio de artefactos rechaza re-subida de releases.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Enforcer `requireReleaseDeps` (perfil release) | 1 | `policies/maven-enforcer/banned-dependencies.example.xml` |
| Política de repositorio de artefactos: releases inmutables | 3 | configuración del repositorio (pendiente, proyecto generado) |
| Revisión de bump MAJOR/MINOR/PATCH | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `release-automation`, `reproducible-builds`, `bom-management`, `api-versioning-deprecation`.
- Fuentes: Semantic Versioning 2.0.0 (semver.org); Apache Maven, "Maven CI Friendly Versions".
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
