---
name: data-modeling
description: "Usar al modelar tablas analíticas: esquema en estrella (hechos y dimensiones), granularidad, claves surrogate, SCD tipo 2, medidas aditivas y alternativas como Data Vault u OBT."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Modelado de datos analítico

## Cuándo aplicar y cuándo no
- Aplica al diseñar marts, hechos/dimensiones y tablas que consumirá BI o ML.
- No aplica al modelo relacional transaccional (ver `normalization-and-denormalization`) ni a modelos de documentos NoSQL.

## Reglas
- **MUST** declarar la granularidad de cada tabla de hechos en una frase ("una fila por línea de pedido") antes de añadir columnas.
- **MUST** separar hechos (medidas numéricas, eventos) de dimensiones (contexto descriptivo).
- **MUST** usar claves surrogate en dimensiones y conservar la clave natural como atributo.
- **MUST** tratar dimensiones que cambian con SCD tipo 2 (`valid_from`, `valid_to`, `is_current`) cuando la historia importa.
- **MUST** usar una dimensión de fecha compartida (conformada) y unidades/monedas explícitas.
- **MUST NOT** mezclar granularidades en una misma tabla de hechos.
- **MUST NOT** sumar medidas no aditivas (ratios, saldos) entre dimensiones; guardar numerador y denominador.
- **SHOULD** empezar con estrella; usar Data Vault solo con muchas fuentes cambiantes y necesidad de auditoría, y OBT (tabla ancha) solo como capa de consumo derivada.
- **SHOULD** marcar columnas PII/clasificación como metadato (ver `data-governance-and-classification`).

## Por qué
La mayoría de errores en informes vienen de granularidad ambigua (fan-out en joins) y de dimensiones sobrescritas que reescriben la historia. La estrella da consultas simples y predecibles; la elección entre estrella, Data Vault y OBT es de contexto, no dogma (comprobar referencias de Kimball/Linstedt, no consultadas aquí).

## Ejemplos
### Mal
```sql
create table sales (order_id int, customer_name text, customer_city text,
                    product_name text, total numeric, line_amount numeric); -- granularidad mixta, nombres sin clave
```
### Bien
```sql
-- granularidad: una fila por línea de pedido
create table dim_customer (
  customer_sk bigint primary key, customer_id text not null, city text,
  valid_from date not null, valid_to date, is_current boolean not null);
create table fct_order_line (
  order_id text not null, line_no int not null,
  customer_sk bigint not null references dim_customer(customer_sk),
  date_key int not null, product_sk bigint not null,
  quantity int not null, amount_eur numeric(12,2) not null,
  primary key (order_id, line_no));
```

## Checklist de revisión
- [ ] Granularidad escrita y única por hecho.
- [ ] Claves surrogate y SCD2 donde hay historia.
- [ ] Medidas aditivas; ratios recalculados, no sumados.
- [ ] Dimensión de fecha conformada; moneda/unidad explícita.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Tests dbt de PK única y relaciones hecho-dimensión | 1 | pendiente (ver `etl-vs-elt-and-dbt`; proyecto generado) |
| Revisión del modelo por el agente revisor | 3 | agente `code-reviewer` + data owner |

Local: PostgreSQL/DuckDB. No hay diferencia de modelado en AWS; preparado para AWS, no verificado en real.

## Relacionados, fuentes y mantenimiento
- Relacionados: `etl-vs-elt-and-dbt`, `data-quality`, `warehouse-options`, `bi-and-reporting`.
- Fuentes: comprobar (bibliografía de modelado dimensional).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
