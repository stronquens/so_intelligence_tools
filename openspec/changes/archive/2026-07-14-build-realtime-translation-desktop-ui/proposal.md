# Proposal

Implementar y poner en produccion la interfaz de escritorio Electron + Vue.js
para la capability `realtime-translation-desktop-ui`.

La primera fase valido la direccion visual con datos mock. Esta continuacion
conecta esa interfaz al controlador Python real, conserva la ventana Tkinter como
fallback manual y hace que el atajo Linux `Ctrl+Alt+Y` abra o alterne la nueva
ventana. La experiencia final debe mantener el layout ya aprobado, reflejar
estados reales y usar animaciones discretas para mejorar legibilidad y acabado.

## Scope

- Mantener la app Electron + Vue separada de captura, proveedores y modelos.
- Conectar Electron con un proceso hijo Python mediante JSON Lines por
  `stdin`/`stdout`.
- Renderizar estados, parciales y bloques reales sin perder la agrupacion EN/ES.
- Hacer funcionales pausa, reanudacion, parada, cambio de modo y activacion del
  microfono traducido.
- Abrir o alternar la ventana Electron desde `Ctrl+Alt+Y` y desde el overlay.
- Añadir transiciones de entrada, streaming, pausa, reconexion y error con
  soporte para `prefers-reduced-motion`.
- Mantener datos mock solo para desarrollo web y pruebas visuales aisladas.
- Validar contrato Python, frontend, build Electron y un smoke test real.
- Hacer que los controles de ventana tengan areas de interaccion amplias,
  feedback animado y comportamiento nativo de cerrar, minimizar y maximizar.
- Permitir cambiar origen y destino usando el catalogo de idiomas publicado por
  el backend, reiniciando la sesion sin perder el historial visible.
- Mostrar cada bloque como una fila de dos columnas alineadas y ofrecer una
  densidad compacta persistente para consultar mas conversacion de un vistazo.
- Adaptar lateral, cabecera, transcript y controles a ventanas estrechas o bajas
  sin cortar desplegables ni hacer desaparecer acciones.
- Tratar `desktop/.tmp/realtime-translator-ui-v3.png` como contrato visual: los
  cambios responsive y de columnas no SHALL alterar sin necesidad controles de
  ventana, banderas, anchura de sidebar, jerarquia o estilo de cabeceras.
- Alimentar el medidor de entrada con niveles PCM reales y distinguir el audio
  del sistema del micrófono físico cuando la voz traducida esté activa.
- Mantener estable el endpoint `so_ai_translated_mic` entre reaperturas y evitar
  que módulos PulseAudio huérfanos desvíen el audio a nombres con sufijo.

## Out Of Scope

- Eliminar la ventana `tkinter` actual como fallback manual.
- Capturar audio desde Electron.
- Hablar directamente con OpenAI, LiteLLM, Ollama u otros proveedores desde la UI.
- Implementar todos los proveedores/modelos que aparecen como opciones futuras.
- Detectar automaticamente todos los idiomas posibles fuera del catalogo
  declarado por esta aplicacion.
- Rediseñar el launcher principal o la ventana de ajustes general.
