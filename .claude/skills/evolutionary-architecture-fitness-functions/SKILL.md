---
name: evolutionary-architecture-fitness-functions
description: "Usar al definir cómo se protegen automáticamente las características de la arquitectura (dependencias, rendimiento, seguridad) mediante fitness functions en CI."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "archunit"
---

# Arquitectura evolutiva y fitness functions

## Cuándo aplicar y cuándo no
- Aplica al cerrar una decisión de arquitectura que debe sobrevivir al tiempo: límites de módulos, tiempos de respuesta, ausencia de ciclos, versiones permitidas.
- No aplica a decisiones locales reversibles ni a reglas que nadie piensa mantener: una fitness function que se ignora en rojo es peor que ninguna.

## Reglas
- **MUST** convertir cada característica arquitectónica priorizada (ver `quality-attributes-atam`) en al menos una fitness function ejecutable o declarar "revisión humana".
- **MUST** ejecutar las fitness functions en CI y que un fallo bloquee el merge (no solo informe).
- **MUST** dar a cada una un dueño, un umbral explícito y un mensaje de error que indique cómo corregir.
- **MUST** versionar las fitness functions junto al código, y evolucionarlas con ADR cuando cambie la decisión.
- **SHOULD** combinar tipos: estructurales (ArchUnit, dependency-cruiser), de rendimiento (test de carga con umbral), de seguridad (escáner de dependencias) y de datos (migraciones compatibles).
- **SHOULD** empezar con pocas (3-5) de alto valor y ampliar por incidentes reales.
- **SHOULD** preferir cambios incrementales guiados por estas reglas antes que reescrituras.
- **MUST NOT** desactivar una fitness function para "pasar el build"; se corrige el código o se enmienda la decisión mediante ADR.
- **MUST NOT** afirmar cumplimiento de características de despliegue AWS solo por pasar tests locales; preparado para AWS, no verificado en real.

## Por qué
Los documentos de arquitectura se erosionan; lo que no se comprueba automáticamente se degrada con cada PR. Las fitness functions convierten decisiones en guardarraíles verificables y hacen barato cambiar con seguridad.

## Ejemplos
### Mal
```text
ADR-012: "El módulo billing no depende de sales." (solo texto; nadie lo comprueba)
```
### Bien
```java
@ArchTest
static final ArchRule billing_does_not_depend_on_sales =
    noClasses().that().resideInAPackage("..billing..")
               .should().dependOnClassesThat().resideInAPackage("..sales..")
               .because("ADR-012: billing consume eventos, no clases de sales");

@ArchTest
static final ArchRule no_cycles =
    slices().matching("com.example.(*)..").should().beFreeOfCycles();
```
```text
Fitness de rendimiento (CI): k6 con umbral  http_req_duration p(95) < 300ms ; fallo = build rojo.
```

## Checklist de revisión
- [ ] Cada característica priorizada tiene fitness function o revisión humana declarada.
- [ ] Se ejecutan en CI y bloquean el merge.
- [ ] Mensajes de error accionables y dueño asignado.
- [ ] Ninguna está desactivada sin ADR.
- [ ] Hay ADR enlazado en cada regla.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Ejemplo ArchUnit de aislamiento de dominio | 1 | `policies/archunit/DomainIsolationRules.java` |
| `make validate` en la fábrica; CI del proyecto generado para el resto | 1 | `Makefile`, CI del proyecto generado |
| Revisión de umbrales y excepciones | 4 | gate de arquitectura (humano) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `layering-rules-archunit`, `quality-attributes-atam`, `connascence-and-coupling`, `tech-debt-management`.
- Fuentes: Ford, Parsons y Kua, "Building Evolutionary Architectures" (O'Reilly, 2.ª ed. 2023).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
