---
name: feature-flags-openfeature
description: "Usar al introducir feature flags en un servicio Java: API OpenFeature, providers, contexto de evaluación, ciclo de vida y limpieza de flags."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Feature flags con OpenFeature

## Cuándo aplicar y cuándo no
- Aplica a activaciones graduales, kill switches y experimentos en servicios Java/Spring Boot.
- No aplica a configuración estática por entorno (ver `config-by-environment`) ni a permisos de usuario (ver `authz-rbac-abac-rebac`): un flag no es autorización.

## Reglas
- **MUST** acceder a los flags a través de la API de OpenFeature (estándar abierto, SDK Java) y no del SDK de un proveedor concreto, para poder cambiar de provider sin tocar el código de negocio.
- **MUST** elegir un provider sin licencia de pago por defecto (D16); fichero/ConfigMap o un servidor OSS compatible con OpenFeature. Comprobar provider concreto y versión.
- **MUST** pasar siempre un valor por defecto seguro en cada evaluación: si el provider cae, el sistema se comporta como "flag apagado".
- **MUST** tipificar y nombrar los flags (`orders.new-pricing.enabled`) con propietario, fecha de creación y fecha de retirada prevista.
- **MUST** clasificar cada flag: release (vida corta), ops/kill switch, experimento o permiso; solo los de release y experimento caducan.
- **MUST** eliminar el flag y el código muerto al completar el despliegue; un flag release sin retirar tras su fecha es deuda.
- **MUST NOT** meter PII ni secretos en el contexto de evaluación; usar identificadores opacos.
- **MUST NOT** anidar flags ni condicionar la corrección de datos a su estado sin plan de migración.
- **SHOULD** evaluar el flag en el borde del caso de uso, no en capas de dominio; inyectar un puerto `FeatureToggles`.
- **SHOULD** registrar cambios de flags en la auditoría y con un hook de OpenFeature para métricas/trazas.
- **SHOULD** probar ambas ramas del flag en tests.

## Por qué
OpenFeature separa la API de evaluación del proveedor: el contexto de evaluación y los hooks (validación, logging, telemetría) son conceptos del estándar. Los flags sin dueño ni fecha acumulan combinaciones imposibles de probar.

## Ejemplos
### Mal
```java
if (System.getenv("NEW_PRICING").equals("true")) { // sin default, sin dueño, difícil de cambiar
    return newPricing(order);
}
```
### Bien
```java
public interface FeatureToggles {
    boolean newPricingEnabled(String tenantId);
}

class OpenFeatureToggles implements FeatureToggles {
    private final Client client = OpenFeatureAPI.getInstance().getClient();

    @Override
    public boolean newPricingEnabled(String tenantId) {
        var ctx = new ImmutableContext(tenantId);       // identificador opaco
        return client.getBooleanValue("orders.new-pricing.enabled", false, ctx); // default seguro
    }
}
```
Firmas de `OpenFeatureAPI`/`ImmutableContext`: comprobar contra el SDK Java de la versión fijada.

## Checklist de revisión
- [ ] Acceso por puerto y API OpenFeature, no SDK de proveedor.
- [ ] Default seguro en cada evaluación.
- [ ] Propietario, tipo y fecha de retirada documentados.
- [ ] Sin PII en el contexto.
- [ ] Tests de ambas ramas; ticket de retirada creado.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit: solo el adaptador `OpenFeature*` importa `dev.openfeature` | 1 | pendiente (`policies/archunit/`) |
| Revisión de propietario/caducidad de flags | 3 | agente `code-reviewer` |
| Revisión trimestral de flags vencidos | 4 | humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `config-by-environment`, `spring-cloud-config-module`, `canary-and-traffic-splitting`, `hexagonal`.
- Fuentes: https://openfeature.dev/docs/reference/intro (consultada 2026-11-07: providers, evaluation context, hooks, SDK Java).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
