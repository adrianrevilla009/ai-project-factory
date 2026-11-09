---
name: requirements-engineering
description: "Usar al redactar o refinar historias, criterios de aceptación y requisitos no funcionales: INVEST, Gherkin y NFR medibles antes de implementar."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Ingeniería de requisitos

## Cuándo aplicar y cuándo no
- Aplica en la fase de intake/plan, al refinar el backlog y cuando un requisito es ambiguo.
- No aplica a correcciones triviales con comportamiento esperado obvio y ya cubierto por tests.

## Reglas
- **MUST** redactar historias como `Como <rol> quiero <capacidad> para <beneficio>`; el beneficio no puede omitirse.
- **MUST** que cada historia cumpla INVEST: Independiente, Negociable, Valiosa, Estimable, Pequeña (Small), Testeable.
- **MUST** expresar criterios de aceptación como escenarios Gherkin (`Given/When/Then`) en lenguaje de dominio, sin UI ni SQL.
- **MUST** incluir al menos un escenario de error o borde por historia, no solo el camino feliz.
- **MUST** definir los NFR con número y método de medida: "p95 < 300 ms bajo 200 rps", no "rápido".
- **MUST** trazar cada requisito a un identificador (`REQ-PAY-012`) enlazado a historia, test y, si aplica, ADR.
- **SHOULD** listar supuestos y preguntas abiertas con responsable y fecha; las respuestas pendientes bloquean el DoR.
- **SHOULD** cubrir categorías de NFR: rendimiento, disponibilidad, seguridad, privacidad, auditoría, accesibilidad, operabilidad.
- **MUST NOT** inventar requisitos legales o normativos: marcarlos "borrador por confirmar" con fuente oficial y fecha.
- **MUST NOT** mezclar solución técnica en el requisito ("usar Redis") salvo restricción real, documentada como tal.

## Por qué
Un requisito ambiguo se paga tres veces: al implementar lo equivocado, al probarlo y al corregirlo. Gherkin convierte la aceptación en ejemplos ejecutables que negocio puede leer; los NFR medibles permiten decidir arquitectura y pruebas de carga con criterio. INVEST mantiene las historias entregables en incrementos pequeños.

## Ejemplos
### Mal
```text
El sistema debe ser rápido y seguro y permitir reembolsos.
```
### Bien
```gherkin
# REQ-PAY-012  (historia PAY-123)
Feature: Reembolso parcial
  Scenario: Reembolso dentro del importe pagado
    Given un pedido pagado de 100.00 EUR
    When el agente reembolsa 40.00 EUR
    Then el pedido muestra 60.00 EUR pendientes de reembolso
    And se registra un evento de auditoría con el agente y el importe

  Scenario: Reembolso superior al importe pagado
    Given un pedido pagado de 100.00 EUR
    When el agente reembolsa 150.00 EUR
    Then se rechaza con el error REFUND_EXCEEDS_PAID
```
```yaml
nfr:
  - id: NFR-PAY-001
    statement: "POST /refunds p95 < 300 ms a 200 rps"
    measured_by: "prueba de carga JMeter en CI"
```

## Checklist de revisión
- [ ] Historia con rol, capacidad y beneficio; cumple INVEST.
- [ ] Escenarios Gherkin con camino feliz y error/borde.
- [ ] NFR medibles con método de medida.
- [ ] IDs de requisito trazados a tests.
- [ ] Preguntas abiertas con dueño; sin requisitos legales inventados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de historias contra el DoR | 3 | agentes `business-analyst` y `product-owner` |
| Escenarios ejecutables (Cucumber u homólogo) en el proyecto generado | 1 | ver skill `bdd`; tests del proyecto generado |
| Validador de trazabilidad requisito-test | - | pendiente |

## Relacionados, fuentes y mantenimiento
- Relacionados: `definition-of-ready-and-done`, `bdd`, `domain-discovery`, `capacity-and-load-modeling`.
- Fuentes: INVEST (Bill Wake, 2003) y sintaxis Gherkin: https://cucumber.io/docs/gherkin/reference/.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
