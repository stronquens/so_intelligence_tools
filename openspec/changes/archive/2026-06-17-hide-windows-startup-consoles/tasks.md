## 1. Hidden Windows Startup Launchers

- [x] 1.1 Update the Windows Startup installers to write hidden launchers for the API and shortcut listener.
- [x] 1.2 Redirect API and shortcut listener output to user-local diagnostic logs.
- [x] 1.3 Ensure reinstalling removes previous visible `.cmd` launchers so Startup does not create duplicates.

## 2. Documentation And Tests

- [x] 2.1 Update Windows Startup tests for the hidden launcher names and contents.
- [x] 2.2 Update Windows documentation with background behavior and log paths.
- [x] 2.3 Reinstall current user Startup entries and stop duplicate current-session processes.

## 3. Validation

- [x] 3.1 Run the focused Windows Startup tests.
- [x] 3.2 Validate the OpenSpec change.
- [x] 3.3 Record validation evidence in the change.
