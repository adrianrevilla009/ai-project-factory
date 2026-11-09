---
name: sbom-generation
description: "Usar al generar, versionar o publicar el SBOM CycloneDX de un servicio Java o de una imagen, o al configurar el plugin CycloneDX en Maven y en CI."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Generación de SBOM (CycloneDX)

## Cuándo aplicar y cuándo no
- Aplica a cada artefacto liberable: JAR/aplicación Spring Boot, imagen de contenedor y bundle frontend.
- No aplica a ramas de trabajo efímeras ni a módulos de test que no se distribuyen.

## Reglas
- **MUST** generar un SBOM en formato CycloneDX (JSON) por cada release, a partir del grafo de dependencias real resuelto.
- **MUST** usar el plugin `org.cyclonedx:cyclonedx-maven-plugin` con versión fijada en `pluginManagement` del parent (`parent-pom`); versión exacta.
- **MUST** en multimódulo producir un SBOM agregado (goal `makeAggregateBom`) y no solo uno por módulo.
- **MUST** generar también el SBOM de la imagen final (`container-images`), no solo del JAR.
- **MUST** adjuntar el SBOM a la release como artefacto y conservarlo con la misma retención que el binario.
- **MUST NOT** editar a mano un SBOM; se regenera siempre desde el build.
- **SHOULD** alimentar el SBOM a la herramienta de análisis de vulnerabilidades y a `license-compliance`.
- **SHOULD** incluir el `serialNumber`/versión de build para trazar qué SBOM corresponde a qué release.

## Por qué
Ante una CVE nueva (p. ej. una librería de logging) la pregunta es "¿dónde la usamos?". Con SBOM por release la respuesta es una búsqueda, no una auditoría manual. El SBOM de la imagen cubre lo que el JAR no ve (paquetes del sistema base).

## Ejemplos
### Mal
```xml
<!-- Sin versión, solo en un módulo, SBOM no adjuntado -->
<plugin>
  <groupId>org.cyclonedx</groupId>
  <artifactId>cyclonedx-maven-plugin</artifactId>
</plugin>
```
### Bien
```xml
<!-- parent pom: pluginManagement fija versión; el módulo raíz agrega -->
<plugin>
  <groupId>org.cyclonedx</groupId>
  <artifactId>cyclonedx-maven-plugin</artifactId>
  <version>${cyclonedx-maven-plugin.version}</version>
  <executions>
    <execution>
      <phase>package</phase>
      <goals><goal>makeAggregateBom</goal></goals>
    </execution>
  </executions>
  <configuration>
    <outputFormat>json</outputFormat>
    <schemaVersion>1.5</schemaVersion>
  </configuration>
</plugin>
```
```text
# Resultado esperado tras mvn -B verify: target/bom.json en la raíz,
# subido en CI como artefacto de la release junto al JAR y a la imagen.
```

## Checklist de revisión
- [ ] Existe `bom.json` agregado tras el build de release.
- [ ] La versión del plugin está fijada en el parent.
- [ ] Hay SBOM de la imagen además del de la aplicación.
- [ ] El SBOM se archiva con la release.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de que el parent configura CycloneDX | 3 | agente `code-reviewer` |
| Paso CI que falla si falta `bom.json` | 1 | pendiente (pipeline del proyecto generado) |
| Validación del SBOM contra el esquema CycloneDX | 1 | pendiente |

> Estado: sin artefactos en la fábrica; la fábrica no ejecuta builds de proyectos.

## Relacionados, fuentes y mantenimiento
- Relacionados: `license-compliance`, `container-images`, `parent-pom`, `reproducible-builds`, `supply-chain`.
- Fuentes: cyclonedx.org (especificación) y documentación del plugin cyclonedx-maven-plugin; consultadas 2026-11-07.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
