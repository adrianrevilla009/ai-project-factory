---
name: scalability-patterns
description: "Usar al diseñar o revisar cómo escala un servicio: statelessness, caché, colas, particionado, backpressure y límites de capacidad."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "review"
---

# Patrones de escalabilidad

## Cuándo aplicar y cuándo no
- Aplica al definir requisitos de carga, al diseñar servicios que escalarán horizontalmente y al diagnosticar cuellos de botella.
- No aplica a optimizar antes de medir ni a sistemas internos de carga baja y estable: no añadir caché ni particionado "por si acaso".

## Reglas
- **MUST** fijar objetivos numéricos (RPS, p95/p99, volumen de datos) antes de elegir patrones; sin número no hay decisión.
- **MUST** mantener los servicios stateless: la sesión y el estado viven en BD, caché externa o token, no en memoria del proceso.
- **MUST** medir antes de optimizar (profiling, métricas, test de carga) e identificar el cuello de botella real, normalmente la BD.
- **MUST** poner timeouts, límites de pool y de cola en toda llamada saliente; las colas deben estar acotadas.
- **MUST** aplicar backpressure o rechazo controlado (429/503 con `Retry-After`) en lugar de aceptar trabajo ilimitado.
- **MUST** definir TTL e invalidación para cada caché y tratar el fallo de caché como degradación, no como caída.
- **SHOULD** escalar primero verticalmente y con índices/consultas (ver bloque de persistencia), después réplicas de lectura, después particionado.
- **SHOULD** mover trabajo no interactivo a colas asíncronas (ver `event-driven`).
- **SHOULD** elegir la clave de partición por patrón de acceso y evitar claves calientes.
- **MUST NOT** escalar réplicas sin comprobar que el pool de conexiones de la BD lo soporta (réplicas x pool <= máximo de conexiones).

## Por qué
La mayoría de "problemas de escala" son consultas sin índice, N+1 o conexiones agotadas; añadir instancias sin atacar el cuello de botella solo multiplica la presión sobre la BD. Los objetivos cuantificados permiten decidir y verificar con test de carga. Preparado para AWS, no verificado en real: el autoescalado real no se reproduce en local.

## Ejemplos
### Mal
```java
private final Map<String, Cart> carts = new HashMap<>();   // estado en memoria: no escala ni sobrevive reinicios
RestClient client = RestClient.create();                    // sin timeouts
```
### Bien
```yaml
# application.yml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10        # 5 réplicas x 10 = 50 conexiones; max_connections de Postgres >= 60
      connection-timeout: 2000
server:
  tomcat:
    threads:
      max: 100
    accept-count: 50               # cola acotada
```
```text
Objetivo: 300 RPS pico, p95 < 300 ms, 50 GB de datos a 12 meses -> réplicas stateless x4, caché de catálogo TTL 60 s.
```

## Checklist de revisión
- [ ] Objetivos de carga numéricos documentados.
- [ ] Sin estado en memoria del proceso.
- [ ] Timeouts, pools y colas acotados.
- [ ] Caché con TTL, invalidación y degradación definidas.
- [ ] Cuello de botella medido, no supuesto; test de carga previsto.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de requisitos de carga y límites de recursos | 3 | agente `code-reviewer` |
| Kyverno/Conftest: requests/limits en manifiestos | 1 | pendiente: `policies/kyverno/` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `consistency-and-cap-tradeoffs`, `twelve-factor`, `cell-based-architecture`, `n-plus-one`.
- Fuentes: Kleppmann, "Designing Data-Intensive Applications" (2017); Google SRE Book, cap. "Handling Overload"..
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
