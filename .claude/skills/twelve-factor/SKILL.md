---
name: twelve-factor
description: "Usar al diseñar, configurar o revisar servicios cloud-native: configuración por entorno, procesos stateless, logs, build/release/run y paridad dev-prod."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Twelve-Factor

## Cuándo aplicar y cuándo no
- Aplica a cualquier servicio desplegable (Spring Boot en contenedor, Kubernetes).
- No aplica de forma literal a herramientas CLI, jobs únicos ni a librerías; adaptar los factores relevantes.

## Reglas
- **MUST** mantener un repositorio por servicio desplegable y un artefacto inmutable (imagen) promovido entre entornos (build, release, run separados).
- **MUST** declarar dependencias explícitamente en `pom.xml`; sin dependencias del sistema implícitas.
- **MUST** externalizar la configuración por entorno (variables de entorno, `ConfigMap`, secret manager); el mismo artefacto sirve a todos los entornos.
- **MUST NOT** guardar secretos en el repositorio ni en la imagen; solo referencias o valores `changeme`/`example` en ejemplos.
- **MUST** tratar servicios de apoyo (BD, broker, caché) como recursos adjuntos configurables por URL.
- **MUST** ser stateless y no compartir nada entre procesos salvo servicios de apoyo; el disco local es efímero.
- **MUST** escribir logs a stdout/stderr en formato estructurado (JSON); la plataforma los enruta.
- **MUST** soportar arranque rápido y apagado ordenado (SIGTERM, `server.shutdown=graceful`).
- **SHOULD** mantener paridad dev/prod: mismas versiones de Postgres, broker, etc. en local con contenedores; declarar lo que no se reproduce (servicios gestionados de AWS, IAM, redes). Preparado para AWS, no verificado en real.
- **SHOULD** tratar tareas administrativas (migraciones) como procesos puntuales (Job/Flyway al desplegar), no como parte oculta del arranque de todas las réplicas.
- **SHOULD** exponer el puerto por configuración (`server.port=${PORT:8080}`).

## Por qué
Estos factores hacen que el mismo artefacto sea portable, escalable y operable por la plataforma. Configuración en la imagen obliga a reconstruir por entorno y rompe la trazabilidad de lo desplegado; estado local rompe el escalado horizontal.

## Ejemplos
### Mal
```yaml
spring:
  datasource:
    url: jdbc:postgresql://prod-db.internal:5432/app    # fijo para un entorno
    password: Sup3rS3cret                              # secreto en el repo
logging:
  file:
    name: /var/log/app.log                             # logs a fichero local
```
### Bien
```yaml
spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USER}
    password: ${DB_PASSWORD}          # inyectado por secret; en local: changeme
server:
  port: ${PORT:8080}
  shutdown: graceful
```
```yaml
# Kubernetes: sin estado local, config externa
env:
  - name: DB_URL
    valueFrom: { configMapKeyRef: { name: app-config, key: db-url } }
  - name: DB_PASSWORD
    valueFrom: { secretKeyRef: { name: app-db, key: password } }
```

## Checklist de revisión
- [ ] Mismo artefacto en todos los entornos; config por variables.
- [ ] Sin secretos ni URLs de entorno en repo/imagen.
- [ ] Logs a stdout en JSON.
- [ ] Sin estado en disco/memoria del proceso; shutdown graceful.
- [ ] Migraciones como paso explícito.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Detección de secretos | 1 | hook de seguridad de la fábrica y escáner de secretos en CI del proyecto |
| Regla Semgrep: secretos/URLs fijas en `application*.yml` | 1 | `policies/semgrep/spring-security-misconfig.yaml` (parcial) |
| Revisión de config de despliegue | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `scalability-patterns`, `cell-based-architecture`, `microservices-decision-guide`.
- Fuentes: 12factor.net (Wiggins; documentación de Spring Boot sobre graceful shutdown y externalized configuration..
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
