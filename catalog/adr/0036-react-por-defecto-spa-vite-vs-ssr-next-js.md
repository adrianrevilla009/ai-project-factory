# ADR-0036: React por defecto: SPA (Vite) vs SSR (Next.js)

- **Estado:** aceptado (por defecto; revisable por el dueño)
- **Fecha:** 2026-11-07

## Contexto
Decisión abierta del brief (§3). No se inventa una respuesta; requiere confirmación humana.

## Opciones
- SPA/Vite: más simple, despliegue S3+CloudFront.
- SSR/Next.js: SEO y rendimiento inicial, más complejidad operativa.

## Decisión
SPA con Vite por defecto; Next.js (SSR) cuando haya SEO/SSR justificado.

## Consecuencias
Por determinar al decidir.
