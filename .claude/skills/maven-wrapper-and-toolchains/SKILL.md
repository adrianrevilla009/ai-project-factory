---
name: maven-wrapper-and-toolchains
description: "Usar al configurar cómo se invoca Maven (mvnw) y qué JDK compila el proyecto: Maven Wrapper, toolchains.xml y consistencia entre local y CI."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Maven Wrapper y toolchains

## Cuándo aplicar y cuándo no
- Aplica a todo proyecto Maven generado: scripts de CI, Dockerfiles de build, documentación de arranque.
- No aplica a proyectos que no usan Maven (frontend con npm tiene su propio gestor).

## Reglas
- **MUST** versionar `mvnw`, `mvnw.cmd` y `.mvn/wrapper/maven-wrapper.properties` en el repositorio.
- **MUST** invocar siempre `./mvnw` (local, CI, Docker); **MUST NOT** depender de un `mvn` instalado en la máquina.
- **MUST** fijar la versión de Maven en el wrapper y exigirla con `maven-enforcer-plugin` (`requireMavenVersion`, ver `enforcer-rules`).
- **MUST** declarar el JDK de compilación con toolchains o con `maven.compiler.release`, no con lo que haya en el `PATH`.
- **SHOULD** usar `maven-toolchains-plugin` y un `toolchains.xml` generado en CI (no versionar rutas absolutas personales).
- **MUST** usar `release` (no solo `source`/`target`) para que la API compilada coincida con el JDK objetivo.
- **SHOULD** fijar la versión del propio plugin del wrapper al actualizarlo y revisar el diff de `maven-wrapper.properties` (la URL de distribución es superficie de ataque).
- **MUST NOT** apuntar `distributionUrl` a repositorios no corporativos sin verificar checksum.

## Por qué
"Funciona en mi máquina" suele ser una versión distinta de Maven o de JDK. El wrapper hace que la versión viaje con el código; los toolchains separan el JDK que ejecuta Maven del que compila, útil durante migraciones de JDK (`jdk-distribution-and-upgrade-cadence`).

## Ejemplos
### Mal
```text
# README: "instala Maven 3.x y Java 21"
mvn clean install        # versión y JDK dependen de cada máquina
```
### Bien
```properties
# .mvn/wrapper/maven-wrapper.properties
distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.9/apache-maven-3.9.9-bin.zip

```
```xml
<!-- parent pom -->
<properties>
  <maven.compiler.release>21</maven.compiler.release>
</properties>
```
```xml
<!-- toolchains.xml generado en CI -->
<toolchains>
  <toolchain>
    <type>jdk</type>
    <provides><version>21</version><vendor>temurin</vendor></provides>
    <configuration><jdkHome>${env.JAVA_HOME}</jdkHome></configuration>
  </toolchain>
</toolchains>
```
```text
./mvnw -B verify
```

## Checklist de revisión
- [ ] `mvnw` y `.mvn/wrapper/` están en git.
- [ ] CI y Dockerfile llaman a `./mvnw`.
- [ ] El enforcer exige la versión de Maven y de Java.
- [ ] `maven.compiler.release` definido en el parent.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| `maven-enforcer-plugin` (`requireMavenVersion`, `requireJavaVersion`) | 1 | `pom.xml` del parent del proyecto generado |
| Revisión de scripts que llamen a `mvn` directo | 3 | agente `code-reviewer` |
| Regla de búsqueda de `mvn ` en CI | 1 | pendiente |

## Relacionados, fuentes y mantenimiento
- Relacionados: `enforcer-rules`, `parent-pom`, `jdk-distribution-and-upgrade-cadence`, `reproducible-builds`.
- Fuentes: maven.apache.org (Maven Wrapper, Guide to Using Toolchains); consultadas 2026-11-07.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
