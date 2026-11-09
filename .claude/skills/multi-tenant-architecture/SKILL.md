---
name: multi-tenant-architecture
description: "Usar al diseñar un sistema que sirve a varios clientes (tenants): modelo de aislamiento de datos, identificación del tenant y límites por tenant."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "review"
---

# Arquitectura multi-tenant

## Cuándo aplicar y cuándo no
- Aplica a productos SaaS o plataformas internas que alojan a varias organizaciones/clientes con datos separados.
- No aplica a aplicaciones de un solo cliente; no introducir `tenant_id` "por si acaso".

## Reglas
- **MUST** decidir el modelo de aislamiento en un ADR: base por tenant, esquema por tenant o tabla compartida con `tenant_id` (silo, bridge, pool), según riesgo, coste y número de tenants.
- **MUST** derivar el tenant de una fuente confiable (claim del token validado, ej. Keycloak realm/claim), nunca de un parámetro o cabecera que controle el cliente.
- **MUST** propagar el tenant en un contexto de petición (hilo, mensajes, logs, trazas) y limpiarlo al terminar.
- **MUST** aplicar el filtro de tenant en un único punto central (filtro de Hibernate, Row Level Security de Postgres o repositorio base), no en cada consulta a mano.
- **MUST** incluir `tenant_id` en claves de caché, claves de objeto, topics/claves de mensajes e índices únicos.
- **MUST** testear aislamiento: un test que cree datos en el tenant A y verifique que B no los ve por ninguna vía.
- **SHOULD** aplicar cuotas y rate limiting por tenant para evitar "vecino ruidoso".
- **SHOULD** usar Row Level Security como defensa en profundidad además del filtro de aplicación.
- **MUST NOT** usar un usuario de BD con `BYPASSRLS` en la aplicación.
- **MUST NOT** mezclar datos de tenants en logs sin etiquetar el tenant.

## Por qué
Una fuga entre tenants es un incidente grave de seguridad y legal. Un filtro olvidado en una consulta basta para exponerlos; centralizarlo y verificarlo con tests convierte un descuido en un fallo detectable. Los modelos más aislados cuestan más operación; los compartidos cuestan más disciplina.

## Ejemplos
### Mal
```java
@GetMapping("/orders")
List<Order> list(@RequestHeader("X-Tenant") String tenant) {      // el cliente elige su tenant
    return repo.findByTenantId(tenant);                           // y cada consulta debe acordarse del filtro
}
```
### Bien
```sql
alter table orders enable row level security;
create policy tenant_isolation on orders
  using (tenant_id = current_setting('app.tenant_id')::uuid);
```
```java
// El tenant sale del JWT validado y se fija por transacción
String tenantId = jwt.getClaimAsString("tenant_id");
UUID tenant = UUID.fromString(tenantId);   // valida el formato
jdbc.queryForObject("select set_config('app.tenant_id', ?, true)", String.class, tenant.toString());
```
```java
@Test void tenantBCannotSeeTenantAOrders() { /* crea en A, consulta como B, espera vacío */ }
```

## Criterios de decisión y trampas
### Cómo decidir
- Elige el modelo de aislamiento por requisitos (regulación, ruido entre vecinos, personalización) y su coste operativo.
- Aísla también cargas, cuotas y observabilidad por tenant.
### Trampas frecuentes
- Aislamiento solo a nivel de aplicación en un sistema con requisitos regulatorios fuertes.
- Un tenant que degrada a los demás.
- Configuración por tenant que se multiplica sin control.
- Migraciones que no escalan con el número de tenants.
- Métricas agregadas que esconden al tenant afectado.
### Evidencia
- Una prueba de aislamiento (datos y rendimiento) entre tenants.

## Checklist de revisión
- [ ] ADR con modelo de aislamiento elegido y alternativas.
- [ ] Tenant extraído del token validado.
- [ ] Filtro centralizado (+ RLS si Postgres compartido).
- [ ] `tenant_id` en cachés, mensajes, índices únicos y logs.
- [ ] Test de aislamiento entre tenants y cuotas por tenant.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test de aislamiento en el proyecto generado | 1 | tests del proyecto generado |
| Regla Semgrep: `@RequestHeader` con nombre de tenant | 1 | pendiente: `policies/semgrep/` |
| Revisión de seguridad del modelo | 3 | agente `security-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `cell-based-architecture`, `scalability-patterns`, `ddd-strategic`.
- Fuentes: PostgreSQL docs, "Row Security Policies"; AWS Well-Architected SaaS Lens (leer como referencia; no verificado en real)..
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
