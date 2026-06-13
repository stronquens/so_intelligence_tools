## 1. OpenSpec Scope

- [x] 1.1 Create proposal, design and task artifacts for the Windows adapter slice.
- [x] 1.2 Define explicit out-of-scope items for shortcuts, startup services and audio.

## 2. Runtime Composition

- [x] 2.1 Add a runtime protocol and `WindowsRuntime` composition object.
- [x] 2.2 Add `build_windows_runtime()` and platform-aware `build_runtime()`.
- [x] 2.3 Update selected text correction entrypoints to use the platform-aware runtime where safe.

## 3. Windows Text Adapters

- [x] 3.1 Add Windows clipboard adapter.
- [x] 3.2 Add Windows keyboard automation adapter for copy/paste and text typing primitives.
- [x] 3.3 Add Windows selected-text and text-insertion adapters.
- [x] 3.4 Add best-effort Windows notification adapter.

## 4. Documentation And Tests

- [x] 4.1 Add focused tests for Windows text adapters using fakes.
- [x] 4.2 Add focused tests for runtime platform selection.
- [x] 4.3 Document current Windows support and limitations.

## 5. Validation

- [x] 5.1 Run relevant pytest subset.
- [x] 5.2 Run ruff on touched source/tests.
- [x] 5.3 Record validation evidence and residual risks in `validation.md`.
