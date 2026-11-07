---
name: status-page-and-comms
description: "Usar al definir la página de estado y la comunicación de incidentes a usuarios y stakeholders durante degradaciones o caídas."
metadata:
  block: "18-observability-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Página de estado y comunicación de incidentes

## Cuándo aplicar y cuándo no
- Aplica a la definición de qué se publica, quién lo publica y con qué plantillas cuando un servicio se degrada.
- No aplica a la gestión técnica del incidente ni al postmortem (ver `incident-management-and-postmortems`, bloque 19).

## Reglas
- **MUST** alojar la página de estado fuera de la infraestructura que monitoriza (otro clúster/cuenta/proveedor), para que siga disponible en un fallo de la plataforma.
- **MUST** definir componentes visibles al usuario (no microservicios internos) y estados: operativo, degradado, interrupción parcial, interrupción mayor, mantenimiento.
- **MUST** asignar un rol de comunicaciones por incidente, distinto del comandante técnico.
- **MUST** publicar una primera actualización en un plazo acordado por tier (p. ej. 15 min para tier 1; el plazo lo fija `tier-model-and-rpo-rto`) y actualizaciones periódicas aunque sean "sin novedades".
- **MUST** usar lenguaje de impacto al usuario, sin jerga interna, sin culpar a terceros y sin prometer hora de resolución no confirmada.
- **SHOULD** usar una herramienta de código abierto autoalojable (p. ej. Cachet, Uptime Kuma o una página estática; elegir por ADR, TODO-VERIFY estado de mantenimiento) en lugar de SaaS de pago por defecto (D16).
- **SHOULD** automatizar solo el borrador desde alertas `critical`; la publicación la aprueba una persona.
- **MUST NOT** publicar datos personales, nombres de clientes ni detalles de vulnerabilidades.
- **MUST NOT** reutilizar la misma plantilla para incidentes de seguridad: pasan por el proceso de seguridad y legal (normativa de notificación: borrador por confirmar con fuente oficial).

## Por qué
Durante un incidente la comunicación competente reduce tickets y escalados y preserva confianza. Una página alojada en el mismo clúster cae justo cuando hace falta.

## Ejemplos
### Mal
```text
"Estamos investigando un problema con el pod orders-7f9 en el nodo ip-10-0-3-4. Lo arreglaremos en 10 minutos."
```
### Bien
```text
[Investigando] 14:05 UTC - Algunos usuarios no pueden completar pedidos desde las 13:52 UTC.
Estamos investigando. Proxima actualizacion antes de las 14:35 UTC.

[Mitigado] 14:28 UTC - Hemos aplicado una mitigacion; los pedidos se completan con normalidad.
Seguimos monitorizando. Publicaremos un resumen en 5 dias laborables.
```

## Checklist de revisión
- [ ] Página fuera del dominio de fallo de la plataforma.
- [ ] Componentes y estados definidos; plantillas por fase.
- [ ] Rol de comunicaciones y plazos por tier.
- [ ] Publicación con aprobación humana.
- [ ] Sin datos personales ni detalles de seguridad.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| Revisión humana: simulacro tabletop de comunicación | 4 | revisión humana, en papel (la fábrica no despliega, ADR-0004) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `alert-routing-and-oncall`, `incident-management-and-postmortems`, `tier-model-and-rpo-rto`.
- Fuentes: buenas prácticas de gestión de incidentes (Atlassian/Google SRE), no verificadas en esta sesión, TODO-VERIFY URL.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
