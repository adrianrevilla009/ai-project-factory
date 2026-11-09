---
name: tech-debt-register
description: "Usar al registrar, priorizar y pagar deuda técnica: entradas con coste, interés, dueño y fecha, enlazadas a TODOs del código."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Registro de deuda técnica

## Cuándo aplicar y cuándo no
- Aplica cuando se toma un atajo consciente, se detecta deuda en revisión o se pospone una mejora necesaria.
- No aplica a incertidumbres futuras (ver `risk-register`) ni a bugs (van al backlog como defectos).

## Reglas
- **MUST** registrar cada atajo consciente en `docs/tech-debt/register.md` (o issues con etiqueta `tech-debt`) en el mismo PR que lo introduce.
- **MUST** que cada entrada incluya: id, descripción, motivo del atajo, coste de pagarla, "interés" (qué duele mientras exista), dueño y fecha de revisión.
- **MUST** que los `TODO`/`FIXME` del código referencien un id del registro (`TODO(TD-012)`).
- **SHOULD** reservar capacidad fija por iteración para pagar deuda (p. ej. 10-20 %, acordado con producto).
- **SHOULD** priorizar por interés y riesgo, no por antigüedad.
- **MUST NOT** usar "deuda técnica" para ocultar trabajo incompleto que incumple la `definition-of-ready-and-done`.
- **MUST NOT** desactivar reglas de calidad (Semgrep, ArchUnit) sin entrada de deuda con caducidad.
- **MUST NOT** dejar entradas sin dueño.

## Por qué
La deuda invisible se acumula hasta frenar la entrega. Medir coste e interés permite negociar su pago con evidencia. Vincular los `TODO` evita comentarios huérfanos.

## Ejemplos
### Mal
```java
// TODO arreglar esto luego
@SuppressWarnings("all")
public Order load(String id) { /* ... */ }
```
### Bien
```java
// TODO(TD-012): consulta sin paginar; migrar a keyset pagination antes de 2027-02-01
public List<Order> listOpenOrders() { /* ... */ }
```
```yaml
- id: TD-012
  title: Listado de pedidos sin paginar
  reason: "Entrega del hito 1; volumen actual < 1000 filas"
  payoff_cost: "2 días"
  interest: "Latencia crece linealmente; riesgo de timeouts"
  owner: "dev-orders"
  review_date: "2026-12-01"
  status: open
```

## Checklist de revisión
- [ ] Todo atajo del PR tiene entrada en el registro.
- [ ] Los `TODO` apuntan a un id válido.
- [ ] Hay dueño, coste e interés por entrada.
- [ ] Las supresiones de reglas tienen caducidad.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `TODO`/`FIXME` sin patrón `TD-\d+` | 1 | pendiente: `policies/semgrep/todo-without-debt-id.yaml` |
| Revisión de supresiones y atajos en el PR | 3 | agente `code-reviewer` |
| Revisión de prioridades con producto | 4 | revisión humana |

> Estado: la regla Semgrep está pendiente.

## Relacionados, fuentes y mantenimiento
- Relacionados: `code-smells-and-refactoring`, `risk-register`, `definition-of-ready-and-done`, `pr-rules`.
- Fuentes: concepto de "technical debt" de Ward Cunningham.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
