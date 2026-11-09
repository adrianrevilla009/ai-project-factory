---
name: third-party-and-supply-chain-risk
description: "Usar al evaluar proveedores y componentes externos como riesgo de negocio: due diligence, cláusulas contractuales, monitorización continua y plan de salida."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Riesgo de terceros y cadena de suministro (visión de programa)

## Cuándo aplicar y cuándo no
- Aplica a proveedores SaaS, subcontratistas y servicios que tratan datos o forman parte de la entrega, vistos como riesgo organizativo.
- No aplica a controles técnicos de dependencias y artefactos (ver `supply-chain`, `sbom`, `image-signing-and-provenance`); este skill los complementa y no los repite.

## Reglas
- **MUST** mantener un inventario de terceros con: servicio, datos que trata, criticidad, propietario interno y fecha de última revisión.
- **MUST** clasificar a cada tercero por nivel de riesgo (p. ej. crítico / alto / normal) y ajustar a ello la profundidad de la due diligence.
- **MUST** pedir evidencias proporcionales antes de contratar: informes de auditoría independientes (p. ej. SOC 2, ISO/IEC 27001) y cuestionario de seguridad; validar alcance y fechas, no solo la existencia del certificado.
- **MUST** incluir en contrato: notificación de incidentes en plazo definido, derecho de auditoría o evidencias, tratamiento y devolución/borrado de datos, subencargados, cumplimiento normativo aplicable (borrador por confirmar con asesoría legal).
- **MUST** documentar un plan de salida para terceros críticos (portabilidad de datos, alternativa, tiempo estimado).
- **MUST** revisar terceros críticos al menos anualmente y ante incidentes públicos del proveedor.
- **SHOULD** limitar el acceso del tercero al mínimo necesario, con credenciales propias, caducidad y auditoría (ver `iam-governance-and-pam`).
- **SHOULD** suscribirse a los avisos de seguridad y a la página de estado de los proveedores críticos.
- **MUST NOT** compartir datos de producción o personales con un tercero sin base contractual y revisión de privacidad.
- **MUST NOT** aceptar el certificado del proveedor como sustituto de controles propios sobre los datos que le enviamos (cifrado, minimización).

## Por qué
Muchos incidentes llegan a través de un proveedor o un componente heredado. El riesgo no se transfiere por contrato: la responsabilidad ante clientes y reguladores sigue siendo nuestra. Un inventario con criticidad y plan de salida evita descubrir la dependencia en mitad de la crisis.

## Ejemplos
### Mal
```text
Se contrata una herramienta de analítica con datos reales de clientes tras ver su
logo de "Seguro" en la web. Sin contrato de encargado, sin plan de salida.
```
### Bien
```yaml
# third-party-register.example.yaml
- vendor: ExampleAnalytics
  service: product-analytics
  data: [pseudonymised-usage-events]     # sin datos personales directos
  criticality: normal
  owner: product-lead
  evidence: [iso27001-cert-scope-checked, security-questionnaire-2026]
  contract: {incident_notice: 48h, subprocessors_listed: true, data_return: 30d}
  exit_plan: "export CSV + sustituir por alternativa abierta; 4 semanas"
  next_review: "2027-11-01"
```

## Criterios de decisión y trampas
### Cómo decidir
- Evalúa proveedores por criticidad y datos compartidos, exige controles proporcionales y vigila cambios; define el plan de salida.
- Incluye librerías y servicios en la evaluación.
### Trampas frecuentes
- Evaluar una vez al contratar.
- Cuestionarios sin verificación.
- Datos compartidos sin acuerdo.
- Sin plan de salida.
- Ignorar a los proveedores de tus proveedores.
### Evidencia
- Un registro de terceros con criticidad, datos, controles y revisión.

## Checklist de revisión
- [ ] El tercero está en el inventario con criticidad y propietario.
- [ ] Se validó alcance y fecha de las certificaciones.
- [ ] El contrato cubre incidentes, datos, subencargados y salida.
- [ ] Terceros críticos tienen plan de salida.
- [ ] Hay fecha de próxima revisión.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de altas de terceros contra la checklist | 3 | agente revisor / PR |
| Valoración legal y de privacidad | 4 | revisión humana |
| Controles técnicos de dependencias | 1 | ver skills `supply-chain` y `dependency-security` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `third-party-risk`, `supply-chain`, `sbom`, `license-compliance`, `threat-intel-and-risk-register`, `pii-and-data-classification`.
- Fuentes: NIST SP 800-161 (gestión de riesgo de cadena de suministro); requisitos contractuales/normativos: borrador por confirmar con fuente oficial.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
