---
name: spring-cloud-config-module
description: "Usar al decidir si añadir Spring Cloud Config Server (módulo opcional, D11) frente a GitOps + Vault, y al configurarlo si se adopta."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Módulo opcional: Spring Cloud Config Server

## Cuándo aplicar y cuándo no
- Aplica solo si el proyecto pide explícitamente un servidor de configuración central (ADR-0011) y la guía de decisión de abajo lo justifica.
- No aplica por defecto: el defecto es GitOps + Vault (ver `config-by-environment`).

## Reglas
- **MUST** partir de GitOps + Vault y documentar por escrito en un ADR del proyecto por qué no basta antes de añadir Config Server.
- **MUST** justificar con al menos uno de: cambio de configuración en caliente sin redespliegue (con `/actuator/refresh` o bus), muchos servicios no Kubernetes, o equipos que ya operan Config Server.
- **MUST NOT** guardar secretos en el repositorio Git del Config Server; usar el backend Vault del servidor o inyección por Vault.
- **MUST** proteger el servidor: autenticación entre servicios (mTLS o OAuth2), sin endpoints abiertos, y cifrado de transporte.
- **MUST** tratarlo como componente de plataforma crítico: al menos 2 réplicas, healthchecks y alerta, porque su caída bloquea arranques.
- **MUST** configurar los clientes con fallo rápido y reintentos acotados (`spring.config.import` con `configserver:`), y valores por defecto seguros.
- **SHOULD** limitar `refresh` a propiedades marcadas como refrescables; el resto exige reinicio.
- **SHOULD** versionar la configuración por etiqueta/rama equivalente al entorno y pasar por PR.
- **MUST NOT** convertirlo en punto único de fallo global: un Config Server por entorno/región, no uno compartido.

## Por qué
Añade un componente que operar, asegurar y mantener disponible; GitOps ya ofrece versionado y auditoría. Solo compensa si necesitas refresco dinámico o una capa común para servicios heterogéneos.

## Guía de decisión
| Pregunta | Sí -> |
|---|---|
| ¿Todo corre en Kubernetes con GitOps? | No hace falta Config Server |
| ¿Necesitas cambiar parámetros sin reiniciar? | Considerar Config Server o flags (`feature-flags-openfeature`) |
| ¿Hay equipo para operarlo con HA? | Si no, no adoptar |

## Ejemplos
### Mal
```yaml
# Config Server apuntando a un repo con credenciales en claro
spring.cloud.config.server.git.uri: https://git.example.com/config.git
spring.cloud.config.server.git.password: changeme-real-token
```
### Bien
```yaml
# Cliente (propiedades)
spring:
  config:
    import: "configserver:https://config.example.internal"
  cloud:
    config:
      fail-fast: true
```

## Criterios de decisión y trampas
### Cómo decidir
- Un servidor de configuración solo cuando hay muchos servicios y cambios frecuentes; para pocos, ficheros por entorno en un repositorio bastan.
- Los secretos no viven en el repositorio de configuración.
### Trampas frecuentes
- Un servidor de configuración como punto único de fallo.
- Secretos en el repositorio de configuración.
- Cambios de configuración sin revisión.
- Recarga en caliente sin entender sus efectos.
- Dependencia del servidor para arrancar sin respaldo.
### Evidencia
- Una prueba de arranque con el servidor de configuración caído.

## Checklist de revisión
- [ ] ADR del proyecto que justifica Config Server frente a GitOps + Vault.
- [ ] Sin secretos en el repo de configuración.
- [ ] Autenticación, TLS y 2+ réplicas.
- [ ] Clientes con fail-fast y reintentos acotados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión del ADR y de la configuración del servidor | 3 | agente `code-reviewer` |
| Regla Semgrep contra literales sensibles en YAML de configuración | 1 | `policies/semgrep/config-literal-secret-in-properties.yaml` |
| Aprobación humana de la decisión de adoptar el módulo | 4 | PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `config-by-environment`, `feature-flags-openfeature`, `secrets-management`, `actuator-and-health`.
- Fuentes: ADR-0011; documentación de Spring Cloud Config. Diseño preparado para AWS, no verificado en real.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
