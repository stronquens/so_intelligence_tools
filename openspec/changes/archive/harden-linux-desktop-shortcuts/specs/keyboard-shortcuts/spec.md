# Delta Spec

## ADDED Requirements

### Requirement: Atajos persistentes y diagnosticables en GNOME
El sistema SHALL registrar los atajos GNOME de forma persistente y ofrecer diagnóstico suficiente para distinguir fallos de captura del atajo, fallos de configuración y fallos de la herramienta.

#### Scenario: Inicio de sesión en GNOME
- **WHEN** el usuario inicia sesión en el escritorio
- **THEN** el sistema SHALL poder revalidar o reaplicar los atajos configurados
- **AND** SHALL poder refrescar el servicio de GNOME responsable de ejecutar atajos personalizados cuando sea necesario

#### Scenario: Un atajo no parece hacer nada
- **WHEN** el usuario pulsa un atajo registrado y no observa efecto visible
- **THEN** el sistema SHALL escribir evidencia temprana en logs de wrapper cuando GNOME haya invocado el comando
- **AND** SHALL permitir distinguir si el fallo ocurrió antes de entrar en Python, al cargar configuración o durante la herramienta
