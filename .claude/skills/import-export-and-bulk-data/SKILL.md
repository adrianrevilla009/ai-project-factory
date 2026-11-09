---
name: import-export-and-bulk-data
description: "Usar al implementar importación/exportación masiva (CSV/Excel/JSON) por usuarios o integraciones: validación, staging, errores por fila e idempotencia."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Importación, exportación y datos masivos

## Cuándo aplicar y cuándo no
- Aplica a cargas de ficheros por usuarios/back-office, migraciones de datos y exportes grandes.
- No aplica a integraciones por API fila a fila ni a ETL analítico fuera del producto. Para el motor de jobs ver `scheduling-and-batch-jobs`.

## Reglas
- **MUST** procesar importaciones de forma asíncrona: subir fichero a almacenamiento, crear `import_job` con estado (`PENDING/RUNNING/DONE/FAILED`) y procesar por chunks.
- **MUST** validar tipo real, tamaño máximo y número máximo de filas antes de procesar; rechazar lo que exceda.
- **MUST** cargar primero a una tabla de staging, validar y luego aplicar; informe de errores por fila (nº de fila, campo, motivo) descargable.
- **MUST** hacer la importación idempotente: clave natural o `import_job_id + row_number` con restricción única; reintentar un job no duplica.
- **MUST** definir si la política es todo-o-nada o parcial con errores, y documentarla al usuario.
- **MUST NOT** interpretar entrada del usuario como fórmula, ruta o SQL; parámetros enlazados siempre; parsers XML sin entidades externas.
- **MUST NOT** cargar el fichero completo en memoria; lectura en streaming.
- **SHOULD** autorizar por tenant y registrar en auditoría quién importó qué (`audit-trail-and-activity-log`).
- **SHOULD** usar inserciones en lote (`batch size` acotado) y deshabilitar `open-in-view`.

## Por qué
Un CSV de 2 millones de filas procesado en la petición causa timeouts y estados a medias. Sin staging y sin errores por fila, el usuario no puede corregir. Sin idempotencia, el reintento duplica registros.

## Ejemplos
### Mal
```java
@PostMapping("/import")
void imp(@RequestParam MultipartFile f) throws IOException {
    for (String line : new String(f.getBytes()).split("\n")) {
        repo.save(parse(line)); // memoria, una a una, sin errores por fila
    }
}
```
### Bien
```sql
CREATE TABLE import_row_error (
  import_job_id UUID NOT NULL, row_number INT NOT NULL, field TEXT, reason TEXT NOT NULL,
  PRIMARY KEY (import_job_id, row_number, field)
);
CREATE UNIQUE INDEX customer_import_uq ON customer_import_stage (import_job_id, row_number);
```
```java
@PostMapping("/imports")
ResponseEntity<Void> upload(@RequestParam MultipartFile f, Principal p) {
    limits.assertAllowed(f); // tamaño, tipo real, filas máx.
    var id = imports.storeAndEnqueue(f, p.getName()); // devuelve 202
    return ResponseEntity.accepted().location(URI.create("/imports/" + id)).build();
}
```

## Checklist de revisión
- [ ] Procesado asíncrono con estado consultable.
- [ ] Límites de tamaño/filas y validación de tipo real.
- [ ] Staging + informe de errores por fila.
- [ ] Idempotente; política parcial/todo-o-nada documentada.
- [ ] Streaming, sin carga completa en memoria; auditoría.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep XXE | 1 | `policies/semgrep/xml-parser-xxe.yaml` |
| Semgrep SQL por concatenación | 1 | `policies/semgrep/sql-string-concat.yaml` |
| Semgrep rutas desde entrada de usuario | 1 | `policies/semgrep/java-path-from-user-input.yaml` |
| Test de reintento de import (sin duplicados) | 1 | tests del proyecto generado |

## Relacionados, fuentes y mantenimiento
- Relacionados: `batching-and-bulk-ops`, `document-and-report-generation`, `idempotency-keys`, `audit-trail-and-activity-log`.
- Fuentes: Spring Batch reference (2026-11-07); límites de subida y antivirus. Preparado para AWS (S3), no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
