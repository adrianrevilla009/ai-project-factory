---
name: mongodb-alternative
description: "Usar solo si se propone MongoDB (o compatible) en lugar de DynamoDB como almacén documental; referencia T3 con criterios y límites."
metadata:
  block: "22-polyglot-persistence"
  tier: T3
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "review"
---

# MongoDB como alternativa documental

## Cuándo aplicar y cuándo no
- Aplica cuando un requisito real (consultas ad hoc sobre documentos anidados, despliegue on-prem, sin acoplamiento a AWS) hace dudar de DynamoDB o de JSONB en Postgres.
- No aplica por defecto: el estándar es Postgres + DynamoDB (ADR-0013). Es una referencia T3, no un camino soportado por la fábrica.

## Reglas
- **MUST** descartar antes Postgres con `jsonb` e índices GIN, que cubre muchos casos documentales sin almacén nuevo.
- **MUST** abrir un ADR con la comparación, el coste operativo (`polyglot-operations-cost`) y el plan de salida.
- **MUST** revisar la licencia y el modelo de distribución antes de elegir edición o servicio gestionado; la fábrica evita licencias de pago por defecto (D16). MongoDB se distribuye bajo la SSPL, que la OSI no reconoce como licencia de código abierto y que obliga a quien ofrezca MongoDB como servicio a licenciarlo o liberar su código (verificado el 2026-11-08); un revisor legal debe validar el uso previsto.
- **MUST** mantener las mismas reglas de oro: una fuente de verdad por agregado, sin doble escritura con Postgres, proyecciones derivadas.
- **MUST NOT** usarlo como event store sin demostrar equivalente de append condicional por versión (índice único `(streamId, version)`).
- **SHOULD** tratar Amazon DocumentDB como producto distinto con API compatible, no como MongoDB.
- **SHOULD** preferir el emulador/contenedor local para pruebas y declarar qué no se reproduce de la variante gestionada.

## Por qué
DynamoDB exige conocer los patrones de acceso de antemano; MongoDB permite consultas más flexibles a costa de operar clusters y de licencias a revisar. Muchas veces el problema real se resuelve con `jsonb` en Postgres. Esta nota evita que la alternativa se adopte sin análisis.

## Ejemplos
### Mal
```text
"Usamos MongoDB para el catálogo y además guardamos el catálogo en Postgres por si acaso."
```
### Bien
```sql
-- Primero probar JSONB en el almacén ya existente
create index idx_product_attrs on product using gin (attributes jsonb_path_ops);
select id from product where attributes @> '{"color":"red"}';
```
```text
Si JSONB no basta (medido): ADR con comparación, fuente de verdad única (Mongo), proyección a OpenSearch derivada, ficha de coste y plan de salida.
```

## Checklist de revisión
- [ ] JSONB en Postgres evaluado y descartado con datos.
- [ ] ADR con coste, licencia (SSPL, revisión legal) y salida.
- [ ] Sin doble escritura con otro almacén.
- [ ] Diferencias entre emulación local y servicio gestionado declaradas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana del ADR en el gate de arquitectura | 4 | `gates/` (revisión humana) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `datastore-selection-guide`, `polyglot-operations-cost`, `dynamodb-data-modeling`, `license-policy`.
- Fuentes: documentación oficial de MongoDB y de Amazon DocumentDB — no consultadas en esta revisión.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T3
