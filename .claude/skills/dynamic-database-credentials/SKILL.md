---
name: dynamic-database-credentials
description: "Usar al configurar el motor de BD de Vault (credenciales dinámicas o roles estáticos) y al planificar su comportamiento en failover de Aurora Global."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Vault: credenciales dinámicas de base de datos

## Cuándo aplicar y cuándo no
- Aplica a servicios que acceden a PostgreSQL/Aurora con usuarios que Vault crea y revoca.
- No aplica a DynamoDB (se accede por IAM/IRSA, no por usuario/clave de BD) ni a credenciales de usuarios finales.
- Local: PostgreSQL en el clúster local sirve para probar el motor. NO se reproduce Aurora Global, su promoción ni la réplica de solo lectura.

## Reglas
- **MUST** usar el motor `database` con un usuario "root" de Vault de privilegios mínimos (crear/alterar/borrar roles de aplicación) y **MUST** rotarlo con `rotate-root` tras configurarlo.
- **MUST** definir un rol Vault por servicio y permiso (`orders-rw`, `orders-ro`) con `default_ttl` corto (p. ej. 1 h) y `max_ttl` acotado, con `creation_statements` que concedan solo los GRANT necesarios.
- **MUST** preferir credenciales dinámicas; usar **roles estáticos** (rotación de un usuario fijo) solo si el sistema no tolera usuarios efímeros (migraciones, herramientas legadas).
- **MUST** que la aplicación renueve el lease o reabra el pool al expirar: el pool de conexiones (HikariCP) debe soportar credenciales rotadas (ver `rotation-and-leases`).
- **MUST** apuntar la conexión de Vault al endpoint de **escritura** del clúster; Vault no puede crear roles en una réplica de solo lectura.
- **TRAMPA, orden en failover (Aurora Global, brief §9):** la secundaria es de solo lectura hasta promoverse. El runbook **MUST** fijar el orden: 1) promover la BD secundaria, 2) actualizar `connection_url` y activar/validar el motor de BD del Vault de esa región, 3) escalar las apps. Hacerlo al revés deja a Vault sin poder emitir credenciales.
- **MUST** tener en cada región su propio Vault y su propio motor de BD (D10): no hay replicación de leases entre clústeres. Las credenciales emitidas en la región caída se consideran perdidas y se recrean.
- **SHOULD** dejar una credencial de emergencia (break-glass, pendiente `audit-and-break-glass`) para recuperar acceso si el motor falla durante el failover.
- **MUST NOT** emitir credenciales con `SUPERUSER` ni con propiedad de esquemas para servicios de aplicación.

## Por qué
Cada instancia con su usuario hace la auditoría atribuible y la revocación inmediata. Pero el motor depende de que la BD sea escribible: en un failover, activar Vault antes de la promoción provoca errores en cascada que parecen caída del propio Vault. Verificar los detalles de Aurora Global (conmutación gestionada vs. manual) en la documentación AWS vigente.

## Ejemplos
### Mal
```text
vault write database/config/orders plugin_name=postgresql-database-plugin \
  connection_url="postgresql://postgres:changeme-example@reader.example.internal:5432/orders" \
  allowed_roles="*"
vault write database/roles/orders db_name=orders default_ttl=0 \
  creation_statements="CREATE ROLE \"{{name}}\" SUPERUSER LOGIN PASSWORD '{{password}}';"
```
### Bien
```text
vault write database/config/orders \
  plugin_name=postgresql-database-plugin \
  connection_url="postgresql://{{username}}:{{password}}@writer.orders.example.internal:5432/orders" \
  allowed_roles="orders-rw" \
  username="vault_admin" password="changeme-example"
vault write -force database/rotate-root/orders

vault write database/roles/orders-rw db_name=orders default_ttl=1h max_ttl=4h \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT orders_rw TO \"{{name}}\";"
```
```text
# Runbook de failover (orden obligatorio)
1. Promover Aurora secundaria a primaria (escribible).
2. Apuntar database/config/orders al nuevo writer; probar vault read database/creds/orders-rw.
3. Reiniciar/reconciliar apps para que obtengan credenciales nuevas.
```

## Checklist de revisión
- [ ] Usuario root de Vault con mínimos privilegios y rotado.
- [ ] Un rol por servicio, TTL corto, GRANT mínimos, sin SUPERUSER.
- [ ] Pool de conexiones tolera rotación.
- [ ] Conexión al endpoint writer; runbook con el orden promover BD, luego motor de Vault.
- [ ] Sin dependencia de replicación Enterprise; ensayo de failover en tabletop.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Conftest: roles de BD sin TTL o con SUPERUSER | 1 | pendiente: `policies/opa-conftest/` |
| Revisión del runbook de failover (orden de pasos) | 4 | revisión humana, ensayo tabletop (`dr-tabletop-exercises`) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `rotation-and-leases`, `policies`, `connection-pooling`, `vault-and-keycloak-dr`, `multi-region-patterns`.
- Fuentes (2026-11-07): https://developer.hashicorp.com/vault/docs/secrets/databases; brief §9 de la fábrica.
- Estado: diseño; preparado para AWS, no verificado en real.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
