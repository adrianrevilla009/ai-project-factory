---
name: failover-and-failback-runbooks
description: "Usar al escribir o revisar el runbook de failover/failback eu-west-1 a eu-central-1: orden de pasos, Aurora Global antes que Vault, decisión de conmutar y vuelta atrás."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Runbooks de failover y failback

## Cuándo aplicar y cuándo no
- Aplica a todo servicio de tier 0-2 y a cada ejercicio tabletop.
- No aplica a fallos de AZ (los absorbe Multi-AZ) ni a incidentes sin pérdida de región (ver `incident-management-and-postmortems`).
- Diseño: preparado para AWS, no verificado en real. Local: solo simulacro documental.

## Reglas
- **MUST** que el runbook tenga criterios de decisión, responsable que autoriza, pasos numerados y verificación por paso.
- **MUST** usar solo acciones de plano de datos para conmutar (ARC routing controls, promoción de BD ya aprovisionada) y **MUST NOT** depender de crear recursos nuevos en la región caída.
- **MUST** respetar este orden:
  1. Declarar el desastre y congelar despliegues; frenar escrituras en la primaria si es alcanzable.
  2.
  3. **Promover Aurora Global (failover con pérdida de datos aceptada) y verificar que hay escritor.**
  4. **Solo después**, activar el motor de BD de Vault de la secundaria (rol dinámico) y rotar credenciales.
  5. Escalar EKS/Argo CD de la secundaria a capacidad plena.
  6. Conmutar tráfico (ARC), subiendo el TTL bajo del DNS si aplica.
  7. Verificar SLOs sintéticos y comunicar.
- **MUST** documentar por qué el orden 3 antes de 4: la secundaria Aurora es de solo lectura hasta promoverse y Vault no puede crear roles dinámicos en ella.
- **MUST** definir failback como operación planificada: restaurar topología, sincronizar y hacer *switchover* (RPO 0) en ventana de baja carga, no un segundo failover.
- **MUST** guardar el runbook fuera de la región afectada (repositorio y copia impresa/offline).
- **SHOULD** automatizar los pasos tras una aprobación manual ("botón"); la conmutación automática por alarma suele dar falsos positivos.
- **MUST NOT** declarar RTO hasta cronometrarlo en un ejercicio.

## Por qué
Un orden equivocado produce errores confusos en mitad del incidente (aplicaciones sin credenciales). La promoción de Aurora ante pérdida de región admite pérdida de datos no replicados y riesgo de split-brain; Aurora intenta una barrera de escritura y guarda una instantánea del volumen antiguo. El failback con switchover sincroniza antes de cambiar roles.

## Ejemplos
### Mal
```text
1. Activar motor de BD de Vault en eu-central-1
2. Promover Aurora
3. Cambiar DNS
```
### Bien
```text
# runbook-failover-tier1.md (extracto, no ejecutar desde la fábrica)
3. Promover Aurora (global cluster ya existente):
   aws rds failover-global-cluster --region eu-central-1 \
     --global-cluster-identifier example-global \
     --target-db-cluster-identifier <ARN secundaria> --allow-data-loss
   Verificar: cluster eu-central-1 con instancia escritora (available).
4. Solo si 3 verificado: vault write database/config/example-pg ... (Vault eu-central-1)
```

## Checklist de revisión
- [ ] Orden Aurora antes que Vault explícito y justificado.
- [ ] Solo plano de datos; sin dependencia de la región caída.
- [ ] Failback por switchover descrito.
- [ ] Cronometrado en un ejercicio; copia fuera de banda.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de runbooks y ejercicio tabletop | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `application-recovery-controller-and-health-checks`, `data-replication-matrix`, `fault-injection-and-game-days`, `multi-region-patterns`.
- Fuente: Aurora Global Database, switchover y failover, https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html (2026-11-07). Comando de Vault de BD.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
