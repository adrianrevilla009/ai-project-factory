---
name: library-selection-and-tech-radar-process
description: "Usar al incorporar, sustituir o retirar una librería o tecnología: criterios de selección, licencia, ADR y mantenimiento de un radar tecnológico."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Selección de librerías y proceso de radar tecnológico

## Cuándo aplicar y cuándo no
- Aplica al añadir una dependencia nueva (Maven, npm), cambiar de herramienta o proponer una tecnología nueva.
- No aplica a actualizar versiones de dependencias ya aprobadas (ver `dependency-hygiene`, `bom-management`).

## Reglas
- **MUST** comprobar primero si el stack ya aprobado cubre la necesidad (Java + Spring Boot + Maven, Terraform, Istio, Keycloak...); las decisiones cerradas D1-D27 no se reabren aquí.
- **MUST** evaluar: necesidad real, madurez y actividad del mantenimiento, licencia, seguridad (CVEs, SBOM), tamaño de dependencias transitivas, integración con el stack y coste de salida.
- **MUST** licencia compatible y sin coste por defecto (D16); las licencias de pago o copyleft fuerte requieren decisión humana en ADR.
- **MUST** registrar la decisión en un ADR cuando la librería sea estructural o difícil de reemplazar.
- **MUST NOT** añadir Lombok (D27) ni una librería que duplique una ya aprobada.
- **MUST** clasificar en el radar: Adopt, Trial, Assess, Hold, con fecha y dueño; revisar el radar cada trimestre.
- **SHOULD** probar con una prueba de concepto acotada antes de pasar a Adopt.
- **SHOULD** aislar la librería tras un puerto/adaptador para reducir el coste de salida.
- **MUST NOT** fijar versiones por criterio propio: usar el BOM y verificar en documentación oficial (comprobar al fijar la versión).

## Por qué
Cada dependencia es deuda de mantenimiento, superficie de ataque y riesgo de licencia. Un proceso corto y explícito evita la proliferación y deja trazabilidad de por qué se eligió cada pieza.

## Ejemplos
### Mal
```xml
<dependency>
  <groupId>org.projectlombok</groupId>
  <artifactId>lombok</artifactId>
</dependency>
```
### Bien
```markdown
# ADR-0045: Librería de resiliencia
Estado: propuesta
Candidatas: Resilience4j, implementación propia
Criterios: licencia (Apache-2.0, comprobar al fijar la versión), actividad del repo, integración con Spring Boot, métricas Micrometer
Decisión: Resilience4j, tras puerto `ResilienceOps`
Radar: Trial (2026-11-07), dueño tech-lead, revisión 2027-02-07
Salida: sustituir el adaptador; ningún import fuera de `infrastructure`
```
```text
Radar:  Adopt  | Trial       | Assess | Hold
        Spring | Resilience4j| ...    | Lombok (prohibido, D27)
```

## Checklist de revisión
- [ ] Se comprobó que el stack aprobado no cubre la necesidad.
- [ ] Licencia, mantenimiento y seguridad evaluados con evidencia.
- [ ] ADR cuando la librería es estructural.
- [ ] Entrada en el radar con anillo, dueño y revisión.
- [ ] Aislada tras un puerto o adaptador.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep contra Lombok | 1 | `policies/semgrep/java-no-lombok.yaml` |
| Dependencias prohibidas con Maven Enforcer | 1 | `policies/maven-enforcer/banned-dependencies.example.xml` |
| Escaneo de licencias/SBOM en CI | 1 | pendiente, en el proyecto generado |
| Revisión humana de ADR y radar | 4 | revisión humana |

> Estado: el escaneo de licencias está pendiente.

## Relacionados, fuentes y mantenimiento
- Relacionados: `adr`, `dependency-hygiene`, `bom-management`, `rfc-process`, `risk-register`.
- Fuentes: concepto de Technology Radar (Thoughtworks (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
