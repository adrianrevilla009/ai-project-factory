---
name: jvm-in-containers
description: Usar al dimensionar o configurar la JVM en contenedores y Kubernetes (memoria, CPU, flags de heap, OOM, GC y límites de recursos coherentes).
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# JVM en contenedores

## Cuándo aplicar y cuándo no
- Aplica a Dockerfiles, manifiestos Kubernetes y configuración de arranque de servicios Java.
- No aplica a imágenes nativas (GraalVM native image), que no tienen heap JVM clásico (ver `startup-and-native`). Nada de esto se ha verificado en un clúster real: preparado para AWS, no verificado en real.

## Reglas
- **MUST** fijar `resources.requests` y `resources.limits` de memoria iguales (QoS Guaranteed/predecible) y declarar CPU request.
- **MUST** dimensionar el heap como porcentaje del límite del contenedor con `-XX:MaxRAMPercentage` (típico 60-75 %); **MUST NOT** fijar `-Xmx` en valor absoluto que ignore el límite del pod.
- **MUST** dejar margen para memoria fuera del heap (metaspace, hilos, buffers directos, código compilado): heap + no-heap debe caber en el límite.
- **MUST** arrancar con `-XX:+ExitOnOutOfMemoryError` para que Kubernetes reinicie el pod en vez de quedar medio vivo.
- **SHOULD** activar `-XX:+HeapDumpOnOutOfMemoryError` con `-XX:HeapDumpPath` en un volumen con espacio, solo si el dump no filtra datos personales fuera de los controles.
- **MUST** ejecutar como usuario no root, imagen base mínima y sin shell innecesaria (ver estándares de contenedores, ADR-0018).
- **SHOULD** pasar opciones con `JAVA_TOOL_OPTIONS` o `JAVA_OPTS` documentadas, no en el `ENTRYPOINT` en duro.
- **SHOULD** dejar que la JVM detecte los CPU del cgroup; **MUST NOT** fijar `-XX:ActiveProcessorCount` sin medir.
- **MUST** configurar `terminationGracePeriodSeconds` mayor que el apagado ordenado de la aplicación (ver `graceful-shutdown-lifecycle`).
- **SHOULD** medir con carga antes de elegir GC; el GC por defecto suele bastar.

## Por qué
Si el heap supera el límite del cgroup, el kernel mata el proceso con OOMKilled sin traza de Java. Un `-Xmx` fijo diverge del límite cuando alguien cambia el manifiesto. Sin `ExitOnOutOfMemoryError`, una JVM en OOM puede quedar degradada y seguir pasando el liveness.

## Ejemplos
### Mal
```yaml
containers:
  - name: orders
    image: registry.example/orders:1.0.0
    command: ["java", "-Xmx4g", "-jar", "app.jar"]   # el límite es 1Gi
    resources:
      limits: { memory: "1Gi" }
```
### Bien
```yaml
containers:
  - name: orders
    image: registry.example/orders:1.0.0
    env:
      - name: JAVA_TOOL_OPTIONS
        value: >-
          -XX:MaxRAMPercentage=70
          -XX:+ExitOnOutOfMemoryError
    resources:
      requests: { memory: "1Gi", cpu: "500m" }
      limits:   { memory: "1Gi" }
    securityContext: { runAsNonRoot: true, readOnlyRootFilesystem: true }
```

## Checklist de revisión
- [ ] Requests y limits de memoria definidos y coherentes.
- [ ] Heap por porcentaje, no `-Xmx` absoluto.
- [ ] `ExitOnOutOfMemoryError` activo; usuario no root.
- [ ] Grace period mayor que el apagado de la aplicación.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Política Kyverno/Rego: pods con limits de memoria y sin root | 1 | `policies/kyverno/`, `policies/opa-conftest/` (pendiente de reglas concretas) |
| Revisión de flags JVM por carga medida | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `profiling-and-leaks`, `graceful-shutdown-lifecycle`, `startup-and-native`, `threads-executors-and-pools`.
- Fuentes: documentación del comando `java` de OpenJDK/Oracle (opciones `MaxRAMPercentage`, `ExitOnOutOfMemoryError`) y Kubernetes "Resource Management"; no consultado en línea.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
