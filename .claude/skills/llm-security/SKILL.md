---
name: llm-security
description: Usar al integrar un LLM o agente en una aplicación (RAG, tools, MCP) para defenderse de inyección de prompt, fuga de datos y acciones excesivas.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Seguridad en aplicaciones con LLM

## Cuándo aplicar y cuándo no
- Aplica a aplicaciones que llaman a un modelo, usan RAG, ejecutan herramientas/MCP o exponen un agente a usuarios o a contenido externo.
- No aplica a la observabilidad de LLM (ver `llm-observability`) ni al uso de agentes de desarrollo sobre este repositorio (ver `gate-protocol`).

## Reglas
- **MUST** tratar toda salida del modelo y todo contenido recuperado (web, documentos, correos, resultados de tools) como **entrada no confiable**: es dato, nunca instrucciones con autoridad.
- **MUST NOT** ejecutar la salida del LLM en un intérprete (SQL, shell, `eval`, plantillas) ni renderizarla como HTML sin codificación; validarla contra esquema estricto (JSON Schema) antes de usarla.
- **MUST** aplicar mínimo privilegio a las herramientas del agente: allowlist de tools, permisos acotados por usuario (la autorización se evalúa con la identidad del usuario, no la del agente), credenciales de corta vida.
- **MUST** exigir confirmación humana para acciones irreversibles, de coste o con efectos externos (pagos, borrados, envíos).
- **MUST** separar privilegios: un agente que lee contenido no confiable no debe tener a la vez acceso a datos sensibles y capacidad de exfiltrar (evitar la combinación datos privados + contenido no confiable + canal de salida).
- **MUST NOT** enviar a un proveedor de modelo PII o secretos sin base y contrato aprobados (ver `pii-and-data-classification`); minimizar y enmascarar.
- **MUST** aplicar control de acceso en la recuperación RAG (filtrar por permisos del usuario antes de construir el contexto).
- **SHOULD** limitar longitud, tasa y coste por usuario (ver `dos-and-rate-limiting`) y fijar un máximo de pasos del agente.
- **SHOULD** registrar prompts, tool calls y decisiones para auditoría, sin PII (ver `audit-trail-and-security-logging`).
- **SHOULD** probar con casos adversarios (inyección directa e indirecta) en una batería de evaluación; no hay defensa perfecta de prompt, la contención es arquitectónica.

## Por qué
Un LLM no distingue de forma fiable instrucciones de datos: un documento recuperado puede ordenarle revelar información o llamar a una herramienta. Por eso el control está fuera del modelo: privilegios, validación y aprobación humana. Referencia de categorías: OWASP Top 10 for LLM Applications (consultado 2026-11-07, comprobar edición vigente).

## Ejemplos
### Mal
```java
String sql = llm.complete("Write SQL for: " + userQuestion);
jdbc.execute(sql);                          // ejecuta salida del modelo con privilegios de la app
```
### Bien
```java
record RefundRequest(@NotBlank String orderId, @DecimalMax("100.00") BigDecimal amount) {}

RefundRequest req = mapper.readValue(llm.completeJson(prompt, schema), RefundRequest.class);
validator.validate(req);                                   // esquema y limites
authz.checkCanRefund(currentUser, req.orderId());          // permisos del USUARIO
if (req.amount().compareTo(AUTO_LIMIT) > 0) approvals.requestHuman(req);   // humano en el bucle
else refunds.execute(req);
```
```text
Politica de tools: allowlist = [search_orders (read-only), create_refund_draft]
Prohibido: shell, acceso a red libre, lectura de ficheros fuera del workspace.
```

## Checklist de revisión
- [ ] Salida del modelo validada por esquema y nunca ejecutada ni renderizada en crudo.
- [ ] Tools en allowlist con permisos del usuario; acciones críticas con aprobación humana.
- [ ] No coexisten datos sensibles, contenido no confiable y canal de exfiltración.
- [ ] RAG filtra por permisos; límites de coste/pasos; sin PII al proveedor.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de diseño del agente y sus tools | 3 | agente `code-reviewer` |
| Batería de pruebas adversarias de prompt injection | 1 | pendiente (tests del proyecto generado) |
| Aprobación humana de nuevas tools con efectos externos | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `llm-observability`, `pii-and-data-classification`, `authz-rbac-abac-rebac`, `injection-families`, `dos-and-rate-limiting`.
- Fuentes: OWASP Top 10 for LLM Applications y OWASP LLM Prompt Injection Prevention Cheat Sheet (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
