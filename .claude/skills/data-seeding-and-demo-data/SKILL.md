---
name: data-seeding-and-demo-data
description: "Usar al cargar datos de demo o de desarrollo en el clúster local: seeds idempotentes, sintéticos y sin PII, aplicados por Job de Kubernetes."
metadata:
  block: "28-local-kubernetes"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Seeding y datos de demo

## Cuándo aplicar y cuándo no
- Aplica a `make local-seed`, a los Jobs de carga inicial y a los datasets de demo del clúster local.
- No aplica a datos de tests unitarios (builders/fixtures) ni a migraciones de esquema (Flyway/Liquibase), que se ejecutan siempre.

## Reglas
- **MUST** que los datos sean sintéticos: generados o escritos a mano, nunca volcados de un entorno real, ni anonimizados a medias.
- **MUST** que el seed sea idempotente: reejecutarlo no duplica ni falla (`INSERT ... ON CONFLICT DO NOTHING`, `PutItem` con clave determinista).
- **MUST** separar esquema (migraciones) de datos de demo; el seed vive en un perfil o carpeta propia y nunca se empaqueta en la imagen de producción.
- **MUST** respetar la regla de no doble escritura (4.5): cada dato se siembra en un único almacén, el de su agregado.
- **MUST** ejecutar el seed como `Job` de Kubernetes con `restartPolicy: OnFailure` y `backoffLimit` acotado, tras `readiness` de la base de datos.
- **SHOULD** usar semilla fija en generadores aleatorios para que la demo sea reproducible.
- **SHOULD** dimensionar el volumen al perfil (`minimal`: cientos de filas; `full`: miles) según `resource-budgets`.
- **MUST NOT** incluir correos, nombres, teléfonos ni documentos reales; usar dominios `example.com` y credenciales `example`/`changeme`.
- **MUST NOT** ejecutar el seed contra endpoints que no sean el clúster local.

## Por qué
Un clúster vacío no demuestra nada y uno con datos reales es una fuga de información. La idempotencia permite `local-up` repetido sin limpiar volúmenes.

## Ejemplos
### Mal
```sql
INSERT INTO customer (email, name) SELECT email, name FROM prod_dump.customer;
```
### Bien
```sql
INSERT INTO customer (id, email, name)
VALUES ('00000000-0000-0000-0000-000000000001', 'demo.user@example.com', 'Demo User')
ON CONFLICT (id) DO NOTHING;
```
```yaml
apiVersion: batch/v1
kind: Job
metadata: { name: seed-demo-data }
spec:
  backoffLimit: 3
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: seed
          image: registry.example/seed:local
          env:
            - { name: DB_PASSWORD, value: changeme-local }
```

## Checklist de revisión
- [ ] Datos sintéticos, dominios `example.com`.
- [ ] Reejecutar `make local-seed` dos veces no cambia el resultado.
- [ ] El seed no está en la imagen desplegable.
- [ ] Un dato se escribe en un solo almacén.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Hook de detección de secretos al editar | 2 | `.claude/hooks/` (pre-tool-use; ver hooks de seguridad) |
| Idempotencia y ausencia de PII | 3 | revisión humana / agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `local-profiles`, `resource-budgets`, `dev-loop`, `cluster-tooling`.
- Fuentes: documentación de Kubernetes sobre Jobs (comprobar URL y campos vigentes).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
