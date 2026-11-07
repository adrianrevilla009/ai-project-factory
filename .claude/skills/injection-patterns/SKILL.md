---
name: injection-patterns
description: "Usar al decidir cómo llegan los secretos de Vault a un pod en Kubernetes: Vault Secrets Operator, Agent Injector o CSI Provider, y cómo los consume Spring Boot."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Vault: patrones de inyección de secretos en pods

## Cuándo aplicar y cuándo no
- Aplica al entregar secretos de Vault a aplicaciones Spring Boot en Kubernetes.
- No aplica a configuración no secreta (ver `config-by-environment`) ni a secretos de build (CI).
- Local: los tres patrones se pueden probar contra Vault en kind/k3d. NO se reproduce IRSA ni el almacenamiento de Secrets cifrado con KMS de EKS.

## Reglas
- **SHOULD** usar **Vault Secrets Operator (VSO)** por defecto: sincroniza a `Secret` de Kubernetes mediante CRDs (`VaultStaticSecret`, `VaultDynamicSecret`) sin sidecar. Es la opción más simple de operar.
- **SHOULD** usar **Agent Injector** (sidecar) cuando se necesita renovación de leases y plantillas de fichero sin `Secret` de K8s; coste: un contenedor extra por pod.
- **SHOULD** usar **CSI Provider** cuando no se quiere persistir el valor en etcd y basta montar un volumen efímero; limitación: rotación y sincronización a variables de entorno más pobre. TODO-VERIFY comportamiento de rotación en la versión fijada.
- **MUST** documentar la elección por servicio en un ADR corto; **MUST NOT** mezclar patrones sin motivo.
- **MUST** preferir montar secretos como **ficheros** y leerlos con `spring.config.import=optional:configtree:/vault/secrets/`; evitar variables de entorno (se filtran en volcados y `/proc`).
- **MUST** que el cifrado de `Secret` en etcd (KMS provider) esté activo si se usa VSO; sin él, el secreto queda en claro en etcd. TODO-VERIFY configuración EKS.
- **MUST** que cada servicio use su ServiceAccount y rol (`auth-methods`); **MUST NOT** compartir un rol entre namespaces.
- **MUST** que la app tolere el cambio del secreto (relectura o reinicio controlado; en VSO, `rolloutRestartTargets`).
- **MUST NOT** registrar valores de secretos en logs, `toString()` ni Actuator (`management.endpoint.env.show-values=NEVER`).
- **MUST NOT** poner un token Vault de larga vida en un `Secret` o `ConfigMap`.

## Por qué
La elección depende de quién renueva y dónde reside el valor. VSO mueve el secreto a etcd (cómodo, exige cifrado en reposo); el injector y el CSI mantienen el valor en el pod. Los ficheros evitan fugas por entorno y permiten rotar sin reiniciar si la app relee.

## Ejemplos
### Mal
```yaml
env:
  - name: DB_PASSWORD
    value: "changeme-example"          # secreto en el manifiesto
  - name: VAULT_TOKEN
    value: "hvs.changeme-example"      # token fijo
```
### Bien
```yaml
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultDynamicSecret
metadata: { name: orders-db, namespace: orders-prod }
spec:
  vaultAuthRef: orders-auth
  mount: database
  path: creds/orders-rw
  destination: { name: orders-db, create: true }
  rolloutRestartTargets:
    - { kind: Deployment, name: orders }
```
```yaml
# Deployment: montar como fichero
volumeMounts: [{ name: db, mountPath: /vault/secrets, readOnly: true }]
volumes: [{ name: db, secret: { secretName: orders-db } }]
```
```properties
spring.config.import=optional:configtree:/vault/secrets/
management.endpoint.env.show-values=NEVER
```
Versiones de API y campos de los CRDs de VSO: TODO-VERIFY en la versión fijada.

## Checklist de revisión
- [ ] Patrón elegido y justificado por servicio.
- [ ] Secretos montados como fichero, no en variables de entorno.
- [ ] Cifrado de Secrets en etcd activo si se usa VSO.
- [ ] ServiceAccount y rol propios por servicio.
- [ ] Reinicio/relectura al rotar; sin secretos en logs ni Actuator.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Hook contra literales de secretos en manifiestos | 2 | `.claude/hooks/pre-tool-use/block_secrets.py` |
| Kyverno: prohibir `env.value` con nombres tipo `*PASSWORD*`/`VAULT_TOKEN` | 1 | pendiente: `policies/kyverno/` |
| Revisión de la elección VSO/agent/CSI | 3 | revisión humana (security-reviewer) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `auth-methods`, `rotation-and-leases`, `secrets-management`, `configuration-properties`, `container-and-k8s-security`.
- Fuentes (2026-11-07): https://developer.hashicorp.com/vault/docs/deploy/kubernetes (TODO-VERIFY ruta y comparativa vigentes).
- Estado: diseño; preparado para AWS, no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
