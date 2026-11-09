---
name: container-and-k8s-security
description: Usar al escribir Dockerfile o manifiestos Kubernetes/Helm para endurecer imágenes, pods, red y RBAC del clúster.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Seguridad de contenedores y Kubernetes

## Cuándo aplicar y cuándo no
- Aplica a Dockerfile, manifiestos/Helm de workloads, NetworkPolicy, RBAC y políticas de admisión.
- No aplica a la firma de imágenes (ver `supply-chain`) ni a IAM de la nube (ver `cloud-iam-least-privilege`).

## Reglas
- **MUST** ejecutar como no root (`runAsNonRoot: true`, UID numérico) con `allowPrivilegeEscalation: false`.
- **MUST** descartar todas las capabilities (`drop: ["ALL"]`) y añadir solo las imprescindibles; **MUST NOT** usar `privileged: true`, `hostNetwork`, `hostPID` ni montar `hostPath` ni el socket del runtime.
- **MUST** usar `readOnlyRootFilesystem: true` con `emptyDir` para rutas de escritura, y `seccompProfile: RuntimeDefault`.
- **MUST** definir `resources.requests/limits` en todos los contenedores.
- **MUST** partir de imagen base mínima y mantenida (distroless o equivalente), multi-stage, sin herramientas de build ni shell en runtime; **MUST NOT** usar `latest`; fijar por digest.
- **MUST NOT** incluir secretos en la imagen ni en variables del manifiesto en claro (ver `secrets-management`).
- **MUST** aplicar `NetworkPolicy` con denegación por defecto y reglas explícitas de entrada/salida.
- **MUST** usar una `ServiceAccount` por workload con `automountServiceAccountToken: false` salvo necesidad, y RBAC de mínimo privilegio; **MUST NOT** usar `cluster-admin` para aplicaciones.
- **SHOULD** aplicar Pod Security Admission en modo `restricted` por namespace y Kyverno/OPA para reglas propias.
- **SHOULD** escanear imágenes (Trivy, OSS) en CI y en registro.
- Honestidad: la fábrica valida manifiestos de forma estática; el comportamiento en un clúster EKS real no está verificado.

## Por qué
Un contenedor comprometido hereda los privilegios con los que corre. Quitar root, capabilities y escritura reduce lo que un atacante puede hacer; la red plana permite movimiento lateral; los tokens de ServiceAccount montados por defecto dan acceso a la API.

## Ejemplos
### Mal
```yaml
containers:
  - name: app
    image: example/app:latest
    securityContext: { privileged: true }
```
### Bien
```dockerfile
FROM maven:3-eclipse-temurin-21 AS build   # tag verificado en Docker Hub el 2026-11-08; fijar por digest en el proyecto
WORKDIR /src
COPY . .
RUN mvn -B -q package -DskipTests
FROM gcr.io/distroless/java21-debian12:nonroot   # imagen y tag verificados en gcr.io el 2026-11-08; fijar por digest
COPY --from=build /src/target/app.jar /app/app.jar
USER 65532:65532
ENTRYPOINT ["java","-jar","/app/app.jar"]
```
```yaml
spec:
  automountServiceAccountToken: false
  securityContext: { runAsNonRoot: true, seccompProfile: { type: RuntimeDefault } }
  containers:
    - name: app
      image: registry.example.com/app@sha256:0000example
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities: { drop: ["ALL"] }
      resources: { requests: { cpu: 100m, memory: 256Mi }, limits: { memory: 512Mi } }
```

## Checklist de revisión
- [ ] No root, sin privilegios, capabilities descartadas, FS de solo lectura.
- [ ] Imagen mínima, fijada por digest, sin secretos.
- [ ] NetworkPolicy deny-by-default y ServiceAccount dedicada.
- [ ] Requests/limits definidos; PSA `restricted` en el namespace.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Kyverno: no root, no privileged, no latest, limits | 1 | pendiente (`policies/kyverno/`) |
| Checkov/Trivy config sobre Dockerfile y manifiestos | 1 | pendiente (CI del proyecto generado) |
| Revisión humana de excepciones de seguridad | 4 | PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `supply-chain`, `secrets-management`, `container-images`, `cloud-iam-least-privilege`, `zero-trust`.
- Fuentes: Kubernetes Pod Security Standards y documentación de Kyverno, OWASP Docker/Kubernetes Cheat Sheets.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
