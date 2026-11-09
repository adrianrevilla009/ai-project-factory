---
name: enforcer-rules
description: "Usar al configurar maven-enforcer-plugin en el parent: versiones mínimas, convergencia, librerías prohibidas (Lombok) y reglas de release."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Reglas del Maven Enforcer

## Cuándo aplicar y cuándo no
- Aplica al definir el build de un proyecto generado (en el parent POM) y al añadir una librería prohibida al catálogo.
- No aplica a reglas de código fuente (van a Semgrep/ArchUnit) ni a vulnerabilidades (ver `dependency-security`).

## Reglas
- **MUST** ejecutar `maven-enforcer-plugin` en fase `validate` desde el parent, con `fail=true`.
- **MUST** incluir: `requireMavenVersion`, `requireJavaVersion`, `requirePluginVersions`, `banDuplicatePomDependencyVersions`, `dependencyConvergence`.
- **MUST** derivar `bannedDependencies` de `catalog/forbidden-libraries.yaml` (fuente de verdad); incluir `org.projectlombok:lombok` (D27, skill `no-lombok`), `log4j:log4j`, `commons-collections:commons-collections`, `joda-time:joda-time`.
- **MUST** usar `searchTransitive=true` para que una dependencia transitiva prohibida también falle.
- **MUST** añadir `requireReleaseDeps` y `requireReleaseVersion` en el perfil `release` (ver `versioning-semver-snapshots`).
- **SHOULD** en módulos `*-domain` banear `org.springframework:*` y `jakarta.persistence:*`.
- **SHOULD** dar un `<message>` accionable en cada regla que apunte al skill.
- **MUST NOT** desactivar el enforcer con `-Denforcer.skip=true` en CI.
- **MUST NOT** añadir excepciones sin ADR y fecha de caducidad.

## Por qué
El hook `forbidden_deps.py` avisa al agente al editar un `pom.xml`, pero solo el enforcer corta el build en CI: una dependencia transitiva con Lombok o Log4j 1.x no aparece en ningún diff. Convergencia y versiones de plugin evitan builds que cambian solos.

## Ejemplos
### Mal
```xml
<plugin>
  <artifactId>maven-enforcer-plugin</artifactId>
  <configuration><fail>false</fail></configuration> <!-- solo avisa -->
</plugin>
```
### Bien
Ver ejemplo completo en `policies/maven-enforcer/banned-dependencies.example.xml`. Extracto:
```xml
<bannedDependencies>
  <searchTransitive>true</searchTransitive>
  <excludes>
    <exclude>org.projectlombok:lombok</exclude>
    <exclude>log4j:log4j</exclude>
  </excludes>
  <message>Libreria prohibida por catalog/forbidden-libraries.yaml</message>
</bannedDependencies>
```
Comprobación local (comando de lectura, no despliega nada):
```text
./mvnw -B validate
```

## Checklist de revisión
- [ ] Enforcer en `validate` con `fail=true`.
- [ ] Lista de baneadas coincide con `catalog/forbidden-libraries.yaml`.
- [ ] `searchTransitive=true`.
- [ ] Perfil release con `requireReleaseDeps`.
- [ ] Sin `enforcer.skip` en CI ni en scripts.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Ejemplo de reglas Enforcer (incluye Lombok) | 1 | `policies/maven-enforcer/banned-dependencies.example.xml` |
| Catálogo de librerías prohibidas | 1 | `catalog/forbidden-libraries.yaml` |
| Hook al editar `pom.xml` | 2 | `.claude/hooks/post-tool-use/forbidden_deps.py` |
| Regla Semgrep contra `import lombok.` | 1 | `policies/semgrep/java-no-lombok.yaml` |
| Sincronía catálogo <-> XML | 3 | pendiente: validador; mientras tanto revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `no-lombok`, `parent-pom`, `dependency-hygiene`, `bom-management`, `dependency-security`.
- Fuentes: Apache Maven Enforcer Plugin, built-in rules (maven.apache.org/enforcer); fecha de referencia 2026-11-07.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
