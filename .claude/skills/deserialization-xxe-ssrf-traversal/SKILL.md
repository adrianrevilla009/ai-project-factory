---
name: deserialization-xxe-ssrf-traversal
description: Usar al deserializar datos externos, parsear XML, llamar a URLs aportadas por el usuario o resolver rutas de fichero, para evitar RCE, XXE, SSRF y path traversal.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Deserialización insegura, XXE, SSRF y path traversal

## Cuándo aplicar y cuándo no
- Aplica a `ObjectInputStream`, Jackson con tipos polimórficos, parsers XML, clientes HTTP con URL dinámica (webhooks, importadores, previews) y lectura/escritura de ficheros con nombres externos.
- No aplica a la subida de ficheros en sí (ver `file-upload-security`) ni a inyección en intérpretes (ver `injection-families`).

## Reglas
- **MUST NOT** usar `ObjectInputStream`/serialización nativa Java con datos externos; usar JSON o Protobuf con esquema.
- **MUST NOT** activar `enableDefaultTyping`/`activateDefaultTyping` de Jackson; si hay polimorfismo, usar `PolymorphicTypeValidator` con allowlist de subtipos.
- **MUST** deshabilitar DTD y entidades externas en todo parser XML (`disallow-doctype-decl`, `XMLConstants.ACCESS_EXTERNAL_DTD` vacío).
- **MUST** validar destinos salientes (SSRF): solo `https`, host en allowlist, resolver DNS y rechazar IPs de loopback, link-local (`169.254.0.0/16`, incluye metadatos de instancia), privadas y reservadas.
- **MUST NOT** seguir redirecciones automáticamente en llamadas con URL aportada por el usuario; revalidar cada salto o deshabilitarlas.
- **MUST** normalizar rutas (`Path.normalize` + `toRealPath`) y comprobar `startsWith(baseDir)` antes de abrir ficheros.
- **SHOULD** forzar IMDSv2 y limitar el egress de red de la carga para que SSRF tenga poco alcance (preparado para AWS, no verificado en real; en local no se reproduce IMDS).
- **SHOULD** aplicar `ObjectInputFilter` si la serialización nativa es inevitable en código heredado.

## Por qué
Los gadgets de deserialización permiten ejecución remota de código sin que el atacante suba código. XXE lee ficheros y hace SSRF desde el parser. SSRF convierte al servidor en proxy hacia la red interna y credenciales de metadatos. Path traversal (`../`) escapa del directorio previsto. Todas comparten causa: confiar en estructuras o destinos que controla el atacante.

## Ejemplos
### Mal
```java
Object o = new ObjectInputStream(request.getInputStream()).readObject();
DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(in);
HttpResponse<String> r = client.send(HttpRequest.newBuilder(URI.create(userUrl)).build(), ofString());
byte[] b = Files.readAllBytes(Path.of("/data/reports", name));   // name = ../../etc/passwd
```
### Bien
```java
DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
f.setXIncludeAware(false);
f.setExpandEntityReferences(false);

Path base = Path.of("/data/reports").toRealPath();
Path target = base.resolve(name).normalize();
if (!target.startsWith(base)) throw new IllegalArgumentException("invalid path");

URI uri = URI.create(userUrl);
if (!"https".equals(uri.getScheme()) || !ALLOWED_HOSTS.contains(uri.getHost()))
    throw new IllegalArgumentException("destination not allowed");
InetAddress ip = InetAddress.getByName(uri.getHost());
if (ip.isAnyLocalAddress() || ip.isLoopbackAddress() || ip.isLinkLocalAddress() || ip.isSiteLocalAddress())
    throw new IllegalArgumentException("internal address");
```
Nota: validar la IP y luego conectar abre una ventana de DNS rebinding; conectar a la IP ya validada.

## Checklist de revisión
- [ ] No hay `ObjectInputStream` ni default typing sobre entrada externa.
- [ ] Todos los parsers XML tienen DTD deshabilitado.
- [ ] Las URL salientes dinámicas pasan allowlist, bloqueo de IP internas y sin redirecciones libres.
- [ ] Toda ruta construida con entrada externa se normaliza y se confina al directorio base.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep: `ObjectInputStream`, default typing | 1 | `policies/semgrep/java-unsafe-deserialization.yaml` |
| Semgrep: rutas con parámetros de request | 1 | `policies/semgrep/java-path-from-user-input.yaml` |
| Regla XXE y SSRF (parsers/clientes) | 1 | pendiente (`policies/semgrep/`) |
| Revisión humana de clientes HTTP con URL dinámica | 4 | PR |

> Estado: reglas probadas con `semgrep --test` (casos en `tests/semgrep/`); detectan patrones sintácticos, no flujos de datos.

## Relacionados, fuentes y mantenimiento
- Relacionados: `injection-families`, `file-upload-security`, `cloud-iam-least-privilege`, `owasp-top10-and-api-top10`.
- Fuentes: OWASP Cheat Sheet Series (Deserialization, XXE Prevention, SSRF Prevention, Input Validation).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
