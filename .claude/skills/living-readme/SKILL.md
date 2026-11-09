---
name: living-readme
description: "Usar al crear o actualizar el README de un proyecto generado o un módulo, para que siga siendo verdadero, ejecutable y corto."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# README vivo

## Cuándo aplicar y cuándo no
- Aplica al README raíz del proyecto generado y al de cada módulo desplegable o librería interna.
- No aplica a la documentación de arquitectura (ver `c4-and-arc42`) ni a runbooks (ver `runbooks`).

## Reglas
- **MUST** incluir: qué es y para quién, requisitos previos con versiones, cómo arrancar en local, cómo ejecutar tests, cómo contribuir y dónde está el resto de docs.
- **MUST** que cada comando del README se pueda copiar y ejecutar tal cual desde un clon limpio.
- **MUST** actualizar el README en el mismo PR que cambia un comando, puerto, variable o requisito.
- **MUST** declarar la madurez de la parte de infraestructura: "preparado para AWS, no verificado en real" cuando aplique, y qué NO se reproduce en local.
- **SHOULD** limitar el README a una pantalla y media; el detalle va a `docs/` con enlaces.
- **SHOULD** enlazar ADRs y el contrato OpenAPI en vez de copiar su contenido.
- **MUST NOT** incluir secretos, ni siquiera de ejemplo que parezcan reales (usar `changeme`/`example`).
- **MUST NOT** duplicar información que ya tiene fuente de verdad (versión en `pom.xml`, puertos en `compose.yaml`).

## Por qué
Un README desactualizado cuesta más que ninguno: el primer día de cada persona nueva se pierde en comandos rotos. Si el README se ejecuta (en CI o en revisión), deja de pudrirse.

## Ejemplos
### Mal
```markdown
# orders-service
Servicio de pedidos. Ver wiki.
Arrancar: ./run.sh   <!-- el script ya no existe -->
```
### Bien
```markdown
# orders-service
Gestiona el ciclo de vida de pedidos. Equipo: orders. Contrato: `docs/api/openapi.yaml`.

## Requisitos
- JDK 21, Maven wrapper incluido, Docker y un clúster Kubernetes local (kind), ver `cluster-tooling`.

## Arranque local
    make local-up
    ./mvnw spring-boot:run -Dspring-boot.run.profiles=local

## Tests
    ./mvnw verify

## Qué NO se reproduce en local
IAM real, ALB/NLB y KMS gestionado. Infra: preparado para AWS, no verificado en real.
```

## Checklist de revisión
- [ ] Un clon limpio llega a "servicio arriba" solo con los comandos del README.
- [ ] Versiones de requisitos coinciden con el build.
- [ ] Hay enlaces a ADRs, OpenAPI y runbooks.
- [ ] Sin secretos ni afirmaciones de madurez no verificadas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validador de afirmaciones honestas sobre AWS (aplica a `.md`) | 1 | `factory/validators/honest_claims.py` |
| Job CI que ejecuta los comandos del bloque "Arranque local" (smoke) | 1 | pendiente, en el proyecto generado |
| Revisión del README en el PR | 3 | agente `code-reviewer` / revisión humana |

> Estado: el job de smoke del README está pendiente.

## Relacionados, fuentes y mantenimiento
- Relacionados: `c4-and-arc42`, `runbooks`, `api-docs`, `pr-rules`, `honest-claims-policy`.
- Fuentes: práctica interna; sin fuente oficial externa.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
