---
name: classical-mlops
description: "Usar al llevar un modelo de ML clásico (scikit-learn, XGBoost, series temporales) a un servicio: reproducibilidad, registro de modelos, validación, despliegue y monitorización de deriva."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# MLOps clásico

## Cuándo aplicar y cuándo no
- Aplica a modelos entrenados con datos propios (clasificación, regresión, previsión) que se consumen desde un servicio Java.
- No aplica a LLM de proveedor (ver `llm-evals`, `llm-gateway`) ni a reglas deterministas.

## Reglas
- **MUST** hacer reproducible el entrenamiento: versión del código, del dataset (hash o snapshot), de dependencias y semilla; guardar todo junto al artefacto.
- **MUST** mantener un registro de modelos con versión, métricas, dataset de origen, fecha y responsable; el servicio carga una versión concreta, nunca "latest".
- **MUST** separar entrenamiento, validación y prueba en el tiempo cuando los datos lo son (evitar fuga de información del futuro) y reportar métricas sobre el conjunto de prueba intacto.
- **MUST** definir un umbral de aceptación y una línea base simple (regla o modelo trivial); un modelo que no la supera no se despliega.
- **MUST** usar el mismo código de preparación de características en entrenamiento y en inferencia (una librería o servicio compartido).
- **MUST** monitorizar en servicio: latencia, errores, distribución de entradas (deriva de datos) y, cuando lleguen etiquetas, calidad real (deriva de rendimiento).
- **MUST** poder volver a la versión anterior sin reentrenar (rollback) y desplegar de forma gradual (sombra o canario).
- **SHOULD** evaluar sesgo entre grupos relevantes y documentar uso previsto y límites en una ficha del modelo (ver `model-risk-and-ai-act-mapping`).
- **SHOULD** servir modelos ligeros en proceso (p. ej. formato ONNX, comprobar runtime Java) o como servicio separado con contrato versionado.
- **SHOULD** orquestar el reentrenamiento con el orquestador de datos del proyecto (ver bloque de datos) y no con scripts manuales.
- **MUST NOT** cargar modelos serializados con `pickle` de origen no confiable: ejecuta código arbitrario al deserializar.
- **MUST NOT** entrenar con datos personales sin base legal y minimización (ver `pii-and-data-classification`).

## Por qué
Un modelo es código más datos; sin versionar ambos, nadie puede reproducir ni explicar una predicción. La mayor parte de los fallos reales son fuga de datos, sesgo de entrenamiento/servicio y deriva silenciosa, no el algoritmo. El registro y el rollback reducen el riesgo de cada despliegue.

## Ejemplos
### Mal
```python
model = pickle.load(open("/tmp/model_final_v2.pkl", "rb"))   # origen desconocido, sin versión
df = pd.read_csv("data.csv")                                  # dataset sin versionar
```
### Bien
```yaml
# model-card.yaml (junto al artefacto en el registro)
name: churn-classifier
version: 3
trained_at: "2026-11-01"
code_commit: "<git sha>"
dataset: { uri: "s3://example-bucket/churn/2026-10", sha256: "<hash>" }
metrics: { auc_test: 0.87, baseline_auc: 0.71 }
acceptance: { auc_test_min: 0.80 }
intended_use: "priorizar llamadas de retención; no para decisiones automáticas de baja"
monitoring: { drift_features: [tenure, plan], alert_psi: 0.2 }
```
```python
# validación temporal, sin fuga del futuro
train, test = df[df.date < "2026-09-01"], df[df.date >= "2026-09-01"]
```
El PSI 0.2 es un umbral habitual de la práctica; calibrar con datos propios.

## Checklist de revisión
- [ ] Entrenamiento reproducible y dataset versionado.
- [ ] Modelo registrado y servicio fijado a una versión.
- [ ] Línea base superada y umbral documentado.
- [ ] Mismo cálculo de características en entrenamiento e inferencia.
- [ ] Monitorización de deriva y plan de rollback.
- [ ] Sin `pickle` no confiable; ficha del modelo completa.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Semgrep: `pickle.load` / `joblib.load` sobre entrada no confiable | 1 | pendiente (`policies/semgrep/`) |
| Puerta de CI: métricas >= umbral y línea base superada | 1 | pendiente (proyecto generado) |
| Revisión de la ficha del modelo | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `model-risk-and-ai-act-mapping`, `llm-evals`, `pii-and-data-classification`, `training-data-licensing-and-provenance`, `dvc-or-lakefs-versioning`.
- Fuentes: documentación de scikit-learn sobre persistencia de modelos y riesgos de pickle (comprobar URL exacta); MLflow, si se usa (licencia y versión: comprobar al fijar la versión).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
