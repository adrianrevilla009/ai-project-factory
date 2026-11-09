# ADR-0036: React por defecto: SPA (Vite) vs SSR (Next.js)

- **Estado:** aceptado
- **Fecha:** 2026-11-07

## Contexto
Decisión que el brief dejaba abierta (§3). El dueño la cerró el 2026-11-09 aceptando la opción indicada en «Decisión».

## Opciones
- SPA/Vite: más simple, despliegue S3+CloudFront.
- SSR/Next.js: SEO y rendimiento inicial, más complejidad operativa.

## Decisión
SPA con Vite por defecto; Next.js (SSR) cuando haya SEO/SSR justificado.

## Consecuencias
Por determinar al decidir.
