# ADR-0004: No desplegar nunca en AWS

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D4 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
No se despliega nunca en AWS, ni en sandbox. Local real + AWS diseñado y validado estáticamente.

## Por qué
Evitar coste y riesgo de cuenta; la fábrica se prueba con local y validación estática.

## Consecuencias
Madurez máxima de infra = nivel 2 (validado estáticamente). Prohibido afirmar 'listo para producción en AWS'. Riesgo asumido: puede fallar al aplicar por primera vez; se documenta en README. Validador `honest_claims` lo hace cumplir.
