---
name: runtime-security
description: "Usar al desplegar o configurar detección de amenazas en runtime en Kubernetes con Falco: reglas, salidas de alertas y ajuste de falsos positivos."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Seguridad en runtime con Falco

## Cuándo aplicar y cuándo no
- Aplica a clústeres con cargas de negocio donde interesa detectar comportamiento anómalo (shell en contenedor, escritura en `/etc`, conexiones inesperadas).
- No sustituye a Pod Security, NetworkPolicy ni al escaneo de imágenes: es una capa de detección, no de prevención.
- No aplica a la fábrica: solo documenta la guía; la fábrica nunca despliega (ADR-0004).

## Reglas
- **MUST** usar Falco (licencia OSS) como detector por defecto; no adoptar productos de pago por defecto (D16).
- **MUST** desplegarlo como DaemonSet con un driver soportado por el kernel de los nodos (comprobar driver eBPF moderno vs módulo, según versión de Falco).
- **MUST** enviar las alertas a un destino persistente (Falcosidekick hacia Loki/Alertmanager/webhook), no solo a stdout del pod.
- **MUST** mantener las reglas propias en un fichero versionado (`custom-rules.yaml`) y no editar el ruleset base.
- **SHOULD** ajustar excepciones con `append`/listas de macros, nunca desactivando una regla entera sin ADR.
- **SHOULD** clasificar prioridades: `CRITICAL`/`ERROR` generan aviso a guardia; `WARNING` solo ticket.
- **MUST NOT** dar a Falco más privilegios de los que su documentación exige.

## Por qué
Las políticas de admisión solo actúan al crear el pod. Un atacante con RCE en la aplicación opera después: abre una shell, lee tokens del ServiceAccount, escanea la red. Falco observa syscalls y lo señala. Sin destino persistente ni ajuste, o se pierde la alerta o se ignora por ruido.

## Ejemplos
### Mal
```yaml
# Se desactiva la regla porque "hace ruido"
- rule: Terminal shell in container
  enabled: false
```
### Bien
```yaml
# custom-rules.yaml: se acota el caso legítimo en vez de apagar la regla
- list: debug_allowed_namespaces
  items: [tooling-debug]

- rule: Terminal shell in container
  exceptions:
    - name: allowed_ns
      fields: [k8s.ns.name]
      comps: [in]
      values: [[tooling-debug]]
  append: true
```
Sintaxis de `exceptions` y `append`: comprobar contra la documentación de Falco de la versión elegida.

## Checklist de revisión
- [ ] Falco corre en todos los nodos de carga (incluidos pools con taints, con tolerations).
- [ ] Las alertas llegan a un sistema persistente y hay un responsable.
- [ ] Reglas propias en repositorio, con tests/revisión.
- [ ] Ninguna regla base desactivada sin justificación.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de values de Falco y reglas propias | 3 | agente `code-reviewer` |
| Política Kyverno que exija el DaemonSet de Falco (pendiente) | 1 | `policies/kyverno/` (pendiente) |
| Decisión de alertado y guardia | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `container-and-k8s-security`, `pod-security-and-admission`, `audit-trail-and-security-logging`.
- Fuentes: documentación oficial de Falco (falco.org/docs) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
