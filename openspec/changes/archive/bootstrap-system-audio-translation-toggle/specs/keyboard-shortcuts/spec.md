# Delta Spec

## ADDED Requirements

### Requirement: Atajo global con semántica toggle para una herramienta persistente
El sistema SHALL permitir que un mismo atajo global inicie o detenga una herramienta persistente según su estado actual.

#### Scenario: Herramienta persistente inactiva
- **WHEN** el usuario pulsa el atajo asignado a una herramienta persistente que no está corriendo
- **THEN** el sistema SHALL iniciar esa herramienta

#### Scenario: Herramienta persistente activa
- **WHEN** el usuario pulsa el mismo atajo asignado a una herramienta persistente que ya está corriendo
- **THEN** el sistema SHALL detener esa herramienta de forma controlada

#### Scenario: Atajo por defecto con bajo riesgo de colisión
- **WHEN** se asigne un atajo inicial a una herramienta persistente nueva
- **THEN** el sistema SHALL preferir una combinación con bajo riesgo de conflicto con atajos habituales del escritorio o de aplicaciones comunes
