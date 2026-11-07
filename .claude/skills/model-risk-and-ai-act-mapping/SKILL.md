---
name: model-risk-and-ai-act-mapping
description: "Usar al clasificar un sistema de IA por riesgo, mapearlo al Reglamento UE de IA (AI Act) y documentar riesgos de modelo; borrador por confirmar legalmente."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Riesgo de modelo y mapeo al AI Act

> Borrador por confirmar: este skill NO es asesoría legal. Toda clasificación debe validarla un responsable legal/compliance con el texto oficial.

## Cuándo aplicar y cuándo no
- Aplica al inicio de cualquier feature con modelos de IA (propios o de terceros) y al cambiar su finalidad, datos o modelo.
- No aplica a herramientas internas de desarrollo sin impacto en usuarios finales (aun así, revisar obligaciones de alfabetización en IA, TODO-VERIFY).

## Reglas
- **MUST** mantener un registro de sistemas de IA (`ai-system-register`): finalidad, modelo y proveedor, datos usados, usuarios afectados, rol (proveedor / desplegador), propietario.
- **MUST** clasificar cada sistema en una categoría preliminar: práctica prohibida, alto riesgo (Anexo III o producto regulado), obligaciones de transparencia (chatbots, contenido sintético) o riesgo mínimo.
- **MUST** parar y escalar a legal si la clasificación apunta a práctica prohibida o alto riesgo; la fábrica no decide.
- **MUST** documentar riesgos de modelo: alucinación, sesgo, deriva, dependencia de proveedor, fuga de datos, abuso; con mitigación y dueño.
- **MUST** informar al usuario cuando interactúa con un sistema de IA (ver `chatbot-design`).
- **SHOULD** usar un marco reconocido (NIST AI RMF, ISO/IEC 42001) como esqueleto de gobernanza, TODO-VERIFY versión vigente.
- **SHOULD** versionar modelo, prompt y dataset de evaluación para poder reconstruir una decisión (ver `prompt-management`, `llm-evals`).
- **MUST NOT** afirmar "cumple el AI Act" o "certificado"; usar "mapeado a requisitos, pendiente de revisión legal".

## Por qué
El AI Act entró en vigor el 1 de agosto de 2024; las prácticas prohibidas se aplican desde el 2 de febrero de 2025, las obligaciones de GPAI desde el 2 de agosto de 2025 y la aplicación general desde el 2 de agosto de 2026, con calendario de alto riesgo escalonado (diciembre 2027 y agosto 2028 según la página de la Comisión) y un paquete "omnibus" de simplificación en curso. Las fechas cambian: verificar siempre contra la fuente oficial antes de planificar. Un registro y una clasificación tempranos evitan descubrir en producción que el sistema era de alto riesgo.

## Ejemplos
### Mal
```yaml
# ai-system-register.yaml
- name: cv-screening
  purpose: "ayuda a RRHH"
  risk: "bajo, es solo una sugerencia"   # sin análisis; selección de personal suele ser alto riesgo
```
### Bien
```yaml
- name: cv-screening
  purpose: "Ordenar candidaturas por adecuación al puesto"
  role: deployer
  model: "third-party-llm, version pinned (TODO-VERIFY contrato)"
  data: ["CV (datos personales)", "oferta de empleo"]
  preliminary_class: high-risk-candidate   # empleo: Anexo III, TODO-VERIFY con legal
  legal_review: pending
  human_oversight: "ver human-in-the-loop; decisión final humana"
  risks:
    - {id: R1, type: bias, mitigation: "evals por subgrupo", owner: "ml-lead"}
    - {id: R2, type: pii-leak, mitigation: "redacción previa", owner: "sec-lead"}
```

## Checklist de revisión
- [ ] El sistema está en el registro con rol y propietario.
- [ ] Hay clasificación preliminar y estado de revisión legal.
- [ ] Riesgos de modelo con mitigación y dueño.
- [ ] Usuarios informados de la interacción con IA.
- [ ] No hay afirmaciones de cumplimiento sin revisión legal.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión legal/compliance de la clasificación | 4 | revisión humana (gate del proyecto) |
| Esquema del registro validado en CI | 1 | pendiente (`factory/validators/`) |
| Revisión de documentación de riesgos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `human-in-the-loop`, `ai-safety-and-red-teaming`, `pii-and-data-classification`, `training-data-licensing-and-provenance`, `chatbot-design`.
- Fuentes: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai (consultado 2026-11-07). Texto legal: Reglamento (UE) 2024/1689 en EUR-Lex, TODO-VERIFY artículos y anexos.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
