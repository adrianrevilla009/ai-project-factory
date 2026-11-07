---
name: training-data-licensing-and-provenance
description: "Usar al reunir datos o documentos para entrenar, afinar o alimentar un RAG: licencias, base legal, procedencia, consentimiento y registro de origen."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Licencias y procedencia de datos de entrenamiento

## Cuándo aplicar y cuándo no
- Aplica a conjuntos usados para entrenar, afinar, evaluar o indexar en un RAG (propios, de clientes, públicos, comprados, sintéticos).
- No aplica al uso de un modelo de proveedor vía API sin entrenar con datos propios (ver sus condiciones y `llm-gateway`).
- Esto no es asesoramiento jurídico: el marco legal es un borrador por confirmar con asesoría legal y fuente oficial.

## Reglas
- **MUST** mantener un registro de procedencia por conjunto de datos: origen, fecha de obtención, licencia o base legal, titular, finalidad permitida, restricciones (uso comercial, atribución, derivadas) y responsable.
- **MUST** verificar que la licencia o el contrato permiten el uso previsto (entrenar, afinar, redistribuir el modelo, uso comercial) antes de incorporar el dato; ante duda, excluirlo hasta aclararlo.
- **MUST** no usar datos de clientes para entrenar sin cláusula contractual o consentimiento que lo permita y sin limitar la finalidad.
- **MUST** clasificar datos personales y aplicar minimización, anonimización o seudonimización antes de entrenar (ver `pii-and-data-classification`); definir la base legal (RGPD, borrador por confirmar).
- **MUST** respetar señales de exclusión del origen (términos de uso, `robots.txt`, avisos de reserva de derechos) y no hacer scraping de fuentes que lo prohíban.
- **MUST** versionar el dataset con hash e identificar qué versión entrenó cada modelo (ver `classical-mlops`).
- **MUST** poder retirar datos: si un titular ejerce sus derechos o caduca una licencia, saber qué modelos e índices se ven afectados y planificar reindexado o reentrenamiento.
- **SHOULD** preferir datos propios, de licencia abierta compatible (CC0, CC-BY, Apache-2.0 según el caso) o sintéticos generados con modelos cuyas condiciones permitan ese uso (TODO-VERIFY por proveedor).
- **SHOULD** mantener la lista de licencias aceptadas y rechazadas por el proyecto y una revisión legal para las dudosas.
- **SHOULD** revisar el dato sintético: puede heredar restricciones del modelo generador y sesgos.
- **MUST NOT** mezclar sin etiquetar datos con licencias incompatibles en un mismo conjunto.
- **MUST NOT** asumir que un dato "público" en la web es de uso libre.

## Por qué
Una vez entrenado, un modelo no "olvida" fácilmente: un dato con licencia incompatible o sin base legal contamina el modelo y obliga a reentrenar. El registro de procedencia permite responder a auditorías, a derechos de los titulares y a requisitos de transparencia de la normativa de IA (borrador por confirmar).

## Ejemplos
### Mal
```text
datos/  (volcado de 40 GB descargado "de internet", sin README, sin licencia, mezclado con tickets de clientes)
```
### Bien
```yaml
# datasets/provenance/support-tickets-2026-10.yaml
id: support-tickets-2026-10
sha256: "<hash del snapshot>"
origin: "tickets internos, cliente ACME (example)"
obtained_at: "2026-10-15"
legal_basis: "contrato marco cláusula 7.2 (uso para mejora del servicio); TODO-VERIFY con legal"
license: "propietaria del cliente"
allowed_use: [fine_tuning_internal, evaluation]
forbidden_use: [redistribution, training_for_other_customers]
pii: { present: true, treatment: "seudonimizado con tokens; mapa en almacén separado" }
retention_until: "2027-10-15"
trained_models: [ticket-classifier:3]
owner: data-steward@example.com
```

## Checklist de revisión
- [ ] Cada dataset tiene ficha de procedencia con licencia/base legal.
- [ ] Uso previsto cubierto por licencia o contrato.
- [ ] PII tratada y finalidad limitada.
- [ ] Versión del dataset enlazada a los modelos que entrenó.
- [ ] Procedimiento de retirada y reentrenamiento definido.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Comprobación en CI de que todo dataset referenciado tiene ficha de procedencia | 1 | pendiente (proyecto generado) |
| Revisión legal de licencias dudosas y bases legales | 4 | revisión humana (asesoría legal) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `pii-and-data-classification`, `classical-mlops`, `model-risk-and-ai-act-mapping`, `intelligent-document-processing`, `vector-store-selection`.
- Fuentes: texto oficial del RGPD y del Reglamento de IA de la UE en EUR-Lex (TODO-VERIFY artículos y fechas de aplicación); textos de licencias en https://creativecommons.org y https://www.apache.org/licenses/ (consulta 2026-11-07, TODO-VERIFY).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
