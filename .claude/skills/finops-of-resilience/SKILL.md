---
name: finops-of-resilience
description: "Usar al presupuestar o comparar estrategias de resiliencia/DR (multi-AZ, warm standby, activo-activo): coste por tier, transferencia entre regiones y coste de la indisponibilidad."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# FinOps de la resiliencia

## Cuándo aplicar y cuándo no
- Aplica al elegir patrón de DR por tier, justificar un presupuesto de resiliencia o revisar un ADR multi-región.
- No aplica al control general de gasto cloud (ver `finops`).
- Las cifras son estimaciones de diseño; ningún precio se ha verificado en una cuenta real. Precios: consultar la calculadora oficial (TODO-VERIFY).

## Reglas
- **MUST** calcular, para cada tier, el coste de la estrategia (cómputo en espera, réplicas de datos, transferencia entre regiones, backups, herramientas) frente al coste de indisponibilidad (ingresos perdidos por hora x RTO esperado + penalizaciones).
- **MUST** elegir la estrategia más barata que cumpla el RPO/RTO del tier, no la más robusta disponible (`tier-model-and-rpo-rto`).
- **MUST** separar en el modelo costes fijos (infra en espera) de variables (replicación proporcional al tráfico).
- **MUST** etiquetar con `tier`, `service` y `dr-role` todos los recursos de resiliencia para atribuir su coste (`finops`).
- **MUST NOT** aplicar activo-activo a tiers 3-4 sin un ADR que lo justifique.
- **SHOULD** apagar o reducir el entorno de warm standby de menor tier fuera de ventana si el RTO lo permite.
- **SHOULD** incluir en el presupuesto el coste de ensayar: game days, restore tests y entornos temporales.
- **SHOULD** revisar el modelo cada trimestre y tras cada cambio de tier.

## Por qué
La resiliencia es un seguro: cada nueve adicional encarece de forma no lineal. Sin comparar contra el coste de la caída, los equipos sobre-protegen servicios tolerantes o dejan sin protección los críticos. El coste de datos entre regiones suele sorprender; se modela explícitamente.

## Ejemplos
### Mal
```text
"Todo en activo-activo en dos regiones por si acaso"  -> duplica el coste sin RTO objetivo.
```
### Bien
```yaml
# resilience-cost.yaml (estimación de diseño, precios por confirmar)
service: orders
tier: 1
downtime_cost_per_hour_eur: 12000      # supuesto del negocio
candidates:
  - strategy: multi-az
    rto_min: 60
    monthly_cost_eur: 3000
  - strategy: warm-standby
    rto_min: 15
    monthly_cost_eur: 5200
    cross_region_transfer_gb_month: 800
decision: warm-standby
rationale: "RTO 15 min cumple tier 1; activo-activo +90% de coste sin ganancia exigida"
review: "2027-02-07"
```

## Checklist de revisión
- [ ] Coste de estrategia y de indisponibilidad por tier.
- [ ] Transferencia entre regiones y backups incluidos.
- [ ] Recursos de resiliencia etiquetados.
- [ ] Ensayos presupuestados.
- [ ] Supuestos y precios marcados como por confirmar.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Checkov custom: exigir tags `tier` y `dr-role` | 1 | pendiente: `policies/iac-checks/` |
| Revisión humana del modelo de coste en el gate | 4 | PR / gate |

## Relacionados, fuentes y mantenimiento
- Relacionados: `tier-model-and-rpo-rto`, `multi-region-patterns`, `data-replication-matrix`, `finops`, `capacity-and-load-modeling`.
- Fuentes: AWS Well-Architected Reliability Pillar y calculadora de precios de AWS — TODO-VERIFY URL y precios (no consultados 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
