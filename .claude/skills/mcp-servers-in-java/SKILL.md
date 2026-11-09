---
name: mcp-servers-in-java
description: "Usar al exponer capacidades propias como servidor MCP (Model Context Protocol) en Java/Spring Boot: transporte, autenticación, herramientas mínimas y seguridad."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Servidores MCP en Java

## Cuándo aplicar y cuándo no
- Aplica al publicar herramientas, recursos o prompts de un servicio para clientes MCP (asistentes, IDEs, otros agentes).
- No aplica si solo un servicio propio llama a sus propias funciones (usar tool calling directo, ver `agents-and-tool-calling`).

## Reglas
- **MUST** elegir transporte según uso: stdio para herramientas locales de un solo usuario; HTTP (Streamable-HTTP o stateless) para servicios compartidos.
- **MUST** autenticar y autorizar todo servidor HTTP: la documentación de Spring AI avisa de que los servidores HTTP exponen un endpoint sin autenticar por defecto. Usar Spring Security con Keycloak (OIDC) y propagar la identidad al ejecutar la tool.
- **MUST NOT** exponer el servidor fuera de localhost sin autenticación, TLS y límites de tasa (ver `rate-limiting-quotas`).
- **MUST** exponer pocas tools de granularidad de caso de uso, con descripciones precisas y esquema de parámetros tipado; las de escritura separadas y con confirmación.
- **MUST** validar cada parámetro como entrada no confiable y autorizar por usuario, no por el cliente MCP.
- **MUST** tratar las descripciones de tools y los resultados como superficie de inyección: no incluir texto de terceros sin sanear en descripciones.
- **SHOULD** usar la autoconfiguración Spring AI (`spring-ai-starter-mcp-server-webmvc` o `-webflux`) con `@McpTool`/`@McpToolParam`, y fijar la versión del BOM.
- **SHOULD** versionar el contrato de tools (nombre y parámetros) y deprecar antes de retirar.
- **MUST** registrar cada invocación con usuario, tool y traza; sin PII en claro (ver `guardrails-and-pii-redaction`).
- **MUST** al consumir servidores MCP de terceros: lista de permitidos, revisión de sus tools y sin confianza implícita (ver `supply-chain`).

## Por qué
MCP convierte tu servicio en una superficie de ataque para agentes: cualquier cliente conectado puede invocar tools. Sin identidad por usuario, el servidor se convierte en un confused deputy con permisos amplios.

## Ejemplos
### Mal
```properties
spring.ai.mcp.server.protocol=STREAMABLE
# sin Spring Security: cualquiera con acceso de red invoca las tools
```
```java
@McpTool(name = "run_query", description = "Ejecuta SQL")
public String runQuery(String sql) { return jdbc.queryForList(sql).toString(); }
```
### Bien
```properties
spring.ai.mcp.server.type=SYNC
spring.ai.mcp.server.protocol=STREAMABLE
spring.security.oauth2.resourceserver.jwt.issuer-uri=https://idp.example.internal/realms/example
```
```java
@Component
class OrderMcpTools {
    private final OrderQueries queries;

    @McpTool(name = "get_order_status", description = "Estado de un pedido del usuario autenticado")
    public OrderStatus getOrderStatus(
            @McpToolParam(description = "Identificador del pedido", required = true) String orderId) {
        return queries.statusFor(CurrentUser.fromSecurityContext(), OrderId.parse(orderId));
    }
}
```
Anotaciones y propiedades comprobadas en la documentación de Spring AI el 2026-11-07; cabeceras de autenticación exactas del transporte. En local se prueba con Keycloak (ADR de identidad); no se reproduce ninguna integración AWS.

## Criterios de decisión y trampas
### Cómo decidir
- Construye un servidor MCP cuando varios agentes necesitan acceder a una capacidad con permisos controlados; expón pocas herramientas y bien definidas.
- Autenticación y autorización como en cualquier API.
### Trampas frecuentes
- Exponer toda tu API como herramientas.
- Sin autenticación o con permisos amplios.
- Herramientas con efectos sin confirmación.
- Descripciones ambiguas que confunden al modelo.
- Sin límites de uso ni registro.
### Evidencia
- Cada herramienta tiene su permiso, su esquema de entrada validado y pruebas de abuso.

## Checklist de revisión
- [ ] Transporte adecuado; HTTP con OIDC y TLS.
- [ ] Tools mínimas, tipadas, autorizadas por usuario.
- [ ] Parámetros validados; sin SQL libre ni shell.
- [ ] Invocaciones auditadas sin PII.
- [ ] Servidores de terceros en lista de permitidos.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep existente de seguridad Spring (endpoints sin autenticar) | 1 | `policies/semgrep/spring-security-misconfig.yaml` |
| Test: llamada sin token a un servidor HTTP devuelve 401 | 1 | tests del proyecto generado |
| Regla específica `@McpTool` con SQL libre | - | pendiente |

## Relacionados, fuentes y mantenimiento
- Relacionados: `agents-and-tool-calling`, `llm-security`, `prompt-injection-defense-for-agents`, `owasp-top10-and-api-top10`, `rate-limiting-quotas`.
- Fuentes: Spring AI Reference, MCP Server Boot Starter (docs.spring.io/spring-ai/reference/api/mcp/mcp-server-boot-starter-docs.html, 2026-11-07); especificación MCP (modelcontextprotocol.io).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
