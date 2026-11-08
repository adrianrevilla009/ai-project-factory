# capabilities

Traduce las respuestas de la entrevista de intake en módulos activos del proyecto.

- `capabilities.yaml` — preguntas de la entrevista (`id`, texto, tipo, valor por defecto) y qué módulos activa cada respuesta.
- `modules-map.yaml` — esqueleto que debe enlazar cada módulo con sus skills, policies y tests. **Las listas están vacías** y la oleada de cada módulo está asignada; falta rellenarlas.
- `interview/intake-script.md` — guion que sigue `project-discover` para hacer las preguntas y registrar las respuestas.

El resultado de la entrevista va a `.factory/state.json` del proyecto generado (`active_modules`) y lo lee el hook `load_context` en cada sesión.
