# Purpose

Definir el comportamiento esperado del servicio de inferencia multimodal que alimentará las herramientas de IA del sistema.
## Requirements
### Requirement: Servicio de inferencia accesible por API
El sistema SHALL exponer un servicio accesible por API local al sistema para recibir peticiones de inferencia desde las herramientas cliente del sistema operativo.

#### Scenario: El cliente invoca una tarea textual
- **WHEN** un script cliente envía una petición válida de texto al servicio local
- **THEN** la API SHALL devolver una respuesta estructurada utilizable por la herramienta solicitante

#### Scenario: El servicio está pensado para uso local al sistema
- **WHEN** el sistema se despliega en una máquina del usuario
- **THEN** la API SHALL poder ejecutarse en local al sistema operativo del usuario aunque el proveedor efectivo de inferencia sea local o remoto

#### Scenario: Puerto local configurable
- **WHEN** otro proceso local ya use el puerto por defecto del backend
- **THEN** el servicio SHALL poder moverse a otro puerto local mediante configuración
- **AND** las herramientas cliente SHALL poder apuntar a la nueva base URL sin cambios de código

### Requirement: Backend Python gestionado dentro del repositorio
El sistema SHALL gestionar el servicio local de inferencia como un proyecto Python con Poetry y un entorno `.venv` dentro del propio repositorio.

#### Scenario: Preparación del entorno del backend
- **WHEN** una persona necesite instalar dependencias o ejecutar comandos del backend
- **THEN** SHALL hacerlo mediante Poetry
- **AND** el entorno virtual SHALL existir dentro de `.venv/` en la raíz del proyecto

### Requirement: Inferencia multimodal sobre modelo local
El sistema SHALL soportar un modelo local multimodal que permita procesar al menos texto e imagen dentro del mismo backend de inferencia.

#### Scenario: Una herramienta envía una imagen para extracción de contenido
- **WHEN** una herramienta cliente envía una imagen o recorte de pantalla a la API
- **THEN** el backend SHALL aceptar la entrada multimodal y producir una respuesta textual asociada a esa imagen

#### Scenario: Una herramienta usa solo texto
- **WHEN** una herramienta cliente envía una petición puramente textual
- **THEN** el backend SHALL atenderla sin exigir entradas visuales adicionales

#### Scenario: Una herramienta envía audio para transcripción
- **WHEN** una herramienta cliente envía un fragmento de audio capturado localmente
- **THEN** el backend SHALL poder procesarlo para devolver una transcripción textual utilizable por la herramienta

#### Scenario: Una herramienta solicita transcripción o traducción en streaming
- **WHEN** una herramienta cliente envía audio continuo o fragmentos sucesivos para procesamiento casi en tiempo real
- **THEN** el backend SHALL poder producir resultados parciales o actualizaciones frecuentes aptas para una interfaz en vivo

### Requirement: Configuración de perfil de razonamiento por petición
El sistema SHALL permitir que las herramientas cliente expresen si una petición prioriza velocidad o razonamiento más profundo.

#### Scenario: Una herramienta solicita respuesta rápida
- **WHEN** una herramienta cliente envía una petición con el modo de razonamiento desactivado o enfocado a baja latencia
- **THEN** el backend SHALL priorizar una respuesta lo más rápida posible

#### Scenario: Una herramienta solicita más deliberación
- **WHEN** una herramienta cliente envía una petición con un nivel de razonamiento mayor
- **THEN** el backend SHALL permitir una respuesta más lenta si eso mejora la calidad esperada

#### Scenario: El backend cambia su estrategia interna
- **WHEN** la implementación necesite resolver estos modos con un solo modelo configurable o con varios perfiles de modelo
- **THEN** la interfaz pública SHALL mantener un contrato estable a nivel de petición

#### Scenario: Gemma 4 usa un mapeo inicial simplificado de thinking
- **WHEN** la primera implementación use Gemma 4 sobre Ollama
- **THEN** `reasoning_mode` SHALL mantenerse como contrato público
- **AND** el backend MAY resolver inicialmente `off` y `low` como thinking desactivado
- **AND** el backend MAY resolver inicialmente `medium` y `high` como thinking activado

#### Scenario: El runtime requiere una señal explícita para desactivar thinking
- **WHEN** el runtime local basado en Ollama necesite una configuración explícita para evitar thinking en peticiones instantáneas
- **THEN** el backend SHALL poder enviar la configuración equivalente a `think: false` para `reasoning_mode=off|low`
- **AND** SHALL poder enviar la configuración equivalente a `think: true` para `reasoning_mode=medium|high`

