# Purpose

Definir el comportamiento esperado del servicio local de inferencia multimodal que alimentará las herramientas de IA del sistema.

## Requirements

### Requirement: Servicio local de inferencia accesible por API
El sistema SHALL exponer un servicio local accesible por API para recibir peticiones de inferencia desde las herramientas cliente del sistema operativo.

#### Scenario: El cliente invoca una tarea textual
- **WHEN** un script cliente envía una petición válida de texto al servicio local
- **THEN** la API SHALL devolver una respuesta estructurada utilizable por la herramienta solicitante

#### Scenario: El servicio está pensado para uso local
- **WHEN** el sistema se despliega en una máquina del usuario
- **THEN** la API SHALL poder ejecutarse en local sin depender de servicios remotos para la inferencia principal

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

### Requirement: Despliegue portable mediante contenedores
El sistema SHALL poder desplegar el servicio de inferencia dentro de Docker para facilitar instalación, aislamiento y portabilidad.

#### Scenario: Despliegue inicial en Linux
- **WHEN** el proyecto se instala en un entorno Linux soportado
- **THEN** el backend SHALL poder levantarse mediante una configuración basada en Docker

#### Scenario: Preparación para otros sistemas
- **WHEN** se quiera portar el proyecto a otro sistema operativo
- **THEN** la arquitectura SHALL mantener la capa de inferencia aislada detrás de la misma interfaz de API

### Requirement: Compatibilidad inicial con Ollama y Gemma
El sistema SHALL permitir una primera implementación basada en Ollama y una familia de modelos Gemma multimodales en local.

#### Scenario: Primera iteración técnica del backend
- **WHEN** el equipo implemente la primera versión del servicio
- **THEN** esta SHALL poder apoyarse en Ollama como runtime de modelo local

#### Scenario: Evolución futura del proveedor local
- **WHEN** el proyecto necesite cambiar de modelo o runtime en una iteración posterior
- **THEN** la interfaz consumida por las herramientas cliente SHALL minimizar el acoplamiento a ese proveedor
