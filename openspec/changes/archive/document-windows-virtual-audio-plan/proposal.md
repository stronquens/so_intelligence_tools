# Document Windows Virtual Audio Plan

## Problem

Linux virtual audio behavior is implemented, but the Windows equivalent has not been documented beyond a short note. Before implementing Windows audio adapters, the repository needs a clear comparison between the current PulseAudio/PipeWire approach and a practical Windows routing plan.

## Scope

- Document how Linux currently handles system audio capture and translated virtual microphone output.
- Document Windows equivalents and constraints.
- Recommend a first Windows implementation path that avoids custom kernel driver work.
- Link the research from Windows support documentation.

## Non-Goals

- Implement Windows audio adapters in this change.
- Install third-party audio drivers on the user's machine.
- Build or ship a custom Windows virtual audio driver.