### Requirement: Despliegue portable mediante contenedores
El sistema SHALL poder desplegar el servicio de inferencia dentro de Docker para facilitar instalacion, aislamiento y portabilidad.

#### Scenario: Despliegue inicial en Linux
- **WHEN** el proyecto se instala en un entorno Linux soportado
- **THEN** el backend SHALL poder levantarse mediante una configuracion basada en Docker

#### Scenario: Preparacion para otros sistemas
- **WHEN** se quiera portar el proyecto a otro sistema operativo
- **THEN** la arquitectura SHALL mantener la capa de inferencia aislada detras de la misma interfaz de API

#### Scenario: El usuario quiere liberar recursos del sistema
- **WHEN** el usuario decide apagar temporalmente la infraestructura local de inferencia
- **THEN** el despliegue SHALL permitir detener los contenedores asociados para liberar recursos del equipo

#### Scenario: Windows user startup
- **WHEN** the project is installed on Windows
- **THEN** the local inference API SHALL provide a user-level Startup launcher installer
- **AND** the launcher SHALL start the API from the project virtual environment without requiring administrator privileges
- **AND** the launcher SHALL run without leaving a visible terminal window open
- **AND** the launcher SHALL write process output to a diagnostic log file.

#### Scenario: El equipo quiere probar otro modelo local
- **WHEN** el proyecto necesite sustituir el modelo local validado por otro nuevo
- **THEN** la arquitectura SHALL permitir cambiar el runtime o perfil de modelo con el menor impacto posible sobre la interfaz publica del API

### Requirement: Compatibilidad inicial con Ollama y Gemma
El sistema SHALL permitir una primera implementación basada en Ollama y una familia de modelos Gemma multimodales en local.

#### Scenario: Primera iteración técnica del backend
- **WHEN** el equipo implemente la primera versión del servicio
- **THEN** esta SHALL poder apoyarse en Ollama como runtime de modelo local

#### Scenario: Runtime recomendado actual para corrección de texto local
- **WHEN** el equipo necesite elegir el runtime recomendado actual para corrección de texto local con baja latencia
- **THEN** el modelo recomendado SHALL ser `gemma4-e2b-longctx:latest`
- **AND** el proyecto MAY mantener evidencia histórica de benchmarks de modelos anteriores en los changes archivados

#### Scenario: Evolución futura del proveedor local
- **WHEN** el proyecto necesite cambiar de modelo o runtime en una iteración posterior
- **THEN** la interfaz consumida por las herramientas cliente SHALL minimizar el acoplamiento a ese proveedor

### Requirement: Ollama startup warm-up
The local inference API SHALL support optional startup warm-up for the configured Ollama model.

#### Scenario: Warm-up is enabled
- **GIVEN** `OLLAMA_WARMUP_ON_STARTUP` is enabled
- **AND** the configured provider is Ollama
- **WHEN** the local inference API starts
- **THEN** it SHALL send a minimal generation request for the configured model
- **AND** it SHALL use the configured Ollama keep-alive value.

#### Scenario: Warm-up fails
- **GIVEN** startup warm-up is enabled
- **AND** Ollama is unreachable
- **WHEN** the local inference API starts
- **THEN** it SHALL log the warm-up failure
- **AND** it SHALL continue starting so `/status` can report the degraded runtime.

### Requirement: Soporte de proveedor remoto OpenAI-compatible
El sistema SHALL poder enrutar peticiones de inferencia a un proveedor remoto OpenAI-compatible sin romper el contrato HTTP consumido por las herramientas cliente.

#### Scenario: El backend usa LiteLLM Proxy
- **WHEN** el sistema se configure con un proveedor remoto compatible con el formato OpenAI Chat Completions
- **THEN** la API SHALL seguir exponiendo los mismos endpoints del proyecto para las herramientas cliente
- **AND** SHALL autenticarse contra el proveedor remoto mediante variables de entorno

#### Scenario: El operador cambia entre proveedor local y remoto
- **WHEN** una persona cambie la configuración del proveedor en `.env`
- **THEN** el backend SHALL poder alternar entre `ollama` y `litellm_proxy` sin exigir cambios en los atajos, runners o herramientas cliente
