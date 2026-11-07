---
name: test-data-management
description: "Usar al crear datos de prueba: builders, fixtures, datasets de integración, anonimización de datos reales y limpieza entre tests."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Gestión de datos de prueba

## Cuándo aplicar y cuándo no
- Aplica a tests unitarios, de integración, e2e y a entornos de pruebas de rendimiento.
- No aplica a datos semilla funcionales de producción (migraciones de referencia): ver `schema-migrations`.

## Reglas
- **MUST NOT** usar datos personales reales en tests ni en entornos no productivos; usar datos sintéticos o anonimizados (ver `pii-and-data-classification`).
- **MUST** crear los datos con builders / object mothers que expongan solo lo relevante para el test; el resto con valores por defecto válidos.
- **MUST** que cada test cree sus propios datos y no dependa de los de otro; aislamiento por transacción con rollback, truncado o contenedor nuevo.
- **MUST** que los identificadores sean únicos por ejecución (UUID o secuencia) para permitir ejecución en paralelo.
- **MUST NOT** compartir un dataset mutable global ("el cliente 1 de data.sql").
- **SHOULD** versionar fixtures grandes junto al test y mantenerlos mínimos.
- **SHOULD** generar volumen para rendimiento con scripts reproducibles (semilla fija), nunca copiando producción.
- **SHOULD** usar el esquema real (migraciones Flyway/Liquibase) para preparar la BD de test, no un DDL paralelo.

## Por qué
Los datos reales filtran privacidad y hacen los tests no reproducibles; los datasets compartidos acoplan tests y provocan flakiness. Un builder con defaults hace explícito qué importa en cada caso.

## Ejemplos
### Mal
```java
// data.sql compartido por toda la suite
// INSERT INTO customer VALUES (1, 'Juan Pérez', 'juan.perez@gmail.com', '12345678Z');
Customer c = customerRepository.findById(1L).orElseThrow();
```
### Bien
```java
public final class CustomerMother {
    public static CustomerBuilder aCustomer() {
        return new CustomerBuilder()
                .id(UUID.randomUUID())
                .name("Test Customer")
                .email("customer-" + UUID.randomUUID() + "@example.test")
                .status(CustomerStatus.ACTIVE);
    }
}

@Test
void blockedCustomerCannotOrder() {
    var customer = aCustomer().status(CustomerStatus.BLOCKED).build();
    assertThatThrownBy(() -> service.placeOrder(customer, order()))
            .isInstanceOf(CustomerBlockedException.class);
}
```
Dominios `example.test` / `example.com` para correos falsos.

## Checklist de revisión
- [ ] Ningún dato personal real en el repositorio ni en fixtures.
- [ ] Builders con defaults válidos; el test solo fija lo relevante.
- [ ] Datos únicos por test y limpieza garantizada.
- [ ] Esquema de test creado con las migraciones reales.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Hook de bloqueo de secretos al escribir ficheros | 2 | `.claude/hooks/pre-tool-use/block_secrets.py` |
| Detección de PII en fixtures (patrones DNI/IBAN/email real) | 1 | pendiente (regla Semgrep o gitleaks custom) |
| Revisión de fixtures | 3 | agente `test-automation` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `db-testing`, `pii-and-data-classification`, `data-privacy-in-db`, `flaky-test-management`, `integration-testing-testcontainers`.
- Fuentes: patrón Object Mother / Test Data Builder (Fowler, https://martinfowler.com/bliki/ObjectMother.html, consultada 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
