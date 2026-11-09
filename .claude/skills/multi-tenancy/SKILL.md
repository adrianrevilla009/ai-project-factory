---
name: multi-tenancy
description: "Usar al diseñar o revisar aislamiento multi-tenant en SQL: discriminador/@TenantId, schema o BD por tenant, RLS, pools por tenant y tests de fugas."
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Multi-tenancy en la capa SQL

## Cuándo aplicar y cuándo no
- Aplica a cualquier servicio que almacene datos de varios clientes/organizaciones en la misma plataforma.
- No aplica a servicios single-tenant. La decisión arquitectónica global está en `multi-tenant-architecture`; aquí solo la persistencia.

## Reglas
- **MUST** elegir y documentar (ADR) el modelo: discriminador en columna, schema por tenant o BD por tenant. Criterio: aislamiento exigido, nº de tenants, coste operativo, migraciones.
- **MUST** resolver el tenant una sola vez en el borde (token/claim validado), propagarlo por un contexto explícito y NO aceptarlo de parámetros del cliente.
- **MUST** con discriminador: columna `tenant_id NOT NULL` en cada tabla de negocio, incluida en índices únicos y claves foráneas compuestas; aplicar el filtro de forma centralizada (`@TenantId` de Hibernate 6.x,) y no query a query.
- **MUST** añadir Row Level Security de PostgreSQL como segunda barrera cuando el modelo sea por discriminador: política `USING (tenant_id = current_setting('app.tenant_id')::uuid)` y rol de aplicación sin `BYPASSRLS` ni ownership de las tablas.
- **MUST** fijar `app.tenant_id` con `SET LOCAL` dentro de la transacción (no `SET` de sesión) para que no se filtre al reutilizar la conexión del pool.
- **MUST** escribir tests de fuga entre tenants: datos del tenant A invisibles e inmodificables desde B, incluyendo queries nativas, jobs asíncronos y caché.
- **MUST NOT** ejecutar SQL nativo o jobs sin contexto de tenant; fallar cerrado si falta.
- **SHOULD** incluir el tenant en claves de caché y en logs/trazas (ver `caching`).
- **SHOULD** en schema/BD por tenant: pool por tenant acotado o pooler externo, y migraciones orquestadas con informe por tenant (ver `schema-migrations`).

## Por qué
Una fuga entre tenants es un incidente de seguridad y de cumplimiento. El filtro por convención ("acuérdate del WHERE") falla tarde o temprano; por eso hay un filtro central más una barrera en la BD. Los modelos con más aislamiento cuestan más: miles de schemas complican migraciones y pools. Verificar la API de multi-tenancy de Hibernate contra su documentación.

## Ejemplos
### Mal
```java
@Query("select o from Order o where o.id = :id")   // sin tenant: cualquier id ajeno es legible
Optional<Order> findById(UUID id);
```
### Bien
```java
@Entity
class Order {
    @Id UUID id;
    @TenantId String tenantId;      // Hibernate lo añade a lecturas y escrituras
}
```
```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
-- en cada transaccion: SET LOCAL app.tenant_id = '<uuid del contexto>';
```
```java
@Test
void tenantB_cannotReadTenantA_order() {
    var id = asTenant("tenant-a", () -> service.create(newOrder()));
    assertThatThrownBy(() -> asTenant("tenant-b", () -> service.get(id)))
        .isInstanceOf(NotFoundException.class);
}
```

## Checklist de revisión
- [ ] ADR con el modelo elegido y su porqué.
- [ ] Tenant derivado del token, nunca del cliente.
- [ ] `tenant_id` en tablas, índices únicos y FKs; filtro central activo.
- [ ] RLS activo con rol sin `BYPASSRLS`, y `SET LOCAL`.
- [ ] Test de fuga A/B (incluye nativas, async, caché).

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Test de fuga entre tenants (lo incluye el proyecto generado) | 1 | tests del proyecto generado |
| Regla Semgrep: `@Query(nativeQuery = true)` sin `tenant_id` | 1 | pendiente (`policies/semgrep/`) |
| Revisión de aislamiento | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `multi-tenant-architecture`, `caching`, `connection-pooling`, `schema-migrations`, `data-privacy-in-db`.
- Fuentes: PostgreSQL docs (Row Security Policies), Hibernate ORM User Guide (multitenancy).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
