---
name: ids-ips-waf-edr
description: "Usar al elegir y desplegar controles de detección y bloqueo: IDS/IPS de red, WAF, EDR y detección en runtime de contenedores, y cómo se ajustan sin romper tráfico legítimo."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# IDS/IPS, WAF y EDR

## Cuándo aplicar y cuándo no
- Aplica a decidir qué capa de detección/bloqueo se añade, en qué modo arranca y cómo se alimenta al SIEM.
- No aplica a limitación de tasa de la propia API (ver `dos-and-rate-limiting`) ni a políticas de red de Kubernetes (ver `container-and-k8s-security`). Son defensa en profundidad: no sustituyen a la validación en código.

## Reglas
- **MUST** desplegar cada control primero en modo detección/solo registro, medir falsos positivos con tráfico real y solo después activar bloqueo.
- **MUST** elegir cada capa por la amenaza que cubre: WAF para HTTP (reglas OWASP CRS sobre ModSecurity/Coraza), IDS/IPS para tráfico de red (p. ej. Suricata), EDR/runtime para hosts y contenedores (p. ej. Falco; Wazuh como agente), en OSS por defecto.
- **MUST** enviar los eventos de todos los controles al SIEM (ver `siem-and-detection-engineering`).
- **MUST** versionar reglas y excepciones (exclusiones por ruta/regla) con justificación y caducidad; nada de desactivar una regla "porque molesta".
- **MUST** definir un procedimiento de bypass de emergencia y quién puede activarlo.
- **SHOULD** ajustar el nivel de paranoia del WAF por aplicación y probarlo en CI con peticiones legítimas de contratos OpenAPI.
- **SHOULD** actualizar firmas/reglas de forma automática con revisión del diff.
- **MUST NOT** considerar el WAF como arreglo de una vulnerabilidad: la vulnerabilidad sigue en el registro con su SLA.
- **MUST NOT** inspeccionar tráfico cifrado de usuarios sin base legal y aviso (privacidad: borrador por confirmar).

## Por qué
Un WAF en bloqueo sin ajustar tumba funcionalidades legítimas y se acaba apagando; uno en solo detección nunca para nada. El rollout por fases y las excepciones con caducidad mantienen el control activo. En AWS existen equivalentes gestionados (AWS WAF, Network Firewall, GuardDuty): preparado para AWS, no verificado en real; en local solo se reproduce la variante OSS, no los servicios gestionados.

## Ejemplos
### Mal
```text
SecRuleEngine On   # directamente en producción, sin periodo de observación
SecRuleRemoveById 942100  # sin comentario ni caducidad
```
### Bien
```text
# waf-rollout.example.conf (sintaxis ModSecurity v3; TODO-VERIFY contra la versión usada)
SecRuleEngine DetectionOnly
# Excepcion SEC-example-12, caduca 2027-03-01: campo "q" de /search genera FP en regla 942100
SecRule REQUEST_URI "@beginsWith /search" \
  "id:1000001,phase:1,pass,nolog,ctl:ruleRemoveTargetById=942100;ARGS:q"
```
Plan: 2 semanas en DetectionOnly, revisión de falsos positivos, paso a bloqueo por aplicación.

## Checklist de revisión
- [ ] Control en modo detección antes de bloquear; criterio de salida definido.
- [ ] Eventos llegan al SIEM.
- [ ] Exclusiones con ticket y caducidad.
- [ ] Hay bypass de emergencia documentado.
- [ ] Las vulnerabilidades mitigadas siguen abiertas en el registro.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Policy que exige exclusiones WAF con campo de caducidad | 1 | pendiente (`policies/opa-conftest/`) |
| Políticas de runtime/admisión de Kubernetes | 1 | `policies/kyverno/workload-baseline.yaml` |
| Revisión de modo y falsos positivos antes de bloquear | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `siem-and-detection-engineering`, `container-and-k8s-security`, `dos-and-rate-limiting`, `vulnerability-management-program`.
- Fuentes (2026-11-07, TODO-VERIFY URLs): OWASP Core Rule Set; documentación de Suricata, Falco, Coraza y Wazuh.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
