---
name: equals-hashcode-tostring
description: Usar al implementar o revisar equals, hashCode, toString y compareTo en clases Java, incluidas entidades JPA y records con datos sensibles.
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# equals, hashCode y toString

## Cuándo aplicar y cuándo no
- Aplica a clases usadas como clave de mapa, elemento de `Set`, comparadas en tests o registradas en logs.
- No aplica a records sin datos sensibles, que ya generan los tres métodos correctamente.

## Reglas
- **MUST** sobrescribir `equals` y `hashCode` juntos, con los mismos campos.
- **MUST** respetar el contrato: reflexivo, simétrico, transitivo, consistente, `equals(null) == false`.
- **MUST NOT** incluir campos mutables en `hashCode` de objetos que se guardan en `HashSet`/claves de `HashMap`.
- **MUST** para entidades JPA: igualdad basada en identificador de negocio o en el id con manejo de `null` antes de persistir, y `hashCode` constante (p. ej. `getClass().hashCode()`); **MUST NOT** incluir asociaciones perezosas.
- **MUST NOT** incluir en `toString` secretos, contraseñas, tokens, datos personales ni asociaciones perezosas (provoca `LazyInitializationException` o N+1).
- **MUST** sobrescribir `toString` de un record que contenga datos sensibles para enmascararlos.
- **SHOULD** usar `Objects.equals`/`Objects.hash`; **MUST** comparar `double` con `Double.compare`.
- **SHOULD** que `compareTo` sea consistente con `equals`; si no, documentarlo.
- **MUST NOT** usar `==` para comparar `String` ni wrappers.

## Por qué
Un `hashCode` que cambia con el estado hace que un objeto "desaparezca" de un `HashSet`. Un `toString` con asociaciones o datos sensibles filtra información a los logs y dispara consultas ocultas. Los records ya generan implementaciones coherentes, por eso se prefieren.

## Ejemplos
### Mal
```java
public class Account {
    private String id; private String password; private List<Tx> transactions;
    @Override public boolean equals(Object o) { return ((Account) o).id.equals(id); } // ClassCastException, NPE
    @Override public String toString() {
        return "Account{id=" + id + ", password=" + password + ", tx=" + transactions + "}";
    }
    // hashCode no sobrescrito
}
```
### Bien
```java
public record Credentials(String username, char[] secret) {
    @Override public String toString() { return "Credentials[username=" + username + ", secret=***]"; }
}

@Entity
public class Account {
    @Id private Long id;
    @Override public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Account other)) return false;
        return id != null && id.equals(other.id);
    }
    @Override public int hashCode() { return getClass().hashCode(); }
    @Override public String toString() { return "Account[id=" + id + "]"; }
}
```
Nota: `char[]` en record usa igualdad por referencia; preferir un tipo con `equals` propio.

## Checklist de revisión
- [ ] `equals` y `hashCode` usan los mismos campos.
- [ ] Las entidades JPA no incluyen asociaciones ni mutables en `hashCode`.
- [ ] `toString` sin secretos, datos personales ni colecciones perezosas.
- [ ] No hay `==` sobre objetos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión de entidades y logs | 3 | agente `code-reviewer` (pendiente de definir) |
| Regla `-Xlint`/Error Prone `EqualsHashCode` en el proyecto generado | 1 | pendiente (comprobar herramienta) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `immutability-and-value-objects`, `jpa-entity-design`, `logging-rules`, `data-privacy-in-db`.
- Fuentes: Javadoc de `java.lang.Object#equals` y `#hashCode`; Effective Java (Bloch) — no verificado en línea.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
