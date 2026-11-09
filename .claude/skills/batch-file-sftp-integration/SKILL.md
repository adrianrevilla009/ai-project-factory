---
name: batch-file-sftp-integration
description: "Usar al integrar por ficheros (CSV/XML) vía SFTP o almacenamiento compartido con Spring Batch: atomicidad, checksums, reinicio e idempotencia."
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Integración por ficheros, batch y SFTP

## Cuándo aplicar y cuándo no
- Aplica a intercambios por lotes con terceros o sistemas heredados que entregan/recogen ficheros (SFTP, bucket, carpeta compartida).
- No aplica a flujos con requisito de baja latencia (usar API o eventos).

## Reglas
- **MUST** transferir con escritura atómica: subir como `name.csv.part` y renombrar a `name.csv` al terminar; el receptor solo lee ficheros sin sufijo temporal.
- **MUST** acompañar cada fichero de checksum (SHA-256) o fichero de control con nº de registros, y validarlo antes de procesar.
- **MUST** procesar cada fichero de forma idempotente: registrar nombre + checksum en una tabla de ficheros procesados y rechazar duplicados.
- **MUST** usar Spring Batch con `chunk`, estado persistente y reinicio (`JobRepository`); **MUST NOT** cargar el fichero completo en memoria.
- **MUST** definir política de errores por registro (`skip` con límite, a fichero de rechazos) y de fichero (mover a `error/`).
- **MUST** autenticación SFTP por clave, **verificación de host key** (nunca aceptar todas) y credenciales en el gestor de secretos.
- **MUST NOT** registrar contenido de registros con PII; cifrar ficheros sensibles en tránsito (SFTP) y reposo, y aplicar retención/borrado.
- **SHOULD** versionar el layout del fichero y documentarlo como contrato (columnas, codificación UTF-8, separador, formato de fecha ISO-8601).
- **SHOULD** carpetas `inbox/`, `processing/`, `done/`, `error/` y ventana de proceso documentada.

## Por qué
Un fichero leído mientras aún se escribe produce cargas parciales silenciosas. Sin idempotencia, un reintento del emisor duplica datos. Aceptar cualquier host key permite un ataque de intermediario. Las APIs de Spring Batch 5 y de la librería SFTP elegida deben verificarse en su documentación.

## Ejemplos
### Mal
```java
List<String> lines = Files.readAllLines(Path.of("/data/in/orders.csv")); // todo en memoria, fichero posiblemente a medias
lines.forEach(l -> repo.save(parse(l)));                                  // sin idempotencia ni reinicio
```
```properties
sftp.allow-unknown-hosts=true
```
### Bien
```java
@Bean
Step importOrdersStep(JobRepository repo, PlatformTransactionManager tx,
                      FlatFileItemReader<OrderRow> reader, OrderWriter writer) {
    return new StepBuilder("importOrders", repo)
        .<OrderRow, OrderEntity>chunk(500, tx)
        .reader(reader)
        .processor(OrderMapper::toEntity)
        .writer(writer)
        .faultTolerant().skipLimit(20).skip(FlatFileParseException.class)
        .build();
}

void ingest(Path file, String sha256) {
    if (!processedFiles.registerIfAbsent(file.getFileName().toString(), sha256)) { return; }
    launcher.run(importJob, new JobParametersBuilder()
        .addString("file", file.toString()).addString("sha256", sha256).toJobParameters());
}
```
```properties
sftp.host=sftp.example.com
sftp.known-hosts=/etc/factory/known_hosts
sftp.password=changeme-example
```

## Criterios de decisión y trampas
### Cómo decidir
- Procesa ficheros con validación previa, idempotencia por nombre y suma de comprobación, y mueve a «procesado» o «error».
- Define el contrato del fichero (formato, codificación, frecuencia).
### Trampas frecuentes
- Procesar un fichero a medio escribir.
- Sin validar antes de cargar.
- Reprocesar el mismo fichero y duplicar datos.
- Credenciales SFTP compartidas.
- Sin alerta si no llega el fichero esperado.
### Evidencia
- Una alerta de fichero no recibido y una prueba con fichero corrupto y repetido.

## Checklist de revisión
- [ ] Entrega atómica (`.part` + rename) y checksum validado.
- [ ] Idempotencia por nombre+checksum; job reiniciable.
- [ ] Proceso por chunks, sin carga total en memoria.
- [ ] Host key verificada, secretos fuera del código.
- [ ] Rechazos, retención y PII tratados; layout documentado.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test de reinicio y de fichero duplicado del job | 1 | tests del proyecto generado (pendiente) |
| Regla Semgrep contra aceptar todas las host keys | 1 | `policies/semgrep/` (pendiente) |
| Revisión de contrato de fichero | 3 | agente `code-reviewer` / revisión humana |

> Estado: artefactos pendientes; revisión humana mientras tanto. En AWS el equivalente (AWS Transfer Family / S3) está preparado para AWS, no verificado en real; en local no se reproduce.

## Relacionados, fuentes y mantenimiento
- Relacionados: `delivery-semantics`, `file-upload-security`, `pii-and-data-classification`, `secrets-management`.
- Fuentes: documentación de Spring Batch (chunk, restart, skip) y de Spring Integration SFTP.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
