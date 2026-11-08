---
name: agents-and-tool-calling
description: "Usar al dar herramientas a un LLM o construir un agente en Java: diseño de tools, permisos mínimos, límites de bucle, idempotencia y confirmación humana de acciones."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Agentes y tool calling

## Cuándo aplicar y cuándo no
- Aplica cuando el LLM decide qué función invocar (Spring AI `@Tool`, LangChain4j `@Tool`) o encadena pasos.
- No aplica a flujos deterministas donde el código decide los pasos: usar un workflow normal y llamar al LLM solo en pasos concretos.

## Reglas
- **MUST** preferir workflow determinista antes que agente; un agente solo si el camino no se puede fijar de antemano.
- **MUST** dar a cada tool el mínimo permiso: operaciones de lectura por defecto; las de escritura en tools separadas.
- **MUST** ejecutar las tools con la identidad y permisos del usuario final, nunca con una cuenta de servicio amplia.
- **MUST** validar los argumentos que propone el modelo como entrada no confiable (tipos, rangos, listas permitidas), igual que en un endpoint REST.
- **MUST** exigir confirmación humana para acciones irreversibles o con efecto externo (pagos, borrados, envíos); ver `human-in-the-loop` (pendiente).
- **MUST** acotar el bucle: máximo de iteraciones, de tool calls, de tokens y de tiempo total; al agotarse, parar con error controlado.
- **MUST** hacer las tools de escritura idempotentes (clave de idempotencia) porque el modelo puede repetir llamadas.
- **SHOULD** describir cada tool con nombre verbal claro, descripción breve y parámetros tipados; pocas tools (decenas hacen que el modelo falle).
- **SHOULD** devolver a la tool resultados mínimos y sin datos que el usuario no deba ver; truncar salidas largas.
- **MUST** registrar cada llamada (tool, argumentos con PII redactada, resultado, usuario, traza); ver `llm-observability`.
- **MUST NOT** permitir que el texto de un resultado de tool (web, documento, email) cambie permisos o dispare tools de escritura sin confirmación (ver `prompt-injection-defense-for-agents`).

## Por qué
Un agente es un bucle no determinista con efectos secundarios. Los riesgos son acciones indebidas por inyección indirecta, costes sin límite y duplicados por reintentos; todos se controlan con límites, permisos del usuario y confirmación.

## Ejemplos
### Mal
```java
@Tool(description = "Ejecuta cualquier SQL")
String runSql(String sql) { return jdbc.queryForList(sql).toString(); } // cuenta de servicio, sin validar
```
### Bien
```java
class OrderTools {
    private final OrderQueries queries;           // lectura, con el usuario actual
    private final PendingActions pending;         // cola de acciones a confirmar

    @Tool(description = "Consulta el estado de un pedido del usuario actual por su id")
    OrderStatus getOrderStatus(String orderId) {
        var id = OrderId.parse(orderId);           // validación estricta
        return queries.statusFor(CurrentUser.get(), id);
    }

    @Tool(description = "Solicita cancelar un pedido; requiere confirmación del usuario")
    PendingAction requestCancel(String orderId, String idempotencyKey) {
        return pending.propose(CurrentUser.get(), new CancelOrder(OrderId.parse(orderId)), idempotencyKey);
    }
}

var answer = chat.prompt().user(question).tools(new OrderTools(queries, pending)).call().content();
```
El límite de iteraciones y la confirmación se implementan en el bucle del framework o en un wrapper propio: la propiedad concreta se comprueba según versión.

## Checklist de revisión
- [ ] Justificado por qué no basta un workflow.
- [ ] Tools con permisos del usuario final y argumentos validados.
- [ ] Acciones irreversibles con confirmación humana.
- [ ] Límites de iteraciones, tokens, tiempo; tools de escritura idempotentes.
- [ ] Trazas de cada tool call.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test: tool de escritura sin confirmación no ejecuta efecto | 1 | tests del proyecto generado |
| Test: el bucle se detiene al superar el máximo | 1 | tests del proyecto generado |
| Revisión del catálogo de tools y permisos | 3 | revisión humana (security-champions) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `mcp-servers-in-java`, `prompt-injection-defense-for-agents`, `llm-security`, `human-in-the-loop` (pendiente), `token-and-cost-budgets` (pendiente).
- Fuentes: Spring AI Reference, Tool Calling (docs.spring.io/spring-ai/reference/api/chatclient.html, 2026-11-07); LangChain4j AI Services (2026-11-07); OWASP Top 10 for LLM Applications (excessive agency) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
