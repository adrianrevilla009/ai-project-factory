---
name: strangler-fig-migration
description: Usar al migrar un sistema legado de forma incremental, redirigiendo funcionalidad al nuevo sistema sin reescritura big-bang.
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Migración Strangler Fig

## Cuándo aplicar y cuándo no
- Aplica al reemplazar un monolito o sistema legado en producción que no puede detenerse.
- No aplica si el sistema es pequeño y la reescritura completa cabe en una iteración, o si no hay punto de interceptación posible.

## Reglas
- **MUST** introducir una fachada/proxy (gateway, ingress) delante del legado para poder redirigir por ruta o capacidad.
- **MUST** migrar por rebanadas verticales pequeñas y reversibles, una capacidad cada vez.
- **MUST** poder volver atrás (feature flag o regla de enrutado) en cada rebanada.
- **MUST** tener un dueño de datos por rebanada: sin doble escritura Postgres+NoSQL; si hace falta sincronizar, usar CDC/eventos con un único escritor.
- **MUST** proteger el modelo nuevo con `anti-corruption-layer`.
- **SHOULD** ejecutar en paralelo (shadow traffic o comparación de respuestas) antes de cortar tráfico.
- **MUST** definir y ejecutar la retirada del legado; una migración sin apagado final es deuda.
- **MUST NOT** añadir funcionalidad nueva al legado salvo corrección crítica.

## Por qué
El big-bang concentra el riesgo en un único corte. Con rebanadas se aprende pronto, se entrega valor continuo y cada paso se puede revertir. El patrón falla cuando se queda a medias: dos sistemas para siempre.

## Ejemplos
### Mal
```text
Plan: reescribir todo en 18 meses y cortar el fin de semana de Navidad.
```
### Bien
```yaml
# Enrutado incremental (ejemplo conceptual para un gateway; adaptar a la herramienta elegida)
routes:
  - path: /api/invoices/**      # rebanada 1: migrada
    target: invoices-service
  - path: /**                   # resto sigue en el legado
    target: legacy-monolith
rollback: "volver /api/invoices/** a legacy-monolith cambiando la ruta"
exit_criteria: "0 peticiones al legado durante 30 días -> apagar"
```

## Checklist de revisión
- [ ] Hay punto de interceptación y rollback por rebanada.
- [ ] Cada rebanada tiene dueño de datos único.
- [ ] Existe ACL entre nuevo y legado.
- [ ] Hay criterio y fecha de apagado del legado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión humana del plan de migración y de los criterios de salida | 4 | ADR del proyecto generado (sin automatización, pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `anti-corruption-layer`, `microservices-decision-guide`, `bff-and-api-gateway`, `evolutionary-architecture-fitness-functions`.
- Fuentes: Martin Fowler, "StranglerFigApplication" (martinfowler.com).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
