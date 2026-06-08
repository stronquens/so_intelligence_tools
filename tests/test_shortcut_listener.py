from __future__ import annotations

import pytest

from so_intelligence_tools.domain.errors import UnsupportedEnvironmentError
from so_intelligence_tools.infrastructure.shortcut_actions import ShortcutActionRegistry
from so_intelligence_tools.infrastructure.shortcut_listener import LinuxShortcutListener


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
