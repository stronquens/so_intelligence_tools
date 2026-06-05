## Context

El proyecto todavía no tiene código de producto. Esta iteración debe crear una base mínima pero creíble para el backend local de inferencia que luego consumirán otras tools del sistema.

La spec viva de `local-inference-api` es amplia e incluye texto, imagen y audio, además de casos batch y streaming. Para no abrir demasiados frentes a la vez, esta primera entrega se centrará en:

- peticiones batch
- texto
- imagen
- despliegue local
- contenedorización

La capa de audio y los flujos en tiempo real quedarán fuera de este cambio aunque la arquitectura no debe cerrarlos.

## Goals / Non-Goals

**Goals**

- Tener un servicio local HTTP arrancable en Linux.
- Tener una interfaz de API consistente para herramientas Python cliente.
- Tener una base reproducible del backend Python con Poetry y `.venv` local.
- Mantener la interfaz pública lo más compatible posible con el formato OpenAI en el alcance soportado.
- Encapsular la dependencia con Ollama detrás de una capa propia.
- Permitir que el cliente pida distintos perfiles de latencia o razonamiento sin acoplarse al runtime concreto.
- Dejar preparado despliegue en Docker.
- Permitir encender, apagar y sustituir el runtime local sin rehacer la capa cliente.
- Soportar al menos una operación textual y una operación con imagen.

**Non-Goals**

- Implementar streaming de audio o texto parcial.
- Resolver todavía multi-model routing complejo.
- Diseñar la orquestación completa de autenticación, observabilidad o colas.
- Optimizar rendimiento fino más allá de una primera experiencia funcional.

## Decisions

Usar un servicio Python con FastAPI para la primera versión del backend.
Motivo: encaja con el resto del stack previsto en Python, facilita validación local, tipado y documentación mínima de endpoints.
Alternativas consideradas: Flask o Node.js. Se descartan en esta iteración porque FastAPI deja una base más fuerte para contratos y crecimiento.

Gestionar el proyecto Python con Poetry y un entorno `.venv` dentro del repo.
Motivo: evita dependencias globales, hace reproducible la instalación y deja claro que cualquier paquete del backend vive dentro del proyecto.
Alternativas consideradas: `venv` manual o instalación global con `pip`. Se descartan porque vuelven más frágil la operativa y facilitan contaminar el host.

Modelar el acceso al runtime local a través de un adaptador interno de Ollama.
Motivo: evita acoplar el resto del servicio a la API concreta de Ollama y deja abierta una futura sustitución.
Alternativas consideradas: llamar a Ollama directamente desde cada endpoint. Se descarta porque mezclaría contrato externo y runtime interno.

Limitar la primera entrega a endpoints batch.
Motivo: reduce riesgo y acelera la validación del núcleo del sistema.
Alternativas consideradas: incluir desde ya endpoints streaming. Se descartan por ampliar demasiado la complejidad del primer change.

Separar configuración del modelo en variables de entorno.
Motivo: el nombre exacto del modelo puede variar según lo que validemos finalmente con Ollama.
Alternativas consideradas: fijar en código una variante cerrada. Se descarta porque todavía estamos en fase de exploración técnica.

Usar `hf.co/unsloth/gemma-4-E2B-it-GGUF:UD-Q4_K_XL` como runtime inicial por defecto.
Motivo: el spike en el portátil objetivo sin GPU dedicada mostró mejor equilibrio de latencia, memoria y rendimiento que `UD-Q8_K_XL`.
Alternativas consideradas: `UD-Q8_K_XL`. Se descarta como perfil inicial porque fue materialmente más lento en CPU-only.

Desplegar tanto el API como el runtime local mediante contenedores controlables.
Motivo: permite apagar infraestructura para liberar CPU, RAM o GPU, y facilita cambiar de modelo o perfil cuando queramos validar una alternativa nueva.
Alternativas consideradas: ejecutar Ollama o el modelo directamente sobre el host y contenerizar solo el API. Se descarta para esta primera iteración porque complica la operativa y hace menos uniforme el ciclo de arranque o sustitución.

Usar `docker compose` y un archivo `.env` como operativa estándar de la primera iteración.
Motivo: simplifica la gestión del stack local, hace explícitas las variables del entorno y da una experiencia uniforme para arrancar, parar y reconfigurar.
Alternativas consideradas: comandos Docker sueltos o configuración distribuida por servicio. Se descartan porque vuelven más frágil la operativa diaria.

Preferir contenedores distintos por modelo o perfil validado en vez de reparametrizar en caliente un mismo contenedor.
Motivo: cuando un modelo necesita un proxy específico o una adaptación de entradas y salidas, resulta más intuitivo y mantenible que viaje junto a su propio runtime en una unidad desplegable propia.
Alternativas consideradas: un único contenedor genérico reconfigurable para todos los modelos. Se descarta como enfoque principal porque mezcla demasiadas responsabilidades y complica las pruebas comparativas.

Exponer un parámetro de `reasoning_mode` en la interfaz pública y resolverlo dentro del adaptador.
Motivo: nos permite ofrecer dos comportamientos de producto claros, "rápido" e "inteligente", sin comprometer todavía si eso se implementa con un solo modelo configurable o con dos perfiles distintos.
Alternativas consideradas: exponer directamente nombres de modelo o flags internas del runtime. Se descarta porque acoplaría las tools cliente a detalles de infraestructura que probablemente cambien.

