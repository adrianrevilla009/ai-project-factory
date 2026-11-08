---
name: tech-debt-management
description: "Usar al registrar, priorizar o pagar deuda técnica y al decidir si un atajo es aceptable; define registro, intereses y presupuesto."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "review"
---

# Gestión de deuda técnica

## Cuándo aplicar y cuándo no
- Aplica cuando se toma un atajo consciente, se detecta un diseño que frena el cambio o se planifica la capacidad de un sprint/fase.
- No aplica a defectos funcionales (son bugs) ni a preferencias de estilo; tampoco para justificar código descuidado como "deuda".

## Reglas
- **MUST** registrar cada deuda aceptada de forma explícita: qué es, por qué se acepta, impacto (interés), coste estimado de pago, dueño y fecha de revisión.
- **MUST** enlazar la deuda a código con un marcador rastreable (`TODO(DEBT-123)`), nunca un `TODO` anónimo.
- **MUST** distinguir deuda deliberada (decisión) de accidental (descubierta); la accidental se registra al detectarla.
- **MUST NOT** aceptar como deuda lo que compromete seguridad, integridad de datos o requisitos legales; eso se corrige antes de entregar.
- **MUST** priorizar por interés (frecuencia de cambio x fricción) y riesgo, no por antigüedad ni por molestia personal.
- **SHOULD** reservar capacidad fija recurrente al pago de deuda (ej. 10-20 % por iteración; valor de partida a calibrar por equipo).
- **SHOULD** pagar deuda junto a cambios funcionales en la misma zona (regla del boy scout) usando refactor seguro con tests (ver `code-smells-and-refactoring`).
- **SHOULD** revisar el registro en cada fase/gate y cerrar o reclasificar elementos caducados.
- **SHOULD** vigilar tendencias (tiempo de build, cobertura de módulos críticos, ciclos, dependencias obsoletas) como señales, no como objetivos en sí.

## Por qué
La deuda no registrada es invisible y se paga con intereses compuestos: cada cambio cuesta más. El registro hace explícito el trade-off y permite a negocio decidir con datos. Sin dueño ni fecha, el registro se convierte en un cementerio.

## Ejemplos
### Mal
```java
// TODO: arreglar esto luego
```
### Bien
```java
// TODO(DEBT-042): consulta sin paginar; aceptable hasta 5k pedidos/cliente. Revisar 2027-02-01.
```
```markdown
| ID       | Descripción                       | Tipo       | Interés                           | Coste pago | Dueño     | Revisión   |
|----------|-----------------------------------|------------|-----------------------------------|------------|-----------|------------|
| DEBT-042 | Listado de pedidos sin paginación | Deliberada | +1 s por cada 1k pedidos del cliente | 2 días     | team-orders | 2027-02-01 |
```
Criterio de decisión: interés alto + zona que cambia a menudo = pagar ya; interés bajo + código estable = tolerar y documentar.

## Checklist de revisión
- [ ] Toda deuda aceptada está en el registro con dueño y fecha.
- [ ] Los `TODO` en código llevan ID de deuda.
- [ ] Nada que afecte seguridad/datos/legal se acepta como deuda.
- [ ] Hay capacidad reservada y priorización por interés.
- [ ] El registro se revisó en el último gate.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `TODO` sin ID `DEBT-` | 1 | pendiente: `policies/semgrep/` |
| Revisión del registro en cada gate | 4 | `gates/` (humano) |
| Revisión de PR | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `code-smells-and-refactoring`, `evolutionary-architecture-fitness-functions`, `quality-attributes-atam`.
- Fuentes: Cunningham, "The WyCash Portfolio Management System" (1992); Fowler, "Technical Debt Quadrant" (martinfowler.com). (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
