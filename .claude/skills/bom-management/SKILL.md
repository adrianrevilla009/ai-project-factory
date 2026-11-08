---
name: bom-management
description: "Usar al fijar versiones de dependencias con un BOM corporativo: importación, overrides, actualización y publicación del BOM."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Gestión de BOM

## Cuándo aplicar y cuándo no
- Aplica al declarar dependencias en cualquier módulo, al crear/actualizar el BOM corporativo y al sobrescribir una versión.
- No aplica a plugins (van en `pluginManagement`, ver `parent-pom`) ni a dependencias npm (lockfiles, ver `dependency-hygiene`).

## Reglas
- **MUST** importar los BOM por `<scope>import</scope>` con `<type>pom</type>` dentro de `dependencyManagement`; orden: BOM corporativo primero, resto después (el primero que declara gana).
- **MUST** que los módulos declaren dependencias SIN `<version>` cuando el BOM la gestiona.
- **MUST** que el BOM corporativo importe `spring-boot-dependencies` y fije versiones de librerías aprobadas (`catalog/approved-libraries.yaml`); las versiones concretas son TODO-VERIFY hasta confirmarlas en fuente oficial.
- **MUST** documentar cada override de versión con comentario, motivo (CVE, bug), ticket y fecha de retirada.
- **SHOULD** versionar el BOM con semver y publicarlo como artefacto propio (`com.example:platform-bom`).
- **SHOULD** que el BOM sea solo `dependencyManagement`: sin `<dependencies>`.
- **MUST NOT** redefinir propiedades `*.version` de Spring Boot sin pasar por el BOM.
- **MUST NOT** usar licencias de pago ni librerías fuera de `approved-libraries.yaml` sin ADR.

## Por qué
Sin BOM, cada servicio resuelve versiones distintas de Jackson, Netty o Logback y los CVE se arreglan N veces. Con un BOM único, subir una versión es un PR y se propaga con Renovate/Dependabot (ver `renovate-dependabot-policy`). Los overrides sin fecha de retirada se vuelven deuda invisible.

## Ejemplos
### Mal
```xml
<dependency>
  <groupId>com.fasterxml.jackson.core</groupId>
  <artifactId>jackson-databind</artifactId>
  <version>2.0.0-example</version> <!-- versión literal en el módulo -->
</dependency>
```
### Bien
```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>com.example</groupId>
      <artifactId>platform-bom</artifactId>
      <version>${platform.bom.version}</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
<!-- en el módulo: sin versión -->
<dependency>
  <groupId>com.fasterxml.jackson.core</groupId>
  <artifactId>jackson-databind</artifactId>
</dependency>
```
Override justificado:
```xml
<!-- OVERRIDE: CVE-XXXX-example, ticket SEC-0000, retirar cuando el BOM >= x.y (2027-01-31) -->
```

## Checklist de revisión
- [ ] Ninguna dependencia gestionada lleva `<version>`.
- [ ] Cada override tiene motivo, ticket y fecha.
- [ ] El BOM no contiene `<dependencies>`.
- [ ] Todas las librerías están en `approved-libraries.yaml`.
- [ ] `mvn dependency:tree` sin versiones divergentes de la misma librería.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Enforcer `banDuplicatePomDependencyVersions` y `dependencyConvergence` | 1 | `policies/maven-enforcer/banned-dependencies.example.xml` |
| Catálogo de librerías aprobadas / prohibidas | 1 | `catalog/approved-libraries.yaml`, `catalog/forbidden-libraries.yaml` |
| Contenido del BOM corporativo | 1 | `catalog/bom/` (pendiente: solo estructura) |
| Revisión de overrides | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `parent-pom`, `dependency-hygiene`, `renovate-dependabot-policy`, `license-compliance`, `versioning-semver-snapshots`.
- Fuentes: Apache Maven, "Introduction to the Dependency Mechanism" (dependency management, import scope) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
