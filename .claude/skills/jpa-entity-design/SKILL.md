---
name: jpa-entity-design
description: Usar al crear o modificar entidades JPA (mapeo, equals/hashCode, enums, relaciones, constructores).
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Diseño de entidades JPA

## Cuándo aplicar y cuándo no
- Aplica a cualquier clase con `@Entity`, `@Embeddable` o `@MappedSuperclass`.
- No aplica a DTOs, records de API ni a acceso JDBC/jOOQ sin mapeo ORM (ver `jdbc-and-jooq`).

## Reglas
- **MUST NOT** usar Lombok (`@Data`, `@Getter`, etc.; D27): escribir getters y constructores a mano.
- **MUST** tener un constructor sin argumentos `protected` (exigido por JPA) y un constructor público o factoría que deje la entidad en estado válido.
- **MUST** mapear enums con `@Enumerated(EnumType.STRING)`; nunca `ORDINAL`.
- **MUST** basar `equals`/`hashCode` en el id o en una clave de negocio inmutable; nunca en todos los campos ni en colecciones perezosas.
- **MUST NOT** usar entidades como DTO de API: el contrato HTTP no debe acoplarse al esquema.
- **MUST** mantener coherentes los dos lados de una relación bidireccional con métodos de ayuda (`addLine`) y `mappedBy` en el lado inverso.
- **SHOULD** usar tipos de valor (`@Embeddable`) para conceptos como `Money` o `Address`.
- **SHOULD** declarar `@Column(nullable = false, length = ...)` coherente con el DDL de la migración.
- **MUST NOT** usar `CascadeType.REMOVE`/`ALL` sobre asociaciones hacia otros agregados.

## Por qué
La entidad es el modelo del agregado, no una bolsa de campos. Un enum ordinal se corrompe al insertar un valor en medio; un `equals` sobre todos los campos dispara cargas perezosas y rompe los `Set` tras persistir. Lombok queda fuera por decisión cerrada D27.

## Ejemplos
### Mal
```java
@Entity
@Data                                   // Lombok prohibido; equals/hashCode con todo
class Invoice {
    @Id @GeneratedValue Long id;
    @Enumerated(EnumType.ORDINAL) Status status;
    @OneToMany(cascade = CascadeType.ALL) List<Line> lines;
}
```
### Bien
```java
@Entity
class Invoice {
    @Id @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private Status status = Status.DRAFT;

    @OneToMany(mappedBy = "invoice", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Line> lines = new ArrayList<>();

    protected Invoice() { }             // JPA

    public void addLine(Line line) {
        lines.add(line);
        line.setInvoice(this);
    }

    @Override public boolean equals(Object o) {
        return o instanceof Invoice other && id != null && id.equals(other.id);
    }
    @Override public int hashCode() { return Invoice.class.hashCode(); }
}
```

## Checklist de revisión
- [ ] Sin Lombok; constructor protegido sin argumentos.
- [ ] Enums en `STRING`.
- [ ] `equals`/`hashCode` no tocan asociaciones perezosas.
- [ ] Relaciones bidireccionales con `mappedBy` y métodos de ayuda.
- [ ] Cascades solo dentro del mismo agregado.
- [ ] La entidad no sale por la API.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: enum sin `EnumType.STRING` | 1 | `policies/semgrep/jpa-enumerated-ordinal.yaml` |
| Regla Semgrep: sin Lombok (D27) | 1 | `policies/semgrep/java-no-lombok.yaml` |
| Regla ArchUnit: entidades no usadas en controllers | 1 | pendiente (`policies/archunit/`) |
| Revisión de modelo de dominio | 3 | agente `code-reviewer` |

> Estado: reglas probadas con `semgrep --test` (casos en `tests/semgrep/`); detectan patrones sintácticos, no flujos de datos.

## Relacionados, fuentes y mantenimiento
- Relacionados: `id-generation`, `lazy-vs-eager`, `optimistic-locking`, `equals-hashcode-tostring`, `ddd-tactical`.
- Fuentes: Jakarta Persistence y guía de usuario de Hibernate ORM — TODO-VERIFY versión y URL; no consultadas en vivo el 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
