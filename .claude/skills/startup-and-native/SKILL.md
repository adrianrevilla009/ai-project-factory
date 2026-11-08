---
name: startup-and-native
description: Usar al optimizar el arranque de una aplicación Spring Boot o al evaluar compilación nativa GraalVM, AOT, CDS o lazy initialization.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Arranque y compilación nativa

## Cuándo aplicar y cuándo no
- Aplica cuando el tiempo de arranque o el consumo de memoria es un requisito medido (autoescalado, funciones, contenedores efímeros).
- No aplica a servicios de larga vida donde el arranque de segundos es irrelevante: no optimizar sin requisito.

## Reglas
- **MUST** medir antes de optimizar: registrar tiempo de arranque (log `Started ... in X seconds`) y memoria base como línea base.
- **MUST** arrancar con JVM estándar por defecto; la imagen nativa es opt-in con justificación en un ADR del proyecto.
- **SHOULD** probar primero opciones baratas: eliminar auto-configuraciones y dependencias no usadas, CDS/AppCDS, `spring.main.lazy-initialization` (con cautela: oculta errores de cableado hasta la primera petición).
- **MUST** que, si se adopta nativo, el build nativo se ejecute en CI y los tests corran también en modo nativo (`native:test`, TODO-VERIFY).
- **MUST** declarar hints para reflexión/recursos (`RuntimeHintsRegistrar`, `@RegisterReflectionForBinding`) en lugar de ficheros JSON manuales cuando sea posible.
- **MUST NOT** usar reflexión dinámica, proxies o carga de clases en tiempo de ejecución sin comprobar su compatibilidad AOT.
- **MUST NOT** asumir que una librería es compatible con nativo; verificar su soporte en su documentación.
- **SHOULD** limitar el trabajo en `@PostConstruct` y `ApplicationRunner` (conexiones remotas, cargas masivas): bloquean el arranque y la readiness.

## Por qué
Nativo reduce arranque y memoria a cambio de builds más lentos, menos dinámica (reflexión, proxies), peor diagnóstico y mayor coste de mantenimiento. Muchas veces CDS o recortar dependencias consigue lo suficiente. Cifras concretas dependen de la aplicación: no se prometen aquí.

## Ejemplos
### Mal
```java
@Component
class CacheWarmer {
    @PostConstruct
    void warm() {
        repository.findAll().forEach(cache::put);   // bloquea el arranque con una carga completa
    }
}
```
### Bien
```java
@Component
class CacheWarmer {
    @EventListener(ApplicationReadyEvent.class)
    @Async
    void warm() {
        repository.findHotItems(PageRequest.of(0, 500)).forEach(cache::put);
    }
}
```
```text
# Build nativo (solo si hay ADR; requiere GraalVM; perfil "native" de spring-boot-starter-parent)
./mvnw -Pnative native:compile
```

## Checklist de revisión
- [ ] Existe línea base medida de arranque y memoria.
- [ ] Hay ADR si se usa nativo.
- [ ] Hints AOT declarados para reflexión/recursos.
- [ ] Tests ejecutados también en nativo (si aplica).
- [ ] `@PostConstruct` sin I/O pesado.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de ADR y de `@PostConstruct` nuevos | 3 | agente `code-reviewer` |
| Job de CI de build nativo | 1 | pendiente (plantilla de CI de proyecto generado) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `graceful-shutdown-lifecycle`, `actuator-and-health`, `upgrade-policy`.
- Fuentes: Spring Boot Reference (GraalVM Native Image, AOT, CDS) y documentación de GraalVM (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
