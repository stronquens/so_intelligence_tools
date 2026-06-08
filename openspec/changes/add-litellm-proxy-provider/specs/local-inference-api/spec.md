# Delta Spec

## ADDED Requirements

### Requirement: Soporte de proveedor remoto OpenAI-compatible
El sistema SHALL poder enrutar peticiones de inferencia a un proveedor remoto OpenAI-compatible sin romper el contrato HTTP consumido por las herramientas cliente.

#### Scenario: El backend usa LiteLLM Proxy
- **WHEN** el sistema se configure con un proveedor remoto compatible con el formato OpenAI Chat Completions
- **THEN** la API SHALL seguir exponiendo los mismos endpoints del proyecto para las herramientas cliente
- **AND** SHALL autenticarse contra el proveedor remoto mediante variables de entorno

#### Scenario: El operador cambia entre proveedor local y remoto
- **WHEN** una persona cambie la configuración del proveedor en `.env`
- **THEN** el backend SHALL poder alternar entre `ollama` y `litellm_proxy` sin exigir cambios en los atajos, runners o herramientas cliente
