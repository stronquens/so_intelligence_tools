# Delta Spec

## MODIFIED Requirements

### Requirement: IntegraciÃ³n inicial orientada a Linux
El sistema SHALL priorizar una integraciÃ³n operativa en Linux sin cerrar la puerta a adaptadores para otros sistemas operativos.

#### Scenario: Primera implementaciÃ³n de atajos
- **WHEN** se construya la primera capa de integraciÃ³n con el sistema
- **THEN** esta SHALL funcionar en Linux como plataforma inicial soportada

#### Scenario: Entorno Linux recomendado para automatizaciÃ³n completa
- **WHEN** la primera integraciÃ³n necesite automatizaciÃ³n fiable de copiar y pegar sobre aplicaciones de terceros
- **THEN** el sistema SHALL considerar `X11` como el entorno Linux recomendado para esa primera iteraciÃ³n

#### Scenario: Portabilidad futura
- **WHEN** sea necesario soportar otro sistema operativo
- **THEN** la lÃ³gica de negocio de las herramientas SHALL permanecer separada del mecanismo especÃ­fico de captura de atajos

#### Scenario: Windows text automation without shortcut registration
- **WHEN** a Windows runtime is introduced for text-focused tools
- **THEN** it SHALL NOT imply that Windows global shortcut registration is complete
- **AND** Windows shortcut installation SHALL remain a separate capability until explicitly designed.
