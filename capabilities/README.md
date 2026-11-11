# capabilities

Traduce las respuestas de la entrevista de intake en **módulos activos** del proyecto, y cada módulo en las skills, políticas y pruebas que guían su implementación. Es lo que decide qué parte de la fábrica se aplica a un proyecto concreto.

## Contenido
| Fichero | Qué es |
|---|---|
| `capabilities.yaml` | Las preguntas de la entrevista: `id`, texto, tipo, valor por defecto, ayuda y qué módulos activa cada respuesta. Incluye `always_on`, los módulos que siempre se aplican |
| `modules-map.yaml` | Para cada módulo, sus bloques y skills, políticas, pruebas y tableros. Es el índice de «qué leer y qué cumplir» de cada módulo |
| `interview/intake-script.md` | El guion que sigue `product-owner` con `business-analyst` para hacer las preguntas, en bloques, registrando las respuestas literales |

## Las preguntas de la entrevista
Las catorce preguntas cubren: multi-tenencia, búsqueda, analítica, documentos con OCR, chatbot con RAG, flujos de trabajo, pagos, notificaciones, tiempo real, back-office, historial completo, tier de resiliencia (0–3, por defecto 1), frontend y datos de categorías especiales (que activa una revisión de cumplimiento).

## Módulos
- **Siempre activos (`always_on`):** `backend-java-spring`, `local-k8s`, `observability`, `ci-cd`, `security`, `testing`, `claude-config`, `devcontainer` y `docs`. Llevan bloques enteros de skills.
- **Activables por la entrevista:** `frontend-react`, `event-sourcing`, `outbox`, `multi-tenant`, `search`, `rag`, `agents`, `idp-documents`, `workflow`, `notifications`, `data-platform`, `payments`, `realtime`, `back-office` y `compliance-review`.

Si una respuesta es «no sé», se aplica el valor por defecto y se registra como supuesto.

## Cómo se usa
1. El comando `/project-init` conduce la entrevista y rellena las capacidades del proyecto.
2. `/capability-select` mapea las respuestas a módulos con `capabilities.yaml` y carga lo que cada módulo necesita desde `modules-map.yaml`.
3. El resultado queda en `.factory/state.json` del proyecto generado (`active_modules`), y el hook `load_context` lo recuerda al agente en cada sesión.
4. El bootstrap copia al proyecto solo las skills de los módulos activos (skill `bootstrap-generated-project-claude-config`).

## Garantías
`make validate` comprueba que todos los módulos que activa `capabilities.yaml` existen en `modules-map.yaml` y que cada skill, bloque, política y prueba que cita existe. Al añadir una pregunta o un módulo, actualiza ambos ficheros.
