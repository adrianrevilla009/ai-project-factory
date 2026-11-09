---
name: multi-tenancy-saas-features
description: "Usar al construir funciones SaaS multi-tenant sobre el modelo ya elegido: onboarding de tenants, planes y límites, configuración por tenant, dominios propios y offboarding."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Funciones SaaS multi-tenant

## Cuándo aplicar y cuándo no
- Aplica a producto B2B con varios clientes (tenants): ciclo de vida del tenant, planes/entitlements, ajustes por tenant, límites y exportación/borrado al salir.
- No aplica a la elección del modelo de aislamiento (silo/pool/bridge): eso está en `multi-tenant-architecture` y `multi-tenancy`. Este skill asume que ya se decidió.

## Reglas
- **MUST** propagar `tenantId` desde el token validado (claim) hasta el acceso a datos mediante un contexto único; nunca desde un parámetro o cabecera del cliente.
- **MUST** modelar el tenant con estado explícito: `PROVISIONING`, `ACTIVE`, `SUSPENDED`, `OFFBOARDING`, `DELETED`; cada transición es idempotente y auditada.
- **MUST** hacer el onboarding como proceso reanudable (saga/workflow) con pasos idempotentes: crear tenant, esquema/filas, realm u organización en Keycloak, admin inicial, valores por defecto.
- **MUST** centralizar planes y límites como "entitlements" (`feature -> limit`) consultados por una sola API interna; no comparar `plan == "PRO"` por el código.
- **MUST** aplicar cuotas por tenant (peticiones, almacenamiento, usuarios) y devolver 429/402 con `code` claro (ver `rate-limiting-quotas`).
- **MUST** guardar configuración por tenant con esquema validado y valores por defecto de plataforma; los cambios se auditan.
- **MUST** incluir `tenant_id` en claves de caché, claves de objetos, nombres de colas/temas y etiquetas de logs/trazas (no en etiquetas de métricas de alta cardinalidad).
- **MUST** tener test de aislamiento: un tenant A nunca lee ni escribe datos de B, incluyendo caché y búsquedas.
- **MUST** definir offboarding: exportación de datos, periodo de gracia, borrado verificable y su evidencia (ligado a retención y legal, por confirmar).
- **SHOULD** limitar el "vecino ruidoso" con límites por tenant en pools, colas y jobs.
- **MUST NOT** hacer lógica `if (tenant == "acme")`; usar configuración o entitlements.
- **MUST NOT** compartir secretos o claves de cifrado entre tenants cuando el contrato exija aislamiento.

## Por qué
El fallo crítico es la fuga entre tenants; el costoso es el código con casos especiales por cliente. Un contexto único, entitlements centralizados y ciclo de vida explícito mantienen una sola base de código con comportamiento configurable y verificable.

## Ejemplos
### Mal
```java
@GetMapping("/invoices")
List<Invoice> list(@RequestParam String tenantId) {      // el cliente elige el tenant
    return repo.findByTenantId(tenantId);
}
if (tenant.getName().equals("acme")) { enableBeta(); }   // caso especial
```
### Bien
```java
@GetMapping("/invoices")
List<Invoice> list() {
    TenantId tenant = TenantContext.require();           // viene del JWT validado
    return repo.findByTenantId(tenant.value());
}

if (entitlements.isEnabled(tenant, Feature.BETA_REPORTS)) { enableBeta(); }
```
```sql
-- Postgres RLS como defensa en profundidad
ALTER TABLE invoice ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON invoice
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

## Checklist de revisión
- [ ] `tenantId` solo desde el token; contexto único.
- [ ] Ciclo de vida del tenant con estados y transiciones idempotentes.
- [ ] Onboarding reanudable.
- [ ] Entitlements y cuotas centralizados.
- [ ] `tenant_id` en caché, colas y almacenamiento.
- [ ] Test de aislamiento entre tenants.
- [ ] Offboarding definido (exportación, borrado, evidencia).

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Test de aislamiento entre tenants (lo incluye el proyecto generado) | 1 | tests del proyecto generado |
| Regla ArchUnit: repositorios solo vía `TenantContext` | 1 | pendiente (`policies/archunit/`) |
| Revisión de entitlements y offboarding | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `multi-tenant-architecture`, `multi-tenancy`, `multi-tenant-observability`, `rate-limiting-quotas`, `feature-flags-openfeature`, `namespaces-quotas-multitenancy`, `payments-and-billing`.
- Fuentes: documentación de PostgreSQL (Row Security Policies) y de Keycloak (organizaciones/realms).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
