from __future__ import annotations

import time

from pynput import keyboard

from so_intelligence_tools.infrastructure.press_and_hold_listener import (
    PressAndHoldShortcutListener,
    _parse_shortcut,
)


def test_parse_shortcut_supports_ctrl_alt_space_variants():
    assert _parse_shortcut("<ctrl>+<alt>+<space>") == {"ctrl", "alt", "space"}
    assert _parse_shortcut("Ctrl + Alt + Space") == {"ctrl", "alt", "space"}
    assert _parse_shortcut("<Primary><Alt>space") == {"ctrl", "alt", "space"}


def test_press_and_hold_listener_invokes_press_and_release():
    events: list[str] = []
    listener = PressAndHoldShortcutListener(
        shortcut="<ctrl>+<alt>+<space>",
        on_press=lambda: events.append("press"),
        on_release=lambda: events.append("release"),
    )

    listener._handle_key_press(keyboard.Key.ctrl_l)
    listener._handle_key_press(keyboard.Key.alt_l)
    assert events == []
    listener._handle_key_press(keyboard.Key.space)
    assert events == ["press"]
    listener._handle_key_press(keyboard.Key.space)
    assert events == ["press"]
    listener._handle_key_release(keyboard.Key.space)
    time.sleep(0.15)

    assert events == ["press", "release"]


def test_press_and_hold_listener_ignores_key_repeat_release():
    events: list[str] = []
    listener = PressAndHoldShortcutListener(
        shortcut="<ctrl>+<alt>+<space>",
        on_press=lambda: events.append("press"),
        on_release=lambda: events.append("release"),
    )

    listener._handle_key_press(keyboard.Key.ctrl_l)
    listener._handle_key_press(keyboard.Key.alt_l)
    listener._handle_key_press(keyboard.Key.space)
    listener._handle_key_release(keyboard.Key.space)
    listener._handle_key_press(keyboard.Key.space)
    time.sleep(0.15)

    assert events == ["press"]
