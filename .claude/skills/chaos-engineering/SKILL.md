---
name: chaos-engineering
description: "Usar al diseñar experimentos de caos y game days: Chaos Monkey for Spring Boot, Chaos Mesh, Toxiproxy, hipótesis, radio de explosión y abortado."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Ingeniería del caos

## Cuándo aplicar y cuándo no
- Aplica cuando el servicio ya tiene observabilidad, SLOs y resiliencia básica (timeouts, retries, circuit breaker) y se quiere comprobar que funcionan.
- No aplica a sistemas sin monitorización ni a producción real desde la fábrica: la fábrica no despliega (ADR-0004); los experimentos son locales o en un entorno de pruebas del proyecto.

## Reglas
- **MUST** formular una hipótesis de estado estable medible ("p95 < 300 ms y errores < 1 % con un pod menos") antes de inyectar el fallo.
- **MUST** limitar el radio de explosión (un servicio, un namespace, un porcentaje) y definir condición de aborto y rollback.
- **MUST** tener observabilidad activa durante el experimento (métricas, trazas, alertas).
- **MUST** empezar en local/entorno de pruebas y con un solo fallo a la vez.
- **MUST NOT** ejecutar experimentos sin aviso al equipo ni fuera de la ventana acordada.
- **MUST NOT** activar Chaos Monkey por defecto: debe estar desactivado salvo perfil explícito.
- **SHOULD** usar la herramienta adecuada: **Chaos Monkey for Spring Boot** (fallos de aplicación: latencia, excepciones, kill de la app), **Toxiproxy** (red entre procesos: latencia, corte, ancho de banda; ideal en tests de integración), **Chaos Mesh** (fallos de pod, red, I/O en Kubernetes).
- **SHOULD** registrar cada game day: hipótesis, resultado, hallazgos y acciones con dueño.
- **SHOULD** automatizar los experimentos que resultaron valiosos como tests de resiliencia (ver `resilience-testing`).

## Por qué
La resiliencia no probada es una suposición. El caos controlado descubre dependencias ocultas y alertas inútiles antes de que lo haga un incidente real; sin hipótesis ni límites es solo sabotaje.

## Ejemplos
### Mal
```text
Matamos pods de producción un viernes a ver qué pasa.
```
### Bien
```yaml
# application-chaos.yml (perfil explícito "chaos-monkey"; TODO-VERIFY nombres de propiedades en la versión usada)
spring:
  profiles:
    include: chaos-monkey
chaos:
  monkey:
    enabled: true
    assaults:
      level: 3
      latencyActive: true
      latencyRangeStart: 500
      latencyRangeEnd: 1500
```
```yaml
# Chaos Mesh (TODO-VERIFY apiVersion/campos): matar un pod del servicio en el namespace de pruebas
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata: { name: orders-pod-kill, namespace: orders-test }
spec:
  action: pod-kill
  mode: one
  selector: { labelSelectors: { app: orders } }
```

## Checklist de revisión
- [ ] Hipótesis medible y condición de aborto escritas.
- [ ] Radio de explosión acotado; entorno no productivo.
- [ ] Observabilidad activa y equipo avisado.
- [ ] Chaos Monkey desactivado por defecto.
- [ ] Hallazgos convertidos en acciones o tests.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión del plan de experimento / game day | 3 | agente `chaos` (`.claude/agents/quality/chaos.md`) |
| Regla OPA/Conftest: chaos-monkey no activo en perfil por defecto | 1 | pendiente (`policies/opa-conftest/`) |
| Gate humano antes de ejecutar experimentos | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `resilience-testing`, `resilience`, `backpressure-and-bulkheads`, `slo-sli-error-budgets`.
- Fuentes: Chaos Monkey for Spring Boot (https://codecentric.github.io/chaos-monkey-spring-boot/), Chaos Mesh (https://chaos-mesh.org/docs/), Toxiproxy (https://github.com/Shopify/toxiproxy); TODO-VERIFY propiedades y versiones a 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
