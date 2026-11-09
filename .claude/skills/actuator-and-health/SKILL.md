---
name: actuator-and-health
description: Usar al configurar Spring Boot Actuator, health checks, liveness/readiness y exposición segura de endpoints de gestión.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Actuator y health checks

## Cuándo aplicar y cuándo no
- Aplica a todo servicio Spring Boot que se ejecute en contenedor u orquestador.
- No aplica a la definición de dashboards y alertas (ver bloque de observabilidad).

## Reglas
- **MUST** incluir `spring-boot-starter-actuator` y exponer solo lo necesario: `management.endpoints.web.exposure.include=health,info,prometheus` (lista explícita).
- **MUST NOT** usar `include=*` ni exponer `env`, `heapdump`, `threaddump`, `beans`, `configprops` sin autenticación.
- **MUST** habilitar sondas: `management.endpoint.health.probes.enabled=true` y usar los grupos `liveness` y `readiness`.
- **MUST** mantener el liveness sin dependencias externas (BD, brokers): solo indica si el proceso está atascado. Las dependencias críticas van en readiness.
- **SHOULD** servir la gestión en un puerto separado (`management.server.port`) no publicado por el ingress.
- **SHOULD** `management.endpoint.health.show-details=when-authorized` (o `never` hacia fuera).
- **SHOULD** crear `HealthIndicator` propios con timeout corto; un indicador lento tumba la sonda.
- **MUST NOT** convertir un fallo de una dependencia opcional en readiness DOWN si el servicio puede degradarse (ver `resilience`).

## Por qué
Si liveness depende de la BD, una caída de la BD reinicia todos los pods en cascada y empeora el incidente. Los endpoints de gestión filtran configuración y memoria; exponerlos por defecto es una vulnerabilidad habitual.

## Ejemplos
### Mal
```yaml
management:
  endpoints:
    web:
      exposure:
        include: "*"          # expone env, heapdump...
  endpoint:
    health:
      show-details: always
```
### Bien
```yaml
management:
  server:
    port: 9091
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
  endpoint:
    health:
      probes:
        enabled: true
      show-details: when-authorized
      group:
        readiness:
          include: readinessState,db
        liveness:
          include: livenessState
```
```yaml
# Kubernetes (manifiesto de ejemplo, no desplegado por la fábrica)
livenessProbe:  { httpGet: { path: /actuator/health/liveness,  port: 9091 } }
readinessProbe: { httpGet: { path: /actuator/health/readiness, port: 9091 } }
```

## Criterios de decisión y trampas
### Cómo decidir
- Separa vivacidad (¿el proceso funciona?) de disponibilidad (¿puede recibir tráfico?); una dependencia caída no debería reiniciar el pod.
- Expón solo lo necesario y por un puerto o red de gestión.
### Trampas frecuentes
- Una comprobación de salud que depende de todas las dependencias y reinicia en cascada.
- Endpoints de gestión públicos.
- Detalles de salud con información sensible.
- Sonda de arranque ausente en aplicaciones lentas de arrancar.
- Métricas de alta cardinalidad.
### Evidencia
- Una prueba comprueba el comportamiento de las sondas cuando una dependencia falla.

## Checklist de revisión
- [ ] Lista explícita de endpoints expuestos, sin `*`.
- [ ] Probes habilitadas; liveness sin dependencias externas.
- [ ] Gestión en puerto interno o protegida.
- [ ] `HealthIndicator` propios con timeout.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep/Conftest contra `exposure.include: "*"` en YAML | 1 | `policies/opa-conftest/` (pendiente) |
| Test de contexto que verifica endpoints expuestos | 1 | tests del proyecto generado |
| Revisión de sondas en manifiestos | 3 | agente `code-reviewer` |

Local: las sondas se pueden probar con Docker Compose o kind; no se reproduce ningún balanceador de AWS (ALB/NLB) ni sus health checks. Preparado para AWS, no verificado en real.

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `graceful-shutdown-lifecycle`, `resilience`, `configuration-properties`, `startup-and-native`.
- Fuentes oficiales: Spring Boot Reference "Actuator" y "Kubernetes Probes", consultadas 2026-11-07; verificado en el apéndice de propiedades de Spring Boot 4.x el 2026-11-08; las propiedades citadas existen.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
