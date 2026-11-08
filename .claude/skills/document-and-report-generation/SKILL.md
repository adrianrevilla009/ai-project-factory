---
name: document-and-report-generation
description: "Usar al generar PDF, Excel/CSV o informes desde el backend: plantillas, asincronía, almacenamiento, límites de memoria y datos sensibles."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Generación de documentos e informes

## Cuándo aplicar y cuándo no
- Aplica a facturas, certificados, extractos, exportes Excel/CSV y informes bajo demanda o programados.
- No aplica a dashboards interactivos (BI) ni a notificaciones (ver `notifications`).

## Reglas
- **MUST** generar de forma asíncrona cualquier informe que pueda superar unos segundos: `POST /reports` devuelve `202` con `reportId`; el cliente consulta estado y descarga.
- **MUST** hacer streaming (no cargar el resultado completo en memoria): cursor/`Stream` hacia el escritor, tamaño de página acotado.
- **MUST** guardar el artefacto en almacenamiento de objetos con TTL y descargarlo por URL firmada de corta vida o endpoint autenticado.
- **MUST** autorizar la descarga contra el propietario/tenant del informe, no solo por conocer el id.
- **MUST** separar plantilla de datos; plantillas versionadas en el repo (HTML→PDF, XLSX).
- **MUST NOT** construir HTML de plantilla concatenando entrada del usuario (XSS/SSRF en conversores HTML→PDF); escapar y bloquear recursos remotos.
- **MUST NOT** incluir más campos personales de los necesarios; marcar el informe con clasificación de datos.
- **SHOULD** neutralizar fórmulas en CSV/Excel (prefijos `=`, `+`, `-`, `@`) para evitar CSV injection.
- **SHOULD** elegir librerías con licencia compatible con D16; licencias de iText/JasperReports/otras: comprobar al fijar la versión.

## Por qué
Un informe síncrono de 200 000 filas agota heap y hilos de petición. Los generadores PDF a partir de HTML pueden resolver URLs internas. Un id adivinable sin autorización expone datos de otros clientes.

## Ejemplos
### Mal
```java
@GetMapping("/report")
byte[] report() { return pdf(repo.findAll()); } // todo en memoria, síncrono, sin autorización
```
### Bien
```java
@PostMapping("/reports")
ResponseEntity<Void> request(@RequestBody ReportRequest r, Principal p) {
    var id = reports.enqueue(r, p.getName());
    return ResponseEntity.accepted().location(URI.create("/reports/" + id)).build();
}

void write(OutputStream out, Principal owner) {
    try (var rows = repo.streamByTenant(tenantOf(owner))) { // Stream cerrado
        rows.map(CsvSanitizer::sanitize).forEach(r -> csv.write(out, r));
    }
}
```

## Checklist de revisión
- [ ] Generación asíncrona con estado y TTL.
- [ ] Streaming, sin colecciones completas en memoria.
- [ ] Descarga autorizada por propietario/tenant.
- [ ] Sin recursos remotos en conversión HTML→PDF; CSV injection mitigado.
- [ ] Licencia de la librería revisada.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep de XXE en parsers XML | 1 | `policies/semgrep/xml-parser-xxe.yaml` |
| Semgrep de rutas desde entrada de usuario | 1 | `policies/semgrep/java-path-from-user-input.yaml` |
| Test de descarga de informe ajeno (403) | 1 | tests del proyecto generado |
| Revisión de licencia y datos incluidos | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `import-export-and-bulk-data`, `scheduling-and-batch-jobs`, `pii-and-data-classification`.
- Fuentes: OWASP CSV Injection (por nombre; URL y versión se fijan al adoptarlas en el proyecto). Preparado para AWS (S3 + URL firmada), no verificado en real; en local se usa un emulador/MinIO.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
