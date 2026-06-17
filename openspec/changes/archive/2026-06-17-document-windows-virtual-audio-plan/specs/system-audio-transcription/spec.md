# system-audio-transcription Delta

## ADDED Requirements

### Requirement: Windows system audio capture plan
The Windows implementation SHALL use WASAPI loopback capture as the preferred approach for capturing the audio rendered by the system output endpoint.

#### Scenario: Windows captures the default output mix
- **WHEN** the user starts system audio translation on Windows
- **THEN** the Windows audio adapter SHALL capture audio from a render endpoint using WASAPI loopback or fail with a clear unsupported-environment message

#### Scenario: Windows per-application capture is requested later
- **WHEN** a future workflow needs to capture or exclude a specific process tree
- **THEN** the implementation MAY use Windows Application Loopback Capture on supported Windows builds rather than forcing all routing through a virtual cable
