---
name: llm-evals
description: "Usar al añadir o cambiar un prompt, modelo, RAG o agente: define datasets de evaluación, métricas, jueces LLM y umbrales que bloquean regresiones en CI."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Evaluaciones de LLM (evals)

## Cuándo aplicar y cuándo no
- Aplica a cualquier funcionalidad con LLM: prompts, cambio de modelo o versión, RAG, extracción, clasificación, agentes con herramientas.
- No aplica a código determinista que solo llama al modelo sin interpretar la respuesta (cubrir con tests normales).

## Reglas
- **MUST** mantener un dataset de evaluación versionado en el repo del proyecto (`evals/datasets/*.jsonl`) con entrada, salida esperada o criterios, y etiqueta de origen.
- **MUST** separar casos de desarrollo y casos de reserva (holdout) que no se usan para ajustar prompts.
- **MUST** incluir casos adversos: entradas vacías, idioma distinto, inyección de prompt (ver `llm-security`) y casos que deben rechazarse.
- **MUST** definir métricas por tarea y umbral numérico antes de empezar a iterar (exactitud por campo, recall@k, tasa de rechazo correcto, latencia p95, coste por petición).
- **MUST** ejecutar los evals en CI ante cambios de prompt, modelo, parámetros o plantilla de recuperación y fallar si se cae por debajo del umbral.
- **MUST** fijar versión de modelo, temperatura y prompt en cada ejecución y guardar el resultado (traza) para comparar.
- **SHOULD** preferir métricas deterministas (esquema válido, igualdad, regex, recall@k) y usar juez LLM solo para criterios abiertos.
- **SHOULD** calibrar el juez LLM contra una muestra etiquetada por personas y medir su acuerdo; usar un modelo distinto al evaluado.
- **SHOULD** repetir casos no deterministas N veces y reportar media y dispersión.
- **MUST NOT** incluir datos personales reales en datasets sin anonimizar (ver `pii-and-data-classification`).
- **MUST NOT** aceptar un cambio porque "se ve mejor" en 3 ejemplos manuales.

## Por qué
Un LLM cambia de comportamiento con cualquier ajuste de prompt o actualización de modelo; sin un conjunto fijo de casos las regresiones se descubren en producción. Los jueces LLM tienen sesgos (preferencia por respuestas largas o por su propio estilo), por eso se calibran. El holdout evita sobreajustar el prompt a los casos que se ven.

## Ejemplos
### Mal
```python
# probado a mano con dos facturas
print(extract("factura_1.pdf"))
```
### Bien
```python
# evals/run_evals.py  (umbrales acordados antes de iterar)
import json, sys

THRESHOLDS = {"field_accuracy": 0.95, "schema_valid": 1.0, "correct_refusal": 0.90}

def run(cases, extract):
    ok_fields = total_fields = valid = 0
    for c in cases:
        out = extract(c["input"])               # modelo y prompt fijados por config
        valid += out.get("_schema_valid", False)
        for k, v in c["expected"].items():
            total_fields += 1
            ok_fields += out.get(k) == v
    n = len(cases)
    return {"field_accuracy": ok_fields / total_fields, "schema_valid": valid / n}

if __name__ == "__main__":
    cases = [json.loads(l) for l in open("evals/datasets/invoices.jsonl")]
    metrics = run(cases, extract=load_extractor())   # load_extractor: del proyecto
    failed = {k: v for k, v in metrics.items() if v < THRESHOLDS[k]}
    sys.exit(1 if failed else 0)
```

## Checklist de revisión
- [ ] Dataset versionado, con holdout y casos adversos.
- [ ] Umbrales numéricos definidos antes de iterar.
- [ ] Evals en CI con modelo, prompt y parámetros fijados.
- [ ] Juez LLM calibrado y distinto del modelo evaluado.
- [ ] Sin PII real en los datasets.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Job de CI que ejecuta `evals/run_evals.py` y falla bajo umbral | 1 | pendiente (workflow del proyecto generado) |
| Revisión de dataset, umbrales y calibración del juez | 3 | agente `code-reviewer` (revisión humana de umbrales) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `llm-observability`, `llm-security`, `intelligent-document-processing`, `token-and-cost-budgets`, `human-in-the-loop`.
- Fuentes: guías de evaluación de proveedores de modelos (p. ej. https://platform.claude.com/docs/en/test-and-evaluate/develop-tests, consultada 2026-11-07, TODO-VERIFY URL exacta).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
