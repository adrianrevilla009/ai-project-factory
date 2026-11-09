---
name: encryption-standards
description: "Usar al elegir algoritmos, longitudes de clave, TLS y cifrado en reposo; define el estándar de cifrado y la migración a criptografía post-cuántica."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Estándares de cifrado

## Cuándo aplicar y cuándo no
- Aplica a definir el catálogo de algoritmos aprobados de la organización y revisar su uso en código, infraestructura y datos.
- No aplica a la operativa de claves y rotación (ver `crypto-tls-mtls-key-rotation`, `envelope-encryption-and-kms`) ni a la gestión de certificados (ver `pki-and-certificate-lifecycle`).

## Reglas
- **MUST** mantener un catálogo corto de algoritmos aprobados y prohibir el resto: AES-GCM (128/256) o ChaCha20-Poly1305 para cifrado autenticado; SHA-256 o superior para hash; RSA >= 3072 o curvas P-256/Ed25519 para firma e intercambio; Argon2id, scrypt o bcrypt para contraseñas.
- **MUST NOT** usar MD5, SHA-1 para seguridad, DES/3DES, RC4, ECB, RSA < 2048 ni PKCS#1 v1.5 para cifrado nuevo.
- **MUST** exigir TLS 1.2 como mínimo y preferir 1.3 en todo tráfico externo e interno (referencia: NIST SP 800-52 Rev. 2).
- **MUST** cifrar en reposo todos los datos con clasificación sensible, con claves gestionadas por KMS/Vault, nunca en el repositorio ni en la imagen.
- **MUST** usar librerías estándar (JCA/Bouncy Castle revisado) y APIs de alto nivel; MUST NOT implementar primitivas propias ni reutilizar IV/nonce.
- **SHOULD** preferir módulos con validación FIPS 140-3 si lo exige el cliente o la normativa.
- **SHOULD** inventariar el uso de criptografía (CBOM simple) para poder migrar; planificar agilidad criptográfica: algoritmo configurable, no cableado.
- **SHOULD** preparar la migración post-cuántica: los estándares FIPS 203 (ML-KEM), 204 (ML-DSA) y 205 (SLH-DSA) se publicaron en 2024; adoptar en modo híbrido cuando el ecosistema (TLS, JDK) lo soporte.
- **MUST** revisar el catálogo al menos una vez al año.

## Por qué
La mayoría de fallos criptográficos son de uso (modo, IV, longitud, claves en código), no de matemática rota. Un catálogo corto y comprobable evita decisiones locales; la agilidad criptográfica evita reescribir todo cuando un algoritmo se deprecia.

## Ejemplos
### Mal
```java
Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
byte[] digest = MessageDigest.getInstance("MD5").digest(data);
```
### Bien
```java
Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
byte[] iv = new byte[12];
new SecureRandom().nextBytes(iv);                       // IV nuevo por mensaje
c.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
byte[] digest = MessageDigest.getInstance("SHA-256").digest(data);
```
La clave `key` procede de KMS/Vault (ver `envelope-encryption-and-kms`).

## Checklist de revisión
- [ ] Solo algoritmos del catálogo; sin modos ECB ni hashes débiles.
- [ ] TLS >= 1.2 configurado explícitamente.
- [ ] Datos sensibles cifrados en reposo con claves gestionadas.
- [ ] IV/nonce únicos; sin primitivas propias.
- [ ] Catálogo revisado en los últimos 12 meses.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep contra algoritmos débiles en Java | 1 | `policies/semgrep/java-weak-crypto.yaml` |
| Checkov/Trivy sobre cifrado en reposo en IaC | 1 | `policies/iac-checks/` (reglas custom pendientes) |
| Revisión anual del catálogo | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `crypto-tls-mtls-key-rotation`, `envelope-encryption-and-kms`, `kms-multi-region-keys`, `pki-and-certificate-lifecycle`, `data-privacy-in-db`.
- Fuentes (2026-11-07): NIST SP 800-57, 800-131A Rev. 2, 800-52 Rev. 2; NIST FIPS 203/204/205 (csrc.nist.gov); OWASP Cryptographic Storage Cheat Sheet.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
