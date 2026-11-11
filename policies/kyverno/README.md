# kyverno

Dos políticas de [Kyverno](https://kyverno.io), el controlador de admisión que acepta o rechaza recursos en un clúster de Kubernetes.

**Estado: escritas y sin ejecutar.** Cada proyecto debe probarlas con la versión de Kyverno que instale.

| Fichero | Qué impone | Skill de origen |
|---|---|---|
| `workload-baseline.yaml` | La línea base de las cargas (Deployments y StatefulSets): solicitudes y límites de CPU y memoria, sondas, perfil seccomp `RuntimeDefault` y prohibición de la etiqueta `latest` | `workload-baseline` |
| `verify-image-signatures.yaml` | Las imágenes del proyecto están firmadas con cosign y se verifican en la admisión | `image-signing-and-provenance`, `admission-verification` |

## Cómo adoptarlas
1. Aplícalas primero en modo **auditoría** (`failureAction: Audit`) y revisa los informes de política hasta que no queden incumplimientos legítimos.
2. Pasa a modo de imposición (`Enforce`) cuando el atraso esté limpio.
3. Decide y documenta qué ocurre si el controlador de admisión no responde (fallar abierto o cerrado) y dale alta disponibilidad.

La acción se declara **por regla** (`validate.failureAction` o `verifyImages[].failureAction`): el campo `spec.validationFailureAction` está deprecado en la documentación de Kyverno.

## Pruebas
Kyverno incluye una herramienta de línea de comandos para probar políticas sin un clúster (`kyverno test`). El proyecto debe añadir casos que pasen y casos que fallen.
