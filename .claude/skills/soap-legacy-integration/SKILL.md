---
name: soap-legacy-integration
description: "Usar al consumir o exponer servicios SOAP/WSDL de sistemas heredados: contrato WSDL, XXE, timeouts y capa anticorrupción."
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Integración SOAP y sistemas heredados

## Cuándo aplicar y cuándo no
- Aplica a clientes o servidores SOAP/WSDL impuestos por un sistema externo o heredado.
- No aplica a APIs nuevas: usar REST/OpenAPI (`openapi-contract-first`) o gRPC salvo mandato contrario.

## Reglas
- **MUST** partir del WSDL/XSD del proveedor como contrato (contract-first) y generar clases en build (JAXB / Spring-WS / CXF); **MUST NOT** editarlas a mano ni versionarlas si se generan.
- **MUST** aislar el servicio SOAP tras una **capa anticorrupción** (puerto + adaptador): el dominio nunca ve tipos JAXB.
- **MUST** configurar timeouts de conexión y lectura y un circuit breaker/reintentos solo en operaciones idempotentes.
- **MUST** deshabilitar DTD y entidades externas en todo parser XML (XXE): `disallow-doctype-decl` o `ACCESS_EXTERNAL_DTD=""`.
- **MUST** TLS (mTLS si el proveedor lo exige) y, si se pide WS-Security, usar la librería estándar (Wss4j) con el mismo tratamiento de secretos que otros credenciales.
- **MUST** mapear `SOAP Fault` a excepciones tipadas del puerto y no filtrar su detalle al cliente final.
- **SHOULD** pruebas con respuestas XML grabadas (WireMock) y validación contra el XSD.
- **SHOULD** registrar el envelope solo con campos sensibles enmascarados.
- **SHOULD** documentar la fecha de retirada o plan de sustitución del sistema heredado.

## Por qué
El XML con entidades externas permite leer ficheros locales o hacer SSRF. Los tipos generados acoplan el dominio al formato del proveedor y cualquier cambio del WSDL rompe todo el código. Sin timeouts, un SOAP lento agota hilos. Las APIs de JAXB/Jakarta XML y de Spring-WS deben verificarse en su documentación.

## Ejemplos
### Mal
```java
DocumentBuilder b = DocumentBuilderFactory.newInstance().newDocumentBuilder(); // XXE por defecto en algunas configuraciones
Document d = b.parse(request.getInputStream());
CustomerType t = soapClient.getCustomer(id);    // tipo JAXB llega al dominio y sin timeout
```
### Bien
```java
DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
f.setXIncludeAware(false);
f.setExpandEntityReferences(false);

public interface CustomerDirectory {                // puerto del dominio
    Customer findById(CustomerId id);
}

class SoapCustomerDirectory implements CustomerDirectory {   // adaptador
    public Customer findById(CustomerId id) {
        try {
            return mapper.toDomain(client.getCustomer(id.value()));
        } catch (SoapFaultClientException e) {
            throw new CustomerLookupException(id, e);
        }
    }
}
```
```xml
<!-- generación en build desde el WSDL del proveedor -->
<wsdlLocation>src/main/resources/wsdl/customer.wsdl</wsdlLocation>
```
(configuración del plugin Maven JAXB/CXF).

## Criterios de decisión y trampas
### Cómo decidir
- Encapsula el servicio SOAP tras un puerto y una capa anticorrupción; trátalo como un tercero poco fiable.
- Genera el cliente desde el contrato y fija las versiones.
### Trampas frecuentes
- Tipos generados del WSDL por todo el dominio.
- Sin tiempos máximos ni reintentos controlados.
- Seguridad débil (sin TLS ni validación de firmas) por «es interno».
- Configuración XML sin protección frente a entidades externas.
- Sin pruebas con respuestas reales del legado.
### Evidencia
- Pruebas con respuestas grabadas del servicio real y un tiempo máximo configurado.

## Checklist de revisión
- [ ] WSDL/XSD versionado; clases generadas en build, no a mano.
- [ ] Capa anticorrupción: sin tipos JAXB en dominio.
- [ ] Timeouts, reintentos solo idempotentes, breaker.
- [ ] Parsers XML sin DTD ni entidades externas.
- [ ] Faults mapeados; logs enmascarados; plan de retirada.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `DocumentBuilderFactory.newInstance()` sin deshabilitar DTD | 1 | `policies/semgrep/xml-parser-xxe.yaml` |
| ArchUnit: dominio no depende de paquetes generados | 1 | `policies/archunit/` (pendiente) |
| Revisión del adaptador | 3 | agente `code-reviewer` |

> Estado: reglas probadas con `semgrep --test` (casos en `tests/semgrep/`); detectan patrones sintácticos, no flujos de datos.

## Relacionados, fuentes y mantenimiento
- Relacionados: `deserialization-xxe-ssrf-traversal`, `wiremock-and-stubbing`, `contract-testing-pact`, `connascence-and-coupling`.
- Fuentes: OWASP XML External Entity Prevention Cheat Sheet; documentación de Spring Web Services.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
