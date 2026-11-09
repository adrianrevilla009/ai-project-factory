---
name: configuration-properties
description: Usar al añadir configuración a un servicio Spring Boot; propiedades tipadas con @ConfigurationProperties, validación y sin secretos en ficheros.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Configuración tipada con @ConfigurationProperties

## Cuándo aplicar y cuándo no
- Aplica a toda propiedad propia de la aplicación (URLs, timeouts, límites, flags).
- No aplica a propiedades estándar de Spring Boot que se ajustan directamente en `application.yml`.

## Reglas
- **MUST** agrupar la configuración propia bajo un prefijo y mapearla con `@ConfigurationProperties` sobre un `record` inmutable.
- **MUST** anotar con `@Validated` y restricciones Jakarta (`@NotBlank`, `@Min`, `@NotNull`) para que el arranque falle ante configuración inválida.
- **MUST** registrar las clases con `@ConfigurationPropertiesScan` o `@EnableConfigurationProperties`.
- **MUST NOT** esparcir `@Value("${...}")` por la lógica de negocio; reservarlo para casos puntuales y triviales.
- **MUST NOT** guardar secretos en `application*.yml` ni en el repositorio; se inyectan por entorno o gestor de secretos. Los ejemplos usan valores `changeme`.
- **SHOULD** usar `Duration` y `DataSize` en vez de números sin unidad.
- **SHOULD** dar valores por defecto seguros con `@DefaultValue` y diferenciar entornos con perfiles o variables, no con ramas `if` en código.
- **SHOULD** añadir `spring-boot-configuration-processor` para metadatos de IDE.

## Por qué
La configuración tipada se valida una vez al arrancar, se documenta en un solo sitio y se prueba sin contexto. Con `@Value` dispersos, un typo se descubre en runtime y los valores sin unidad (`timeout: 30`) son ambiguos.

## Ejemplos
### Mal
```java
@Service
class PaymentClient {
    @Value("${payments.timeout}") int timeout;          // ¿segundos? ¿ms?
    @Value("${payments.api-key}") String apiKey;
}
```
### Bien
```java
@ConfigurationProperties(prefix = "payments")
@Validated
record PaymentsProperties(
        @NotBlank String baseUrl,
        @NotNull @DefaultValue("5s") Duration timeout) {}
```
```yaml
payments:
  base-url: https://payments.example.test
  timeout: 3s
# la clave llega por variable de entorno PAYMENTS_API_KEY (valor local: changeme)
```

## Checklist de revisión
- [ ] Propiedades propias en un `record` con prefijo y `@Validated`.
- [ ] Unidades explícitas (`Duration`, `DataSize`).
- [ ] Sin secretos reales en ficheros versionados.
- [ ] Sin `@Value` en lógica de negocio.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Escaneo de secretos en commits | 2 | hooks de seguridad de `.claude/hooks/` |
| Regla Semgrep contra `@Value` en servicios | 1 | pendiente (`policies/semgrep/`) |
| Revisión de propiedades nuevas | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `project-layout`, `actuator-and-health`, `http-clients-and-timeouts`, `twelve-factor`.
- Fuentes oficiales: Spring Boot Reference, "Externalized Configuration" (docs.spring.io/spring-boot).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
