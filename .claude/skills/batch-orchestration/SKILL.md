---
name: batch-orchestration
description: "Usar al diseñar pipelines batch orquestados con Airflow o Dagster: DAGs idempotentes, reintentos, backfills, particiones por intervalo, alertas y secretos."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Orquestación batch (Airflow / Dagster)

## Cuándo aplicar y cuándo no
- Aplica a cargas programadas con dependencias, reintentos y backfills en la plataforma de datos.
- No aplica a tareas `@Scheduled` de un microservicio (ver `scheduling-and-batch`; la regla Semgrep está en `policies/semgrep/java-scheduled-without-lock.yaml`) ni a flujos de CI/CD (ver `argo-workflows-and-events`).

## Reglas
- **MUST** hacer cada tarea idempotente y parametrizada por intervalo de datos (no por `now()`): re-ejecutar el mismo intervalo da el mismo resultado.
- **MUST** escribir con patrón "overwrite de partición" o `MERGE`, nunca `INSERT` ciego.
- **MUST** fijar `catchup=False` por defecto; los backfills son una acción explícita y acotada.
- **MUST** definir reintentos con backoff y timeout por tarea, y alerta ante fallo final.
- **MUST** leer credenciales de un backend de secretos (Vault OSS, D16), no de variables de DAG ni del código.
- **MUST NOT** hacer trabajo pesado en el scheduler/parseo del DAG (consultas o llamadas de red a nivel de módulo).
- **MUST NOT** pasar datasets grandes por XCom/metadatos; pasar referencias (ruta, partición).
- **SHOULD** preferir modelo por activos (Dagster) o datasets/assets (Airflow) cuando el dato es el objeto de gestión; DAG de tareas si es proceso.
- **SHOULD** emitir eventos OpenLineage (ver `data-contracts-and-lineage`).
- **SHOULD** separar orquestación de transformación: el orquestador llama a dbt/Spark, no contiene la lógica SQL.

## Por qué
Los reintentos y backfills solo son seguros si las tareas son idempotentes; una tarea basada en `now` duplica o pierde datos al reintentar. Airflow y Dagster son OSS (Apache-2.0), sin licencia de pago. Conceptos DAG, `@dag`, `catchup` y `default_args`: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html (consultado 2026-11-07). Dagster: comprobar (la URL de documentación redirige a dagster.io/docs; no verificado el detalle del modelo de activos).

## Ejemplos
### Mal
```python
with DAG("sales_daily", schedule="@daily", start_date=datetime(2020, 1, 1), catchup=True) as dag:
    load = PythonOperator(task_id="load",
        python_callable=lambda: load_rows(date.today()))   # now(), no idempotente
```
### Bien
```python
@dag(schedule="@daily", start_date=datetime(2026, 1, 1), catchup=False,
     default_args={"retries": 3, "retry_delay": timedelta(minutes=5)})
def sales_daily():
    @task(execution_timeout=timedelta(hours=1))
    def load(data_interval_start=None):
        day = data_interval_start.date()
        overwrite_partition("lake.sales", day, extract(day))  # misma entrada, mismo resultado
    load()
sales_daily()
```
Comprobar la firma de contexto (`data_interval_start`) en la versión de Airflow usada (comprobar al fijar la versión).

## Checklist de revisión
- [ ] Cada tarea es idempotente y recibe el intervalo, no la hora actual.
- [ ] `catchup=False`; backfill documentado con rango.
- [ ] Reintentos, timeout y alerta definidos.
- [ ] Secretos desde backend, nada en el repo.
- [ ] Sin lógica SQL pesada ni XCom voluminoso.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep: `catchup=True` | 1 | `policies/semgrep/airflow-catchup-true.yaml` |
| Detección de secretos en repo | 1 | hook de seguridad de la fábrica (`.claude/hooks/`) |
| Test de idempotencia (ejecutar dos veces y comparar) | 1 | pendiente (proyecto generado) |
| Revisión de DAG nuevo | 3 | revisión humana |

En local se reproduce con Airflow/Dagster en contenedores. No se reproduce MWAA ni su integración IAM; preparado para AWS, no verificado en real.

## Relacionados, fuentes y mantenimiento
- Relacionados: `etl-vs-elt-and-dbt`, `data-quality`, `data-platform-cost`, `cdc-and-streaming`.
- Fuentes: documentación Apache Airflow (URL arriba, 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
