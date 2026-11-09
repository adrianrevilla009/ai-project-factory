---
name: ai-safety-and-red-teaming
description: "Usar al planificar pruebas adversarias (red teaming) de un sistema con LLM propio: alcance escrito, categorías de riesgo, casos de prueba, severidad y remediación."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Seguridad de IA y red teaming

## Cuándo aplicar y cuándo no
- Aplica a sistemas con LLM que construye y opera el propio equipo: chatbots, RAG, agentes con herramientas.
- No aplica a sistemas de terceros ni a modelos de proveedores sin autorización por escrito: **solo sistemas propios, con alcance y reglas de compromiso escritos y firmados**.
- Complementa `llm-security` (controles defensivos); este skill cubre la verificación adversaria periódica.

## Reglas
- **MUST** tener un documento de alcance antes de probar: sistemas incluidos y excluidos, entornos (nunca producción con datos reales sin acuerdo), ventana temporal, responsables, canal de contacto y criterio de parada.
- **MUST** obtener autorización escrita del dueño del sistema y respetar las condiciones de uso del proveedor del modelo.
- **MUST** ejecutar las pruebas en un entorno aislado con datos sintéticos o anonimizados y credenciales de prueba de mínimo privilegio.
- **MUST** cubrir como mínimo: inyección de prompt directa e indirecta (documentos, webs, correos), fuga de prompt de sistema y de datos de otros tenants, abuso de herramientas/agentes (acciones no autorizadas), salidas dañinas o fuera de política, consumo excesivo de recursos y sesgo.
- **MUST** registrar cada caso: entrada, salida, categoría, severidad, reproducibilidad y versión de modelo/prompt.
- **MUST** convertir cada hallazgo confirmado en un caso de regresión del dataset de `llm-evals` y en una remediación con responsable y fecha.
- **MUST** tratar los resultados (que pueden contener contenido dañino o datos) como confidenciales y almacenarlos con acceso restringido.
- **SHOULD** repetir ante cada cambio de modelo, prompt, herramienta o fuente de datos, y al menos una vez por trimestre.
- **SHOULD** combinar casos manuales con generación automática de variantes, revisando los resultados a mano.
- **SHOULD** revisar el sistema frente a OWASP Top 10 for LLM Applications (edición 2025, publicada en noviembre de 2024) y frente a los requisitos de `model-risk-and-ai-act-mapping`.
- **MUST NOT** usar los resultados para atacar sistemas ajenos ni publicar técnicas de elusión contra un proveedor sin seguir su divulgación responsable.
- **MUST NOT** desactivar los controles de producción para "facilitar" la prueba y olvidar reactivarlos.

## Por qué
Los controles defensivos solo demuestran su valor cuando alguien intenta romperlos de forma sistemática. Sin alcance escrito, una prueba puede ser una intrusión no autorizada; sin registro, los hallazgos no se reproducen ni se convierten en regresiones. El objetivo es mejorar el sistema propio.

## Ejemplos
### Mal
```text
"Voy a probar si puedo hacer jailbreak al chatbot de otra empresa para ver qué responde."
```
### Bien
```yaml
# redteam/scope-2026Q4.yaml  (firmado por el dueño del sistema antes de empezar)
system: support-assistant (entorno staging, datos sintéticos)
owner: product-owner@example.com
window: 2026-11-10 .. 2026-11-14
in_scope: [chat endpoint, retrieval over synthetic kb, tool: create_ticket]
out_of_scope: [produccion, proveedor del modelo, otros tenants reales]
stop_if: [datos reales expuestos, impacto en servicio compartido]
categories: [prompt_injection_indirect, system_prompt_leak, tool_abuse, cross_tenant_leak]
report_to: security-lead@example.com
```
```json
{"id":"RT-014","category":"prompt_injection_indirect","input_ref":"kb/doc-77.md","expected":"ignore embedded instructions","observed":"called create_ticket","severity":"high","regression_case":"evals/datasets/adversarial.jsonl#RT-014"}
```

## Criterios de decisión y trampas
### Cómo decidir
- Pruebas adversariales antes del despliegue y de forma continua: inyección de instrucciones, fuga de datos, abuso de herramientas y contenido dañino.
- Los hallazgos se corrigen con controles, no solo con instrucciones al modelo.
### Trampas frecuentes
- Una prueba única antes del lanzamiento.
- Corregir solo con más texto en el prompt.
- Sin repetir al cambiar de modelo.
- Resultados sin dueño.
- Ignorar el abuso de las herramientas.
### Evidencia
- Un conjunto de casos adversariales ejecutado en cada cambio y sus resultados registrados.

## Checklist de revisión
- [ ] Alcance y autorización escritos antes de empezar.
- [ ] Entorno aislado, datos sintéticos, credenciales mínimas.
- [ ] Categorías mínimas cubiertas y casos registrados.
- [ ] Cada hallazgo tiene remediación y caso de regresión.
- [ ] Resultados almacenados con acceso restringido.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Aprobación del documento de alcance antes de la prueba | 4 | revisión humana (dueño del sistema y responsable de seguridad) |
| Casos adversos como regresión en CI | 1 | pendiente (ver `llm-evals`) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `llm-security`, `llm-evals`, `guardrails-and-pii-redaction`, `model-risk-and-ai-act-mapping`, `human-in-the-loop`.
- Fuentes: OWASP Top 10 for LLM Applications (https://genai.owasp.org, edición 2025); NIST AI RMF. Normativa aplicable: borrador por confirmar con fuente oficial.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
