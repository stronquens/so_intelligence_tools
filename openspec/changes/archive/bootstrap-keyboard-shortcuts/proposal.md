# Proposal

## Summary

Implementar la primera iteración de `keyboard-shortcuts` como una integración Linux-first capaz de:

- registrar un atajo global
- asociarlo a una capability concreta
- disparar el flujo real de `selected-text-correction`

## Why

`local-inference-api` y `python-tool-runners` ya están listos, pero todavía no existe una forma nativa de sistema para activar una herramienta desde cualquier aplicación. El siguiente paso natural es cerrar el primer camino vertical completo para el usuario:

- pulsar atajo
- leer selección
- corregir con el modelo local
- reemplazar el texto

## Scope

### In scope

- listener global de atajos en Linux
- mapeo explícito entre atajo y acción
- primer atajo asociado a `selected-text-correction`
- integración real de selección y reemplazo de texto mediante portapapeles y automatización del escritorio
- tests automatizados del registro y disparo de acciones

### Out of scope

- soporte robusto para Wayland
- UI de configuración de atajos
- múltiples shortcuts avanzados
- soporte de acciones temporales mantenidas

## Expected Outcome

Al final del change, el proyecto debe poder ejecutar una herramienta visible de usuario a través de un atajo global en Linux, quedando `keyboard-shortcuts` conectado con `selected-text-correction`.
