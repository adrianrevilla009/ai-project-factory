---
name: honest-claims-policy
description: "Usar al redactar cualquier texto sobre AWS, infraestructura o madurez: qué se puede afirmar y qué no, con la fórmula obligatoria de honestidad."
metadata:
  block: "29-cloud-readiness"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "hook"
---

# Política de afirmaciones honestas

## Cuándo aplicar y cuándo no
- Aplica a READMEs, ADRs, informes, skills, mensajes de commit y respuestas del agente que mencionen AWS, Terraform, EKS o madurez de infraestructura.
- No aplica a texto sobre código de aplicación con tests ejecutados, donde se puede afirmar lo que los tests demuestran.

## Reglas
- **MUST** usar la fórmula "preparado para AWS, no verificado en real" cuando se hable del estado de la infraestructura.
- **MUST NOT** afirmar que algo esté listo para producción en AWS, ni probado, testado, verificado, validado o desplegado en AWS real, ni que "funciona en AWS real". Son los patrones que rechaza el validador.
- **MUST** reflejar que la fábrica nunca despliega (ADR-0004) ni hace `terraform plan` contra una cuenta (ADR-0037); el techo es "validada estáticamente".
- **MUST** que una mención de esas frases como ejemplo malo vaya precedida de negación o prohibición ("nunca", "no está", "prohibido afirmar"); es lo que el validador admite. Preferir describir el patrón sin repetirlo.
- **MUST** usar el marcador de exclusión del validador solo al citar un mal ejemplo, y con motivo en la misma línea.
- **MUST** tratar normativa y legal como borrador por confirmar con fuente oficial y fecha.
- **SHOULD** sustituir adjetivos de calidad por evidencia: qué peldaño de `static-verification-ladder` se superó y cuándo.
- **MUST NOT** relajar el validador o el hook para que pase un texto; corregir el texto.

## Por qué
Un agente que dice "listo" sin evidencia genera falsa seguridad en quien decide. La regla se aplica con script, no con ruego: un texto deshonesto no llega al repositorio.

## Ejemplos
### Mal
```markdown
La infraestructura ha quedado terminada y comprobada contra la nube real.
```
(Redacción equivalente al patrón rechazado, sin la frase literal para no activar el validador.)
### Bien
```markdown
Infraestructura: validada estáticamente (2026-11-07). Preparado para AWS, no verificado en real.
No se ha desplegado ni ejecutado plan contra ninguna cuenta (ADR-0004, ADR-0037).
```
```text
Prohibido afirmar que el despliegue está probado en AWS real.
```

## Checklist de revisión
- [ ] Ninguna frase afirma verificación o despliegue real en AWS.
- [ ] Aparece la fórmula de honestidad en el estado de infraestructura.
- [ ] Normativa marcada como borrador con fuente y fecha.
- [ ] Las exclusiones del validador tienen motivo.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validador de afirmaciones (`make validate`) | 1 | `factory/validators/honest_claims.py` |
| Hook al editar ficheros de texto | 2 | `.claude/hooks/post-tool-use/maturity_label_check.py` |
| Revisión de redacción dudosa | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `maturity-labels`, `static-verification-ladder`, `verify-before-asserting`, `local-parity-matrix`.
- Fuentes: `CLAUDE.md` (regla 2), `catalog/adr/0004-no-desplegar-nunca-en-aws.md`, `catalog/adr/0037-terraform-plan-contra-una-cuenta-aws-vacia.md`.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
