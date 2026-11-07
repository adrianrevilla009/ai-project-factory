---
name: file-upload-and-streaming
description: Usar al recibir subidas multipart o servir descargas grandes en Spring (límites, almacenamiento, streaming) sin cargar ficheros completos en memoria.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Subida y streaming de ficheros en Spring

## Cuándo aplicar y cuándo no
- Aplica a endpoints `multipart/form-data`, descargas de ficheros y exportaciones grandes.
- No aplica a la seguridad del contenido (validación de tipo, antivirus): ver `file-upload-security` (bloque 07); este skill cubre la plataforma.

## Reglas
- **MUST** configurar límites explícitos: `spring.servlet.multipart.max-file-size`, `max-request-size` y límite a nivel de proxy/gateway.
- **MUST NOT** usar `file.getBytes()` ni cargar el fichero entero en memoria; usar `getInputStream()` y copiar por flujo.
- **MUST NOT** usar `getOriginalFilename()` como ruta de destino; generar un nombre propio (UUID) y guardar el original como metadato.
- **MUST** cerrar los streams (try-with-resources) y manejar el fallo parcial (borrar el parcial).
- **SHOULD** subir ficheros grandes directamente al almacenamiento de objetos con URL prefirmada en lugar de pasar por el servicio.
- **MUST** servir descargas con `StreamingResponseBody` o `InputStreamResource`, con `Content-Disposition` y `Content-Type` explícitos.
- **MUST** que las exportaciones grandes lean por páginas/cursor, no `findAll()`.
- **MUST** comprobar autorización sobre el recurso antes de abrir el stream.
- **SHOULD** declarar el almacén detrás de una interfaz (`FileStorage`) para cambiar disco local por S3 sin tocar el controlador. En local no se reproduce S3 real; se usa un emulador (preparado para AWS, no verificado en real).

## Por qué
Cargar ficheros completos en memoria permite agotar el heap con pocas peticiones. Los nombres controlados por el cliente habilitan path traversal. Los límites en varias capas evitan que el fallo ocurra tarde y de forma costosa.

## Ejemplos
### Mal
```java
@PostMapping("/files")
void upload(@RequestParam MultipartFile file) throws IOException {
    byte[] data = file.getBytes();                                    // todo en memoria
    Files.write(Path.of("/data/" + file.getOriginalFilename()), data); // path traversal
}
```
### Bien
```java
@PostMapping("/files")
ResponseEntity<FileRef> upload(@RequestParam MultipartFile file) throws IOException {
    String storedName = UUID.randomUUID().toString();
    try (InputStream in = file.getInputStream()) {
        storage.save(storedName, in, file.getSize());
    }
    return ResponseEntity.status(CREATED).body(new FileRef(storedName, file.getOriginalFilename()));
}

@GetMapping("/files/{id}")
ResponseEntity<StreamingResponseBody> download(@PathVariable String id) {
    StreamingResponseBody body = out -> { try (var in = storage.open(id)) { in.transferTo(out); } };
    return ResponseEntity.ok()
        .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"export.bin\"")
        .contentType(MediaType.APPLICATION_OCTET_STREAM)
        .body(body);
}
```
```yaml
spring:
  servlet:
    multipart:
      max-file-size: 10MB
      max-request-size: 12MB
```

## Checklist de revisión
- [ ] Límites de tamaño configurados en app y en proxy.
- [ ] Sin `getBytes()` ni `findAll()` en rutas de fichero.
- [ ] Nombre de destino generado, no el original.
- [ ] Autorización comprobada antes de servir.
- [ ] Almacén tras interfaz.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `getOriginalFilename()` en construcción de rutas / `getBytes()` en MultipartFile | 1 | pendiente |
| Revisión de endpoints de fichero | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `file-upload-security`, `controllers-and-validation`, `spring-data-rules`.
- Fuentes: Spring Framework Reference (Multipart, Asynchronous Requests / StreamingResponseBody) y Spring Boot Reference (propiedades multipart) — TODO-VERIFY URL y versión, consulta 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
