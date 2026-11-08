---
name: graceful-shutdown-lifecycle
description: Usar al configurar parada ordenada de servicios Spring Boot (server.shutdown=graceful), timeouts de fase y ciclo de vida de beans y tareas.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Parada ordenada y ciclo de vida

## Cuándo aplicar y cuándo no
- Aplica a servicios Spring Boot en contenedores con despliegues rolling, autoescalado o spot.
- No aplica a jobs batch de vida corta sin tráfico entrante (ver `batch-file-sftp-integration`).

## Reglas
- **MUST** activar `server.shutdown=graceful` y fijar `spring.lifecycle.timeout-per-shutdown-phase` (p. ej. `25s`).
- **MUST** que el timeout de la fase sea menor que el periodo de gracia del orquestador (en Kubernetes, `terminationGracePeriodSeconds`) con margen.
- **MUST** dejar de recibir tráfico antes de parar: readiness pasa a DOWN al iniciar el apagado (comportamiento de Spring Boot con probes) y se considera un pequeño `preStop` de espera para la propagación del balanceador.
- **MUST** liberar recursos en `@PreDestroy` o `SmartLifecycle`/`DisposableBean`, de forma rápida e idempotente.
- **MUST** que los executors propios usen `setWaitForTasksToCompleteOnShutdown(true)` y `setAwaitTerminationSeconds(...)`; no crear `new Thread` sin gestión.
- **MUST** que los consumidores de mensajes dejen de consumir y terminen o devuelvan los mensajes en curso antes de cerrar (ver `delivery-semantics`).
- **SHOULD** diseñar las operaciones para ser idempotentes: un SIGKILL tras el timeout puede cortar trabajo.
- **MUST NOT** capturar SIGTERM manualmente ni usar `System.exit` en código de negocio.

## Por qué
Sin parada ordenada, cada despliegue corta peticiones en vuelo y produce errores 5xx visibles. Si el timeout de Spring supera el periodo de gracia del orquestador, el proceso muere a mitad por SIGKILL y la configuración no sirve.

## Ejemplos
### Mal
```yaml
# Valores por defecto: server.shutdown=immediate, sin timeout de fase
spring:
  application:
    name: orders
```
```java
new Thread(this::processQueue).start();   // hilo sin ciclo de vida
```
### Bien
```yaml
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 25s
```
```java
@Bean
ThreadPoolTaskExecutor reportExecutor() {
    var executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(4);
    executor.setWaitForTasksToCompleteOnShutdown(true);
    executor.setAwaitTerminationSeconds(20);
    return executor;
}
```
```yaml
# Kubernetes (ejemplo, no desplegado por la fábrica)
terminationGracePeriodSeconds: 40   # > 25s de Spring + preStop
```

## Checklist de revisión
- [ ] `server.shutdown: graceful` y timeout de fase definido.
- [ ] Timeout de Spring < periodo de gracia del orquestador.
- [ ] Executors y consumidores con parada ordenada.
- [ ] Sin hilos manuales ni `System.exit`.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Conftest: `terminationGracePeriodSeconds` y probes en manifiestos | 1 | `policies/opa-conftest/` (pendiente) |
| Test de integración de apagado con petición en vuelo | 1 | tests del proyecto generado |
| Revisión de configuración de ciclo de vida | 3 | agente `code-reviewer` |

Local: se puede comprobar con `docker stop` o `kill -TERM`; no se reproduce el drenaje de un ALB/target group de AWS. Preparado para AWS, no verificado en real.

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `actuator-and-health`, `resilience`, `delivery-semantics`, `startup-and-native`.
- Fuentes oficiales: Spring Boot Reference "Graceful Shutdown", consultada 2026-11-07; comprobar comportamiento de readiness durante el apagado en la versión vigente.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
