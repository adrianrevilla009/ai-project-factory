---
name: id-generation
description: Usar al elegir estrategia de clave primaria (secuencia, identity, UUID) o al exponer ids en APIs.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Generación de identificadores

## Cuándo aplicar y cuándo no
- Aplica al definir `@Id`, tablas nuevas y ids visibles en URLs o eventos.
- No aplica a claves naturales impuestas por un sistema externo (se mapean como clave de negocio única).

## Reglas
- **MUST** decidir la estrategia por entidad y documentarla si se desvía del defecto del proyecto.
- **SHOULD** usar `SEQUENCE` con `allocationSize` igual al `INCREMENT BY` de la secuencia en BD, para permitir batching de inserts (ver `batching-and-bulk-ops`).
- **MUST NOT** usar `GenerationType.AUTO` sin saber qué estrategia resuelve el dialecto.
- **MUST NOT** asumir que `IDENTITY` permite batch de inserts: Hibernate debe insertar para conocer el id.
- **SHOULD** usar UUID (preferible v7, ordenable por tiempo) cuando el id se genera fuera de la BD o en sistemas distribuidos; guardarlo con tipo `uuid` nativo, no `varchar(36)`.
- **MUST NOT** usar UUID v4 aleatorio como PK en motores que ordenan físicamente por PK sin medir el impacto en índices.
- **MUST NOT** exponer ids secuenciales enumerables en APIs públicas cuando la enumeración sea un riesgo; usar un id público separado.
- **MUST NOT** generar ids con `max(id)+1`.

## Por qué
Cada estrategia cambia el comportamiento de escritura: IDENTITY desactiva el batching, las secuencias necesitan ir a BD cada `allocationSize` valores, los UUID aleatorios fragmentan índices B-tree. Elegir tarde obliga a migrar claves foráneas.

## Ejemplos
### Mal
```java
@Id
@GeneratedValue                    // AUTO: el dialecto decide
private Long id;
// y en el servicio: new Order(repo.findMaxId() + 1)
```
### Bien
```java
@Id
@GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "order_seq")
@SequenceGenerator(name = "order_seq", sequenceName = "order_seq", allocationSize = 50)
private Long id;

@Column(nullable = false, unique = true, updatable = false)
private UUID publicId = UUID.randomUUID(); // id expuesto en la API
```
```sql
CREATE SEQUENCE order_seq START WITH 1 INCREMENT BY 50;
```
`UUID.randomUUID` genera v4; para v7 hace falta librería o generador propio.

## Checklist de revisión
- [ ] Estrategia explícita (no `AUTO`).
- [ ] `allocationSize` = `INCREMENT BY` de la secuencia.
- [ ] Ids públicos no enumerables si procede.
- [ ] UUID guardado como tipo nativo.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep para `@GeneratedValue` sin estrategia | 1 | pendiente (`policies/semgrep/`) |
| Revisión de modelo de datos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `jpa-entity-design`, `batching-and-bulk-ops`, `db-design-conventions`.
- Fuentes: guía de usuario de Hibernate ORM (identifier generators).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
