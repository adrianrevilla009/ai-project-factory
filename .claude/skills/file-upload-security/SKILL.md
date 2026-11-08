---
name: file-upload-security
description: Usar al implementar subida o descarga de ficheros (multipart, URLs prefirmadas) para validar tipo, tamaño, nombre y almacenamiento seguro.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Seguridad en subida de ficheros

## Cuándo aplicar y cuándo no
- Aplica a endpoints multipart, subidas directas a almacenamiento de objetos con URL prefirmada y servicio posterior de esos ficheros.
- No aplica a lectura de ficheros internos de configuración ni a parsing XML (ver `deserialization-xxe-ssrf-traversal`).

## Reglas
- **MUST** limitar tamaño de fichero y de petición (`spring.servlet.multipart.max-file-size`, `max-request-size`) y número de partes.
- **MUST** validar el tipo con allowlist de extensiones y comprobar el contenido real (magic bytes, p. ej. Apache Tika), no el `Content-Type` del cliente.
- **MUST NOT** usar `getOriginalFilename()` como ruta; generar un nombre propio (UUID) y guardar el original solo como metadato.
- **MUST** almacenar fuera del directorio servido por el servidor web y, preferiblemente, en almacenamiento de objetos privado.
- **MUST** servir las descargas con `Content-Disposition: attachment`, `X-Content-Type-Options: nosniff` y un `Content-Type` fijado por el servidor.
- **MUST** exigir autenticación y autorización por objeto también en la descarga (evitar IDOR).
- **SHOULD** analizar con antivirus/sandbox antes de marcar el fichero como disponible (estado `PENDING` → `CLEAN`).
- **SHOULD** reprocesar imágenes (re-codificar) para eliminar payloads y metadatos EXIF.
- **SHOULD** en URLs prefirmadas: caducidad corta, tamaño y `Content-Type` condicionados, clave de objeto generada por el servidor.
- **MUST NOT** descomprimir archivos sin límite de tamaño total, de entradas y de profundidad (zip bomb) ni sin validar las rutas internas (zip slip).

## Por qué
Un fichero subido es entrada no confiable de gran tamaño: puede ser un ejecutable renombrado, HTML con scripts servido desde tu origen, una bomba de descompresión o una ruta `../../` que sobreescribe ficheros. Confiar en la extensión o en el `Content-Type` del cliente no protege.

## Ejemplos
### Mal
```java
@PostMapping("/upload")
void upload(@RequestParam MultipartFile file) throws IOException {
    file.transferTo(new File("/var/www/uploads/" + file.getOriginalFilename()));
}
```
### Bien
```java
private static final Set<String> ALLOWED = Set.of("image/png", "image/jpeg", "application/pdf");

@PostMapping("/upload")
UploadResponse upload(@RequestParam MultipartFile file) throws IOException {
    if (file.getSize() > MAX_BYTES) throw new PayloadTooLargeException();
    String detected = new Tika().detect(file.getInputStream());   // contenido real
    if (!ALLOWED.contains(detected)) throw new UnsupportedMediaTypeException(detected);
    String key = UUID.randomUUID().toString();
    storage.put(key, file.getInputStream(), detected);             // almacen privado
    metadata.save(key, file.getOriginalFilename(), Status.PENDING_SCAN);
    return new UploadResponse(key);
}
```
```text
# Zip slip: al extraer, resolver cada entrada contra el destino y rechazar si
# target.normalize() no empieza por el directorio destino.
```

## Checklist de revisión
- [ ] Límites de tamaño configurados y probados.
- [ ] Tipo validado por contenido y allowlist.
- [ ] Nombre generado por el servidor; el original solo como metadato.
- [ ] Ficheros fuera del directorio web; descarga con `attachment` y `nosniff`.
- [ ] Autorización por objeto en descarga; extracción de archivos con límites.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep: nombre original/rutas desde request | 1 | `policies/semgrep/java-path-from-user-input.yaml` |
| Test con ficheros maliciosos (doble extensión, MIME falso, zip slip) | 1 | tests del proyecto generado (pendiente de plantilla) |
| Revisión humana del flujo de subida | 4 | PR |

> Estado: reglas probadas con `semgrep --test` (casos en `tests/semgrep/`); detectan patrones sintácticos, no flujos de datos.

## Relacionados, fuentes y mantenimiento
- Relacionados: `deserialization-xxe-ssrf-traversal`, `security-headers-cors-csrf`, `input-validation-output-encoding`, `authz-rbac-abac-rebac`.
- Fuentes: OWASP File Upload Cheat Sheet, consultado 2026-11-07; propiedades `spring.servlet.multipart.*` TODO-VERIFY en la versión de Spring Boot del proyecto.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
