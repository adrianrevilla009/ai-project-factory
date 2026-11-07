---
name: incident-response-playbooks-and-forensics
description: "Usar al escribir playbooks de respuesta a incidentes de seguridad y al definir preservación de evidencia y cadena de custodia forense."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Playbooks de respuesta a incidentes y forense

## Cuándo aplicar y cuándo no
- Aplica a incidentes de seguridad (credenciales comprometidas, malware, exfiltración, abuso interno) y a la evidencia que dejan.
- No aplica a incidentes de disponibilidad sin componente de seguridad (ver `incident-management-and-postmortems`); esos reutilizan la coordinación, no el análisis forense.

## Reglas
- **MUST** basar el ciclo de respuesta en un marco publicado: NIST SP 800-61 Rev. 3 (abril 2025, sustituye a Rev. 2) alineado con CSF 2.0.
- **MUST** tener un playbook por escenario probable (credencial filtrada, ransomware, fuga de datos, cuenta cloud comprometida) con roles, decisiones y criterios de escalado.
- **MUST** definir quién declara el incidente, quién lidera, quién comunica y quién decide contención; incluir contactos fuera de banda.
- **MUST** preservar evidencia antes de erradicar: copiar logs, snapshots y memoria cuando sea viable, con hash y registro de quién la manejó (cadena de custodia).
- **MUST** guardar la evidencia en almacenamiento de solo escritura y acceso restringido.
- **MUST** consultar a legales/DPO desde el inicio si hay datos personales: los plazos de notificación son un borrador por confirmar con fuente oficial (p. ej. RGPD, 72 h a la autoridad; TODO-VERIFY texto vigente).
- **SHOULD** ejecutar simulacros (tabletop) al menos una vez al año y actualizar los playbooks con lo aprendido.
- **SHOULD** sincronizar relojes (NTP) y conservar logs suficientes para reconstruir la línea temporal.
- **MUST NOT** apagar o reconstruir un sistema afectado sin haber decidido qué evidencia se pierde.
- **MUST NOT** usar canales posiblemente comprometidos (correo corporativo) para coordinar un incidente de cuenta comprometida.

## Por qué
Bajo presión se improvisa; un playbook convierte decisiones difíciles en pasos ensayados. La evidencia es frágil: reiniciar un nodo o rotar logs destruye lo que permite saber el alcance real y, si procede, sustentar acciones legales.

## Ejemplos
### Mal
```text
Alguien detecta un acceso anómalo, borra el pod y recrea el clúster "para limpiar".
No se guardaron logs ni imagen. Nadie sabe qué datos se leyeron.
```
### Bien
```yaml
# playbook-leaked-credential.example.yaml
trigger: "secreto expuesto en repositorio o log"
roles: {commander: oncall-security, comms: comms-lead, legal: dpo}
steps:
  1_contain:   "revocar y rotar la credencial (ver secret-scanning-and-leak-response)"
  2_preserve:  "exportar logs de acceso de las últimas 90 d; sha256 y registro de custodia"
  3_scope:     "buscar usos de la credencial en audit logs"
  4_eradicate: "eliminar el acceso persistente creado, si lo hay"
  5_recover:   "validar con monitorización reforzada 72 h"
  6_learn:     "postmortem sin culpables en 5 días laborables"
evidence_store: write-once-bucket   # ver backup-vault-immutability-and-restore-tests
```
```text
sha256sum evidence/access-log-2026-11-07.json >> evidence/CHAIN.txt
```

## Checklist de revisión
- [ ] Existe playbook para cada escenario prioritario.
- [ ] Roles y contactos fuera de banda definidos.
- [ ] Hay paso de preservación de evidencia antes de erradicar.
- [ ] Cadena de custodia y almacén de solo escritura definidos.
- [ ] Legales/DPO implicados; plazos marcados como por confirmar.
- [ ] Simulacro anual registrado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de playbooks contra esta checklist | 3 | agente revisor / PR |
| Simulacros y decisiones legales | 4 | revisión humana (sin artefacto automático) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `vulnerability-sla-and-incident-response`, `incident-management-and-postmortems`, `secret-scanning-and-leak-response`, `status-page-and-comms`, `audit-trail-and-security-logging`, `ransomware-resilience`.
- Fuentes (verificado 2026-11-07): NIST SP 800-61 Rev. 3, https://csrc.nist.gov/pubs/sp/800/61/r3/final. Normativa de notificación: borrador por confirmar con fuente oficial.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
