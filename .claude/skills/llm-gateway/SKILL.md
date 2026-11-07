---
name: llm-gateway
description: "Usar al decidir cómo acceden los servicios a proveedores LLM: pasarela central vs cliente directo, enrutado de modelos, claves, cuotas, caché, fallback y auditoría."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Pasarela de LLM (LLM gateway)

## Cuándo aplicar y cuándo no
- Aplica cuando varios servicios o equipos consumen LLMs, o cuando se necesita control de coste, claves y datos enviados.
- No aplica a un único servicio piloto: basta un cliente con timeouts tras un puerto propio (ver `spring-ai-and-langchain4j`); documentar el umbral para migrar.

## Reglas
- **MUST** centralizar el acceso a proveedores en un único punto (pasarela propia o producto open source) cuando haya más de un consumidor; los servicios no guardan claves de proveedor.
- **MUST** autenticar a cada consumidor (identidad de servicio vía Keycloak/OIDC) y atribuir cada llamada a servicio, equipo y entorno.
- **MUST** aplicar cuotas y límites de tasa por consumidor y tope de tokens por petición (ver `rate-limiting-quotas`, `token-and-cost-budgets` pendiente).
- **MUST** registrar metadatos de cada llamada (modelo, tokens, latencia, coste, versión de prompt, resultado); el contenido completo solo con redacción de PII y retención definida (ver `llm-observability`).
- **MUST** definir una lista de modelos permitidos por entorno y clasificación de datos; datos restringidos solo a proveedores aprobados.
- **SHOULD** soportar fallback entre modelos/proveedores con las mismas garantías de datos, circuit breaker y timeouts (ver `resilience`).
- **SHOULD** cachear solo respuestas deterministas y sin datos personales, con clave que incluya tenant, prompt@versión y modelo.
- **MUST NOT** crear una pasarela propia si un producto con licencia permisiva cubre el caso; evaluar antes y registrar la decisión. Sin licencias de pago por defecto (D16).
- **MUST** ejecutar las comprobaciones de guardarraíles (PII, inyección) en la pasarela o justo antes de ella (ver `guardrails-and-pii-redaction`).
- **MUST NOT** afirmar que una integración con un servicio gestionado de AWS está verificada; solo "preparado para AWS, no verificado en real". En local se usa un modelo local (por ejemplo Ollama) y NO se reproducen cuotas, IAM ni guardarraíles gestionados del proveedor.

## Por qué
Sin punto central, las claves se dispersan, el coste es opaco, no hay forma de cortar un consumidor desbocado y cada equipo reinventa reintentos y redacción de PII. La pasarela añade un salto y un punto único de fallo: debe ser simple, redundante y observable.

## Ejemplos
### Mal
```java
// cada servicio con su clave y URL del proveedor
var model = OpenAiChatModel.builder().apiKey("sk-example-hardcoded").baseUrl("https://api.openai.com").build();
```
### Bien
```yaml
spring:
  ai:
    openai:
      base-url: https://llm-gateway.example.internal   # única URL permitida
      api-key: ${LLM_GATEWAY_TOKEN}                   # token de servicio, no clave del proveedor
```
```yaml
# política de la pasarela (ilustrativa, formato depende del producto elegido)
consumers:
  claims-service:
    allowed_models: [general-small, general-large]
    max_tokens_per_request: 4000
    rate_limit_per_minute: 120
    data_classification_max: internal
```
Los nombres de propiedades de Spring AI son TODO-VERIFY por proveedor y versión.

## Checklist de revisión
- [ ] Un único punto de salida a proveedores; sin claves de proveedor en servicios.
- [ ] Identidad, cuotas y atribución de coste por consumidor.
- [ ] Modelos permitidos según clasificación de datos.
- [ ] Logs con metadatos y PII redactada.
- [ ] Fallback y timeouts definidos; decisión build/buy documentada.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: URL de proveedor LLM directa en código principal | 1 | `policies/semgrep/llm-direct-provider-url.yaml` |
| Regla Semgrep de secretos literales | 1 | `policies/semgrep/config-literal-secret-in-properties.yaml` |
| Revisión de la decisión de pasarela | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `llm-observability`, `llm-security`, `rate-limiting-quotas`, `resilience`, `secrets-management`, `model-risk-and-ai-act-mapping`.
- Fuentes: documentación del producto de pasarela elegido — TODO-VERIFY; sin fuente oficial única.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