Preferir primero un contrato lógico de niveles de razonamiento, por ejemplo `off`, `low`, `medium`, `high`.
Motivo: esa forma es más expresiva que una simple dicotomía y deja abierta una implementación inicial donde solo activemos un subconjunto real como `off` y `high`.
Alternativas consideradas: exponer solo dos modos fijos, `fast` e `intelligent`. Se descarta como contrato principal porque puede quedarse corto rápido, aunque siga siendo útil como preset de producto.

## Reasoning Strategy Recommendation

La mejor forma de acometerlo es separar el contrato externo de la estrategia interna:

- contrato externo: cada petición puede incluir `reasoning_mode`
- implementación interna: el adaptador decide cómo traducirlo al runtime real

Recomendación de producto:

- soportar en API `off`, `low`, `medium`, `high`
- documentar presets de producto:
  - `instant` -> `off`
  - `smart` -> `medium` o `high`

Recomendación de implementación inicial:

- empezar con un solo punto de entrada del API
- dejar que el adaptador de Ollama mapee cada modo a una estrategia interna
- permitir que esa estrategia sea una de estas dos sin cambiar el contrato:
  - un solo modelo con prompting distinto
  - dos perfiles o incluso dos modelos distintos, uno rápido y otro más deliberativo

Mi preferencia para esta primera iteración es esta:

- no exponer dos modelos distintos al cliente
- sí permitir internamente dos perfiles de ejecución
- para Gemma 4 sobre Ollama, mapear inicialmente:
  - `off` y `low` -> thinking desactivado
  - `medium` y `high` -> thinking activado mediante `<|think|>` en el `system` prompt

Motivo: si más adelante descubrimos que la mejor experiencia real en local requiere un modelo rápido y otro más capaz, podremos cambiarlo dentro del adaptador sin romper ninguna tool cliente.

## Deployment Strategy Recommendation

La mejor forma de acometer el despliegue de esta primera iteración es separar responsabilidades dentro de `docker compose`:

- contenedor del API local
- uno o más contenedores de runtime local de inferencia
- archivo `.env` para la configuración del stack
- posibilidad de que cada runtime viaje con su propio proxy o adaptador cuando haga falta

Eso nos da tres ventajas prácticas:

- apagar todo cuando no se use
- volver a encenderlo sin depender de instalaciones manuales en el host
- probar un modelo nuevo levantando un contenedor nuevo en lugar de reescribir clientes

Mi recomendación aquí es:

- mantener un único contrato de API
- mantener un único adaptador lógico de runtime
- permitir que por debajo el runtime activo cambie sin afectar a las tools cliente
- tratar cada modelo o perfil validado como una unidad desplegable propia cuando necesite proxy o ajustes específicos

## Proposed API Shape

Primera aproximación de endpoints:

- `GET /health`
- `GET /status`
- `POST /v1/text/generate`
- `POST /v1/image/extract-text`

Contrato orientativo:

- `GET /health`
  - output: estado mínimo de vida del API

- `GET /status`
  - output: estado operativo del runtime o runtimes configurados

- `POST /v1/text/generate`
  - input: prompt, system_prompt opcional, `reasoning_mode` opcional, parámetros opcionales
  - output: respuesta compatible con el formato OpenAI dentro del alcance soportado

- `POST /v1/image/extract-text`
  - input: imagen enviada por `multipart/form-data`, `reasoning_mode` opcional
  - output: respuesta compatible con el formato OpenAI dentro del alcance soportado

No hace falta que la primera versión cierre todavía el contrato definitivo de todas las tools futuras, pero sí debe dejar clara la forma general de integración.

## Risks / Trade-offs

[Compatibilidad de modelo] -> No todos los modelos locales ofrecen el mismo nivel real de soporte multimodal.
Mitigación: desacoplar el nombre del modelo vía configuración y documentar una variante validada.

[Compatibilidad OpenAI parcial] -> No todos los comportamientos del API local podrán replicar de forma perfecta el ecosistema OpenAI.
Mitigación: mantener compatibilidad fuerte en el formato de petición y respuesta dentro del alcance que soportemos y documentar claramente lo que queda fuera.

[Complejidad de Docker] -> Encapsular API y runtime local puede complicar la experiencia inicial.
Mitigación: mantener una topología simple en `docker compose`, con un servicio API y uno o varios runtimes bien delimitados.

[Contrato demasiado pronto] -> Si la API nace demasiado cerrada, puede frenar tools futuras.
Mitigación: diseñar endpoints pequeños y consistentes, con metadata extensible.

[Semántica de reasoning poco real] -> El runtime local puede no soportar de forma nativa niveles de thinking como los imaginamos en producto.
Mitigación: tratar `reasoning_mode` como contrato lógico del producto y resolverlo en el adaptador con la mejor estrategia disponible.

## Migration Plan

No hay migración de datos.

El orden previsto es:

1. concretar delta spec de la primera iteración
2. scaffold del servicio API y bootstrap de Poetry
3. integración con Ollama
4. empaquetado Docker
5. validación manual con peticiones reales

## Open Questions

- Qué topología exacta de contenedores validaremos primero para API y runtime local.
- Cómo evolucionaremos el mapeo de `reasoning_mode` si más adelante añadimos modelos con niveles de thinking nativos.
