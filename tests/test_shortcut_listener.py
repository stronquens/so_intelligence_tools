from __future__ import annotations

import pytest

from so_intelligence_tools.domain.errors import UnsupportedEnvironmentError
from so_intelligence_tools.infrastructure.shortcut_actions import ShortcutActionRegistry
from so_intelligence_tools.infrastructure.shortcut_listener import (
    LinuxShortcutListener,
    WindowsShortcutListener,
    build_shortcut_listener,
    _parse_windows_hotkey,
)


def test_shortcut_listener_rejects_wayland(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    registry = ShortcutActionRegistry()
    registry.register("selected-text-correction", lambda: "ok")
    listener = LinuxShortcutListener(
        shortcut_to_action={"<ctrl>+<space>": "selected-text-correction"},
        registry=registry,
    )

    with pytest.raises(UnsupportedEnvironmentError, match="Wayland"):
        listener.start()


def test_build_shortcut_listener_selects_windows_listener():
    registry = ShortcutActionRegistry()
    listener = build_shortcut_listener(
        shortcut_to_action={"<ctrl>+<alt>+c": "selected-text-correction"},
        registry=registry,
        action_delay_seconds=0.2,
        action_cooldown_seconds=2.0,
        platform_name="win32",
    )

    assert isinstance(listener, WindowsShortcutListener)
    assert listener._action_delay_seconds == 0.2
    assert listener._action_cooldown_seconds == 2.0


def test_parse_windows_hotkey_supports_ctrl_alt_letter():
    modifiers, key = _parse_windows_hotkey("<ctrl>+<alt>+c")

    assert modifiers == 0x0001 | 0x0002
    assert key == ord("C")


def test_build_shortcut_listener_selects_linux_listener():
    registry = ShortcutActionRegistry()
    listener = build_shortcut_listener(
        shortcut_to_action={"<ctrl>+<space>": "selected-text-correction"},
        registry=registry,
        platform_name="linux",
    )

    assert isinstance(listener, LinuxShortcutListener)


def test_build_shortcut_listener_rejects_unsupported_platform():
    registry = ShortcutActionRegistry()

    with pytest.raises(UnsupportedEnvironmentError, match="No hay listener"):
        build_shortcut_listener(
            shortcut_to_action={"<ctrl>+<space>": "selected-text-correction"},
            registry=registry,
            platform_name="darwin",
        )


def test_shortcut_handler_does_not_raise_unexpected_action_errors(tmp_path):
    registry = ShortcutActionRegistry()
    registry.register("bad-action", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    listener = WindowsShortcutListener(
        shortcut_to_action={"<ctrl>+<alt>+c": "bad-action"},
        registry=registry,
        event_log_path=tmp_path / "shortcut.log",
    )

    listener._build_handler("bad-action")()

    assert "crashed action=bad-action" in (tmp_path / "shortcut.log").read_text(
        encoding="utf-8"
    )


def test_shortcut_handler_ignores_repeated_trigger_during_cooldown(tmp_path):
    calls: list[str] = []
    registry = ShortcutActionRegistry()
    registry.register("selected-text-correction", lambda: calls.append("ok") or "done")
    listener = WindowsShortcutListener(
        shortcut_to_action={"<ctrl>+<alt>+c": "selected-text-correction"},
        registry=registry,
        action_cooldown_seconds=2.0,
        event_log_path=tmp_path / "shortcut.log",
    )
    handler = listener._build_handler("selected-text-correction")

    handler()
    handler()

    log = (tmp_path / "shortcut.log").read_text(encoding="utf-8")
    assert calls == ["ok"]
    assert "completed action=selected-text-correction" in log
    assert "ignored action=selected-text-correction reason=cooldown" in log
