---
name: schema-registry-and-evolution
description: Usar al definir o cambiar esquemas de eventos (Avro/Protobuf/JSON Schema) y modos de compatibilidad en un schema registry.
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
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
- **SHOULD** preferir un registry con licencia OSS (p. ej. Apicurio Registry); Confluent Schema Registry se publica bajo la Confluent Community License, salvo las librerías cliente (Apache 2.0), y no es una licencia de código abierto permisiva (D16; verificado el 2026-11-08).

## Por qué
Productores y consumidores se despliegan en momentos distintos: el esquema es el contrato. Una compatibilidad no transitiva permite romper consumidores que aún leen versiones antiguas. El registro automático desde la aplicación deja que un despliegue erróneo cambie el contrato sin revisión. Modos de compatibilidad y propiedades deben contrastarse con la documentación del registry elegido.

## Ejemplos
### Mal
```json
{"type":"record","name":"OrderCreated","fields":[
  {"name":"id","type":"string"},
  {"name":"total","type":"string"}
]}
```
El campo `total` pasa de `double` a `string`: cambio de tipo incompatible.

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

## Criterios de decisión y trampas
### Cómo decidir
- Registro de esquemas con una regla de compatibilidad explícita por tema; el productor falla si el cambio es incompatible.
- Elige la compatibilidad según quién se actualiza primero (productores o consumidores).
### Trampas frecuentes
- Compatibilidad desactivada «para ir más rápido».
- Esquemas sin documentación.
- Cambios de tipo.
- Registrar esquemas desde producción sin revisión.
- Eventos sin versión de esquema.
### Evidencia
- El pipeline del productor comprueba la compatibilidad antes de desplegar.

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
- Fuentes: documentación de Apicurio Registry y de Confluent Schema Registry (compatibilidad), Avro y Protobuf (reglas de evolución).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
