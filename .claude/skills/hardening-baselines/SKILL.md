---
name: hardening-baselines
description: "Usar al definir o revisar líneas base de endurecimiento (CIS Benchmarks) para imágenes, nodos, clústeres y servicios, con desviaciones documentadas."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Líneas base de endurecimiento (CIS)

## Cuándo aplicar y cuándo no
- Aplica a imágenes base, nodos, Kubernetes, bases de datos y servicios expuestos que necesitan una configuración segura de partida.
- No aplica a vulnerabilidades de paquetes (ver `image-scanning`) ni a políticas de admisión específicas (ver `pod-security-and-admission`).

## Reglas
- **MUST** elegir una línea base publicada (CIS Benchmark de la tecnología y versión concretas) y registrar cuál y qué perfil (Level 1 / Level 2).
- **MUST** aplicar la línea base como código (imagen construida, módulo Terraform, manifiesto), no como lista manual que se ejecuta una vez.
- **MUST** documentar cada desviación: control, motivo, riesgo aceptado, aprobador y fecha de revisión.
- **MUST** medir conformidad de forma automática y periódica, y tratar la regresión como hallazgo con SLA.
- **MUST** usar imágenes mínimas (distroless o equivalente) y usuario no root en contenedores.
- **SHOULD** empezar por Level 1 (impacto operativo bajo) y adoptar Level 2 donde el riesgo lo justifique.
- **SHOULD** versionar la línea base y revisarla cuando el benchmark o la tecnología cambien de versión mayor.
- **MUST NOT** aplicar un benchmark entero a ciegas en producción sin probarlo antes en un entorno equivalente.
- **MUST NOT** afirmar conformidad total con CIS; indicar el porcentaje de controles pasados y las excepciones.

## Por qué
Los valores por defecto de casi cualquier software priorizan facilidad de uso, no seguridad. Una línea base reconocida evita decidir cada ajuste desde cero y da un criterio objetivo para auditoría; como código, impide que cada servidor derive por su cuenta.

## Ejemplos
### Mal
```text
Un administrador aplicó "los ajustes de seguridad del blog" a mano en 3 de 10 nodos.
No hay registro de qué versión de benchmark se usó.
```
### Bien
```yaml
# baseline.example.yaml
target: kubernetes-node
benchmark: "CIS Kubernetes Benchmark"
version: "<fijar en el BOM>"
profile: level-1
as_code: terraform/modules/node-baseline
scan: kubescape scan framework cis   # comprobar nombre del framework en la versión instalada
deviations:
  - control: "1.2.x"                  # ejemplo ilustrativo
    reason: "requerido por el agente de observabilidad"
    risk_accepted_by: security-lead
    review_by: "2027-03-01"
```
```dockerfile
FROM gcr.io/distroless/java21-debian12:nonroot
COPY app.jar /app.jar
USER nonroot
ENTRYPOINT ["java","-jar","/app.jar"]
```
Etiqueta de imagen: comprobar al fijar la versión; fijar por digest en el proyecto real.

## Checklist de revisión
- [ ] Benchmark, versión y perfil registrados.
- [ ] La línea base es código versionado.
- [ ] Cada desviación tiene motivo, aprobador y fecha.
- [ ] Hay medición automática de conformidad.
- [ ] Contenedores sin root, imágenes mínimas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Rego de Dockerfile (usuario no root, etc.) | 1 | `policies/opa-conftest/dockerfile.rego` |
| Baseline de workloads en admisión | 1 | `policies/kyverno/workload-baseline.yaml` |
| Aprobación de desviaciones | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `container-images`, `container-and-k8s-security`, `workload-baseline`, `cspm-and-posture`, `pod-security-and-admission`.
- Fuentes: CIS Benchmarks, https://www.cisecurity.org/cis-benchmarks (comprobar no consultado, versiones y licencia de uso); Kubescape https://github.com/kubescape/kubescape (verificado 2026-11-07).
- Cloud: preparado para AWS, no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
