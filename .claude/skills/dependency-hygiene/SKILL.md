---
name: dependency-hygiene
description: "Usar al añadir, quitar o revisar dependencias Maven/npm: mínimas, declaradas, sin no usadas, sin transitivas implícitas y con lockfile."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Higiene de dependencias

## Cuándo aplicar y cuándo no
- Aplica al añadir una dependencia, al limpiar un POM o `package.json`, y en revisiones de PR que tocan el build.
- No aplica a la gestión de CVE (ver `dependency-security`) ni a licencias (ver `license-compliance`).

## Reglas
- **MUST** justificar toda dependencia nueva en el PR (qué problema resuelve y alternativa JDK/Spring considerada); debe estar en `catalog/approved-libraries.yaml` o llevar ADR.
- **MUST** declarar explícitamente lo que el código usa (no depender de transitivas): `mvn dependency:analyze` sin "used undeclared".
- **MUST** eliminar las "unused declared" salvo excepción documentada (`ignoredUnusedDeclaredDependencies`).
- **MUST** usar `scope` correcto: `test`, `provided`, `runtime`; **MUST NOT** dejar librerías de test en `compile`.
- **MUST** excluir transitivas problemáticas con `<exclusions>` comentadas, no con versiones forzadas ad hoc.
- **MUST** commitear el lockfile de frontend (`package-lock.json` o `pnpm-lock.yaml`) e instalar en CI con `npm ci` / `pnpm install --frozen-lockfile`.
- **SHOULD** preferir `starter` de Spring Boot sobre listas manuales de artefactos.
- **SHOULD** revisar el árbol (`dependency:tree`) cuando una dependencia añade más de ~10 transitivas.
- **MUST NOT** añadir librerías abandonadas (sin release en >2 años) sin ADR.

## Por qué
Cada dependencia es superficie de ataque, de licencia y de mantenimiento. Las transitivas implícitas rompen cuando el proveedor las retira. Un lockfile ausente convierte `npm install` en una lotería diaria.

## Ejemplos
### Mal
```xml
<dependency>
  <groupId>org.junit.jupiter</groupId>
  <artifactId>junit-jupiter</artifactId> <!-- scope compile por omisión sin BOM de test -->
</dependency>
```
```text
npm install   # en CI, ignora el lockfile
```
### Bien
```xml
<dependency>
  <groupId>org.junit.jupiter</groupId>
  <artifactId>junit-jupiter</artifactId>
  <scope>test</scope>
</dependency>
<plugin>
  <artifactId>maven-dependency-plugin</artifactId>
  <executions><execution>
    <id>analyze</id>
    <goals><goal>analyze-only</goal></goals>
    <configuration><failOnWarning>true</failOnWarning></configuration>
  </execution></executions>
</plugin>
```
```text
npm ci
```
(versión del plugin)

## Checklist de revisión
- [ ] Dependencia nueva justificada y en el catálogo.
- [ ] `dependency:analyze` limpio.
- [ ] Scopes correctos.
- [ ] Lockfile actualizado y usado con `ci`/`frozen-lockfile`.
- [ ] Sin librerías prohibidas (`forbidden-libraries.yaml`).

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| `maven-dependency-plugin:analyze-only` con `failOnWarning` | 1 | parent POM del proyecto generado (ejemplo en el bloque Bien) |
| Enforcer `dependencyConvergence` y librerías prohibidas | 1 | `policies/maven-enforcer/banned-dependencies.example.xml` |
| Hook de librerías prohibidas | 2 | `.claude/hooks/post-tool-use/forbidden_deps.py` |
| Justificación de nuevas dependencias | 3 | revisión humana / agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `enforcer-rules`, `bom-management`, `dependency-security`, `license-compliance`, `sbom-generation`.
- Fuentes: Apache Maven Dependency Plugin (analyze goals); documentación de npm (`npm ci`); fecha de referencia 2026-11-07.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
