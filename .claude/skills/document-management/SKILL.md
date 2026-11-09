---
name: document-management
description: "Usar al diseñar el almacenamiento de documentos de usuario (PDF, contratos, adjuntos): objeto en S3 más metadatos en BD, versionado, retención, hash y control de acceso."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Gestión documental

## Cuándo aplicar y cuándo no
- Aplica a aplicaciones que guardan, versionan, buscan y descargan documentos de negocio.
- No aplica a la extracción de datos (ver `intelligent-document-processing`) ni a la validación de subidas (ver `file-upload-security`).

## Reglas
- **MUST** guardar el binario en almacenamiento de objetos (S3 en AWS; MinIO en local) y los metadatos en la base transaccional; nunca el binario en la BD relacional salvo ficheros diminutos justificados.
- **MUST** no duplicar la escritura de metadatos en Postgres y NoSQL (regla 4.5): una sola fuente de verdad por dato.
- **MUST** guardar por documento: id, hash SHA-256, tamaño, tipo MIME detectado, propietario/tenant, clasificación de datos, versión, fecha, clave del objeto.
- **MUST** tratar los documentos como inmutables: una modificación crea una versión nueva; el borrado es lógico y con retención definida.
- **MUST** servir descargas mediante URL prefirmada de corta duración o un endpoint que compruebe autorización por documento y tenant (ver `authz-rbac-abac-rebac`).
- **MUST** cifrar en reposo (SSE-KMS en AWS; preparado para AWS, no verificado en real) y en tránsito.
- **MUST** definir retención y borrado según clasificación y normativa aplicable (borrador por confirmar con fuente oficial).
- **MUST** ordenar el flujo para evitar objetos huérfanos: subir a una clave temporal, registrar metadatos y confirmar; un job limpia temporales caducados.
- **SHOULD** generar claves de objeto opacas (UUID) y no derivarlas del nombre original, que se guarda como metadato.
- **SHOULD** activar versionado del bucket y reglas de ciclo de vida para versiones antiguas.
- **MUST NOT** exponer el bucket públicamente ni devolver rutas internas al cliente.
- **MUST NOT** usar el nombre de fichero del usuario como ruta (ver `file-upload-security`).

## Por qué
Binario y metadatos tienen ritmos y costes distintos: el objeto escala barato en S3 y los metadatos necesitan transacciones y consultas. El hash permite detectar duplicados y manipulación, y la inmutabilidad da trazabilidad. Los fallos típicos son enlaces adivinables, borrados sin retención y objetos huérfanos tras subidas a medias.

## Ejemplos
### Mal
```java
Files.copy(upload.getInputStream(), Path.of("/data/" + upload.getOriginalFilename())); // path traversal, sin hash, sin versión
```
### Bien
```java
@Transactional
public DocumentVersion store(UUID tenantId, UUID docId, InputStream in, String originalName) {
    String key = "tenant/" + tenantId + "/doc/" + docId + "/" + UUID.randomUUID();
    HashingResult stored = objectStore.putWithSha256(key, in);       // sube y calcula SHA-256
    int next = versions.nextVersion(docId);
    return versions.save(new DocumentVersion(docId, next, key, stored.sha256(),
            stored.size(), originalName, Instant.now()));
}
```
```sql
CREATE TABLE document_version (
  document_id uuid NOT NULL, version int NOT NULL, object_key text NOT NULL,
  sha256 char(64) NOT NULL, size_bytes bigint NOT NULL, original_name text NOT NULL,
  created_at timestamptz NOT NULL, PRIMARY KEY (document_id, version));
```

## Criterios de decisión y trampas
### Cómo decidir
- Almacena con versión, metadatos, permisos y retención; sirve descargas con comprobación de autorización por documento.
- Separa contenido y metadatos.
### Trampas frecuentes
- Enlaces permanentes públicos.
- Permisos solo por carpeta.
- Sin versionado ni retención.
- Nombres de archivo del usuario como ruta.
- Sin registro de acceso.
### Evidencia
- Una prueba comprueba que un usuario no puede acceder al documento de otro.

## Checklist de revisión
- [ ] Binario en objeto, metadatos en una sola base.
- [ ] Hash, versión y tenant por documento.
- [ ] Descarga autorizada por documento (sin enlaces permanentes).
- [ ] Cifrado, retención y borrado definidos.
- [ ] Limpieza de temporales y claves opacas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Checkov: bucket S3 sin acceso público y con cifrado | 1 | pendiente (`policies/iac-checks/`) |
| Test de autorización por documento (IDOR) | 1 | pendiente (proyecto generado) |
| Revisión de retención y clasificación | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `intelligent-document-processing`, `ocr-options`, `file-upload-security`, `pii-and-data-classification`, `storage-and-load-balancing`.
- Fuentes: documentación oficial de Amazon S3 (versionado, SSE-KMS, URL prefirmadas). En local MinIO no reproduce IAM/KMS de AWS.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
