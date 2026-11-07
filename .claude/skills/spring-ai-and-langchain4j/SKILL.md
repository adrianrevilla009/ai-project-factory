---
name: spring-ai-and-langchain4j
description: "Usar al elegir o integrar un framework LLM en Java/Spring Boot (Spring AI o LangChain4j): criterios de elección, abstracciones, aislamiento del proveedor y pruebas."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Spring AI y LangChain4j

## Cuándo aplicar y cuándo no
- Aplica al añadir llamadas a un LLM, embeddings, RAG, memoria o tool calling a un servicio Java.
- No aplica a ML clásico (ver `classical-mlops`, pendiente) ni a llamadas puntuales sin lógica, donde basta un cliente HTTP con timeout.

## Reglas
- **MUST** elegir UN framework por servicio y registrar la decisión en un ADR del proyecto (criterios: integración Spring Boot, madurez de la API, cobertura de proveedores y vector stores necesarios).
- **SHOULD** preferir Spring AI en servicios Spring Boot (autoconfiguración, `ChatClient`, advisors, observabilidad Micrometer); LangChain4j si se necesita `AiServices` declarativo o cobertura que Spring AI no tenga.
- **MUST** fijar la versión del BOM del framework en `dependencyManagement`; ambos evolucionan rápido y sus APIs cambian entre versiones menores (TODO-VERIFY versión vigente al arrancar el proyecto).
- **MUST** encapsular el framework tras un puerto propio (`interface AnswerGenerator`) en la capa de aplicación; el dominio no importa `org.springframework.ai` ni `dev.langchain4j`.
- **MUST** configurar timeouts, reintentos acotados y modelo/temperatura por propiedades, no en código.
- **MUST** leer claves del proveedor desde el gestor de secretos (ver `secrets-management`), nunca de `application.yml`.
- **MUST NOT** mezclar ambos frameworks en el mismo servicio.
- **SHOULD** probar con un `ChatModel` falso en tests unitarios y con un modelo local (Ollama) solo en tests de integración marcados.
- **MUST NOT** usar Lombok (D27).

## Por qué
Los frameworks LLM son capas finas sobre APIs de proveedor que cambian cada trimestre. Un puerto propio limita el radio de cambio a un adaptador, permite sustituir proveedor o framework y hace testeable la lógica sin red ni coste de tokens.

## Ejemplos
### Mal
```java
@Service
class ClaimService {
    String summarize(Claim c) {
        var client = ChatClient.create(chatModel);          // framework en el dominio
        return client.prompt().user("Resume: " + c.text()).call().content(); // sin límites ni plantilla
    }
}
```
### Bien
```java
public interface ClaimSummarizer {            // puerto, sin tipos del framework
    String summarize(String claimText);
}

@Component
class SpringAiClaimSummarizer implements ClaimSummarizer {
    private final ChatClient chat;

    SpringAiClaimSummarizer(ChatClient.Builder builder) {
        this.chat = builder.defaultSystem("Resume reclamaciones en 3 frases. Responde en español.").build();
    }

    @Override
    public String summarize(String claimText) {
        return chat.prompt().user(u -> u.text("Texto:\n{text}").param("text", claimText)).call().content();
    }
}
```
```yaml
spring:
  ai:
    openai:
      api-key: ${LLM_API_KEY}   # inyectada desde el gestor de secretos
```
Nombres de API (`ChatClient`, `defaultSystem`, `prompt().user(...)`, advisors) comprobados contra la documentación de Spring AI el 2026-11-07; propiedades por proveedor: TODO-VERIFY.

## Checklist de revisión
- [ ] Un solo framework y ADR de la decisión.
- [ ] Dominio sin imports del framework.
- [ ] Versión fijada; timeouts y modelo en configuración.
- [ ] Sin claves en el repo; tests sin red.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit: `domain..` no depende de `org.springframework.ai..`/`dev.langchain4j..` | 1 | `policies/archunit/` (pendiente) |
| Regla Semgrep: sin Lombok | 1 | `policies/semgrep/java-no-lombok.yaml` |
| Revisión de la decisión de framework | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `llm-gateway`, `rag-architecture`, `agents-and-tool-calling`, `llm-security`, `secrets-management`.
- Fuentes: Spring AI Reference, ChatClient API (docs.spring.io/spring-ai/reference/api/chatclient.html, 2026-11-07); LangChain4j, AI Services (docs.langchain4j.dev/tutorials/ai-services, 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
