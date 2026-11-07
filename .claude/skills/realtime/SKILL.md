---
name: realtime
description: "Usar al añadir actualizaciones en tiempo real a la SPA con SSE o WebSocket: elección, autenticación, reconexión, integración con TanStack Query y límites."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Tiempo real en la UI (SSE y WebSocket)

## Cuándo aplicar y cuándo no
- Aplica a notificaciones, estados de proceso, tableros vivos y chats.
- No aplica si basta con polling razonable o con refetch al recuperar foco (primera opción, más simple). Los eventos de dominio en backend: `event-driven`, `notifications`.

## Reglas
- **MUST** elegir SSE si el flujo es solo servidor -> cliente (reconexión automática y `Last-Event-ID` integrados); WebSocket solo si hay mensajería bidireccional de baja latencia.
- **MUST** autenticar con la sesión por cookie HttpOnly (patrón BFF, `auth-and-session`) o con un ticket de un solo uso y vida corta; el navegador no permite cabeceras personalizadas en `EventSource` ni en `new WebSocket`.
- **MUST NOT** poner tokens de larga vida en la URL (acaban en logs y proxies); **MUST** validar `Origin` en el servidor WebSocket.
- **MUST** reconectar con backoff exponencial y jitter, reanudar desde el último evento (id) y tolerar duplicados (`idempotency-and-deduplication`).
- **MUST** tratar los mensajes como invalidaciones o deltas sobre la caché de servidor: `queryClient.invalidateQueries` o `setQueryData`, no un segundo almacén de estado paralelo.
- **MUST** cerrar la conexión al desmontar, al cerrar sesión y en pestañas ocultas si no es necesaria; una sola conexión compartida por app, no una por componente.
- **MUST** validar el esquema de cada mensaje (Zod) antes de usarlo; ignorar tipos desconocidos (compatibilidad hacia delante).
- **SHOULD** usar latidos (heartbeat) menores que el timeout de inactividad de balanceadores y proxies (en ALB el valor por defecto es 60 s; TODO-VERIFY) y comprobar el comportamiento del CDN con respuestas en streaming.
- **SHOULD** tener degradación: si falla el canal, volver a polling y mostrar estado "sin conexión".
- Sobre HTTP/1.1 los navegadores limitan conexiones por dominio (alrededor de 6); con HTTP/2 se relaja (TODO-VERIFY).

## Por qué
Una conexión viva multiplica el coste de infraestructura y los casos de fallo (redes móviles, proxys, expiración de sesión). Tratar los eventos como invalidación de caché mantiene una única fuente de verdad y simplifica la reconexión.

## Ejemplos
### Mal
```ts
const ws = new WebSocket(`wss://api.example.com/live?token=${accessToken}`); // token en la URL
ws.onmessage = (e) => setOrders(JSON.parse(e.data)); // sin validar, sin reconexion
```
### Bien
```ts
const es = new EventSource("/api/orders/stream", { withCredentials: true }); // cookie de sesion via BFF
const Event = z.object({ type: z.string(), orderId: z.string() });

es.addEventListener("order-updated", (e) => {
  const msg = Event.safeParse(JSON.parse((e as MessageEvent).data));
  if (msg.success) queryClient.invalidateQueries({ queryKey: ["orders", msg.data.orderId] });
});
// EventSource reconecta solo y reenvia Last-Event-ID; el servidor reanuda desde ese id.
```

## Checklist de revisión
- [ ] Justificado frente a polling; SSE salvo necesidad bidireccional.
- [ ] Autenticación por cookie o ticket; sin token en URL; `Origin` validado.
- [ ] Reconexión con backoff, reanudación y tolerancia a duplicados.
- [ ] Mensajes validados y aplicados a la caché de TanStack Query.
- [ ] Una conexión por app, cerrada al salir.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: token en URL de WebSocket/EventSource | 1 | `policies/semgrep/frontend-realtime-token-in-url.yaml` (sin ejecutar en la fábrica) |
| Test de reconexión con servidor simulado | 2 | tests del proyecto generado (pendiente) |
| Revisión de límites de timeout en LB/CDN | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `state-management`, `auth-and-session`, `security-frontend`, `notifications`, `idempotency-and-deduplication`, `alb-nlb-and-tls-termination`.
- Fuentes: MDN (Server-sent events, WebSocket API) y RFC 6455 — TODO-VERIFY URLs; no consultadas 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
