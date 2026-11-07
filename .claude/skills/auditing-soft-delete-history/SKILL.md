---
name: auditing-soft-delete-history
description: Usar al añadir campos de auditoría, borrado lógico o historial de cambios a entidades SQL (Spring Data Auditing, Envers, tablas de historial).
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Auditoría, borrado lógico e historial

## Cuándo aplicar y cuándo no
- Aplica a `created_at/by`, `updated_at/by`, `deleted_at`, versionado de filas y trazabilidad de cambios en datos de negocio.
- No aplica al audit trail de seguridad (ver `audit-trail-and-security-logging`) ni a event sourcing (ver `event-sourcing`).

## Reglas
- **MUST** auditar con mecanismo central (`@EntityListeners(AuditingEntityListener.class)` + `@CreatedDate`, `@LastModifiedDate`, `@CreatedBy`, `@LastModifiedBy`), no a mano en cada servicio.
- **MUST** guardar instantes en UTC (`Instant`, `timestamptz`) y el autor como identificador estable del sujeto (claim `sub`), no nombre visible.
- **MUST** decidir por entidad entre borrado físico, lógico o archivado; el borrado lógico no es el defecto.
- **MUST** con borrado lógico: filtrar en todas las lecturas (`@SQLRestriction` de Hibernate, TODO-VERIFY nombre según versión), excluir filas borradas de índices únicos con índice parcial (`WHERE deleted_at IS NULL`) y definir una purga con plazo.
- **MUST** tratar el derecho de supresión: un borrado lógico NO cumple una petición de supresión de datos personales (ver `data-privacy-in-db`).
- **MUST NOT** usar historial como sustituto de backup ni como bus de eventos.
- **SHOULD** para historial completo preferir Hibernate Envers o tablas `_history` mediante trigger; elegir una y documentarla. Envers duplica escrituras y crece: definir retención.
- **SHOULD** que el historial sea append-only y que la aplicación no tenga permisos de UPDATE/DELETE sobre él.

## Por qué
La auditoría hecha a mano se olvida justo en el caso que luego importa. El borrado lógico se vende como "recuperable" pero rompe unicidades, infla tablas, ralentiza consultas y deja datos personales vivos. El historial tiene coste de escritura y almacenamiento, por lo que cada entidad debe justificarlo.

## Ejemplos
### Mal
```java
public void delete(UUID id) {
    Customer c = repo.findById(id).orElseThrow();
    c.setDeleted(true);                      // y cada query debe acordarse de "where deleted = false"
}
```
```sql
CREATE UNIQUE INDEX uq_customer_email ON customer (email);   -- impide recrear un cliente borrado
```
### Bien
```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
abstract class Auditable {
    @CreatedDate  Instant createdAt;
    @LastModifiedDate Instant updatedAt;
    @CreatedBy String createdBy;
    @LastModifiedBy String updatedBy;
}

@Entity
@SQLRestriction("deleted_at is null")
class Customer extends Auditable {
    Instant deletedAt;
}
```
```sql
CREATE UNIQUE INDEX uq_customer_email_active ON customer (email) WHERE deleted_at IS NULL;
```
Requiere `@EnableJpaAuditing` y un `AuditorAware<String>` que lea el sujeto autenticado.

## Checklist de revisión
- [ ] Auditoría vía listener/`@EnableJpaAuditing`, con `AuditorAware`.
- [ ] Borrado lógico justificado, filtrado centralmente y con índices únicos parciales.
- [ ] Plazo de purga definido; supresión de PII tratada aparte.
- [ ] Historial append-only con retención declarada.
- [ ] Tiempos en UTC.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla ArchUnit: entidades de negocio extienden `Auditable` | 1 | pendiente (`policies/archunit/`) |
| Revisión de decisiones de borrado/historial | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `data-privacy-in-db`, `schema-migrations`, `audit-trail-and-security-logging`, `jpa-entity-design`.
- Fuentes: Spring Data JPA Reference (Auditing), Hibernate ORM / Envers User Guide — TODO-VERIFY versión y URL; no verificado 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
