---
name: vector-store-selection
description: "Usar al elegir dónde guardar embeddings para búsqueda semántica o RAG: pgvector, OpenSearch u otros, con criterios de escala, filtrado, consistencia y coste."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Selección de almacén vectorial

## Cuándo aplicar y cuándo no
- Aplica al diseñar búsqueda semántica, RAG o deduplicación por similitud.
- No aplica a búsqueda por palabras clave pura (índice de texto) ni a la elección del modelo de embeddings en sí.

## Reglas
- **MUST** empezar por la opción más simple que cubra el volumen: pgvector en el Postgres existente si hay menos de unos pocos millones de vectores (umbral orientativo, medir en el proyecto).
- **MUST** decidir con una prueba medida sobre datos propios: recall@k frente a búsqueda exacta, latencia p95 y coste (ver `llm-evals`).
- **MUST** no duplicar el dato maestro: el vector es un derivado reconstruible de la fuente; si la fuente es Postgres y el vector va a otro motor, usar outbox/CDC y declararlo derivado (regla 4.5, sin doble escritura).
- **MUST** guardar con cada vector: id de la fuente, versión del modelo de embeddings, dimensión y tenant; un cambio de modelo exige reindexar todo.
- **MUST** aplicar filtros de autorización (tenant, permisos del documento) en la propia consulta vectorial, no después de recuperar.
- **MUST** elegir la métrica de distancia que corresponde al modelo (coseno, producto interno o L2) y usar el mismo operador que el índice.
- **SHOULD** usar índice HNSW en pgvector para consultas con buena relación velocidad/recall (más memoria y build lento) e IVFFlat si importa más el tiempo de construcción; TODO-VERIFY versión de pgvector instalada.
- **SHOULD** valorar OpenSearch (k-NN) cuando ya se opera para búsqueda de texto y se necesita búsqueda híbrida (léxica + vectorial) o escala horizontal; preparado para AWS, no verificado en real.
- **SHOULD** medir recall tras cambios de parámetros del índice (`ef_search`, `lists`/`probes`).
- **MUST NOT** adoptar un servicio gestionado de pago por defecto (D16) sin ADR con coste.
- **MUST NOT** indexar PII sin clasificación y política de borrado: borrar la fuente implica borrar sus vectores.

## Por qué
Un almacén vectorial adicional añade operación, sincronización y un segundo sitio donde viven datos sensibles. Con volúmenes moderados, pgvector da transacciones, filtros SQL y una sola copia de seguridad. Cuando el volumen, la búsqueda híbrida o el aislamiento de carga lo exigen, un motor dedicado compensa. Los índices aproximados pierden recall, así que hay que medirlo.

## Ejemplos
### Mal
```sql
-- sin índice, sin versión de modelo, filtro de tenant aplicado en Java tras recuperar
SELECT id FROM chunks ORDER BY embedding <-> :q LIMIT 10;
```
### Bien
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE chunk (
  id uuid PRIMARY KEY, tenant_id uuid NOT NULL, doc_id uuid NOT NULL,
  embedding_model text NOT NULL, embedding vector(1024) NOT NULL, text text NOT NULL);
CREATE INDEX chunk_embedding_hnsw ON chunk USING hnsw (embedding vector_cosine_ops);

SELECT id, text FROM chunk
WHERE tenant_id = :tenant AND embedding_model = :model
ORDER BY embedding <=> :query_embedding
LIMIT 10;
```
La dimensión (1024) es un ejemplo; debe coincidir con el modelo elegido. Un filtro selectivo con índice aproximado puede devolver menos de k resultados: probar `hnsw.iterative_scan` si la versión lo soporta (TODO-VERIFY).

## Checklist de revisión
- [ ] Opción más simple evaluada primero, con recall y latencia medidos.
- [ ] Vector tratado como derivado; sin doble escritura.
- [ ] Modelo y dimensión registrados; plan de reindexado.
- [ ] Filtro de tenant/permisos dentro de la consulta.
- [ ] Borrado de la fuente propaga a los vectores.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Test de aislamiento por tenant en consultas vectoriales | 1 | pendiente (proyecto generado) |
| Revisión del ADR de selección con medidas | 3 | agente `code-reviewer` / revisión humana |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `llm-evals`, `llm-security`, `pii-and-data-classification`, `idor-and-object-level-authorization`, `token-and-cost-budgets`.
- Fuentes: README de pgvector (HNSW, IVFFlat, `vector_cosine_ops`) vía https://pgxn.org/dist/vector/, consultado 2026-11-07; documentación de OpenSearch k-NN (TODO-VERIFY).
- En local OpenSearch/pgvector corren en contenedor; no se reproduce el dimensionado ni el aislamiento de un servicio gestionado en AWS.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
