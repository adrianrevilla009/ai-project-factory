---
name: ocr-options
description: "Usar al elegir el motor OCR de un pipeline de documentos: Tesseract local frente a servicios gestionados o modelos de visión, con criterios de calidad, coste y privacidad."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Opciones de OCR

## Cuándo aplicar y cuándo no
- Aplica al decidir cómo convertir imágenes o PDF escaneados en texto/estructura dentro de un proyecto.
- No aplica a PDF con capa de texto nativa (extraer el texto directamente) ni al diseño del pipeline completo (ver `intelligent-document-processing`).

## Reglas
- **MUST** comprobar primero si el PDF tiene texto embebido; usar OCR solo en páginas sin él.
- **MUST** decidir el motor con una muestra etiquetada del dominio real (al menos 50 documentos de calidad variable) y métricas de `llm-evals`: tasa de error de caracteres/campos, tablas, manuscrito.
- **MUST** aislar el motor tras una interfaz (`OcrEngine`) que devuelva texto, confianza, página y coordenadas, para poder cambiarlo.
- **MUST** registrar motor y versión por documento (trazabilidad).
- **MUST** evaluar privacidad antes de enviar documentos a un servicio externo: clasificación de datos, región, retención y acuerdo con el proveedor (ver `pii-and-data-classification`).
- **MUST** preprocesar de forma explícita (rotación, deskew, resolución ~300 dpi) y medir su efecto; no asumirlo.
- **SHOULD** usar Tesseract (licencia Apache 2.0, ejecución local, sin coste por página) como opción por defecto de la fábrica para texto impreso limpio; comprobar versión y paquetes de idioma al fijar el proyecto.
- **SHOULD** valorar un servicio gestionado (p. ej. Amazon Textract, preparado para AWS, no verificado en real) o un modelo de visión cuando haya tablas, formularios o manuscrito y los datos lo permitan.
- **SHOULD** limitar páginas por documento, tamaño y tiempo por página; procesar en cola asíncrona.
- **MUST NOT** tratar la confianza del motor como probabilidad calibrada sin comprobarlo.
- **MUST NOT** introducir un servicio de pago por defecto (D16); si se elige, documentarlo en un ADR con coste estimado.

## Por qué
La calidad del OCR condiciona todo lo posterior: un error en un dígito del importe sobrevive a la extracción. Los motores difieren mucho según el tipo de documento, y solo una muestra propia lo revela. Local frente a servicio externo es una decisión de privacidad y coste, no solo de calidad.

## Ejemplos
### Mal
```java
String text = new Tesseract().doOCR(file);   // sin comprobar capa de texto, sin versión, sin confianza
```
### Bien
```java
public interface OcrEngine {
    OcrResult read(Path image, OcrOptions options);   // texto + confianza + bbox por palabra
    String name();
    String version();
}

OcrResult readPage(PdfPage page, OcrEngine ocr) {
    if (page.hasEmbeddedText()) return OcrResult.fromEmbedded(page.text());
    Path img = preprocessor.render(page, 300);        // 300 dpi, deskew
    return ocr.read(img, OcrOptions.of("spa+eng"));
}
```
Comparativa mínima a rellenar con la muestra del proyecto:
```text
motor        CER   campos_ok   tablas   coste/1000 pag   datos salen de la red
tesseract    ...   ...         ...      0                no
servicio X   ...   ...         ...      ...              si
```

## Checklist de revisión
- [ ] Se usa texto embebido cuando existe.
- [ ] Decisión basada en muestra etiquetada propia.
- [ ] Interfaz `OcrEngine` y versión registrada por documento.
- [ ] Privacidad y retención evaluadas si es externo.
- [ ] Sin servicio de pago por defecto sin ADR.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Evaluación del motor con la muestra etiquetada | 3 | revisión humana de la comparativa (ADR del proyecto) |
| Revisión de privacidad del servicio externo | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `intelligent-document-processing`, `document-management`, `llm-evals`, `pii-and-data-classification`, `file-upload-security`.
- Fuentes: https://github.com/tesseract-ocr/tesseract (licencia Apache 2.0, consultada 2026-11-07); documentación oficial de Amazon Textract (comprobar precios y regiones).
- En local no se reproduce Textract; se usa Tesseract como sustituto funcional, con calidad distinta.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
