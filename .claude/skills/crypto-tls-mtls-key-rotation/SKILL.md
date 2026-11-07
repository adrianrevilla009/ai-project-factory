---
name: crypto-tls-mtls-key-rotation
description: Usar al cifrar o firmar datos, hashear contraseñas, configurar TLS/mTLS o diseñar la rotación de claves y certificados.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Criptografía, TLS/mTLS y rotación de claves

## Cuándo aplicar y cuándo no
- Aplica a cifrado en reposo y en aplicación, hashing de contraseñas, firmas, generación de aleatorios, TLS externo/interno, mTLS entre servicios y gestión de ciclo de vida de claves.
- No aplica a la gestión de credenciales de aplicación (ver `secrets-management`) ni a tokens JWT (ver `jwt-and-sessions`).

## Reglas
- **MUST NOT** diseñar primitivas propias; usar bibliotecas contrastadas (JCA con proveedores estándar, Tink) y APIs de alto nivel.
- **MUST** usar AES-GCM (o ChaCha20-Poly1305) con nonce/IV único por mensaje; **MUST NOT** usar ECB, DES/3DES, RC4, MD5 ni SHA-1 para seguridad.
- **MUST** hashear contraseñas con Argon2id, bcrypt o scrypt (`DelegatingPasswordEncoder` de Spring Security); **MUST NOT** usar SHA-256 simple ni sin sal.
- **MUST** usar `SecureRandom` para tokens, IVs y sales.
- **MUST** exigir TLS 1.2 como mínimo (preferir 1.3) en todo tráfico, también interno; verificar certificado y nombre de host, **MUST NOT** deshabilitar la verificación ni usar `TrustAllManager`.
- **MUST** usar mTLS entre servicios cuando la política de zero-trust lo requiera; en malla Istio, `PeerAuthentication` en modo `STRICT` (D-Istio).
- **MUST** cifrar con claves gestionadas (KMS: AWS KMS, preparado para AWS no verificado en real); envelope encryption para datos grandes. En local se sustituye por una clave de prueba: KMS real no se reproduce.
- **MUST** definir rotación para cada clave y certificado (automática donde sea posible), con soporte de versión de clave (`kid`) para descifrar con la anterior durante la transición.
- **SHOULD** emitir certificados de vida corta y automatizar renovación (cert-manager u homólogo, TODO-VERIFY).
- **SHOULD** tener plan de agilidad criptográfica (algoritmo y versión almacenados junto al dato).

## Por qué
La mayoría de fallos criptográficos son de uso (modo, IV repetido, verificación desactivada), no del algoritmo. Sin rotación, una clave filtrada compromete todo el histórico; sin `kid`, rotar rompe el descifrado.

## Ejemplos
### Mal
```java
Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
MessageDigest.getInstance("MD5").digest(password.getBytes());
SSLContext ctx = trustAllContext();   // desactiva la verificacion
```
### Bien
```java
byte[] iv = new byte[12];
new SecureRandom().nextBytes(iv);
Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
c.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
c.updateAAD(context);                                  // vincula el contexto
byte[] ct = c.doFinal(plaintext);                      // guardar: kid + iv + ct

PasswordEncoder enc = PasswordEncoderFactories.createDelegatingPasswordEncoder();
String hash = enc.encode(rawPassword);
```
```yaml
# Istio: exigir mTLS en el namespace
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: example-app }
spec: { mtls: { mode: STRICT } }
```

## Checklist de revisión
- [ ] Algoritmos y modos de la lista permitida; IV/nonce único.
- [ ] Contraseñas con hash adaptativo y sal.
- [ ] TLS 1.2+ con verificación completa; mTLS donde corresponda.
- [ ] Claves en KMS/gestor con rotación y `kid`.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep: MD5/SHA-1/DES/ECB, `Random` | 1 | `policies/semgrep/java-weak-crypto.yaml` |
| Conftest: `PeerAuthentication` STRICT | 1 | pendiente (`policies/opa-conftest/`) |
| Revisión humana de diseño criptográfico | 4 | PR |

> Regla Semgrep sin ejecutar aún (TODO-VERIFY).

## Relacionados, fuentes y mantenimiento
- Relacionados: `secrets-management`, `jwt-and-sessions`, `zero-trust`, `pii-and-data-classification`.
- Fuentes: OWASP Cryptographic Storage, Password Storage y TLS Cheat Sheets; documentación Istio (PeerAuthentication), consultadas 2026-11-07, TODO-VERIFY versiones.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
