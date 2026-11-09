---
name: read-replicas-and-routing
description: Usar al enrutar lecturas a réplicas de PostgreSQL (AbstractRoutingDataSource, readOnly) y al tratar el retraso de replicación.
metadata:
  block: "03-persistence-sql"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Réplicas de lectura y enrutado

## Cuándo aplicar y cuándo no
- Aplica cuando la carga de lectura justifica réplicas, o cuando se usan réplicas gestionadas (p. ej. RDS/Aurora) y la aplicación decide a cuál ir.
- No aplica si una sola instancia con buenos índices y caché basta: medir antes (ver `indexing-and-query-plans`, `caching`).

## Reglas
- **MUST** enrutar solo por intención declarada: `@Transactional(readOnly = true)` hacia réplica, el resto al primario. Implementación típica: `AbstractRoutingDataSource` + `LazyConnectionDataSourceProxy` para decidir tras conocer el flag `readOnly`.
- **MUST** asumir retraso de replicación: una lectura en réplica puede no ver una escritura recién confirmada.
- **MUST** que los flujos "escribo y leo lo escrito" (read-your-writes), validaciones y lecturas dentro de transacciones de escritura vayan al primario.
- **MUST NOT** escribir ni bloquear (`FOR UPDATE`) contra una réplica; fallar de forma explícita.
- **MUST NOT** usar réplicas para decisiones que exijan consistencia fuerte (saldos, stock, unicidad).
- **SHOULD** tener pools y métricas separados por destino (ver `connection-pooling`) y health check que degrade a primario si la réplica cae o su retraso supera un umbral.
- **SHOULD** limitar el retraso aceptado por caso de uso y documentarlo.
- **SHOULD** tener en la matriz local una réplica de PostgreSQL solo si el equipo necesita probar el enrutado; el retraso real, failover y endpoints gestionados NO se reproducen en local. Preparado para AWS, no verificado en real.

## Por qué
Las réplicas escalan lecturas, no escrituras, y a cambio introducen consistencia eventual. El fallo típico es el usuario que guarda un dato y no lo ve al recargar. Enrutar por convención explícita evita que una lectura "inocente" tome decisiones con datos viejos.

## Ejemplos
### Mal
```java
@Transactional
public Order pay(UUID id) {
    Order o = replicaRepo.findById(id).orElseThrow(); // puede estar desfasado
    o.markPaid();
    return o;
}
```
### Bien
```java
class RoutingDataSource extends AbstractRoutingDataSource {
    @Override
    protected Object determineCurrentLookupKey() {
        return TransactionSynchronizationManager.isCurrentTransactionReadOnly()
                ? DbRole.REPLICA : DbRole.PRIMARY;
    }
}

@Bean
DataSource dataSource(DataSource primary, DataSource replica) {
    var routing = new RoutingDataSource();
    routing.setTargetDataSources(Map.of(DbRole.PRIMARY, primary, DbRole.REPLICA, replica));
    routing.setDefaultTargetDataSource(primary);
    routing.afterPropertiesSet();
    return new LazyConnectionDataSourceProxy(routing);
}

@Transactional(readOnly = true)
public List<OrderSummary> list() { /* a replica */ }
```

## Checklist de revisión
- [ ] Solo `readOnly = true` va a réplica; el resto al primario.
- [ ] Los flujos read-your-writes usan el primario.
- [ ] Existe degradación a primario si la réplica no está sana.
- [ ] Pools y métricas separados.
- [ ] Documentado qué no se replica en local.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Test de enrutado (lectura vs. escritura) en el proyecto generado | 1 | pendiente (tests del proyecto generado) |
| Revisión de casos de uso enrutados a réplica | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `transactions`, `connection-pooling`, `caching`, `consistency-and-cap-tradeoffs`.
- Fuentes: Spring Framework API (`AbstractRoutingDataSource`, `LazyConnectionDataSourceProxy`), documentación de PostgreSQL (replicación).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
