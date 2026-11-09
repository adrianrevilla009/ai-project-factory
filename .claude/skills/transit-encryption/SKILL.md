---
name: transit-encryption
description: "Usar al cifrar datos con el motor Transit de Vault y al decidir si un dato puede leerse desde varias regiones (Transit no comparte claves entre clústeres)."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Vault Transit: cifrado como servicio

## Cuándo aplicar y cuándo no
- Aplica a cifrar campos sensibles (PII, tokens) sin que la app maneje la clave, firmar/verificar y HMAC.
- **No aplica a datos que deben descifrarse en más de una región**: ahí se usa cifrado de sobre con claves multi-región de KMS (ver `envelope-encryption-and-kms`).
- Local: Transit funciona en Vault dev. NO se reproduce KMS ni claves multi-región.

## Reglas
- **TRAMPA (brief §9, D10):** con un clúster Vault independiente por región, **el material de claves de Transit no se comparte**. Un `ciphertext` `vault:v1:...` generado en la región A **no** puede descifrarse en la B. **MUST NOT** diseñar datos replicados entre regiones cifrados con Transit.
- **MUST** reservar Transit para datos cuya lectura es local a una región (o aislados por celda), o como capa adicional sobre datos que ya usan sobre-cifrado KMS.
- **MUST NOT** resolver la limitación exportando claves (`exportable=true`) para copiarlas entre clústeres, ni asumiendo replicación Enterprise (D16, no se asume).
- **MUST** una clave por propósito (`orders-pii`), nunca una clave global; `deletion_allowed=false` por defecto.
- **MUST** rotar claves con `transit/keys/<k>/rotate` y fijar `min_decryption_version`; tras rotar, rewrapear los datos antiguos (`transit/rewrap`) de forma gradual.
- **SHOULD** usar `convergent_encryption` solo si se necesita búsqueda por igualdad, aceptando la fuga de igualdad.
- **MUST** pasar el contexto (`context`) con claves derivadas cuando se separan inquilinos.
- **MUST** guardar el ciphertext junto con la versión de clave (ya viene en el prefijo) y registrar qué región lo produjo.
- **MUST NOT** conceder a la app permisos de gestión de claves (ver `policies`).

## Por qué
El error clásico es "tenemos Vault en ambas regiones, así que ciframos con Transit y replicamos la base": tras un failover, los datos no se pueden leer. Transit es excelente para evitar claves en la app, pero su alcance es el clúster que posee la clave. Los datos multi-región necesitan una clave que ambas regiones puedan usar, que es la función de las claves multi-región de KMS.

## Ejemplos
### Mal
```java
// Aurora Global replica esta columna a eu-west-1 y eu-central-1,
// pero el ciphertext solo lo entiende el Vault de la región que lo creó.
String ct = vaultTransit.encrypt("orders-pii", plaintext);   // vault:v1:...
orderRepository.save(new Order(id, ct));                     // fila replicada entre regiones
```
### Bien
```java
// Dato local a la región/celda: Transit sí
String ct = vaultTransit.encrypt("orders-pii", plaintext);
localCache.put(id, ct);

// Dato que se lee en ambas regiones: sobre con clave multi-región de KMS
byte[] dek = kms.generateDataKey(multiRegionKeyId);          // clave KMS multi-región
byte[] blob = aesGcmEncrypt(dek.plaintext(), plaintext, aad);
orderRepository.save(new Order(id, blob, dek.encrypted()));
```
```text
vault write -f transit/keys/orders-pii type=aes256-gcm96
vault write transit/keys/orders-pii/config min_decryption_version=2 deletion_allowed=false
```

## Criterios de decisión y trampas
### Cómo decidir
- Cifrado como servicio: la aplicación envía datos y recibe texto cifrado sin ver las claves; para datos que deben leerse en varias regiones, cifrado de sobre con claves multi-región del proveedor.
- El material de claves no se comparte entre clústeres independientes.
### Trampas frecuentes
- Suponer que dos instalaciones independientes pueden descifrar lo del otro.
- Claves de cifrado de datos guardadas con los datos.
- Sin rotación ni versiones de clave.
- Cifrar y perder la clave.
- Usar el servicio para volúmenes que necesitan otro enfoque.
### Evidencia
- Una prueba de descifrado en la región secundaria y una rotación ensayada.

## Checklist de revisión
- [ ] Ningún dato replicado entre regiones depende de una clave Transit.
- [ ] Datos multi-región usan envelope encryption con KMS multi-región.
- [ ] Una clave por propósito; sin `exportable`; rotación y rewrap planificados.
- [ ] La app solo tiene `encrypt`/`decrypt`, no gestión de claves.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Conftest: claves Transit con `exportable=true` en IaC | 1 | pendiente: `policies/opa-conftest/` |
| Revisión del mapa de datos por región (qué se lee dónde) | 4 | revisión humana, junto a `data-replication-matrix` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `envelope-encryption-and-kms`, `vault-and-keycloak-dr`, `data-replication-matrix`, `crypto-tls-mtls-key-rotation`, `pii-and-data-classification`.
- Fuentes (2026-11-07): https://developer.hashicorp.com/vault/docs/secrets/transit; ADR-0010; brief §9. AWS KMS multi-Region keys: https://docs.aws.amazon.com/kms/latest/developerguide/multi-region-keys-overview.html.
- Estado: diseño; preparado para AWS, no verificado en real.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
