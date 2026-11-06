# Checklist · Gate 5 · Cloud readiness

- [ ] Cada componente de infra con etiqueta de madurez (máximo: validado estáticamente)
- [ ] Validación estática pasada: terraform validate, tflint, fmt, Checkov/Trivy, OPA sobre plan
- [ ] Documentación dice 'preparado para AWS, no verificado en real'
- [ ] Informe de coste estimado por tier (sin desplegar)
- [ ] Tabletop de DR ejecutado y documentado
- [ ] Matriz de paridad AWS↔local actualizada
- [ ] Riesgo de primer apply documentado en el README
