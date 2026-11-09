---
name: docker-multistage
description: "Usar al escribir o revisar un Dockerfile de Java o React: multi-stage, imagen mínima, usuario no root, FS de solo lectura, caché de capas, labels y multi-arch."
metadata:
  block: "15-artifacts-and-registry"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Dockerfile multi-stage

## Cuándo aplicar y cuándo no
- Aplica a Dockerfiles de servicios Spring Boot y de frontend estático (nginx sin privilegios).
- No aplica a ajuste de JVM en contenedor (ver `jvm-in-containers`) ni a políticas de pod (ver `container-and-k8s-security`).

## Reglas
- **MUST** separar stages: `build` (JDK + Maven), opcional `layers` (extraer capas del JAR) y `runtime` (JRE mínimo). Nada de Maven, fuentes ni caches en la imagen final.
- **MUST** fijar la imagen base por tag de versión y, para release, por digest (`@sha256:`); **MUST NOT** usar `latest`.
- **MUST** usar imágenes de runtime mínimas (JRE slim/distroless).
- **MUST** ejecutar como usuario no root (`USER` numérico) y compatible con `readOnlyRootFilesystem`; los directorios escribibles (`/tmp`) se montan como `emptyDir`.
- **MUST** ordenar capas para la caché: primero `pom.xml`/`package*.json` y resolución de dependencias, luego el código. Usar `RUN --mount=type=cache` de BuildKit para `~/.m2`.
- **MUST** añadir labels OCI (`org.opencontainers.image.source`, `.revision`, `.version`, `.created`) para trazabilidad.
- **SHOULD** construir multi-arch (`linux/amd64`, `linux/arm64`) con `docker buildx build --platform` si se despliega en Graviton y x86.
- **MUST NOT** copiar secretos con `COPY`/`ARG`; usar `RUN --mount=type=secret`.
- **SHOULD** `.dockerignore` con `.git`, `target`, `node_modules`.

## Por qué
La imagen final es superficie de ataque y coste de transferencia. Sin shell ni build tools y sin root, un RCE tiene mucho menos margen. Un orden de capas correcto convierte builds de minutos en segundos. Los labels enlazan la imagen con el commit para el `trace` del puerto.

## Ejemplos
### Mal
```dockerfile
FROM maven:latest
COPY . /app
RUN mvn package
CMD ["java", "-jar", "/app/target/orders.jar"]
```
### Bien
```dockerfile
# syntax=docker/dockerfile:1
FROM eclipse-temurin:21-jdk AS build
WORKDIR /src
COPY pom.xml .
RUN --mount=type=cache,target=/root/.m2 mvn -q -B dependency:go-offline
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -q -B -DskipTests package

FROM eclipse-temurin:21-jre AS runtime
ARG REVISION=unknown
LABEL org.opencontainers.image.source="https://github.com/example-org/orders" \
      org.opencontainers.image.revision="${REVISION}"
RUN groupadd -g 10001 app && useradd -u 10001 -g app -M app
WORKDIR /app
COPY --from=build /src/target/orders.jar app.jar
USER 10001
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```
Las etiquetas `21-jdk`/`21-jre` son ejemplo; fijar versión y digest reales por proyecto.

## Checklist de revisión
- [ ] Al menos dos stages; la final no contiene build tools.
- [ ] Base fijada por versión (digest en release), sin `latest`.
- [ ] `USER` numérico no root; funciona con FS de solo lectura.
- [ ] Caché de dependencias antes del código.
- [ ] Labels OCI presentes; sin secretos en capas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest sobre Dockerfile: tag/digest, `latest`, USER no root | 1 | `policies/opa-conftest/dockerfile.rego` (escrita, no ejecutada aquí) |
| Admisión: `runAsNonRoot`, FS de solo lectura | 1 | pendiente (`policies/kyverno/`) |
| Escaneo de imagen | 1 | ver `image-scanning` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `image-scanning`, `jvm-in-containers`, `container-and-k8s-security`, `startup-and-native`.
- Fuentes: Docker multi-stage https://docs.docker.com/build/building/multi-stage/ ; OCI annotations https://github.com/opencontainers/image-spec/blob/main/annotations.md.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
