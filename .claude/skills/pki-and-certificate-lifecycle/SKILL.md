---
name: pki-and-certificate-lifecycle
description: "Usar al diseñar la PKI interna o el ciclo de vida de certificados TLS (emisión, renovación automática, revocación, inventario) con cert-manager u otra CA."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# PKI y ciclo de vida de certificados

## Cuándo aplicar y cuándo no
- Aplica a certificados de servidor, de cliente (mTLS) y de firma gestionados por la organización, y a la CA interna.
- No aplica a la rotación de claves de aplicación (ver `crypto-tls-mtls-key-rotation`) ni a la elección de algoritmos (ver `encryption-standards`).

## Reglas
- **MUST** automatizar emisión y renovación (ACME con cert-manager en Kubernetes, o la CA gestionada del proveedor); la renovación manual no escala.
- **MUST** asumir validez cada vez más corta: la CA/Browser Forum aprobó (ballot SC-081v3, 2025-04-11) máximos de 200 días desde 2026-03-15, 100 días desde 2027-03-15 y 47 días desde 2029-03-15 para certificados TLS públicos (fuente secundaria; TODO-VERIFY en cabforum.org).
- **MUST** mantener un inventario de certificados con dueño, entorno, fecha de caducidad y método de renovación, y alertar con antelación (p. ej. 30/14/7 días) sobre cualquier certificado sin renovar.
- **MUST** proteger la clave privada de la CA raíz fuera de línea; emitir con CA intermedias de ámbito limitado (por entorno o dominio).
- **MUST** generar claves en el sistema que las usa (CSR) y no copiarlas por correo ni tickets; claves privadas nunca en Git.
- **MUST** definir revocación y respuesta ante compromiso: quién revoca, en cuánto tiempo y cómo se reemite.
- **SHOULD** usar certificados de vida corta para mTLS interno (la malla Istio emite y rota los suyos) en lugar de certificados manuales.
- **SHOULD** monitorizar Certificate Transparency de los dominios propios para detectar emisiones no autorizadas.
- **SHOULD** usar registros CAA para limitar qué CA puede emitir para el dominio.
- **MUST NOT** usar certificados autofirmados en producción para tráfico entre servicios sin CA de confianza distribuida; MUST NOT desactivar la validación de certificados en clientes.

## Por qué
Las caídas por certificados caducados son un clásico evitable, y con plazos de 47 días la renovación manual deja de ser viable. Una jerarquía con raíz offline e intermedias acotadas limita el daño de un compromiso. En local se reproduce con una CA de desarrollo (cert-manager con emisor `selfSigned`/CA propia); la CA pública, CT y CAA reales no se reproducen en local.

## Ejemplos
### Mal
```yaml
# Certificado emitido a mano, renovación en un calendario personal
apiVersion: v1
kind: Secret
metadata: {name: tls-cert}
data: {tls.key: "changeme-base64-private-key"}   # clave privada en Git
```
### Bien
```yaml
# cert-manager.io/v1 (TODO-VERIFY version de API contra la instalada)
apiVersion: cert-manager.io/v1
kind: Certificate
metadata: {name: orders-api, namespace: orders}
spec:
  secretName: orders-api-tls
  dnsNames: ["orders.example.com"]
  duration: 1440h        # 60 dias
  renewBefore: 480h      # renueva con 20 dias de margen
  privateKey: {algorithm: ECDSA, size: 256, rotationPolicy: Always}
  issuerRef: {name: internal-ca, kind: ClusterIssuer}
```

## Checklist de revisión
- [ ] Emisión y renovación automáticas con alerta si falla.
- [ ] Inventario con dueño y caducidad.
- [ ] Raíz offline, intermedias acotadas, CAA configurado.
- [ ] Ninguna clave privada en repositorio.
- [ ] Procedimiento de revocación y reemisión probado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Rego: `Certificate` con `renewBefore`, `duration` y emisor declarados | 1 | pendiente (`policies/opa-conftest/`) |
| Detección de secretos/claves privadas en commits | 2 | hook de seguridad de la fábrica (`.claude/hooks/`) |
| Revisión de jerarquía CA y revocación | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `encryption-standards`, `crypto-tls-mtls-key-rotation`, `mtls-strict-and-peer-auth`, `ingress-and-egress-gateways`.
- Fuentes (2026-11-07): calendario SC-081v3 según fuentes secundarias (encryptionconsulting.com, sslinsights.com), pendiente de confirmar en cabforum.org; documentación de cert-manager — TODO-VERIFY.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
