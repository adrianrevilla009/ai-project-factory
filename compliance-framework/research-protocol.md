# Protocolo de investigación normativa
1. Partir del cuestionario de aplicabilidad y de la normativa candidata del perfil de dominio.
2. Para cada norma, buscar la **fuente oficial** (diario oficial, EUR-Lex, regulador). Nunca de memoria.
3. Crear la ficha (`regulation-entry.schema.yaml`) con `status: draft-to-confirm`, URL oficial y `verified_at`.
4. Mapear obligaciones a controles (`obligation-to-control-mapping.schema.yaml`) reutilizando los controles ya mapeados en proyectos anteriores.
5. El agente `compliance-analyst` **prepara, no dictamina**. Un humano de legal/cumplimiento valida en el Gate 0 y se registra.
6. Las normas activan cosas concretas (p. ej. residencia de datos → SCP de regiones; supresión + event sourcing → cifrado por sujeto).
