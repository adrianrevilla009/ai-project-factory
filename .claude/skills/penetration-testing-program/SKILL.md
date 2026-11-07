---
name: penetration-testing-program
description: "Usar al planificar o revisar pruebas de penetración sobre sistemas propios: alcance y reglas de compromiso por escrito, metodología, informe y seguimiento."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Programa de pruebas de penetración (solo sistemas propios)

## Cuándo aplicar y cuándo no
- Aplica a pentests periódicos o previos a una salida a producción sobre sistemas que la organización posee o tiene autorización escrita para probar.
- No aplica a pruebas contra terceros sin autorización, ni a acciones ofensivas decididas por un agente de IA de forma autónoma. Los agentes de la fábrica NO ejecutan pentests; solo ayudan a redactar alcance, plan e informe. La fábrica tampoco despliega (ADR-0004).

## Reglas
- **MUST** disponer de un documento de autorización firmado antes de cualquier prueba: alcance (dominios, IPs, cuentas, entornos), exclusiones, ventana horaria, contactos de emergencia, tipo de prueba (caja negra/gris/blanca) y reglas de compromiso (RoE).
- **MUST** preferir un entorno de staging con datos sintéticos; si se prueba producción, acordar límites (sin denegación de servicio, sin exfiltración real de datos, sin ingeniería social salvo autorización expresa).
- **MUST** confirmar la titularidad: si el sistema está en un proveedor cloud, comprobar su política vigente de pruebas de seguridad (TODO-VERIFY por proveedor).
- **MUST** definir un canal de parada inmediata y un contacto del SOC/on-call informado de la ventana.
- **MUST** exigir informe con hallazgo, evidencia reproducible, impacto, severidad y recomendación, más un resumen ejecutivo.
- **MUST** abrir cada hallazgo en el registro de `vulnerability-management-program` con SLA y programar un retest.
- **SHOULD** basar la metodología en referencias públicas (OWASP WSTG, NIST SP 800-115, PTES) y en ASVS para el nivel de cobertura.
- **SHOULD** rotar proveedor o equipo cada pocos ciclos y combinar con pruebas internas continuas (DAST, SAST).
- **MUST NOT** almacenar credenciales o datos extraídos durante la prueba fuera del repositorio cifrado acordado; destruirlos al cerrar.
- **MUST NOT** ampliar el alcance durante la prueba sin adenda firmada.

## Por qué
Una prueba sin autorización escrita es un incidente legal; una prueba sin límites es un incidente operativo. El alcance y las RoE protegen al evaluador y a la organización, y el retest es lo que convierte el informe en reducción real de riesgo. Marco legal aplicable: borrador por confirmar con asesoría jurídica.

## Ejemplos
### Mal
```text
"Probad lo que queráis en *.example.com durante este mes."
Sin firma, sin exclusiones, sin contacto del SOC.
```
### Bien
```yaml
# pentest-roe.example.yaml
authorization: {signed_by: "CISO", date: "2026-11-07", reference: "SEC-example-01"}
scope_in: ["staging.example.com", "api-staging.example.com"]
scope_out: ["prod.example.com", "third-party payment provider"]
window: "2026-12-01T08:00Z/2026-12-12T18:00Z"
forbidden: [denial_of_service, social_engineering, real_data_exfiltration]
emergency_contacts: ["soc-oncall@example.com"]
deliverables: [executive_summary, technical_findings, retest_report]
```

## Checklist de revisión
- [ ] RoE firmadas y vigentes en la ventana de la prueba.
- [ ] Alcance e exclusiones explícitos; titularidad confirmada.
- [ ] SOC/on-call avisado y canal de parada definido.
- [ ] Hallazgos volcados al registro con SLA y retest planificado.
- [ ] Datos de la prueba destruidos o custodiados según lo acordado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Hook/permisos que impiden a los agentes lanzar herramientas ofensivas contra hosts no listados | 2 | pendiente |
| Aprobación de RoE por el responsable de seguridad | 4 | revisión humana (gate) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `dast-and-attack-simulation`, `vulnerability-management-program`, `asvs-mapping`, `bug-bounty-and-disclosure`.
- Fuentes (2026-11-07, TODO-VERIFY URLs exactas): OWASP Web Security Testing Guide; NIST SP 800-115; PTES; política de pruebas de seguridad del proveedor cloud usado.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
