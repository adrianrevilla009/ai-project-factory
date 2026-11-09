---
name: security-gates
description: "Usar al añadir gates de seguridad al pipeline: SAST, secretos, SCA, escaneo de imagen, IaC, SBOM y firma, con umbrales y excepciones VEX."
metadata:
  block: "16-ci-cd"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Security gates del pipeline

## Cuándo aplicar y cuándo no
- Aplica a PR y rama principal de cualquier proyecto generado.
- No aplica al detalle de cada herramienta (ver `dependency-security`, `container-and-k8s-security`, `supply-chain`, `security-testing-sast-dast`).

## Reglas
- **MUST** ejecutar SAST (Semgrep con las reglas de `policies/semgrep/`), detección de secretos y SCA en cada PR.
- **MUST** escanear la imagen con Trivy y Grype y el árbol de dependencias con OWASP Dependency-Check (D17); fallar en severidad CRITICAL/HIGH con arreglo disponible.
- **MUST** escanear IaC (Checkov/Conftest, `terraform validate`) antes de cualquier `plan`.
- **MUST** generar SBOM CycloneDX por build, subirlo a Dependency-Track y firmar la imagen (cosign) tras pasar los gates.
- **MUST** registrar excepciones como VEX/archivo de ignorados con motivo, dueño y caducidad; nunca ignorar en silencio.
- **MUST NOT** usar licencias de pago por defecto (D16); Xray es opcional (D17).
- **MUST NOT** exponer secretos a jobs de PR de forks.
- **SHOULD** ejecutar escaneos programados (nightly) además de en PR: aparecen CVEs nuevas sin cambio de código.

## Por qué
Cada herramienta tiene puntos ciegos; la cobertura redundante (D17) los reduce. Las excepciones con caducidad evitan que el ruido acumulado haga invisible un hallazgo real.

## Ejemplos
### Mal
```yaml
- run: trivy image app:latest || true
```
### Bien
```yaml
- run: >
    trivy image --exit-code 1 --severity CRITICAL,HIGH --ignore-unfixed
    --vex vex.openvex.json registry.example.com/shop/orders@${{ needs.build.outputs.digest }}
  # flags comprobar contra la versión de Trivy fijada
- run:./mvnw -B org.cyclonedx:cyclonedx-maven-plugin:makeAggregateBom   #
- run: semgrep scan --config policies/semgrep --error
```

## Criterios de decisión y trampas
### Cómo decidir
- Capas complementarias: secretos, SAST, dependencias, imagen, IaC y DAST; ninguna sustituye a las demás.
- Bloquea por severidad y explotabilidad, no por cualquier hallazgo; una política de excepciones con plazo evita la fatiga.
- Firma y SBOM al final, sobre el artefacto que se despliega.
### Trampas frecuentes
- Bloquear con cualquier hallazgo de baja severidad: se acaba desactivando el escáner.
- Escaneos sin base de datos actualizada.
- Falsos positivos sin triaje que se acumulan.
- Escanear la imagen de ayer y desplegar la de hoy.
- Resultados en un sitio que nadie mira.
### Evidencia
- Los hallazgos entran en el flujo de trabajo del equipo con propietario y plazo, y hay un SBOM por build.

## Checklist de revisión
- [ ] SAST, secretos, SCA, imagen e IaC presentes y bloqueantes.
- [ ] Sin `|| true` ni `continue-on-error` en escaneos.
- [ ] SBOM generado, publicado y firma tras los gates.
- [ ] Excepciones con motivo, dueño y caducidad.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Reglas Semgrep de seguridad | 1 | `policies/semgrep/` |
| Regla Rego: escaneos sin `|| true` | 1 | pendiente |
| Checkov custom para IaC | 1 | `policies/iac-checks/` (pendiente de contenido) |
| Revisión de excepciones VEX | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `supply-chain`, `dependency-security`, `container-and-k8s-security`, `quality-gates`, `secrets-management`.
- Fuentes: ADR-0017 (`catalog/adr/0017-escaneo-y-sbom.md`); docs oficiales de Trivy, Grype, CycloneDX.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
