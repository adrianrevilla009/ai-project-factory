---
name: tier-model-and-rpo-rto
description: "Usar al declarar o revisar el tier de resiliencia (0-3) y los objetivos RPO/RTO de un proyecto, antes de diseñar multi-AZ, multi-región o backups."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Modelo de tiers y objetivos RPO/RTO

## Cuándo aplicar y cuándo no
- Aplica al inicio de un proyecto (fase de arquitectura), al cambiar la criticidad de un servicio y al revisar costes de DR.
- No aplica a decisiones de rendimiento no relacionadas con desastres (ver `capacity-and-load-modeling`).
- Diseño solamente (D4): la fábrica no despliega; la infraestructura queda "preparada para AWS, no verificado en real". Regiones: eu-west-1 primaria, eu-central-1 secundaria (D6).

## Reglas
- **MUST** declarar un tier por servicio en un fichero `resilience.yaml` del proyecto (tier, RPO, RTO, aprobador de negocio).
- **MUST** usar **Tier 1 (warm standby)** como defecto para servicios de cara a cliente salvo decisión documentada.
- **MUST** tratar los valores de la tabla como "valores de partida, a validar con negocio", no como compromisos.
- **MUST** derivar la infraestructura del tier: el tier activa módulos Terraform concretos, no al revés.
- **MUST NOT** declarar Tier 0 sin haber resuelto la región de escritura por agregado y la ruta de datos multi-región (ver `data-replication-matrix`).
- **SHOULD** distinguir RPO/RTO de fallo de AZ (casi cero) del de región (el tier).
- **SHOULD** revisar el tier cada año o tras un incidente mayor.
- **MUST NOT** prometer RTO/RPO sin un ejercicio que lo respalde (`fault-injection-and-game-days`).

## Por qué
El coste crece de forma no lineal con el tier; sin un tier explícito cada equipo improvisa. Un RPO de "cero" con replicación asíncrona es una promesa falsa. La estrategia (backup, pilot light, warm standby, active/active) la define la documentación oficial de AWS sobre DR; los números de la fábrica son punto de partida.

| Tier | Estrategia | RPO | RTO | Uso |
|---|---|---|---|---|
| 0 | Activo-activo / warm standby con replicación continua | segundos | minutos | Núcleo transaccional crítico |
| 1 (defecto) | Warm standby | ~minutos | < 1 h | Cara a cliente |
| 2 | Pilot light | < 1 h | horas | Back-office |
| 3 | Backup y restauración | 24 h | 24 h+ | No críticos |

Principio: **estabilidad estática**; la capacidad secundaria ya existe y el failover solo usa acciones de plano de datos.

## Ejemplos
### Mal
```yaml
# resilience.yaml
service: payments-api
rpo: 0
rto: 5m        # sin tier, sin aprobador, sin ejercicio
```
### Bien
```yaml
# resilience.yaml
service: payments-api
tier: 1                      # warm standby (defecto)
regions: { primary: eu-west-1, secondary: eu-central-1 }
rpo: 5m
rto: 45m
approved_by: example-business-owner
last_exercise: 2026-10-20    # tabletop, ver game days
data_write_region: per-aggregate   # ver data-replication-matrix
```

## Criterios de decisión y trampas
### Cómo decidir
- Asigna un nivel de resiliencia por servicio según el impacto de negocio y sus objetivos de punto y tiempo de recuperación; cada nivel tiene un coste asociado y acordado.
- Revisa los niveles con el negocio, no solo con técnicos.
### Trampas frecuentes
- Todo en el nivel más alto «por seguridad».
- Objetivos que nadie ha probado.
- Dependencias de un nivel inferior para un servicio crítico.
- Tiempos medidos en teoría.
- Sin revisión cuando cambia el negocio.
### Evidencia
- Cada servicio tiene su nivel, sus objetivos y la fecha de su último ensayo.

## Checklist de revisión
- [ ] Existe `resilience.yaml` con tier, RPO, RTO y aprobador.
- [ ] El tier coincide con los módulos de infraestructura activados.
- [ ] RPO/RTO realistas frente a la replicación elegida (asíncrona implica RPO > 0).
- [ ] Hay fecha del último ejercicio.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de arquitectura y aprobación de negocio | 4 | revisión humana (gate de arquitectura) |
| Conftest: exigir `tier` en `resilience.yaml` | 1 | pendiente (`policies/opa-conftest/`) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `multi-az-patterns`, `multi-region-patterns`, `finops-of-resilience`, `fault-injection-and-game-days`.
- Fuente: AWS Whitepaper "Disaster Recovery of Workloads on AWS", https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html (verificado 2026-11-07). Los RPO/RTO numéricos son de la fábrica, por confirmar con negocio.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
