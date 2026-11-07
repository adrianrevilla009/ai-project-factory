---
name: grpc-protobuf
description: Usar al definir o cambiar servicios gRPC y mensajes Protobuf (diseño de .proto, números de campo, errores, deadlines).
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# gRPC y Protobuf

## Cuándo aplicar y cuándo no
- Aplica a comunicación interna servicio-a-servicio de baja latencia o con streaming, y a esquemas Protobuf compartidos.
- No aplica a APIs públicas para navegadores (preferir REST, `rest-design-guidelines`) salvo gateway gRPC-web justificado.

## Reglas
- **MUST** nombrar paquetes con versión: `package orders.v1;` y ubicar los `.proto` en un directorio propio (`src/main/proto/orders/v1/`).
- **MUST NOT** reutilizar ni cambiar el número ni el tipo de un campo; al borrar, `reserved` número y nombre.
- **MUST** añadir enums con valor 0 `*_UNSPECIFIED`; **MUST NOT** cambiar semántica de valores existentes.
- **MUST** usar mensajes de request/response propios por RPC (`GetOrderRequest`), nunca tipos primitivos o compartidos entre RPC.
- **MUST** fijar deadline en cada llamada cliente y propagarlo; **MUST NOT** llamadas sin deadline.
- **MUST** devolver errores con códigos `Status` correctos (`NOT_FOUND`, `INVALID_ARGUMENT`, `FAILED_PRECONDITION`...), no `UNKNOWN` ni `INTERNAL` por defecto.
- **MUST** ejecutar `buf lint` y `buf breaking` contra la rama principal en CI.
- **SHOULD** usar `google.protobuf.Timestamp` y wrappers/`optional` para presencia explícita.
- **SHOULD** reintentar solo operaciones idempotentes mediante service config, con backoff.

## Por qué
Protobuf es compatible hacia atrás por números de campo: reutilizarlos corrompe datos silenciosamente. Los deadlines evitan que un servicio lento acumule hilos y arrastre a toda la cadena.

## Ejemplos
### Mal
```proto
message Order {
  string id = 1;
  int32 total = 2;      // luego se cambia a string total = 2; rompe a los clientes
  string status = 3;
}
```
### Bien
```proto
syntax = "proto3";
package orders.v1;

message Order {
  reserved 4;
  reserved "legacy_note";
  string id = 1;
  Money total = 2;
  OrderStatus status = 3;
}
enum OrderStatus { ORDER_STATUS_UNSPECIFIED = 0; ORDER_STATUS_PAID = 1; }
message GetOrderRequest { string id = 1; }
service OrderService { rpc GetOrder(GetOrderRequest) returns (Order); }
```
```java
OrderServiceGrpc.OrderServiceBlockingStub stub =
    OrderServiceGrpc.newBlockingStub(channel).withDeadlineAfter(2, TimeUnit.SECONDS);
```

## Checklist de revisión
- [ ] Paquete versionado; sin números de campo reutilizados (`reserved`).
- [ ] Enums con `_UNSPECIFIED = 0`.
- [ ] Request/response dedicados por RPC.
- [ ] Deadline en cada cliente; códigos de estado correctos.
- [ ] `buf lint` y `buf breaking` en verde.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| `buf lint` + `buf breaking` en CI (configuración `buf.yaml` del proyecto generado) | 1 | pendiente: plantilla de pipeline; la fábrica no la contiene (ADR-0038) |
| Revisión de `.proto` | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `backward-compatibility-rules`, `schema-registry-and-evolution`, `sdk-generation`, `contract-testing-pact`.
- Fuentes: protobuf.dev (guía de estilo y de actualización de mensajes), grpc.io (deadlines, status codes), buf.build docs — TODO-VERIFY, no consultadas en vivo el 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
