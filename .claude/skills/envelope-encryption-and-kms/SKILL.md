---
name: envelope-encryption-and-kms
description: "Usar al cifrar datos de aplicación con cifrado de sobre (DEK/KEK), KMS y claves multi-región, y al decidir entre Vault Transit y KMS para datos entre regiones."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Cifrado de sobre y KMS

## Cuándo aplicar y cuándo no
- Aplica al cifrado a nivel de campo o fichero cuyos datos se leen desde más de una región, o que exceden lo razonable para Transit.
- No aplica al cifrado en reposo gestionado por el servicio (EBS, RDS) ni a TLS (ver `crypto-tls-mtls-key-rotation`).

## Reglas
- **MUST** usar cifrado de sobre: una clave de datos (DEK) por objeto/registro cifra el dato; una clave maestra (KEK) cifra la DEK. Se guarda la DEK cifrada junto al dato.
- **MUST** respetar ADR-0010: Vault Transit NO comparte material de claves entre regiones (clúster independiente por región). Los datos leídos desde ambas regiones MUST usar claves multi-región de KMS.
- **MUST** usar, en AWS, una clave multi-región (primaria + réplicas) con políticas de clave y alias gestionados por región; preparado para AWS, no verificado en real. En local no se reproduce KMS real: usar un adaptador de prueba con clave falsa (`changeme`).
- **MUST** usar AEAD (AES-GCM) con contexto de cifrado (encryption context) ligado al tenant/registro, para impedir copiar un blob a otro registro.
- **MUST NOT** persistir DEK en claro, loguearla ni reutilizar una misma DEK para volúmenes grandes sin límite.
- **MUST NOT** implementar primitivas propias; usar la librería de cifrado de sobre del proveedor o Tink/JCA según `crypto-tls-mtls-key-rotation`.
- **MUST** habilitar rotación automática de la KEK y almacenar el identificador de versión/clave con el texto cifrado para poder descifrar histórico.
- **SHOULD** usar Vault Transit cuando los datos son mono-región y se quiere evitar que la clave salga de Vault.
- **SHOULD** minimizar llamadas a KMS cacheando DEK descifradas con TTL corto y límite de uso.
- **SHOULD** aislar el acceso: la identidad de la aplicación solo `Encrypt/Decrypt/GenerateDataKey` sobre su clave.

## Por qué
Las claves multi-región de KMS comparten identificador y material entre regiones, de modo que un texto cifrado en una región se descifra en otra sin llamada entre regiones; cada réplica es un recurso independiente (política, alias, estado). No se pueden convertir claves existentes en multi-región: hay que re-cifrar. Transit por región, en cambio, mantiene el aislamiento de fallo pero no sirve para datos compartidos.

## Ejemplos
### Mal
```java
// una única clave AES fija en el código y sin contexto
SecretKeySpec key = new SecretKeySpec("0123456789abcdef".getBytes(), "AES");
Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
```
### Bien
```java
public interface DataKeyService {
    DataKey generate(String keyAlias, Map<String, String> encryptionContext); // plaintext + encrypted DEK
    byte[] decrypt(byte[] encryptedDek, Map<String, String> encryptionContext);
}
// Cifrado: AES-GCM con la DEK; se guarda {encryptedDek, keyVersion, iv, ciphertext}.
// Contexto: Map.of("tenant", tenantId, "record", recordId).
```
```text
# Elección: mono-región -> Vault Transit | multi-región -> KMS multi-región + sobre
```

## Checklist de revisión
- [ ] DEK por objeto, KEK en KMS/Transit; DEK nunca en claro en disco.
- [ ] Datos multi-región con clave multi-región, no con Transit.
- [ ] AES-GCM con encryption context; versión de clave almacenada.
- [ ] Rotación automática y política de clave mínima por región.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep contra cifrados débiles (ECB, DES) | 1 | `policies/semgrep/java-weak-crypto.yaml` |
| Checkov/Conftest: claves KMS con rotación y réplicas definidas | 1 | pendiente (`policies/iac-checks/`) |
| Revisión del diseño de cifrado | 3 | agente `code-reviewer` + revisión de seguridad |

## Relacionados, fuentes y mantenimiento
- Relacionados: `transit-encryption`, `crypto-tls-mtls-key-rotation`, `data-privacy-in-db`, `vault-and-keycloak-dr`, `multi-region-patterns`.
- Fuentes: https://docs.aws.amazon.com/kms/latest/developerguide/multi-region-keys-overview.html (consultada 2026-11-07); ADR-0010.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
