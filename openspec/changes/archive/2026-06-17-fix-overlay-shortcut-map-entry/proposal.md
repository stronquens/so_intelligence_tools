# Fix Overlay Shortcut Map Entry

## Why

The shortcut reference currently says the desktop overlay opens with `Ctrl + Space`, while `Ctrl + Alt + A` is listed as the planned Assistant shortcut. On the current Windows installation, `Ctrl + Alt + A` is the working shortcut that opens or toggles the main overlay.

This mismatch makes the shortcut map less useful and creates an apparent collision between the overlay launcher and the future Assistant action.

## Scope

- Document `Ctrl + Alt + A` as the Windows shortcut for opening/toggling the main overlay.
- Update desktop overlay defaults so `Open overlay` uses `Ctrl + Alt + A`.
- Remove the default `Ctrl + Alt + A` assignment from Assistant.
- Migrate the old exact desktop settings default pair without overwriting unrelated user customizations.

## Out Of Scope

- Registering new global shortcuts.
- Changing dictation or selected-text correction shortcuts.
- Implementing the Assistant action.
