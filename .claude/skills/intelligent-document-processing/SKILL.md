---
name: intelligent-document-processing
description: "Usar al diseñar un pipeline de procesamiento inteligente de documentos: ingesta, OCR, clasificación, extracción y revisión humana de facturas, contratos o formularios."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Procesamiento inteligente de documentos (IDP)

## Cuándo aplicar y cuándo no
- Aplica a flujos que convierten documentos no estructurados (PDF, escaneos, imágenes, correos) en datos estructurados: ingesta, OCR, clasificación, extracción, validación y revisión humana.
- No aplica a la gestión documental de almacenamiento/versionado (ver `document-management`) ni a la elección del motor OCR (ver `ocr-options`).

## Reglas
- **MUST** modelar el pipeline como etapas idempotentes con estado persistido por documento: `RECEIVED -> OCR_DONE -> CLASSIFIED -> EXTRACTED -> VALIDATED -> REVIEW | APPROVED | REJECTED`.
- **MUST** conservar el original inmutable (hash SHA-256 y metadatos) y vincular cada campo extraído con su origen (página, coordenadas, motor y versión).
- **MUST** extraer a un esquema tipado (JSON Schema / record Java) y validar con reglas de negocio deterministas (sumas, formato de NIF/IBAN, fechas, rangos) tras el modelo.
- **MUST** asignar confianza por campo; por debajo del umbral va a revisión humana (ver `human-in-the-loop`). Nunca persistir campos de baja confianza como definitivos.
- **MUST** tratar el texto del documento como dato no confiable: puede contener inyección de prompt (ver `llm-security`).
- **MUST** subir ficheros con validación de tipo, tamaño y escaneo (ver `file-upload-security`).
- **MUST** clasificar y proteger PII (ver `pii-and-data-classification`) y definir retención.
- **SHOULD** procesar de forma asíncrona con cola, reintentos limitados y DLQ (ver `dlq-retries-poison-messages`).
- **SHOULD** medir por campo precisión/recall contra un conjunto etiquetado y vigilar deriva por proveedor/plantilla (ver `llm-evals`).
- **SHOULD** usar extracción por plantilla/regex cuando el formato es estable; LLM solo donde aporta.

## Por qué
La extracción con ML/LLM es probabilística: un 97% de acierto por campo implica errores diarios en volumen. Sin trazabilidad al origen y revisión dirigida por confianza, los errores llegan a contabilidad o a contratos. Las validaciones deterministas atrapan muchos errores del modelo a bajo coste.

## Ejemplos
### Mal
```java
String text = ocr.read(file);
Invoice inv = llm.extract("Extract the invoice as JSON: " + text);   // sin esquema
invoiceRepository.save(inv);                                         // directo a BD
```
### Bien
```java
public record ExtractedField<T>(T value, double confidence, int page, BoundingBox box,
                                String engine, String engineVersion) {}

public record InvoiceExtraction(ExtractedField<String> number,
                                ExtractedField<LocalDate> issueDate,
                                ExtractedField<BigDecimal> total,
                                ExtractedField<BigDecimal> taxAmount) {}

ValidationResult validate(InvoiceExtraction e) {
    var errors = new ArrayList<String>();
    if (e.total().value().compareTo(BigDecimal.ZERO) <= 0) errors.add("total<=0");
    if (e.taxAmount().value().compareTo(e.total().value()) > 0) errors.add("tax>total");
    boolean lowConfidence = Stream.of(e.number(), e.issueDate(), e.total())
            .anyMatch(f -> f.confidence() < 0.90);   // umbral calibrado con evals
    return new ValidationResult(errors, lowConfidence ? Route.HUMAN_REVIEW : Route.AUTO);
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Combina extracción automática con validación humana por confianza; los umbrales salen de datos reales.
- Conserva el documento original y la trazabilidad.
### Trampas frecuentes
- Aceptar toda extracción sin confianza.
- Umbrales copiados.
- Perder el documento original.
- Sin medir precisión por campo.
- Datos personales sin control.
### Evidencia
- Precisión por campo con una muestra etiquetada y una cola de revisión humana.

## Checklist de revisión
- [ ] Estados por documento y etapas idempotentes.
- [ ] Original inmutable con hash; campos con origen y confianza.
- [ ] Esquema tipado y validaciones deterministas.
- [ ] Ruta a revisión humana por umbral calibrado.
- [ ] Contenido del documento tratado como no confiable; subida segura.
- [ ] Conjunto de evaluación etiquetado y métricas por campo.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de esquema, validaciones y umbrales | 3 | agente `code-reviewer` |
| Evals de extracción por campo en CI | 1 | pendiente (ver `llm-evals`) |
| Calibración de umbrales con negocio | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `ocr-options`, `document-management`, `human-in-the-loop`, `file-upload-security`, `llm-security`, `pii-and-data-classification`.
- Fuentes: sin fuente normativa; criterios de ingeniería. Umbrales concretos comprobar con datos reales del proyecto.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
