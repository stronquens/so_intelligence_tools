# voice-translation-virtual-microphone Delta

## ADDED Requirements

### Requirement: Windows virtual microphone plan
The Windows implementation SHALL initially depend on an installed virtual audio cable driver for translated microphone output instead of creating a custom kernel audio driver.

#### Scenario: Virtual cable is available
- **WHEN** the user starts translated virtual microphone output on Windows
- **AND** a configured virtual cable playback endpoint is available
- **THEN** the Windows audio adapter SHALL write translated PCM to that playback endpoint
- **AND** the paired recording endpoint SHALL be the microphone selected by external call apps

#### Scenario: Virtual cable is missing
- **WHEN** no configured Windows virtual cable endpoint is available
- **THEN** the tool SHALL show a clear setup error rather than pretending that a virtual microphone exists

#### Scenario: Custom driver is considered later
- **WHEN** the project needs a bundled first-party virtual microphone driver
- **THEN** that work SHALL be treated as a separate driver project with WDK, signing, installer, administrator, and maintenance planning
