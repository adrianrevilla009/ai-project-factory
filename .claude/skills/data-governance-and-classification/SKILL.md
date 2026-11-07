---
name: data-governance-and-classification
description: "Usar al definir dueños, catálogo, niveles de clasificación y etiquetas de datos en una plataforma analítica (lago, warehouse, marts) antes de abrir acceso a consumidores."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Gobierno y clasificación de datos en la plataforma de datos

## Cuándo aplicar y cuándo no
- Aplica al crear datasets, tablas o dominios nuevos en el lago/warehouse y al exponerlos a analistas, BI o ML.
- No aplica a la clasificación de campos en bases transaccionales de un servicio (ver `pii-and-data-classification`).

## Reglas
- **MUST** asignar a cada dataset un dueño de negocio (data owner) y un custodio técnico (steward) registrados en el catálogo.
- **MUST** clasificar cada columna con una etiqueta de una taxonomía cerrada: `public`, `internal`, `confidential`, `restricted` (+ marca `pii` y `special-category` cuando aplique).
- **MUST** heredar la clasificación aguas abajo: una tabla derivada tiene como mínimo la clasificación más alta de sus entradas, salvo anonimización documentada.
- **MUST** mantener la clasificación como metadatos versionados en Git (YAML junto al modelo), no solo en una UI.
- **MUST NOT** publicar en una zona de consumo (gold/marts) datos sin clasificar.
- **SHOULD** usar un catálogo OSS (p. ej. DataHub u OpenMetadata, TODO-VERIFY licencia y versión) en lugar de un producto de pago (D16).
- **SHOULD** revisar la clasificación cada trimestre y al cambiar el esquema.

## Por qué
Sin dueño nadie decide quién accede ni cuánto se retiene; sin etiqueta por columna, el enmascarado y la retención (skill `access-control-masking-and-retention`) no pueden automatizarse. Que la clasificación viaje con el código permite revisarla en PR.

## Ejemplos
### Mal
```yaml
# models/customers.yml
models:
  - name: dim_customer
    description: "clientes"
```
### Bien
```yaml
# models/customers.yml (dbt)
models:
  - name: dim_customer
    description: "Cliente maestro para analítica"
    meta:
      owner: "team-sales-data"
      steward: "data-platform"
      classification: confidential
      retention_days: 1095
    columns:
      - name: email
        meta: { classification: restricted, pii: true }
      - name: country_code
        meta: { classification: internal }
```

## Checklist de revisión
- [ ] Todo dataset nuevo tiene `owner`, `steward` y `classification`.
- [ ] Cada columna personal lleva `pii: true`.
- [ ] Las tablas derivadas no bajan la clasificación sin justificación escrita.
- [ ] El catálogo refleja los metadatos de Git.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana de PR de modelos (agente `code-reviewer`) | 3 | PR del proyecto generado |
| Test de esquema que exige `meta.owner` y `meta.classification` (dbt/script) | 1 | pendiente, en el proyecto generado |
| Regla Conftest sobre YAML de modelos | 1 | pendiente (`policies/opa-conftest/`) |

> Estado: sin artefacto en este repo todavía; la comprobación es revisión humana hasta crear la regla.

## Relacionados, fuentes y mantenimiento
- Relacionados: `pii-and-data-classification`, `data-contracts-and-lineage`, `access-control-masking-and-retention`, `gdpr-in-the-lake`.
- Fuentes: documentación de DataHub/OpenMetadata — TODO-VERIFY URL y versión. Normativa: borrador por confirmar con fuente oficial.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
