---
name: private-registry
description: "Usar al montar un registro privado de imágenes (Harbor) on-prem: proyectos, replicación, escaneo, caché proxy y firma."
metadata:
  block: "21-on-prem-hybrid"
  tier: T3
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Registro privado (Harbor)

## Cuándo aplicar y cuándo no
- Aplica cuando las imágenes deben residir en infraestructura propia o el clúster no tiene salida a registros públicos.
- Harbor es la opción OSS por defecto (D16, sin licencias de pago). Referencia T3.

## Reglas
- **MUST** proyectos privados por equipo, con cuentas robot de mínimo privilegio para CI; MUST NOT usar credenciales personales en pipelines.
- **MUST** escaneo de vulnerabilidades al subir y política que bloquee despliegue por severidad (ver `image-scanning`).
- **MUST** desplegar solo imágenes por digest y firmadas (ver `image-signing-and-provenance`).
- **SHOULD** proyecto de caché proxy para registros públicos, evitando dependencias directas de Internet.
- **SHOULD** políticas de retención de tags y réplica a un segundo sitio.
- **MUST NOT** usar el tag `latest` en despliegues.

## Por qué
El registro es parte de la cadena de suministro: si se compromete o cae, nada se despliega o se despliega lo equivocado.

## Ejemplos
### Mal
```yaml
image: registry.example.internal/orders:latest
```
### Bien
```yaml
image: registry.example.internal/team-orders/orders@sha256:0000000000000000000000000000000000000000000000000000000000000000  # digest de ejemplo (example)
```
La política Kyverno de firmas ya existe y se aplica a este registro.

## Checklist de revisión
- [ ] Proyectos privados y robots por equipo.
- [ ] Escaneo y bloqueo por severidad.
- [ ] Imágenes por digest y firmadas.
- [ ] Caché proxy y retención configuradas.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| Verificación de firmas de imagen | 1 | `policies/kyverno/verify-image-signatures.yaml` |
| Revisión de configuración de Harbor | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `image-scanning`, `image-signing-and-provenance`, `supply-chain`, `artifact-repository-port`.
- Fuentes (consultada 2026-11-07): https://goharbor.io/docs/ (versión documentada v2.15.0). TODO-VERIFY detalles de proxy cache y robots en la versión usada.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T3
