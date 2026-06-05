## ADDED Requirements

### Requirement: Primera iteración batch para texto e imagen
La primera implementación de `local-inference-api` SHALL limitarse a peticiones batch de texto e imagen antes de abordar flujos de audio o streaming.

#### Scenario: Una herramienta envía una petición textual
- **WHEN** una herramienta cliente envía una petición textual válida a la primera versión del API
- **THEN** el servicio SHALL devolver una respuesta textual estructurada

#### Scenario: Una herramienta envía una imagen para extracción textual
- **WHEN** una herramienta cliente envía una imagen válida a la primera versión del API
- **THEN** el servicio SHALL procesarla y devolver el texto resultante en una respuesta estructurada

### Requirement: Endpoint de salud del servicio
La primera implementación del API SHALL exponer un endpoint mínimo de salud para comprobar disponibilidad del servicio.

#### Scenario: Comprobación local de disponibilidad
- **WHEN** un cliente o proceso de validación consulta el endpoint de salud
- **THEN** el servicio SHALL responder con un estado legible por máquina indicando que el API está levantado

### Requirement: Endpoint separado para estado operativo
La primera implementación del API SHALL exponer un endpoint separado para consultar el estado operativo del runtime local y de la infraestructura asociada.

#### Scenario: Un cliente necesita conocer el estado del runtime
- **WHEN** una herramienta o proceso consulta el endpoint de estado
- **THEN** el servicio SHALL responder con información operativa del runtime configurado sin mezclar esa responsabilidad con el healthcheck básico

### Requirement: Adaptador interno para Ollama
El servicio SHALL encapsular la comunicación con Ollama detrás de una capa interna propia en lugar de mezclarla directamente con los endpoints HTTP.

#### Scenario: El endpoint textual necesita inferencia
- **WHEN** una petición HTTP requiere ejecutar el modelo local
- **THEN** el endpoint SHALL delegar la llamada al runtime a un adaptador interno de Ollama

### Requirement: Perfil de razonamiento configurable en la primera iteración
La primera implementación del API SHALL aceptar un nivel de razonamiento configurable por petición para distinguir entre respuestas rápidas y respuestas más deliberadas.

#### Scenario: Una herramienta pide el modo más rápido
- **WHEN** una herramienta cliente envía una petición con `reasoning_mode` desactivado o equivalente
- **THEN** el servicio SHALL intentar minimizar la latencia de la respuesta

#### Scenario: Una herramienta pide un modo más inteligente
- **WHEN** una herramienta cliente envía una petición con `reasoning_mode` superior
- **THEN** el servicio SHALL permitir una estrategia interna más deliberativa aunque aumente la latencia

#### Scenario: La estrategia interna cambia sin romper la API
- **WHEN** el equipo cambie la forma interna de implementar estos modos
- **THEN** el contrato HTTP SHALL seguir exponiendo el mismo concepto de `reasoning_mode`

#### Scenario: Gemma 4 resuelve thinking como mapping inicial binario
- **WHEN** la primera implementación use Gemma 4 sobre Ollama
- **THEN** `reasoning_mode=off` y `reasoning_mode=low` SHALL resolverse inicialmente con thinking desactivado
- **AND** `reasoning_mode=medium` y `reasoning_mode=high` SHALL resolverse inicialmente con thinking activado

### Requirement: Runtime local contenedorizado y sustituible
La primera implementación SHALL desplegar el runtime local de inferencia de forma contenedorizada para poder arrancarlo, detenerlo o sustituirlo con fricción baja.

#### Scenario: El usuario quiere liberar recursos
- **WHEN** el usuario decide parar temporalmente el runtime local
- **THEN** la infraestructura SHALL permitir detener los contenedores asociados sin desmontar la integración del proyecto

#### Scenario: El equipo quiere probar otro modelo local
- **WHEN** el equipo sustituye el modelo o perfil de runtime validado por otro nuevo
- **THEN** el cambio SHALL poder hacerse sin rediseñar el contrato HTTP del servicio

#### Scenario: Un modelo necesita su propio proxy o adaptador
- **WHEN** un modelo local requiera una adaptación específica de entradas o salidas
- **THEN** ese modelo SHALL poder desplegarse junto a su propio proxy o capa auxiliar dentro de su unidad contenedorizada

### Requirement: Runtime inicial validado por spike
La primera implementación SHALL tomar como runtime inicial validado el perfil más rápido confirmado por el spike local del proyecto.

#### Scenario: Selección del runtime inicial en portátil sin GPU dedicada
- **WHEN** el backend local-inference-api se arranque por primera vez en el entorno objetivo actual
- **THEN** el runtime inicial por defecto SHALL ser `hf.co/unsloth/gemma-4-E2B-it-GGUF:UD-Q4_K_XL`

### Requirement: Orquestación del stack mediante Docker Compose
La primera implementación SHALL definir la infraestructura local del servicio mediante `docker compose` y un archivo `.env`.

#### Scenario: El usuario arranca el stack local
- **WHEN** el usuario pone en marcha la infraestructura de inferencia
- **THEN** la operativa SHALL estar definida mediante `docker compose`

#### Scenario: El usuario necesita configurar el stack
- **WHEN** el usuario modifica variables del entorno del despliegue
- **THEN** esas variables SHALL vivir en un archivo `.env` o equivalente documentado

### Requirement: Formato OpenAI-compatible en respuestas soportadas
La primera implementación SHALL devolver respuestas OpenAI-compatible dentro del alcance de endpoints y modalidades que esta iteración soporte.

#### Scenario: Una herramienta cliente espera un formato estándar
- **WHEN** una herramienta consume el endpoint textual o multimodal soportado
- **THEN** el servicio SHALL responder usando estructuras compatibles con la API de OpenAI dentro del alcance documentado

### Requirement: Entrada de archivo mediante multipart en la primera iteración
La primera implementación SHALL aceptar archivos multimodales por `multipart/form-data` cuando una petición incluya imagen u otros ficheros soportados.

#### Scenario: Una herramienta sube una imagen
- **WHEN** una herramienta cliente envía una imagen al endpoint multimodal soportado
- **THEN** la API SHALL aceptar esa entrada mediante `multipart/form-data`

## MODIFIED Requirements

### Requirement: Servicio local de inferencia accesible por API

#### Scenario: La primera versión ofrece una superficie mínima estable
- **WHEN** se implementa la primera iteración del servicio
- **THEN** la API SHALL ofrecer al menos un endpoint de salud y endpoints batch para texto e imagen
- **THEN** la API SHALL permitir expresar un perfil de razonamiento por petición

### Requirement: Despliegue portable mediante contenedores

#### Scenario: La primera versión se despliega como base portable
- **WHEN** el equipo valida la primera iteración del backend
- **THEN** el servicio SHALL poder arrancarse mediante Docker con la configuración mínima documentada
- **THEN** el runtime local SHALL poder arrancarse y detenerse mediante la misma operativa documentada
