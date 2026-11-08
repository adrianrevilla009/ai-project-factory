---
name: schema-registry-and-evolution
description: Usar al definir o cambiar esquemas de eventos (Avro/Protobuf/JSON Schema) y modos de compatibilidad en un schema registry.
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Schema registry y evolución de esquemas

## Cuándo aplicar y cuándo no
- Aplica a eventos que viajan por Kafka (u otro bus) con esquema Avro, Protobuf o JSON Schema.
- No aplica a APIs REST (ver `api-versioning-deprecation`) ni a eventos intra-proceso que no cruzan el límite del servicio.

## Reglas
- **MUST** registrar todo esquema de evento en un registry; **MUST NOT** publicar JSON libre sin esquema en topics compartidos.
- **MUST** fijar la compatibilidad del subject en `BACKWARD_TRANSITIVE` o `FULL_TRANSITIVE` como mínimo para topics con consumidores de terceros.
- **MUST** comprobar compatibilidad en CI antes de fusionar un cambio de esquema.
- **MUST** añadir campos nuevos como opcionales con valor por defecto; **MUST NOT** borrar ni renombrar campos usados, ni cambiar su tipo.
- **MUST NOT** reutilizar un número de campo Protobuf eliminado (usar `reserved`).
- **MUST** desactivar el registro automático de esquemas en producción (`auto.register.schemas=false`); los esquemas se publican desde CI.
- **SHOULD** una estrategia de subject coherente (`TopicNameStrategy` por defecto) y un solo tipo de evento por topic salvo decisión explícita.
- **SHOULD** romper con un topic nuevo versionado (`orders.v2`) cuando el cambio es incompatible, con doble publicación temporal.
- **SHOULD** preferir un registry con licencia OSS (p. ej. Apicurio Registry); la licencia de Confluent Schema Registry no es OSS permisiva (D16): TODO-VERIFY licencia vigente antes de adoptarlo.

## Por qué
Productores y consumidores se despliegan en momentos distintos: el esquema es el contrato. Una compatibilidad no transitiva permite romper consumidores que aún leen versiones antiguas. El registro automático desde la aplicación deja que un despliegue erróneo cambie el contrato sin revisión. Modos de compatibilidad y propiedades deben contrastarse con la documentación del registry elegido (TODO-VERIFY).

## Ejemplos
### Mal
```json
{"type":"record","name":"OrderCreated","fields":[
  {"name":"id","type":"string"},
  {"name":"total","type":"string"}   // antes era "double": cambio de tipo
]}
```
### Bien (campo nuevo opcional con default)
```json
{"type":"record","name":"OrderCreated","namespace":"com.example.orders","fields":[
  {"name":"id","type":"string"},
  {"name":"total","type":"double"},
  {"name":"currency","type":["null","string"],"default":null}
]}
```
```properties
# serializador del productor: el esquema lo publica CI, no la aplicación
auto.register.schemas=false
use.latest.version=false
```
```protobuf
message OrderCreated {
  reserved 3;            // campo "discount" eliminado
  reserved "discount";
  string id = 1;
  double total = 2;
  string currency = 4;
}
```

## Checklist de revisión
- [ ] El esquema está en el registry y en el repo (`schemas/`).
- [ ] Compatibilidad transitiva configurada; chequeo en CI.
- [ ] Campos nuevos opcionales con default; nada borrado/renombrado.
- [ ] `auto.register.schemas=false` fuera de desarrollo.
- [ ] Cambios incompatibles = topic/versión nueva con plan de migración.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Chequeo de compatibilidad en CI contra el registry | 1 | pipeline del proyecto generado (pendiente) |
| Revisión de cambios en `schemas/` | 3 | agente `code-reviewer` |

> Estado: sin artefacto en este repositorio todavía (pendiente). Revisión humana del cambio de contrato.

## Relacionados, fuentes y mantenimiento
- Relacionados: `asyncapi-event-contracts`, `backward-compatibility-rules`, `kafka-producers-consumers`.
- Fuentes: documentación de Apicurio Registry y de Confluent Schema Registry (compatibilidad), Avro y Protobuf (reglas de evolución) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
