---
name: rag-architecture
description: "Usar al diseñar un sistema RAG (ingesta, chunking, embeddings, recuperación, reranking, generación con citas): decisiones de arquitectura y fallos típicos."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Arquitectura RAG

## Cuándo aplicar y cuándo no
- Aplica al responder con LLM sobre conocimiento propio que cambia o que no cabe en el prompt.
- No aplica si el corpus cabe en el contexto y casi no cambia (basta el prompt), ni si hace falta razonamiento sobre datos tabulares (usar SQL/herramientas, ver `agents-and-tool-calling`).

## Reglas
- **MUST** separar dos pipelines: ingesta (offline, idempotente, reintentable) y consulta (online, con timeout).
- **MUST** guardar con cada chunk metadatos: `source_id`, `version`, `acl` (grupos autorizados), `tenant`, `updated_at`, ubicación (página/sección).
- **MUST** filtrar por `acl` y `tenant` en la consulta al vector store, antes de que el texto llegue al LLM; nunca filtrar después de generar.
- **MUST** versionar el modelo de embeddings junto al índice; cambiar de modelo implica reindexar entero (los vectores no son comparables).
- **MUST** exigir citas: la respuesta incluye `source_id` y ubicación; si no hay contexto relevante, responder "no lo sé" en lugar de inventar.
- **SHOULD** chunking por estructura (secciones/párrafos) con solapamiento pequeño, y medir tamaños con datos reales, no por defecto.
- **SHOULD** recuperación híbrida (léxica + vectorial) y reranking si la precisión lo exige.
- **MUST NOT** tratar el contenido recuperado como instrucciones: va delimitado y declarado como dato (ver `prompt-injection-defense-for-agents`).
- **MUST** evaluar con un conjunto dorado (recall@k de recuperación y fidelidad de respuesta) antes de cambiar chunking, modelo o k (ver `llm-evals`, pendiente).
- **MUST NOT** doble escritura: el índice vectorial es derivado y reconstruible desde la fuente de verdad.

## Por qué
La mayoría de fallos de RAG son de recuperación (chunk malo, filtro ausente, índice obsoleto), no del modelo. Los permisos deben aplicarse en la recuperación: un LLM no puede "olvidar" lo que ya vio.

## Ejemplos
### Mal
```java
var docs = vectorStore.similaritySearch("vacaciones");       // sin filtro de acl/tenant
String ctx = docs.stream().map(Document::getText).collect(joining("\n"));
return chat.prompt().user("Contesta con: " + ctx + "\n" + question).call().content();
```
### Bien
```java
var request = SearchRequest.builder()
    .query(question).topK(6).similarityThreshold(0.6)
    .filterExpression("tenant == 'example-tenant' && acl in ['hr','all']") // expresión construida desde el principal autenticado
    .build();
var docs = vectorStore.similaritySearch(request);
if (docs.isEmpty()) return Answer.unknown();
return generator.answerWithCitations(question, docs); // contexto delimitado y citas obligatorias
```
Las firmas exactas de `SearchRequest` y filtros dependen de la versión de Spring AI.

## Checklist de revisión
- [ ] Ingesta idempotente y separada de consulta.
- [ ] Metadatos de ACL/tenant y filtro previo.
- [ ] Modelo de embeddings versionado; plan de reindexado.
- [ ] Respuesta con citas y camino "no sé".
- [ ] Conjunto dorado y métricas de recuperación.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test de integración: usuario sin permiso no recupera chunks restringidos | 1 | tests del proyecto generado |
| Evaluación en CI con conjunto dorado | 2 | pendiente (`llm-evals`) |
| Revisión de diseño de recuperación | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `rag-over-enterprise-docs`, `vector-store-selection` (pendiente), `llm-security`, `llm-observability`, `pii-and-data-classification`.
- Fuentes: Spring AI Reference, RAG y VectorStore (docs.spring.io/spring-ai/reference); OWASP Top 10 for LLM Applications.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
