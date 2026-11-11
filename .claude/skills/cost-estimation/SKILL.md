---
name: cost-estimation
description: "Usar al estimar el coste de la infraestructura AWS diseñada (Infracost o equivalente) sin desplegar; incluye el sobrecoste por tier de resiliencia."
metadata:
  block: "29-cloud-readiness"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Estimación de coste

## Cuándo aplicar y cuándo no
- Aplica al diseñar o cambiar infraestructura Terraform y al elegir tier de resiliencia (`catalog/resilience-tiers.yaml`).
- No aplica a facturas reales ni a FinOps de cuentas operativas: la fábrica no despliega (ADR-0004), así que no hay gasto medido.

## Reglas
- **MUST** presentar toda cifra como estimación de diseño con supuestos explícitos (región, horas/mes, tráfico, almacenamiento), nunca como coste real.
- **MUST** estimar desde el código o HCL sin credenciales AWS. Infracost admite analizar un directorio Terraform. Alternativa: tabla propia con precios oficiales fechados.
- **MUST** citar la fuente y fecha de cada precio unitario; los precios se verifican en la página oficial de AWS, no se memorizan.
- **MUST** reflejar el multiplicador del tier: 0 activo-activo (muy alto, aprox. 2x), 1 warm standby (alto, defecto), 2 pilot light (medio), 3 backup y restauración (bajo).
- **MUST** incluir las dos regiones del diseño (eu-west-1 primaria, eu-central-1 secundaria, D6) y la transferencia entre regiones en tiers 0 a 2.
- **SHOULD** dar rango (mínimo/esperado/pico) en vez de cifra única.
- **SHOULD** comparar el coste con el RTO/RPO del tier para que el negocio decida.
- **MUST NOT** afirmar que el coste "se verificó" ni usar la estimación como compromiso presupuestario.

## Por qué
El coste es una restricción de arquitectura. Sin estimación, el tier por defecto (warm standby) o una NAT Gateway por AZ se descubren tarde. Con la etiqueta de estimación se evita que una cifra de diseño se tome por dato medido.

## Ejemplos
### Mal
```markdown
El sistema costará 1.200 EUR al mes en AWS.
```
### Bien
```markdown
Estimación de diseño (2026-11-07), no coste real. Supuestos: eu-west-1 + eu-central-1,
tier 1 (warm standby), 730 h/mes, precios de la web oficial de AWS.
| Componente | Rango mensual | Fuente de precio |
|---|---|---|
| EKS + nodos (2 regiones) | por calcular | calculadora oficial |
Sobrecoste tier 0 frente a tier 1: aprox. 2x en componentes replicados.
```
```text
infracost breakdown --path infra/
```

## Criterios de decisión y trampas
### Cómo decidir
- Estima el coste a partir del diseño con precios de la fuente oficial y fecha, por nivel de resiliencia y con supuestos explícitos (horas, volumen, transferencia).
- Presenta rangos y lo que no incluye.
### Trampas frecuentes
- Cifras de memoria sin fuente.
- Olvidar la transferencia, los registros y las copias.
- Una única cifra precisa que aparenta certeza.
- Estimar solo la opción elegida.
- No actualizar con el uso real.
### Evidencia
- Una hoja de supuestos con fuente y fecha de cada precio y los costes que no incluye.

## Checklist de revisión
- [ ] Marcado como estimación con supuestos y fecha.
- [ ] Precios con fuente oficial y fecha; sin fuente no se pone cifra.
- [ ] Tier y segunda región reflejados.
- [ ] Sin credenciales AWS en el flujo.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Afirmaciones honestas (no "verificado") | 1 | `factory/validators/honest_claims.py` |
| Presencia de estimación en el PR de infra | 3 | revisión humana (regla pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `static-verification-ladder`, `cost-visibility`, `dr-tabletop-exercises`, `maturity-labels`.
- Fuentes: `catalog/resilience-tiers.yaml`; documentación de Infracost y precios de AWS.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
