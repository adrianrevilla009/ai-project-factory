---
name: threat-modeling-stride
description: Usar al diseñar un servicio, flujo o integración nuevos para identificar amenazas con STRIDE sobre un diagrama de flujo de datos y registrar mitigaciones.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "gate"
---

# Modelado de amenazas con STRIDE

## Cuándo aplicar y cuándo no
- Aplica a servicios nuevos, cambios de arquitectura, nuevas integraciones externas y nuevos tipos de dato sensible.
- No aplica a cambios cosméticos o refactors sin nuevas fronteras de confianza.

## Reglas
- **MUST** partir de un diagrama de flujo de datos (DFD) con actores, procesos, almacenes, flujos y fronteras de confianza.
- **MUST** evaluar cada elemento y flujo que cruce una frontera con las seis categorías: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege.
- **MUST** registrar por amenaza: id, descripción, impacto, probabilidad, mitigación, dueño y estado.
- **MUST** convertir cada mitigación aceptada en una historia o tarea con prueba asociada.
- **MUST** documentar los riesgos aceptados con firma del dueño del producto y fecha de revisión.
- **SHOULD** versionar el modelo junto al código (`docs/security/threat-model-<servicio>.md`) y revisarlo cuando cambie el DFD.
- **SHOULD** incluir abuso de negocio (cupones, reintentos, enumeración), no solo técnica.
- **MUST NOT** limitar el modelo a una checklist genérica sin DFD.

## Por qué
Los fallos de diseño no los encuentra ningún escáner. Dibujar fronteras de confianza obliga a preguntarse dónde se valida identidad y datos. STRIDE es mecánico y repetible; su valor es que las mitigaciones acaben como tareas con test.

## Ejemplos
### Mal
```markdown
Amenazas: hackeo, DDoS. Mitigación: firewall.
```
### Bien
```markdown
# Threat model: orders-service
DFD (texto):
  [Browser] --HTTPS--> (API Gateway) --mTLS--> (orders-service) --> [(orders-db)]
  frontera 1: Internet | DMZ ; frontera 2: malla de servicios | base de datos

| Id | Elemento | STRIDE | Amenaza | Mitigación | Prueba | Estado |
|---|---|---|---|---|---|---|
| T1 | Browser -> Gateway | S | Token robado reutilizado | tokens cortos + audiencia | `TokenAudienceIT` | hecho |
| T2 | orders-service | E | Acceso a pedidos de otro tenant | filtro por tenant en repositorio | `CrossTenantIT` | hecho |
| T3 | orders-db | I | Volcado con PII en claro | cifrado en reposo + minimización | revisión de config | pendiente |
| T4 | Gateway | D | Ráfagas sobre /search | rate limit por cliente | `RateLimitIT` | pendiente |
```

## Checklist de revisión
- [ ] Existe DFD con fronteras de confianza.
- [ ] Cada flujo que cruza frontera tiene fila STRIDE.
- [ ] Cada mitigación tiene prueba o tarea enlazada.
- [ ] Los riesgos aceptados tienen firma y fecha.
- [ ] El modelo se actualizó con el último cambio de arquitectura.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Gate de diseño: exige modelo de amenazas en servicios con API/PII | 3 | `gates/` |
| Validador que busque `docs/security/threat-model-*.md` en el proyecto generado | 2 | pendiente |
| Calidad del modelo | 4 | revisión humana (security champion) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `secure-sdlc-nist-ssdf`, `zero-trust`, `owasp-top10-and-api-top10`, `dos-and-rate-limiting`.
- Fuentes: OWASP Threat Modeling Cheat Sheet (cheatsheetseries.owasp.org); descripción de STRIDE de Microsoft SDL.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
