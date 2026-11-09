---
name: db-design-conventions
description: "Usar al diseñar tablas, columnas, tipos y constraints en PostgreSQL: nombres, tipos de dinero/fecha, NOT NULL, claves y checks."
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Convenciones de diseño de base de datos

## Cuándo aplicar y cuándo no
- Aplica a cada migración que cree o altere tablas, columnas, constraints y tipos.
- No aplica a esquemas de terceros que no controlamos ni a NoSQL (ver bloque de NoSQL).

## Reglas
- **MUST** nombres en inglés, `snake_case`, tablas en singular o plural según una única convención del proyecto, sin palabras reservadas ni comillas obligatorias.
- **MUST** clave primaria en toda tabla; estrategia de ids según `id-generation`.
- **MUST** declarar `NOT NULL` por defecto; `NULL` solo si "desconocido" es un estado de negocio real.
- **MUST** integridad en la BD, no solo en la aplicación: `FOREIGN KEY`, `UNIQUE`, `CHECK` (estados válidos, importes >= 0).
- **MUST** dinero como `numeric(p,s)` (o enteros en la unidad menor) más moneda (código ISO 4217); nunca `float`/`double`.
- **MUST** instantes como `timestamptz` en UTC; fechas de calendario como `date`; nunca guardar fechas como texto.
- **MUST** nombrar explícitamente constraints e índices (`pk_`, `fk_`, `uq_`, `chk_`, `idx_`) para que las migraciones sean predecibles.
- **MUST NOT** usar `text` libre para valores de dominio cerrado sin `CHECK` o tabla de referencia; evitar enums nativos de BD si cambian a menudo (añadir valores es migración).
- **MUST NOT** guardar listas separadas por comas ni JSON para datos que se consultan o relacionan; `jsonb` solo para atributos realmente flexibles, indexado si se filtra.
- **SHOULD** columnas de auditoría coherentes (ver `auditing-soft-delete-history`) y tamaños acotados (`varchar(n)` o `CHECK (length(...))`) donde el dominio los tenga.
- **SHOULD** desnormalizar solo con medición que lo justifique y documentándolo.

## Por qué
El esquema vive más que cualquier versión del código y lo usan varios servicios, informes y herramientas. Las restricciones en BD son la última defensa frente a bugs y escrituras fuera de la aplicación. Los errores de tipo (float para dinero, fechas sin zona) son baratos de evitar y carísimos de migrar después.

## Ejemplos
### Mal
```sql
CREATE TABLE Orders (
  id serial,
  total float,
  status varchar(255),
  created varchar(30),
  tags text            -- 'a,b,c'
);
```
### Bien
```sql
CREATE TABLE customer_order (
  id          uuid        NOT NULL,
  customer_id uuid        NOT NULL,
  total       numeric(12,2) NOT NULL,
  currency    char(3)     NOT NULL,
  status      text        NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT pk_customer_order PRIMARY KEY (id),
  CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES customer (id),
  CONSTRAINT chk_order_total CHECK (total >= 0),
  CONSTRAINT chk_order_status CHECK (status IN ('NEW','PAID','CANCELLED'))
);
CREATE INDEX idx_order_customer ON customer_order (customer_id);
```

## Criterios de decisión y trampas
### Cómo decidir
- Convenciones de nombres, tipos y restricciones escritas y comprobadas: el esquema es un contrato.
- Restricciones en la base de datos (claves, unicidad, no nulo) además de en el código.
### Trampas frecuentes
- Tipos genéricos (todo texto) que impiden validar.
- Sin claves foráneas «por rendimiento» y con datos huérfanos.
- Marcas de tiempo sin zona o en zonas distintas.
- Nombres inconsistentes entre tablas.
- Columnas reutilizadas para varios significados.
### Evidencia
- Una revisión del esquema contra las convenciones y migraciones que las respetan.

## Checklist de revisión
- [ ] Nombres `snake_case` y constraints nombrados.
- [ ] PK, FKs, UNIQUE y CHECK definidos en la BD.
- [ ] Dinero en `numeric`, instantes en `timestamptz`.
- [ ] `NOT NULL` por defecto; los `NULL` están justificados.
- [ ] Sin listas en texto ni JSON para datos relacionales.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep (SQL): `float`/`double` o `serial` sin PK en migraciones | 1 | pendiente (`policies/semgrep/`) |
| Revisión de migraciones | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `schema-migrations`, `id-generation`, `indexing-and-query-plans`, `jpa-entity-design`.
- Fuentes: documentación de PostgreSQL (Data Types, Constraints).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
