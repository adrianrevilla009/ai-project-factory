---
name: upgrade-policy
description: Usar al actualizar Spring Boot, Spring Framework o Java en un proyecto, o al fijar la política de versiones y soporte del stack.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Política de actualización de Spring Boot

## Cuándo aplicar y cuándo no
- Aplica a subidas de versión de Spring Boot, Spring Framework, Spring Modulith, Spring Cloud y de la versión de Java.
- No aplica a parches de dependencias menores gestionadas por Renovate/Dependabot (`renovate-dependabot-policy`, bloque 09).

## Reglas
- **MUST** estar en una línea de Spring Boot con soporte OSS vigente; comprobar las fechas de fin de soporte en la página oficial de versiones (TODO-VERIFY, no fijadas aquí).
- **MUST** subir versiones de parche dentro de la línea con frecuencia (mensual como objetivo) y por PR automático.
- **MUST** subir de línea menor/mayor de una en una, sin saltos, siguiendo la guía de migración oficial (Release Notes y Migration Guide del wiki de Spring Boot).
- **MUST** eliminar APIs `@Deprecated` en la línea actual antes de saltar a la siguiente.
- **MUST** gestionar versiones por el BOM de Spring Boot (`bom-management`); **MUST NOT** fijar a mano versiones de librerías que el BOM ya gestiona sin comentario justificado.
- **MUST** una subida por PR, con suite completa verde y sin mezclar cambios funcionales.
- **SHOULD** compatibilidad de Spring Cloud/Modulith verificada en su matriz oficial antes de subir Boot.
- **SHOULD** ejecutar OpenRewrite o la herramienta de migración oficial como ayuda, revisando el diff (TODO-VERIFY receta disponible).
- **MUST NOT** usar versiones SNAPSHOT/milestone/RC en ramas de producción.

## Por qué
Las líneas sin soporte dejan de recibir parches de seguridad. Subir poco y a menudo es más barato y seguro que saltos grandes tras años de deuda. La fábrica no fija números de versión en el skill porque caducan: la fuente de verdad es la documentación oficial en el momento de subir.

## Ejemplos
### Mal
```xml
<parent>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-parent</artifactId>
  <version>2.7.18</version>   <!-- línea sin soporte, sin plan de subida -->
</parent>
<dependency>
  <groupId>com.fasterxml.jackson.core</groupId>
  <artifactId>jackson-databind</artifactId>
  <version>2.9.0</version>    <!-- sobrescribe el BOM -->
</dependency>
```
### Bien
```xml
<parent>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-parent</artifactId>
  <version>${spring-boot.version}</version> <!-- definido en el parent corporativo, ver parent-pom -->
</parent>
<!-- jackson-databind sin <version>: lo gestiona el BOM -->
```
```text
Plan de subida (en el PR):
1. Compilar con -Xlint:deprecation y listar usos de APIs deprecadas.
2. Leer la Migration Guide de la línea destino.
3. Subir Boot; ejecutar suite completa y tests de contrato.
4. Registrar el cambio en el CHANGELOG del proyecto.
```

## Checklist de revisión
- [ ] La línea de Boot tiene soporte vigente (fecha comprobada).
- [ ] Una sola subida por PR, sin saltos de línea.
- [ ] Sin APIs deprecadas pendientes.
- [ ] Versiones gestionadas por el BOM.
- [ ] Suite completa verde.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Maven Enforcer: prohibir SNAPSHOT/RC en release | 1 | `enforcer-rules` (bloque 09, pendiente) |
| Renovate/Dependabot para parches | 1 | pendiente (política bloque 09) |
| Revisión humana de subidas de línea | 4 | gate de arquitectura |

## Relacionados, fuentes y mantenimiento
- Relacionados: `bom-management`, `parent-pom`, `renovate-dependabot-policy`, `startup-and-native`.
- Fuentes: Spring Boot: página de versiones soportadas y Migration Guide (wiki oficial) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
