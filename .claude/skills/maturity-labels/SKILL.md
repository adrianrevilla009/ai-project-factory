---
name: maturity-labels
description: "Usar al escribir un README, informe o ADR sobre infraestructura: qué etiqueta de madurez poner (validada estáticamente, no verificada en real) y dónde."
metadata:
  block: "29-cloud-readiness"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "hook"
---

# Etiquetas de madurez

## Cuándo aplicar y cuándo no
- Aplica a todo directorio con Terraform, a informes de verificación y a cualquier documento que describa el estado de infraestructura.
- No aplica a código de aplicación probado con tests, cuya madurez se expresa con cobertura y gates.

## Reglas
- **MUST** que cada directorio con ficheros `.tf` tenga un `README.md` con una etiqueta de madurez.
- **MUST** usar solo estos niveles, de menor a mayor: `borrador` (sin ejecutar nada), `validada estáticamente` (superó `static-verification-ladder`), `simulada en local` (comportamiento reproducible comprobado en kind, con límites de `local-parity-matrix`).
- **MUST** que el techo para infraestructura AWS sea `validada estáticamente`; no existe nivel superior en la fábrica (ADR-0004).
- **MUST** acompañar el nivel con la fórmula "preparado para AWS, no verificado en real".
- **MUST** indicar fecha y herramientas con versión en la etiqueta, para que caduque de forma visible.
- **SHOULD** degradar la etiqueta a `borrador` si cambia el código y no se repite la escalera.
- **MUST NOT** inventar niveles ("certificada", "auditada", "lista") ni usar la etiqueta para sugerir despliegue real.
- **MUST NOT** copiar la etiqueta de otro módulo sin ejecutar la escalera en este.

## Por qué
Los agentes tienden a redondear hacia arriba. Una etiqueta cerrada, con fecha y herramientas, convierte la madurez en un dato comprobable y bloquea el optimismo.

## Ejemplos
### Mal
```markdown
# Módulo network
Infraestructura terminada y aprobada.
```
### Bien
```markdown
# Módulo network
Madurez: validada estáticamente (2026-11-07; terraform validate, tflint, checkov, conftest).
Preparado para AWS, no verificado en real. No se ha ejecutado plan ni apply.
No reproducido en local: WAF, Shield, CloudFront, multi-región (ver parity-matrix).
```

## Checklist de revisión
- [ ] Todo directorio `.tf` tiene README con etiqueta.
- [ ] El nivel es uno de los tres definidos y coincide con lo ejecutado.
- [ ] Incluye fecha, herramientas y la fórmula de honestidad.
- [ ] No hay palabras de madurez inventadas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validador: README con etiqueta junto a Terraform | 1 | `factory/validators/honest_claims.py` |
| Hook tras editar texto | 2 | `.claude/hooks/post-tool-use/maturity_label_check.py` |
| Contraste etiqueta vs. evidencia | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `static-verification-ladder`, `honest-claims-policy`, `local-parity-matrix`, `cost-estimation`.
- Fuentes: ADR-0004 y ADR-0037 en `catalog/adr/`. Los tres niveles son convención de la fábrica, revisables por el dueño.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
