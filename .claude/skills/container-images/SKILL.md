---
name: container-images
description: "Usar al escribir Dockerfiles o construir imágenes de servicios Spring Boot: base mínima, usuario no root, multi-stage, digest fijado, capas, escaneo y firma."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Imágenes de contenedor

## Cuándo aplicar y cuándo no
- Aplica a todo Dockerfile o build de imagen (Dockerfile, buildpacks, Jib) de un servicio del proyecto generado.
- No aplica a imágenes de terceros que solo se consumen (se rigen por `supply-chain` y por la política de admisión del clúster).

## Reglas
- **MUST** usar build multi-stage: una etapa de build (JDK) y una etapa final solo con JRE y el artefacto.
- **MUST** fijar la imagen base por versión y por digest (`@sha256:`) en la etapa final; actualizar el digest mediante Renovate (`renovate-dependabot-policy`).
- **MUST NOT** usar la etiqueta `latest` ni imágenes sin versión.
- **MUST** ejecutar como usuario no root (`USER` numérico) y sin privilegios añadidos.
- **MUST NOT** incluir secretos, `.git`, claves ni `settings.xml` con credenciales en la imagen ni en capas intermedias; usar `.dockerignore`.
- **MUST** usar una base de distribución OpenJDK libre y soportada (`jdk-distribution-and-upgrade-cadence`); sin runtimes de pago por defecto (D16).
- **SHOULD** usar el JAR en capas de Spring Boot (`-Djarmode=tools … extract --layers`, el modo vigente según la documentación de Spring Boot, comprobado el 2026-11-08; `layertools` es el nombre antiguo) para cachear dependencias frente a código.
- **SHOULD** declarar `HEALTHCHECK` solo si el orquestador no lo cubre; en Kubernetes se usan probes.
- **MUST** escanear la imagen y generar su SBOM (`sbom-generation`) en CI; fallar con vulnerabilidades críticas según `vulnerability-sla-and-incident-response`.
- **SHOULD** firmar la imagen y verificar la firma en admisión (Kyverno, pendiente en `policies/kyverno/`). Preparado para AWS, no verificado en real: publicar en ECR queda fuera de la fábrica (D4).

## Por qué
Una imagen con shell, gestor de paquetes y root amplía la superficie de ataque y el tamaño. El digest evita que una etiqueta mutable cambie el contenido sin que se note, y las capas ordenadas reducen tiempo de build y de pull.

## Ejemplos
### Mal
```dockerfile
FROM openjdk:latest
COPY . /app
WORKDIR /app
RUN ./mvnw package
ENV DB_PASSWORD=changeme-example
CMD ["java", "-jar", "target/app.jar"]
```
### Bien
```dockerfile
FROM eclipse-temurin:21-jdk@sha256:<digest-example> AS build   # tag verificado en Docker Hub el 2026-11-08; fijar el digest real en el proyecto
WORKDIR /workspace
COPY mvnw pom.xml ./
COPY .mvn .mvn
RUN ./mvnw -B dependency:go-offline
COPY src src
RUN ./mvnw -B package -DskipTests \
 && java -Djarmode=tools -jar target/app.jar extract --layers --destination /workspace/extracted

FROM eclipse-temurin:21-jre@sha256:<digest-example> AS runtime
RUN useradd --system --uid 10001 app
USER 10001
WORKDIR /app
COPY --from=build /workspace/extracted/dependencies/ ./
COPY --from=build /workspace/extracted/spring-boot-loader/ ./
COPY --from=build /workspace/extracted/snapshot-dependencies/ ./
COPY --from=build /workspace/extracted/application/ ./
ENTRYPOINT ["java", "-jar", "application.jar"]
```

## Criterios de decisión y trampas
### Cómo decidir
- Etapas múltiples, imagen final mínima, usuario sin privilegios y versión fijada por digest; separa las capas que cambian poco de las que cambian mucho.
- Construye una imagen una vez y promociónala.
### Trampas frecuentes
- Etiquetas `latest`.
- Herramientas de compilación en la imagen final.
- Secretos dentro de la imagen.
- Contenedores que corren como administrador.
- Imágenes enormes que ralentizan los despliegues.
### Evidencia
- Un escáner de imágenes y una política de admisión comprueban la base y el usuario.

## Checklist de revisión
- [ ] Multi-stage, imagen final solo JRE.
- [ ] Base con versión y digest; sin `latest`.
- [ ] `USER` no root; `.dockerignore` presente.
- [ ] Sin secretos en capas.
- [ ] Escaneo y SBOM en CI.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Rego sobre Dockerfile (sin `latest`, con `USER`) | 1 | pendiente: `policies/opa-conftest/` |
| Política de admisión (no root, imágenes firmadas) | 1 | pendiente: `policies/kyverno/` |
| Hook de secretos antes de escribir ficheros | 2 | `.claude/hooks/` |
| Revisión de Dockerfile | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `sbom-generation`, `build-caching-and-speed`, `jdk-distribution-and-upgrade-cadence`, `supply-chain`, `renovate-dependabot-policy`.
- Fuentes: docs.docker.com (best practices for Dockerfile, multi-stage), documentación de Spring Boot (container images); consultadas 2026-11-07; el comando `-Djarmode=tools extract --layers` se verificó el 2026-11-08 en https://docs.spring.io/spring-boot/reference/packaging/container-images/dockerfiles.html.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
