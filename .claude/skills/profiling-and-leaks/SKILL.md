---
name: profiling-and-leaks
description: Usar al investigar latencia, uso de CPU/memoria, fugas de memoria o fugas de hilos y recursos en una aplicación Java; define método y herramientas.
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Profiling y fugas

## Cuándo aplicar y cuándo no
- Aplica a regresiones de rendimiento, crecimiento anómalo de heap, OOM, pausas de GC, agotamiento de hilos o conexiones.
- No aplica a optimización especulativa sin síntoma medido ni a microbenchmarks sin JMH.

## Reglas
- **MUST** medir antes de optimizar: definir la métrica (p99, throughput, heap tras GC), reproducir, cambiar una cosa, volver a medir.
- **MUST** perfilar con la herramienta del JDK primero: Java Flight Recorder (`jcmd <pid> JFR.start`) y `jcmd <pid> Thread.print`, `GC.heap_info`.
- **MUST** distinguir fuga de uso alto: una fuga es heap *después de GC completos* creciente en el tiempo.
- **MUST** capturar un heap dump (`jcmd <pid> GC.heap_dump`) en dos instantes y comparar los objetos retenidos (analizador como Eclipse MAT); buscar el camino al GC root.
- **MUST** tratar los heap dumps como datos sensibles: pueden contener credenciales y datos personales; no subirlos a herramientas externas ni a tickets.
- **MUST NOT** perfilar en producción con agentes de alto coste sin aprobación; JFR con configuración por defecto es de bajo overhead (TODO-VERIFY cifras).
- **SHOULD** vigilar causas típicas: cachés sin límite ni expiración, `ThreadLocal` no limpiado en pools, listeners no desregistrados, colecciones estáticas, `ClassLoader` retenido, conexiones/streams sin cerrar.
- **SHOULD** usar JMH para microbenchmarks; **MUST NOT** medir con `System.currentTimeMillis` en bucle y sin calentamiento.
- **SHOULD** exponer métricas JVM (heap, GC, hilos) y alertar sobre tendencias.

## Por qué
Optimizar sin datos suele mover el cuello de botella o empeorar la legibilidad. Un heap alto no es una fuga: la JVM usa la memoria disponible hasta el siguiente GC. La comparación de dos dumps muestra qué crece, no solo qué es grande.

## Ejemplos
### Mal
```java
// "Parece lento": se cambia a parallelStream() y se sube -Xmx sin medir
static final Map<String, Session> SESSIONS = new HashMap<>();   // nunca se purga
```
### Bien
```java
// cache acotada y con expiración (Caffeine u otra)
Cache<String, Session> sessions = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterAccess(Duration.ofMinutes(30))
    .build();
```
```text
# diagnóstico (comandos de lectura; sustituir <pid>)
jcmd <pid> VM.flags
jcmd <pid> GC.heap_info
jcmd <pid> JFR.start duration=60s filename=/tmp/rec.jfr
jcmd <pid> GC.heap_dump /tmp/heap-1.hprof
```

## Checklist de revisión
- [ ] Hay métrica base y comparación antes/después.
- [ ] Se distinguió fuga de uso alto con heap post-GC.
- [ ] Cachés y mapas estáticos tienen límite y expiración.
- [ ] Los dumps se almacenan y borran como datos sensibles.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión de cachés/`ThreadLocal`/recursos en PR | 3 | agente `code-reviewer` (pendiente de definir) |
| Dashboards y alertas de métricas JVM | 4 | revisión humana (pendiente; ver skills de observabilidad) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `jvm-in-containers`, `caching`, `connection-pooling`, `threads-executors-and-pools`.
- Fuentes: documentación de `jcmd` y Java Flight Recorder (docs.oracle.com / openjdk.org); Eclipse MAT — TODO-VERIFY URL y versión; no consultado en línea.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
