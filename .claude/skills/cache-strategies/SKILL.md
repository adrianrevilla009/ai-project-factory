---
name: cache-strategies
description: "Usar al introducir Redis como caché (cache-aside, TTL, invalidación, evicción, stampede) delante de Postgres o DynamoDB."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Estrategias de caché con Redis

Complementa `caching` (visión general en el bloque Spring); aquí, la caché como datastore adicional.

## Cuándo aplicar y cuándo no
- Aplica a lecturas costosas o muy repetidas cuyo dato tolera cierta obsolescencia.
- No aplica a datos que exigen lectura fuerte (saldos, stock en el momento de pagar) ni como almacén primario: la caché se puede perder en cualquier momento.

## Reglas
- **MUST** usar cache-aside por defecto: leer caché, si falla leer la fuente y poblar; la escritura va a la fuente y luego invalida (`DEL`) la clave.
- **MUST** poner TTL a toda clave de caché; sin TTL, un bug de invalidación se vuelve permanente.
- **MUST** configurar `maxmemory` y `maxmemory-policy` explícitos; para caché pura `allkeys-lru` es un buen defecto según la documentación de Redis. `noeviction` devuelve error al llenarse.
- **MUST** que la aplicación funcione (más lenta) si Redis cae: timeout corto y degradación a la fuente (ver `resilience`).
- **MUST** prevenir stampede en claves calientes: TTL con jitter y bloqueo/single-flight por clave al regenerar.
- **MUST** prefijar claves con servicio, entidad y versión de esquema (`orders:v2:{id}`) y, si hay multi-tenant, el tenant (ver `multi-tenancy`).
- **MUST NOT** cachear datos personales sin TTL acotado y sin contemplar su borrado (ver `gdpr-and-immutable-events`).
- **MUST NOT** usar la misma instancia Redis para caché evictable y para datos persistentes (las políticas `volatile-*` lo permiten pero la documentación recomienda instancias separadas).
- **SHOULD** medir hit ratio (`keyspace_hits` / (`keyspace_hits` + `keyspace_misses`)) y `evicted_keys`.

## Por qué
Una caché sin TTL, sin límite de memoria o sin degradación se convierte en una segunda base de datos inconsistente y en un punto único de fallo. Invalidar tras escribir (en vez de actualizar la caché) evita carreras de orden entre escritores.

## Ejemplos
### Mal
```java
public Product get(String id) {
    Product p = redis.get("p" + id);             // sin prefijo/version
    if (p == null) { p = repo.find(id); redis.set("p" + id, p); } // sin TTL, sin timeout
    return p;
}
```
### Bien
```java
public Product get(String id) {
    String key = "catalog:v2:product:" + id;
    try {
        Product hit = redis.get(key);
        if (hit != null) return hit;
    } catch (RedisException e) { metrics.cacheDown(); }   // degrada a la fuente
    Product p = singleFlight.load(key, () -> repo.find(id));
    safeSet(key, p, Duration.ofMinutes(10).plusSeconds(ThreadLocalRandom.current().nextInt(60)));
    return p;
}
```
```text
maxmemory 512mb
maxmemory-policy allkeys-lru
```

## Criterios de decisión y trampas
### Cómo decidir
- Elige el patrón por tolerancia a obsolescencia: lectura con caché lateral, escritura simultánea o invalidación por eventos; decide la caducidad y el comportamiento si la caché cae.
- La caché nunca es la fuente de verdad.
### Trampas frecuentes
- Caché sin caducidad ni invalidación.
- Estampida cuando caduca una clave popular.
- Datos de distintos usuarios mezclados.
- Depender de la caché para que el sistema funcione.
- Sin medir aciertos.
### Evidencia
- Una prueba con la caché caída demuestra que el sistema sigue funcionando, más lento.

## Checklist de revisión
- [ ] Toda clave tiene TTL (con jitter en las calientes).
- [ ] `maxmemory` y política de evicción configuradas.
- [ ] Caída de Redis no tumba la API.
- [ ] Escritura invalida, no sobrescribe la caché.
- [ ] Claves con prefijo/versión y sin PII sin control.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de TTL, timeouts y degradación | 3 | agente `code-reviewer` |
| Regla Semgrep: `opsForValue().set(` sin `Duration` | pendiente | `policies/semgrep/` (no existe aún) |

ElastiCache en AWS: preparado para AWS, no verificado en real; en local se usa Redis/Valkey OSS en contenedor y no se reproducen failover ni cifrado gestionado. Licencia: Redis 8 se publica con AGPLv3 además de RSALv2 y SSPLv1 (desde mayo de 2025; verificado el 2026-11-08); Valkey es el fork con licencia permisiva; elegir por ADR (D16).

## Relacionados, fuentes y mantenimiento
- Relacionados: `caching`, `resilience`, `data-sync-pitfalls`, `read-replicas-and-routing`, `multi-tenancy`.
- Fuentes (verificadas 2026-11-07): https://redis.io/docs/latest/develop/reference/eviction/
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
