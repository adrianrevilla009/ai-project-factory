---
name: anti-corruption-layer
description: Usar al integrar con un sistema legado o externo cuyo modelo no debe contaminar el dominio propio.
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Anti-Corruption Layer (ACL)

## Cuándo aplicar y cuándo no
- Aplica al consumir sistemas legados, SOAP, proveedores externos o contextos con lenguaje distinto al propio.
- No aplica a contextos con modelo compartido deliberado (shared kernel) ni a integraciones triviales de un solo campo.

## Reglas
- **MUST** aislar el modelo ajeno en un paquete `adapter.out.<system>`; nada fuera de él importa sus tipos.
- **MUST** traducir en la ACL (traductor/mapper) a tipos del dominio propio; los DTO externos no cruzan la frontera.
- **MUST** exponer el sistema externo mediante un puerto del dominio con lenguaje propio (`CustomerDirectory`, no `LegacyCrmClient`).
- **MUST** gestionar en la ACL errores, timeouts y formatos raros del externo, devolviendo errores de dominio.
- **SHOULD** testear el traductor con casos reales anonimizados del sistema externo.
- **SHOULD** que la ACL sea la única parte que cambia cuando el externo cambia.
- **MUST NOT** reutilizar clases generadas (WSDL/OpenAPI del tercero) en el dominio o la aplicación.

## Por qué
Sin ACL, el modelo del legado se filtra: nombres, estados y quirks acaban en tu dominio y lo vuelven imposible de cambiar. La traducción es un coste pequeño y localizado frente a una dependencia conceptual permanente.

## Ejemplos
### Mal
```java
class InvoiceService {
    LegacyCustomerDto c = legacyClient.getCust(id);   // tipos del legado en la aplicación
    if ("A".equals(c.getStatCd())) { ... }
}
```
### Bien
```java
// puerto del dominio
public interface CustomerDirectory { Optional<Customer> find(CustomerId id); }

// adapter.out.legacycrm
class LegacyCrmCustomerDirectory implements CustomerDirectory {
    private final LegacyCrmClient client;
    LegacyCrmCustomerDirectory(LegacyCrmClient client) { this.client = client; }
    public Optional<Customer> find(CustomerId id) {
        return client.getCust(id.value()).map(LegacyCrmTranslator::toDomain);
    }
}
final class LegacyCrmTranslator {
    static Customer toDomain(LegacyCustomerDto d) {
        return new Customer(new CustomerId(d.getCustId()),
            "A".equals(d.getStatCd()) ? CustomerStatus.ACTIVE : CustomerStatus.INACTIVE);
    }
}
```

## Checklist de revisión
- [ ] Los tipos externos solo existen en el paquete del adaptador.
- [ ] El puerto usa lenguaje del dominio.
- [ ] Errores y timeouts del externo se traducen.
- [ ] El traductor tiene tests.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| ArchUnit: `domain`/`application` no dependen de `..adapter..` (cubre los tipos externos aislados ahí) | 1 | `policies/archunit/HexagonalArchitectureRules.java` |
| Revisión de la traducción | 3 | revisión de PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `hexagonal`, `ddd-strategic`, `strangler-fig-migration`, `soap-legacy-integration`.
- Fuentes: Eric Evans, "Domain-Driven Design" (2003), patrón Anticorruption Layer; Microsoft Azure Architecture Center, "Anti-corruption layer pattern" — TODO-VERIFY URL.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
