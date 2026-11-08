---
name: maven-multimodule-layout
description: "Usar al estructurar o revisar un proyecto Maven multimódulo: módulos, aggregator vs parent, dependencias entre módulos y límites de arquitectura."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Layout Maven multimódulo

## Cuándo aplicar y cuándo no
- Aplica al crear un servicio Java/Spring Boot con más de un módulo Maven o al añadir/mover módulos.
- No aplica a microservicios triviales de un solo módulo: no partir en módulos "por si acaso".

## Reglas
- **MUST** separar el `pom.xml` raíz en dos roles claros: parent (configuración heredada, ver `parent-pom`) y aggregator (`<modules>`). Pueden coincidir en el raíz, pero sin lógica de negocio.
- **MUST** nombrar módulos por responsabilidad, no por capa técnica genérica: `orders-domain`, `orders-application`, `orders-adapter-rest`, `orders-adapter-jpa`, `orders-boot`.
- **MUST** que `*-domain` no dependa de Spring, JPA ni de adaptadores; solo del JDK y librerías puras.
- **MUST** que las dependencias entre módulos formen un DAG dirigido hacia el dominio (adapter -> application -> domain). Cero ciclos.
- **MUST** que solo el módulo `*-boot` aplique `spring-boot-maven-plugin` y contenga la clase `@SpringBootApplication`.
- **SHOULD** declarar las versiones de módulos internos con `${project.version}` en `dependencyManagement` del parent, nunca literales repetidos.
- **SHOULD** usar un módulo `*-bom` o `dependencyManagement` propio si hay más de 3 módulos publicables (ver `bom-management`).
- **MUST NOT** crear módulos `common`/`utils` cajón de sastre.
- **MUST NOT** usar `<scope>system</scope>` ni `systemPath`.

## Por qué
La estructura de módulos es la forma más barata de hacer cumplir la arquitectura hexagonal: si `domain` no tiene Spring en el classpath, no puede importarlo. Un módulo cajón de sastre acaba siendo el núcleo de un monolito acoplado (ver `connascence-and-coupling`). El orden de reactor lo calcula Maven desde las dependencias, no desde el orden de `<modules>`.

## Ejemplos
### Mal
```xml
<modules>
  <module>common</module>   <!-- utilidades de todo tipo -->
  <module>service</module>  <!-- entidades JPA + controllers + dominio juntos -->
</modules>
```
### Bien
```xml
<!-- pom.xml raíz -->
<packaging>pom</packaging>
<modules>
  <module>orders-domain</module>
  <module>orders-application</module>
  <module>orders-adapter-rest</module>
  <module>orders-adapter-jpa</module>
  <module>orders-boot</module>
</modules>
```
```xml
<!-- orders-application/pom.xml: depende solo del dominio -->
<dependency>
  <groupId>com.example.orders</groupId>
  <artifactId>orders-domain</artifactId>
  <version>${project.version}</version>
</dependency>
```
Build parcial: `./mvnw -pl orders-boot -am verify` compila el módulo y lo que necesita.

## Checklist de revisión
- [ ] `*-domain` no tiene Spring/JPA en su árbol de dependencias.
- [ ] No hay ciclos ni módulos `common`/`utils`.
- [ ] Solo `*-boot` empaqueta el ejecutable.
- [ ] Versiones internas vía `${project.version}`.
- [ ] Reglas ArchUnit de límites de módulo pasan.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit de aislamiento de dominio | 1 | `policies/archunit/DomainIsolationRules.java` |
| Regla ArchUnit de límites entre módulos | 1 | `policies/archunit/ModuleBoundaryRules.java` |
| Enforcer `bannedDependencies` en `*-domain` (sin Spring/JPA) | 1 | `policies/maven-enforcer/banned-dependencies.example.xml` |
| Hook de guarda de arquitectura tras editar | 2 | `.claude/hooks/post-tool-use/architecture_guard.py` |
| Revisión de la partición de módulos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `parent-pom`, `bom-management`, `enforcer-rules`, `clean-architecture`, `connascence-and-coupling`.
- Fuentes: Apache Maven, "Guide to Working with Multiple Modules" (maven.apache.org) — consultar vigente (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
