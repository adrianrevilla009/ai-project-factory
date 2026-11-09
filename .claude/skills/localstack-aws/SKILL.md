---
name: localstack-aws
description: "Usar al probar código que usa S3, SQS, SNS, DynamoDB u otros servicios AWS con LocalStack en local o CI, y para saber qué NO reproduce."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# LocalStack para tests de servicios AWS

## Cuándo aplicar y cuándo no
- Aplica a tests de integración de adaptadores que usan el AWS SDK for Java v2 contra S3, SQS, SNS, DynamoDB, etc.
- No aplica a validar IAM, SCP, KMS real, redes/VPC, cuotas, latencias o consistencia de AWS: LocalStack no lo reproduce.

## Reglas
- **MUST** tratar LocalStack como emulador de API para tests de comportamiento del adaptador, nunca como evidencia de que funciona en AWS.
- **MUST** documentar en el test o README qué servicios se emulan y qué NO se reproduce (políticas IAM reales, SCP, cifrado KMS con claves reales, límites y throttling, eventual consistency real).
- **MUST** configurar el endpoint por propiedades (`endpointOverride`) solo en el perfil de test; el código de producción no conoce LocalStack.
- **MUST** usar credenciales falsas obvias (`example`/`changeme`) en el contenedor; nunca credenciales reales.
- **SHOULD** levantar LocalStack con Testcontainers (módulo LocalStack) y fijar la imagen con tag explícito.
- **SHOULD** limitar los servicios habilitados a los necesarios para acelerar el arranque.
- **MUST NOT** afirmar "probado en AWS" ni "listo para producción en AWS" por pasar tests en LocalStack; la fórmula es "preparado para AWS, no verificado en real" (ADR-0004).
- **MUST** tener en cuenta que desde el 2026-03-23 no existe la edición Community: la imagen requiere cuenta y auth token, y el plan gratuito es solo para uso no comercial (verificado el 2026-11-08, ver `aws-emulation`). En un proyecto corporativo su uso exige plan de pago y un ADR; preferir emuladores sin cuenta (DynamoDB Local, ElasticMQ, MinIO) cuando basten.
- **MUST NOT** depender de funcionalidades de pago de LocalStack por defecto (D16); si un test las requiere, es una decisión explícita y documentada.

## Por qué
Emular la API acelera el feedback y evita costes y credenciales, pero oculta justo lo que suele fallar en AWS: permisos, políticas de recurso y configuración de red. Por eso el resultado verde es evidencia parcial y debe declararse así.

## Ejemplos
### Mal
```java
// Cliente construido con endpoint de LocalStack dentro del código de producción
S3Client s3 = S3Client.builder().endpointOverride(URI.create("http://localhost:4566")).build();
// README: "storage verificado con LocalStack, listo"  (mala redacción: sugiere evidencia en AWS real)
```
### Bien
```java
@Testcontainers
class DocumentStorageIT {
    @Container
    static LocalStackContainer localstack =
        new LocalStackContainer(DockerImageName.parse("localstack/localstack:<tag-fijo>")) // fijar un tag concreto; requiere auth token
            .withServices(LocalStackContainer.Service.S3);

    S3Client s3 = S3Client.builder()
        .endpointOverride(localstack.getEndpoint())
        .region(Region.of(localstack.getRegion()))
        .credentialsProvider(StaticCredentialsProvider.create(
            AwsBasicCredentials.create("example-access", "example-changeme")))
        .build();

    @Test
    void storesAndReadsDocument() { /* put + get del adaptador */ }
}
```
Limitaciones documentadas: sin IAM real, sin KMS real, sin VPC; verificación pendiente en AWS real.

## Criterios de decisión y trampas
### Cómo decidir
- Para DynamoDB, el emulador oficial o un contenedor de DynamoDB Local suele bastar y no exige cuenta; usa un emulador generalista solo si el servicio no tiene alternativa (ver `aws-emulation` por la licencia).
- Pruebas de adaptador contra el emulador; comportamiento de IAM, cuotas y consistencia se declara «no verificado».
### Trampas frecuentes
- Concluir que funciona en AWS porque pasa en el emulador (permisos, consistencia, cuotas, latencias y mensajes de error difieren).
- Ramas `if (local)` en el código de producción.
- Credenciales reales en un contenedor de pruebas.
- Fijar la imagen sin tag y que el CI cambie de comportamiento un día.
### Evidencia
- Un apartado del README que lista qué servicios se emulan y qué no se reproduce.

## Checklist de revisión
- [ ] El endpoint de LocalStack solo existe en configuración de test.
- [ ] Se enumera lo que no se reproduce.
- [ ] Ninguna afirmación de verificación en AWS real.
- [ ] Credenciales claramente falsas; imagen con tag fijo.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validador de afirmaciones honestas | 1 | `factory/validators/honest_claims.py` (`make validate`) |
| Revisión de limitaciones declaradas | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `integration-testing-testcontainers`, `cloud-iam-least-privilege`, `verify-before-asserting`.
- Fuentes: documentación de LocalStack y AWS SDK for Java v2 — https://blog.localstack.cloud/the-road-ahead-for-localstack/ (fin de la edición Community, 2026-03-23); la cobertura de servicios se comprueba en la documentación de la edición contratada.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
