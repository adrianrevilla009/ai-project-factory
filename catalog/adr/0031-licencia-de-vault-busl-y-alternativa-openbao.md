# ADR-0031: Licencia de Vault (BUSL) y alternativa OpenBao

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión adicional tomada durante la Oleada 0.

## Decisión
Se usa Vault OSS por defecto; se documenta que su licencia es BUSL (no OSI) y que OpenBao es la alternativa de código abierto.

## Por qué
Vault está bajo BUSL 1.1 (licenciante IBM desde el 2025-02-27) y OpenBao, el fork de la Linux Foundation, bajo MPL 2.0 (verificado el 2026-11-08). Para uso interno no suele haber restricción, pero un revisor legal debe confirmarlo.

## Consecuencias
Los skills de Vault citan ambas opciones; la elección final requiere confirmación legal.
