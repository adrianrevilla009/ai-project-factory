---
name: api-versioning-deprecation
description: Usar al decidir cómo versionar una API pública o interna y al deprecar y retirar versiones u operaciones.
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Versionado y deprecación de APIs

## Cuándo aplicar y cuándo no
- Aplica cuando un cambio rompe (o puede romper) a algún consumidor, o al retirar operaciones.
- No aplica a cambios compatibles (campos opcionales nuevos): ver `backward-compatibility-rules`.

## Reglas
- **MUST** usar versión mayor en la ruta para APIs REST (`/v1/orders`); minor/patch solo en `info.version` del contrato.
- **MUST** preferir evolución compatible dentro de la misma versión mayor; una versión nueva solo para cambios rompientes inevitables.
- **MUST** mantener como máximo dos versiones mayores vivas por API.
- **MUST** anunciar la deprecación con antelación mínima acordada (por defecto 6 meses) y marcar `deprecated: true` en OpenAPI.
- **MUST** emitir cabeceras `Deprecation` (RFC 9745) y `Sunset` (RFC 8594) en respuestas de recursos deprecados, con enlace `Link: rel="deprecation"` a la guía de migración.
- **MUST** medir el uso por versión y consumidor (métrica con etiqueta `api_version`) antes de retirar.
- **MUST NOT** retirar una versión con tráfico de consumidores conocidos sin acuerdo explícito.
- **SHOULD** no versionar por cabecera o parámetro salvo requisito de gateway justificado en ADR.

## Por qué
La versión en ruta es visible en logs, métricas, gateways y caches; permite enrutar y retirar con datos. Limitar versiones vivas acota el coste de mantenimiento.

## Ejemplos
### Mal
```java
@GetMapping("/orders")           // cambia el formato de 'total' sin avisar
OrderResponse get() { ... }
```
### Bien
```java
@RestController
@RequestMapping("/v1/orders")
class OrdersV1Controller {
    @GetMapping("/{id}")
    ResponseEntity<OrderV1> get(@PathVariable UUID id) {
        return ResponseEntity.ok()
            .header("Deprecation", "@1767225600")   // fecha en epoch seg., formato RFC 9745
            .header("Sunset", "Wed, 01 Jul 2027 00:00:00 GMT")
            .header("Link", "<https://docs.example.com/migrate-v2>; rel=\"deprecation\"")
            .body(service.getV1(id));
    }
}
```
Los valores de fecha son ilustrativos; confirmar sintaxis de `Deprecation` contra RFC 9745.

## Checklist de revisión
- [ ] Versión mayor en ruta; sin versión por defecto implícita.
- [ ] Cambio rompiente justificado; no cabía de forma compatible.
- [ ] `deprecated: true` + cabeceras + guía de migración.
- [ ] Métrica de uso por versión disponible.
- [ ] Fecha de retirada comunicada a consumidores.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Diff de compatibilidad OpenAPI en CI | 1 | pendiente (ver `backward-compatibility-rules`) |
| Aprobación humana de la fecha de retirada | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `backward-compatibility-rules`, `openapi-contract-first`, `rest-design-guidelines`, `sdk-generation`.
- Fuentes: RFC 8594 (Sunset), RFC 9745 (Deprecation HTTP header).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
