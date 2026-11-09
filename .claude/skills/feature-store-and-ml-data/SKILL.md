---
name: feature-store-and-ml-data
description: "Usar al preparar datos de entrenamiento y features para ML: feature store, joins point-in-time, consistencia offline/online, versionado de datasets y datos personales."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Feature store y datos para ML

## Cuándo aplicar y cuándo no
- Aplica cuando varios modelos reutilizan features, o cuando hay serving online de features además de entrenamiento batch.
- No aplica a un único modelo con features calculadas en la propia petición; ahí un feature store añade coste sin valor (ver `classical-mlops`).

## Reglas
- **MUST** construir los conjuntos de entrenamiento con joins point-in-time (solo valores conocidos en el instante del evento) para evitar fuga de datos del futuro.
- **MUST** definir cada feature una vez (código versionado) y usar la misma definición para offline y online, evitando training-serving skew.
- **MUST** versionar datasets de entrenamiento (snapshot/tag de tabla + hash de código + parámetros) para reproducir un modelo.
- **MUST** aplicar la clasificación del dato: features derivadas de `pii` heredan la etiqueta y las reglas de RGPD (supresión, finalidad).
- **MUST NOT** usar como feature atributos protegidos o proxies sin evaluación de sesgo y base legal.
- **MUST NOT** hacer doble escritura a store online y a la BD transaccional como fuente de verdad; el online se materializa desde el offline.
- **SHOULD** usar Feast (OSS, https://docs.feast.dev/, consultada 2026-11-07) u otra solución OSS; no adoptar productos gestionados de pago por defecto (D16).
- **SHOULD** fijar TTL y frescura esperada por feature y monitorizarlas.

## Por qué
La fuga temporal produce modelos excelentes en validación y malos en producción. Feast documenta los joins point-in-time y la separación offline (entrenamiento) / online (baja latencia). Versión y soporte de stores concretos. En local se usan stores de ejemplo (fichero/SQLite/Redis); no se reproduce DynamoDB ni servicios gestionados de AWS: preparado para AWS, no verificado en real.

## Ejemplos
### Mal
```python
# toma el estado ACTUAL del cliente para eventos pasados
df = events.merge(customers_current, on="customer_id")
```
### Bien
```python
# definición única (Feast)
from feast import FeatureView, Field, Entity
from feast.types import Float32

customer = Entity(name="customer", join_keys=["customer_id"])
orders_30d = FeatureView(
    name="customer_orders_30d",
    entities=[customer],
    ttl=timedelta(days=1),
    schema=[Field(name="orders_30d", dtype=Float32)],
    source=orders_source,
)
# entrenamiento: get_historical_features(entity_df con event_timestamp, ...)
```

## Checklist de revisión
- [ ] Entrenamiento usa joins point-in-time.
- [ ] Una definición por feature para offline y online.
- [ ] Dataset de entrenamiento versionado y reproducible.
- [ ] Features con PII heredan clasificación y supresión.
- [ ] Evaluación de sesgo registrada.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test de no-fuga: ninguna fila de entrenamiento usa valores posteriores a su `event_timestamp` | 1 | pendiente, proyecto generado |
| Revisión de definiciones de features y de datos personales | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `classical-mlops`, `gdpr-in-the-lake`, `data-quality`, `data-contracts-and-lineage`.
- Fuentes: documentación de Feast (URL arriba). API concreta.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
