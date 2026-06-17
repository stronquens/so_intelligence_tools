from __future__ import annotations

import time

from pynput import keyboard

from so_intelligence_tools.infrastructure.press_and_hold_listener import (
    PressAndHoldShortcutListener,
    _normalize_key,
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


def test_normalize_key_maps_ctrl_letter_control_character():
    key = keyboard.KeyCode(char="\x04")

    assert _normalize_key(key) == "d"


def test_normalize_key_maps_windows_virtual_key_letter():
    key = keyboard.KeyCode.from_vk(ord("D"))

    assert _normalize_key(key) == "d"


def test_press_and_hold_listener_invokes_ctrl_alt_letter_shortcut_from_control_character():
    events: list[str] = []
    listener = PressAndHoldShortcutListener(
        shortcut="<ctrl>+<alt>+d",
        on_press=lambda: events.append("press"),
        on_release=lambda: events.append("release"),
    )

    listener._handle_key_press(keyboard.Key.ctrl_l)
    listener._handle_key_press(keyboard.Key.alt_l)
    listener._handle_key_press(keyboard.KeyCode(char="\x04"))
    assert events == ["press"]
    listener._handle_key_release(keyboard.KeyCode(char="\x04"))
    time.sleep(0.15)

    assert events == ["press", "release"]


def test_press_and_hold_listener_invokes_ctrl_alt_letter_shortcut_from_virtual_key():
    events: list[str] = []
    listener = PressAndHoldShortcutListener(
        shortcut="<ctrl>+<alt>+d",
        on_press=lambda: events.append("press"),
        on_release=lambda: events.append("release"),
    )

    listener._handle_key_press(keyboard.Key.ctrl_l)
    listener._handle_key_press(keyboard.Key.alt_l)
    listener._handle_key_press(keyboard.KeyCode.from_vk(ord("D")))
    assert events == ["press"]
    listener._handle_key_release(keyboard.KeyCode.from_vk(ord("D")))
    time.sleep(0.15)

    assert events == ["press", "release"]



def test_press_and_hold_listener_writes_event_log(tmp_path):
    listener = PressAndHoldShortcutListener(
        shortcut="<ctrl>+<alt>+d",
        on_press=lambda: None,
        on_release=lambda: None,
        event_log_path=tmp_path / "events.log",
    )

    listener._handle_key_press(keyboard.Key.ctrl_l)
    listener._handle_key_press(keyboard.Key.alt_l)
    listener._handle_key_press(keyboard.KeyCode(char="\x04"))

    log = (tmp_path / "events.log").read_text(encoding="utf-8")
    assert "press key=ctrl" in log
    assert "press key=alt" in log
    assert "press key=d" in log
    assert "shortcut-started" in log
