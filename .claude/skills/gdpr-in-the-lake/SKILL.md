---
name: gdpr-in-the-lake
description: "Usar al diseñar borrado, rectificación, minimización y bases legales sobre datos personales en lago/warehouse (formatos append-only, backups, copias derivadas). Borrador legal."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# RGPD en el lago de datos

> Borrador técnico por confirmar con asesoría legal y fuente oficial; no es asesoramiento jurídico.

## Cuándo aplicar y cuándo no
- Aplica cuando el lago, warehouse o feature store contienen datos personales de personas en la UE.
- No aplica a datos agregados verdaderamente anónimos (la anonimización debe poder defenderse; la seudonimización sigue siendo dato personal).

## Reglas
- **MUST** mantener un inventario de dónde vive cada dato personal (tablas, copias, marts, features) enlazado al catálogo.
- **MUST** poder atender una solicitud de supresión (art. 17) propagándola a raw, silver, gold, features y exportaciones, salvo excepciones del art. 17(3).
- **MUST** definir base legal y finalidad por dataset; no reutilizar para fines incompatibles.
- **MUST** minimizar: no ingerir columnas personales que ningún caso de uso necesite.
- **MUST** documentar cómo se tratan los backups (expiración dentro de un plazo definido, sin restauración selectiva de datos ya suprimidos).
- **SHOULD** separar la identidad (tabla de claves) de los atributos analíticos; borrar la clave rompe el vínculo (crypto-shredding o tokenización).
- **SHOULD** usar tablas con borrado a nivel de fila (Apache Iceberg/Delta) y compactar y expirar snapshots para eliminar físicamente los ficheros.
- **MUST NOT** dar por cumplida una supresión solo con `DELETE` lógico mientras sigan snapshots, ficheros huérfanos o time travel con el dato.
- **MUST NOT** afirmar cumplimiento RGPD completo: solo "diseñado para facilitar", pendiente de revisión legal.

## Por qué
Los formatos del lago son inmutables por diseño; un `DELETE` solo escribe metadatos nuevos y el dato sigue en ficheros antiguos. El art. 17 exige supresión sin dilación indebida cuando aplica un motivo (fuente: https://gdpr-info.eu/art-17-gdpr/, consultada 2026-11-07, texto no oficial; confirmar en EUR-Lex). En Iceberg, `expire_snapshots` y `remove_orphan_files` existen como procedimientos de Spark (https://iceberg.apache.org/docs/latest/spark-procedures/, 2026-11-07); semántica exacta por versión.

## Ejemplos
### Mal
```sql
DELETE FROM silver.customers WHERE customer_id = 42;
-- listo; los snapshots anteriores siguen conteniendo el dato
```
### Bien
```sql
DELETE FROM silver.customers WHERE customer_id = 42;
CALL system.expire_snapshots(table => 'silver.customers',
                             older_than => TIMESTAMP '2026-11-07 00:00:00');
CALL system.remove_orphan_files(table => 'silver.customers');
-- repetir en gold.*, features.* y registrar en erasure_log (sin PII)
```
```yaml
# erasure_log (sin datos personales)
request_id: "req-example-001"
subject_token: "tok_example"
completed_layers: [raw, silver, gold, features]
completed_at: "2026-11-07"
```

## Checklist de revisión
- [ ] Inventario de datos personales actualizado.
- [ ] Flujo de supresión cubre todas las capas y copias derivadas.
- [ ] Snapshots y huérfanos se purgan en plazo definido.
- [ ] Backups: política de expiración documentada.
- [ ] Revisión legal pendiente registrada.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana del flujo de supresión y de la base legal | 3 | agente `code-reviewer` + DPO del cliente |
| Test del proyecto: tras supresión, el id no aparece en ninguna capa (incl. time travel) | 1 | pendiente, proyecto generado |

## Relacionados, fuentes y mantenimiento
- Relacionados: `data-governance-and-classification`, `access-control-masking-and-retention`, `pii-and-data-classification`, `consent-and-dsar-management`.
- Fuentes: art. 17 RGPD (URL arriba); documentación de Iceberg. Plazos (art. 12(3)).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
