---
name: c4-and-arc42
description: "Usar al documentar la arquitectura de un proyecto: diagramas C4 (contexto, contenedores, componentes) y estructura arc42 para la documentación completa."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Documentación de arquitectura: C4 + arc42

## Cuándo aplicar y cuándo no
- Aplica a cualquier proyecto generado con más de un contenedor desplegable, y a cada cambio que altere límites, dependencias o despliegue.
- No aplica a scripts o librerías de un solo módulo, donde basta el README vivo.

## Reglas
- **MUST** mantener como mínimo los niveles C4 1 (System Context) y 2 (Container); el nivel 3 (Component) solo para contenedores complejos. El nivel 4 (Code) no se dibuja a mano: se genera o se omite.
- **MUST** que cada elemento del diagrama tenga nombre, tecnología y responsabilidad en una línea; cada flecha, un verbo y el protocolo (`HTTPS/JSON`, `Kafka`).
- **MUST** usar arc42 como esqueleto de documentación: contexto y alcance, restricciones, estrategia de solución, vista de bloques, vista de ejecución, vista de despliegue, conceptos transversales, decisiones (enlazar ADR), calidad, riesgos, glosario.
- **MUST** que la sección de decisiones de arc42 enlace a los ADR en lugar de duplicarlos.
- **MUST** que los diagramas sean código versionado (ver `diagrams-as-code`) y se actualicen en el mismo PR que el cambio.
- **SHOULD** añadir un diagrama de despliegue C4 que distinga lo local (kind/k3d) de lo previsto para AWS, indicando que lo segundo está "preparado para AWS, no verificado en real".
- **SHOULD** añadir diagramas dinámicos solo para flujos críticos (alta de pedido, pago).
- **MUST NOT** representar en el diagrama de despliegue servicios AWS sin equivalente local sin marcar qué no se reproduce en local (ver matriz de paridad).
- **MUST NOT** mezclar niveles de abstracción en un mismo diagrama.

## Por qué
C4 ofrece vistas jerárquicas y simples para audiencias distintas; arc42 aporta una plantilla de qué documentar y dónde, evitando documentos monolíticos y huecos. Juntos: C4 para los dibujos, arc42 para la estructura. Fuentes: https://c4model.com/ (niveles: contexto, contenedores, componentes, código; suplementarios: landscape, dinámico, despliegue) y https://arc42.org/ (consultadas 2026-11-07).

## Ejemplos
### Mal
```text
Un diagrama con cajas de colores sin leyenda: "API", "DB", "Cloud", flechas sin etiqueta,
con clases Java y servicios AWS en el mismo plano.
```
### Bien
```text
docs/architecture/
  01-introduccion-y-objetivos.md      # arc42 §1
  03-contexto-y-alcance.md            # + diagrama C4 nivel 1
  05-vista-de-bloques.md              # + diagrama C4 nivel 2/3
  06-vista-de-ejecucion.md            # diagrama dinámico del flujo de pago
  07-vista-de-despliegue.md           # C4 despliegue: local vs previsto AWS
  09-decisiones.md                    # índice de ADR
  11-riesgos-y-deuda.md               # enlaza risk-register y tech-debt-register
```
```text
Billing API [Spring Boot] --"publica PaymentCaptured (Kafka)"--> Orders Service [Spring Boot]
```

## Checklist de revisión
- [ ] Existen niveles 1 y 2 y reflejan el código actual.
- [ ] Cada elemento y relación está etiquetado (tecnología, verbo, protocolo).
- [ ] arc42: las secciones aplicables existen; las no aplicables dicen por qué.
- [ ] Sección de decisiones enlaza ADR.
- [ ] Despliegue distingue local / previsto AWS y lo no reproducido en local.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Hook de parada: exigir docs al cambiar código | 2 | `.claude/hooks/stop/require_docs_updated.py` |
| Guardia de arquitectura por reglas de dependencia | 1 | `policies/archunit/ModuleBoundaryRules.java` |
| Revisión de coherencia diagrama-código | 3 | agente `architecture-guardian` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `diagrams-as-code`, `adr`, `living-readme`, `architecture-testing-archunit`, `parity-matrix-maintenance`.
- Fuentes: https://c4model.com/, https://arc42.org/ (2026-11-07). Lista exacta de secciones arc42.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
