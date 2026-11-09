---
name: parent-pom
description: "Usar al crear o modificar el parent POM corporativo o el pom raíz: propiedades, pluginManagement, perfiles y herencia de Spring Boot."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Parent POM

## Cuándo aplicar y cuándo no
- Aplica al definir el pom padre de un servicio o del conjunto corporativo, y al añadir plugins o propiedades compartidas.
- No aplica a versiones de librerías de terceros (ver `bom-management`) ni a reglas de build prohibidas (ver `enforcer-rules`).

## Reglas
- **MUST** fijar en propiedades: `java.version` (o `maven.compiler.release`), `project.build.sourceEncoding=UTF-8` y `project.build.outputTimestamp` (ver `reproducible-builds`).
- **MUST** declarar versiones de plugins en `<pluginManagement>`; ningún plugin sin versión explícita.
- **MUST** usar `maven.compiler.release` en lugar de `source`/`target` para compilar contra la API correcta del JDK.
- **MUST** aplicar el enforcer (`maven-enforcer-plugin`) desde el parent con las reglas de `enforcer-rules`.
- **SHOULD** heredar de `spring-boot-starter-parent` solo si el parent corporativo no puede importar el BOM de Spring Boot; si ya hay parent corporativo, importar `spring-boot-dependencies` por scope `import`.
- **SHOULD** mantener perfiles mínimos (`ci`, `release`); la lógica específica de entorno va fuera del POM.
- **MUST NOT** declarar `<repositories>` ni `<pluginRepositories>` en el POM: la resolución va por `settings.xml`/mirror corporativo.
- **MUST NOT** meter dependencias reales en `<dependencies>` del parent salvo las realmente universales (p. ej. test).
- **MUST NOT** usar rangos de versión (`[1.0,)`), `LATEST` ni `RELEASE`.

## Por qué
El parent es el único sitio donde cambiar una política afecta a todos los módulos. Plugins sin versión hacen que el build cambie con la versión de Maven instalada; repositorios en el POM abren la puerta a dependency confusion y rompen el mirror corporativo.

## Ejemplos
### Mal
```xml
<repositories>
  <repository><id>random</id><url>http://repo.example.invalid/maven</url></repository>
</repositories>
<build><plugins>
  <plugin><artifactId>maven-compiler-plugin</artifactId></plugin> <!-- sin versión -->
</plugins></build>
```
### Bien
```xml
<properties>
  <maven.compiler.release>21</maven.compiler.release>
  <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  <project.build.outputTimestamp>2026-01-01T00:00:00Z</project.build.outputTimestamp>
</properties>
<build>
  <pluginManagement>
    <plugins>
      <plugin>
        <artifactId>maven-compiler-plugin</artifactId>
        <version></version>
      </plugin>
    </plugins>
  </pluginManagement>
</build>
```

## Checklist de revisión
- [ ] Todos los plugins con versión en `pluginManagement`.
- [ ] `release` en lugar de `source`/`target`; encoding UTF-8.
- [ ] Sin `<repositories>` ni rangos de versión.
- [ ] Enforcer activo desde el parent.
- [ ] `outputTimestamp` definido.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Enforcer `requirePluginVersions`, `requireMavenVersion`, `requireJavaVersion` | 1 | `policies/maven-enforcer/banned-dependencies.example.xml` |
| Hook de librerías prohibidas al editar `pom.xml` | 2 | `.claude/hooks/post-tool-use/forbidden_deps.py` |
| Revisión del parent al cambiar políticas globales | 3 | revisión humana (factory-owner) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `maven-multimodule-layout`, `bom-management`, `enforcer-rules`, `reproducible-builds`, `maven-wrapper-and-toolchains`.
- Fuentes: Apache Maven POM Reference y documentación de Spring Boot (using the Maven plugin / parent).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
