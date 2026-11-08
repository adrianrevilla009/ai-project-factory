---
name: http-clients-and-timeouts
description: Usar al crear o revisar llamadas HTTP salientes desde Spring (RestClient, WebClient, clientes declarativos) para fijar timeouts, pool y propagación de contexto.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Clientes HTTP y timeouts

## Cuándo aplicar y cuándo no
- Aplica a cualquier llamada HTTP saliente a otro servicio, API de terceros o servicio cloud vía HTTP.
- No aplica a mensajería (Kafka, SQS: ver bloque 06) ni a acceso a base de datos (pool JDBC, bloque 03).

## Reglas
- **MUST** definir timeout de conexión y de lectura explícitos en todo cliente; el valor por defecto del JDK/librería puede ser infinito o muy alto.
- **MUST** construir los clientes desde el builder inyectado (`RestClient.Builder`, `WebClient.Builder`) para heredar observabilidad y codecs de Spring Boot.
- **MUST NOT** hacer `new RestTemplate()` ni `HttpClient.newHttpClient()` sueltos en código de negocio.
- **MUST** externalizar URL base y timeouts en `@ConfigurationProperties` (ver `configuration-properties`), un bloque por dependencia.
- **MUST** que el timeout total de la petición entrante sea mayor que la suma de timeouts salientes encadenados (presupuesto de latencia).
- **SHOULD** preferir `RestClient` (Spring Framework 6.1+) en código bloqueante y `WebClient` solo en stacks reactivos.
- **SHOULD** reintentar solo operaciones idempotentes y combinarlo con `resilience`.
- **MUST NOT** registrar cuerpos, cabeceras `Authorization` ni tokens en logs de cliente.

## Por qué
Sin timeout, un proveedor lento agota los hilos del servicio llamante y la caída se propaga en cascada. Un timeout explícito convierte un fallo de otro en un error rápido y manejable. Las propiedades genéricas `spring.http.client.*` dependen de la versión de Spring Boot (TODO-VERIFY versión mínima); la configuración por código es estable.

## Ejemplos
### Mal
```java
@Service
class PaymentGateway {
    private final RestTemplate http = new RestTemplate(); // sin timeouts, sin observabilidad

    PaymentResult charge(ChargeRequest req) {
        return http.postForObject("https://payments.example.com/charge", req, PaymentResult.class);
    }
}
```
### Bien
```java
@ConfigurationProperties("clients.payments")
record PaymentsClientProperties(URI baseUrl, Duration connectTimeout, Duration readTimeout) {}

@Configuration
class PaymentsClientConfig {
    @Bean
    RestClient paymentsRestClient(RestClient.Builder builder, PaymentsClientProperties p) {
        var factory = new JdkClientHttpRequestFactory(
            HttpClient.newBuilder().connectTimeout(p.connectTimeout()).build());
        factory.setReadTimeout(p.readTimeout());
        return builder.baseUrl(p.baseUrl().toString()).requestFactory(factory).build();
    }
}
```
```yaml
clients:
  payments:
    base-url: https://payments.example.com
    connect-timeout: 500ms
    read-timeout: 2s
```

## Checklist de revisión
- [ ] Cada cliente tiene connect y read timeout configurables.
- [ ] No hay `new RestTemplate()` ni clientes JDK sin configurar.
- [ ] Reintentos solo en operaciones idempotentes.
- [ ] No se loguean credenciales ni cuerpos sensibles.
- [ ] Los timeouts encadenados caben en el presupuesto de la petición entrante.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `new RestTemplate()` / `HttpClient.newHttpClient()` | 1 | `policies/semgrep/spring-http-client-without-timeout.yaml` |
| Test de configuración que verifica timeouts en properties | 1 | tests del proyecto generado (pendiente) |
| Revisión de clientes nuevos | 3 | agente `code-reviewer` |

> Estado: reglas probadas con `semgrep --test` (casos en `tests/semgrep/`); detectan patrones sintácticos, no flujos de datos.

## Relacionados, fuentes y mantenimiento
- Relacionados: `resilience`, `configuration-properties`, `graceful-shutdown-lifecycle`, `reactive-vs-blocking`.
- Fuentes: Spring Framework Reference (REST Clients) y Spring Boot Reference (HTTP clients) — TODO-VERIFY URL y versión, consulta 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
