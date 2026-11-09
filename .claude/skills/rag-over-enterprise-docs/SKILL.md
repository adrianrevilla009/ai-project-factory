---
name: rag-over-enterprise-docs
description: "Usar al montar RAG sobre documentos corporativos (PDF, Office, wikis): conectores, parsing, permisos heredados, frescura, borrado y datos personales."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# RAG sobre documentos corporativos

## Cuándo aplicar y cuándo no
- Aplica a asistentes internos sobre SharePoint/Confluence/drives/PDF con permisos por documento.
- No aplica a corpus públicos sin permisos (basta `rag-architecture`) ni a extracción estructurada de formularios (ver `intelligent-document-processing`, pendiente).

## Reglas
- **MUST** heredar los permisos de la fuente: capturar la ACL original en la ingesta y re-sincronizarla de forma periódica; un cambio de permisos debe reflejarse en el índice en un SLA definido.
- **MUST** soportar borrado y expiración: cuando el documento se elimina en la fuente, se eliminan sus chunks y vectores (derecho de supresión, ver `gdpr-in-the-lake`).
- **MUST** clasificar el corpus antes de indexar (ver `pii-and-data-classification`); no indexar categorías prohibidas y redactar PII que no deba llegar al modelo (ver `guardrails-and-pii-redaction`).
- **MUST** registrar por documento: hash de contenido, versión, estado de parsing, errores; la ingesta es incremental por hash, no reprocesa todo.
- **MUST** poner OCR/parsing de PDFs escaneados en una cola con revisión de calidad; un parsing malo envenena la recuperación en silencio.
- **SHOULD** conservar estructura (títulos, tablas como texto estructurado, número de página) para citas navegables.
- **SHOULD** deduplicar versiones: indexar solo la vigente y marcar las obsoletas con `valid_to`.
- **MUST NOT** copiar el documento completo al vector store si basta un puntero a la fuente + chunks; el original sigue en su sistema.
- **MUST NOT** usar una cuenta de servicio con acceso total para responder a usuarios sin aplicar el filtro de ACL del usuario final.
- **MUST** tratar el texto de los documentos como no confiable (prompt injection indirecta, ver `prompt-injection-defense-for-agents`).

## Por qué
El riesgo principal es la fuga: el asistente con cuenta de servicio amplia revela a cualquiera lo que solo veían unos pocos. El segundo es la obsolescencia: respuestas fiables en apariencia basadas en una política derogada.

## Ejemplos
### Mal
```java
// ingesta con cuenta de servicio, ACL descartada, sin hash ni versión
for (Path p : Files.list(root).toList()) {
    vectorStore.add(splitter.apply(List.of(reader.read(p))));
}
```
### Bien
```java
record IngestedDoc(String sourceId, String contentHash, Instant sourceModified,
                   Set<String> allowedGroups, Instant validTo) {}

void ingest(SourceDoc d) {
    if (registry.hashUnchanged(d.id(), d.contentHash())) return;      // incremental
    vectorStore.delete(filter("source_id == '" + d.id() + "'"));        // reemplazo, no duplicado
    var chunks = splitter.apply(List.of(parser.parse(d)));
    chunks.forEach(c -> c.getMetadata().putAll(Map.of(
        "source_id", d.id(), "acl", d.allowedGroups(), "page", c.pageOf())));
    vectorStore.add(chunks);
    registry.record(d);
}
```
El filtro por `source_id` debe construirse con valores validados, no con texto libre del usuario.

## Checklist de revisión
- [ ] ACL capturada, sincronizada y filtrada en consulta con la identidad del usuario.
- [ ] Borrado en la fuente propaga al índice (probado).
- [ ] Clasificación/PII tratadas antes de indexar.
- [ ] Ingesta incremental con hash y versión; obsoletos excluidos.
- [ ] Calidad de parsing medida en una muestra.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test: documento borrado/permiso revocado deja de recuperarse | 1 | tests del proyecto generado |
| Revisión de conectores y cuentas de servicio | 3 | revisión humana (security-champions) |
| Regla/política automática de ACL | - | pendiente |

## Relacionados, fuentes y mantenimiento
- Relacionados: `rag-architecture`, `pii-and-data-classification`, `gdpr-in-the-lake`, `ocr-options` (pendiente), `llm-security`.
- Fuentes: RGPD arts. 17 y 25 (borrador por confirmar con fuente oficial, EUR-Lex).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
