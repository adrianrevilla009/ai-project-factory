---
name: forms-and-validation
description: "Usar al construir formularios React: React Hook Form con esquemas Zod, mensajes de error accesibles, errores del servidor y envío seguro."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Formularios y validación

## Cuándo aplicar y cuándo no
- Aplica a cualquier formulario con más de un campo o con reglas de validación.
- No aplica a un input de búsqueda suelto sincronizado con la URL (ver `state-management`).

## Reglas
- **MUST** usar React Hook Form con `zodResolver` y un esquema Zod por formulario; el tipo del formulario sale de `z.infer`.
- **MUST** que la validación del cliente sea ayuda de UX: el backend valida siempre (`input-validation-output-encoding`).
- **MUST** mostrar los errores junto al campo, enlazados con `aria-invalid` y `aria-describedby`, y mover el foco al primer error al enviar.
- **MUST** deshabilitar el envío mientras `isSubmitting` para evitar dobles envíos; la idempotencia real es del backend (`idempotency-keys`).
- **MUST** mapear los errores 400/422 del servidor (Problem Details) a campos con `setError`.
- **SHOULD** compartir el esquema entre formulario y cliente API solo si procede del contrato OpenAPI; no duplicar reglas a mano (comprobar generación de Zod desde OpenAPI).
- **SHOULD** valores por defecto explícitos en `defaultValues`; sin inputs no controlados mezclados.
- **MUST NOT** guardar contraseñas ni datos sensibles en el estado global ni en el almacenamiento del navegador.
- **MUST NOT** usar `any` en los handlers (`typescript-strict-rules`).

## Por qué
Un esquema único da validación, tipos y mensajes coherentes. React Hook Form reduce renders al no controlar cada tecla. El cliente puede ser eludido, por eso el servidor es la autoridad. Los errores accesibles son requisito de WCAG 2.2 (comprobar criterio exacto). Firmas de `zodResolver` y de `useForm` dependen de versión (comprobar al fijar la versión).

## Ejemplos
### Mal
```tsx
const [email, setEmail] = useState('');
const [error, setError] = useState('');
<input value={email} onChange={e => setEmail(e.target.value)} />
<button onClick={() => { if (!email.includes('@')) setError('mal'); else api.post(email); }}>Enviar</button>
```
### Bien
```tsx
const Schema = z.object({
  email: z.string().email('Email no válido'),
  quantity: z.coerce.number().int().min(1),
});
type FormValues = z.infer<typeof Schema>;

const { register, handleSubmit, setError, formState: { errors, isSubmitting } } =
  useForm<FormValues>({ resolver: zodResolver(Schema), defaultValues: { email: '' } });

const onSubmit = handleSubmit(async (values) => {
  const res = await createOrder(values);
  if (res.status === 422) setError('email', { message: res.problem.detail });
});

<form onSubmit={onSubmit} noValidate>
  <input {...register('email')} aria-invalid={!!errors.email} aria-describedby="email-err" />
  {errors.email && <p id="email-err" role="alert">{errors.email.message}</p>}
  <button disabled={isSubmitting}>Enviar</button>
</form>
```

## Checklist de revisión
- [ ] Esquema Zod + `zodResolver`; tipos inferidos.
- [ ] Errores accesibles y foco al primer error.
- [ ] Errores del servidor mapeados a campos.
- [ ] Envío bloqueado durante `isSubmitting`; backend valida.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| eslint-plugin-jsx-a11y (etiquetas, aria) | 1 | pendiente (configuración del proyecto generado) |
| Test de componente: envío inválido muestra error asociado | 3 | tests del proyecto generado |
| Revisión de formularios | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `state-management`, `typescript-strict-rules`, `error-handling-and-boundaries`, `error-handling-problem-details`, `input-validation-output-encoding`.
- Fuentes: documentación de React Hook Form, Zod y @hookform/resolvers (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
