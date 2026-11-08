---
name: caching
description: Usar al añadir caché a la capa de persistencia (Spring Cache, caché de 2º nivel de Hibernate, Redis/Caffeine) o al decidir si cachear.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Caché sobre datos SQL

## Cuándo aplicar y cuándo no
- Aplica a `@Cacheable`, caché de 2º nivel/consultas de Hibernate, caches locales (Caffeine) o distribuidas (Redis).
- No aplica a caché HTTP/CDN ni a la caché de 1er nivel (ver `persistence-context-and-flush`).

## Reglas
- **MUST** medir antes de cachear: identificar la consulta lenta o frecuente y corregir antes N+1, índices y proyecciones (ver `n-plus-one`, `indexing-and-query-plans`).
- **MUST** definir por caché: clave, TTL, tamaño máximo y estrategia de invalidación; sin TTL ni límite no se despliega.
- **MUST** incluir el tenant (y cualquier dimensión de autorización) en la clave en sistemas multi-tenant (ver `multi-tenancy`).
- **MUST NOT** cachear entidades JPA gestionadas en una caché de aplicación; cachear DTOs/valores inmutables.
- **MUST NOT** cachear datos sensibles o PII sin decisión explícita (ver `data-privacy-in-db`).
- **MUST NOT** cachear dentro de una transacción esperando consistencia fuerte: la caché puede servir un valor anterior al commit.
- **SHOULD** limitar la caché de 2º nivel de Hibernate a entidades de lectura casi exclusiva (catálogos, configuración).
- **SHOULD** exponer métricas de hit ratio y evicciones (Micrometer) y alertar sobre ratios bajos.
- **SHOULD** proteger contra stampede (carga única por clave: `sync = true` en `@Cacheable`).

## Por qué
Una caché cambia la consistencia del sistema: añade un segundo sitio con el dato. Es la solución más barata de escribir y la más cara de depurar. Cachear para tapar un N+1 oculta el defecto y lo traslada a los arranques en frío. Una caché local por instancia diverge entre réplicas; una distribuida añade latencia y un punto de fallo.

## Ejemplos
### Mal
```java
@Cacheable("products")                     // sin TTL, sin tenant, devuelve entidad gestionada
public Product findBySku(String sku) { return repo.findBySku(sku); }
```
### Bien
```java
@Cacheable(cacheNames = "productSummaryBySku",
           key = "T(com.acme.TenantContext).current() + ':' + #sku",
           sync = true)
public ProductSummary findSummary(String sku) {
    return repo.findSummaryBySku(sku);     // proyección inmutable
}

@CacheEvict(cacheNames = "productSummaryBySku",
            key = "T(com.acme.TenantContext).current() + ':' + #cmd.sku()")
@Transactional
public void rename(RenameProduct cmd) { /* ... */ }
```
```java
Caffeine.newBuilder().maximumSize(10_000).expireAfterWrite(Duration.ofMinutes(10)).recordStats();
```

## Checklist de revisión
- [ ] Hay evidencia de que la consulta es el cuello de botella.
- [ ] Cada caché declara TTL, tamaño y política de invalidación.
- [ ] La clave incluye tenant/identidad cuando aplica.
- [ ] No se cachean entidades gestionadas ni PII sin justificar.
- [ ] Existen métricas de hit/miss.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep: `@Cacheable` sin `key`/TTL configurado | 1 | pendiente (`policies/semgrep/`) |
| Revisión de decisiones de caché | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `multi-tenancy`, `n-plus-one`, `data-privacy-in-db`, `read-replicas-and-routing`.
- Fuentes: Spring Framework Reference (Cache Abstraction), Hibernate ORM User Guide (caching) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
