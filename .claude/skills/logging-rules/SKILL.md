---
name: logging-rules
description: Usar al añadir o revisar logs en Java con SLF4J; define niveles, formato estructurado, correlación y qué nunca debe registrarse.
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Reglas de logging

## Cuándo aplicar y cuándo no
- Aplica a cualquier `log.*` en código de producción y a la configuración del backend de logs.
- No aplica a salida de herramientas CLI cuyo contrato es stdout, ni a métricas/trazas (ver observabilidad).

## Reglas
- **MUST** usar la fachada SLF4J con un logger `private static final` por clase; **MUST NOT** usar `System.out/err` ni `printStackTrace()`.
- **MUST** usar placeholders (`log.info("order {} paid", id)`), nunca concatenación.
- **MUST** pasar la excepción como último argumento (`log.error("charge failed for order {}", id, e)`) para conservar la traza.
- **MUST NOT** registrar secretos, tokens, contraseñas, números de tarjeta, ni datos personales sin enmascarar.
- **MUST NOT** registrar cuerpos completos de petición/respuesta por defecto.
- **MUST** respetar los niveles: ERROR = requiere acción; WARN = anómalo pero recuperado; INFO = hitos de negocio; DEBUG/TRACE = diagnóstico, apagado por defecto.
- **MUST NOT** registrar y relanzar la misma excepción (ver `exceptions-and-error-handling`).
- **SHOULD** emitir logs estructurados (JSON) con `traceId` y `spanId` vía MDC; limpiar el MDC al terminar la tarea.
- **SHOULD** proteger logs costosos de construir con `log.isDebugEnabled()` o suplier lambda.
- **MUST NOT** registrar dentro de bucles calientes sin muestreo.

## Por qué
Los logs son un canal de fuga habitual de datos personales y credenciales y su retención suele ser larga. La concatenación evalúa el mensaje aunque el nivel esté desactivado. Sin identificador de correlación, seguir una petición entre servicios es inviable. Requisitos de privacidad/normativa: borrador por confirmar con fuente oficial.

## Ejemplos
### Mal
```java
System.out.println("Processing " + order);
try { pay(order); }
catch (Exception e) {
    log.error("Error: " + e.getMessage());   // sin traza
    e.printStackTrace();
}
log.info("login user=" + user + " password=" + password);
```
### Bien
```java
private static final Logger log = LoggerFactory.getLogger(PaymentService.class);

log.info("processing order {}", order.id());
try {
    pay(order);
} catch (GatewayException e) {
    log.error("payment failed for order {}", order.id(), e);
    throw new PaymentFailedException(order.id(), e);
}
log.info("login succeeded for user {}", user.id());
```

## Checklist de revisión
- [ ] Sin `System.out`, `printStackTrace` ni concatenación en logs.
- [ ] Excepciones pasadas como último argumento y registradas una sola vez.
- [ ] Sin secretos ni datos personales; niveles correctos.
- [ ] Logs con `traceId` en MDC.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Reglas Semgrep: `printStackTrace`, `System.out/err`, concatenación en log | 1 | `policies/semgrep/java-logging.yaml` |
| Hook de bloqueo de secretos en edición de ficheros | 2 | `.claude/hooks/pre-tool-use/block_secrets.py` |
| Revisión de datos personales en logs | 3 | agente `code-reviewer` (pendiente de definir) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `exceptions-and-error-handling`, `no-lombok`, `equals-hashcode-tostring`, `data-privacy-in-db`.
- Fuentes: documentación de SLF4J (slf4j.org, API de logging parametrizado) — no verificado en línea.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
