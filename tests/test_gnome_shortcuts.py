from __future__ import annotations

from pathlib import Path
import sys

from so_intelligence_tools.infrastructure.gnome_shortcuts import (
    GnomeShortcutManager,
    SELECTED_TEXT_SHORTCUT_PATH,
)


def test_install_selected_text_shortcut_adds_path_and_sets_values(monkeypatch):
    calls: list[tuple[str, str, str, str | None]] = []

    def fake_gsettings(action: str, schema: str, key: str, value: str | None = None) -> str:
        calls.append((action, schema, key, value))
        if action == "get":
            return "@as []"
        return ""

    monkeypatch.setattr(GnomeShortcutManager, "_gsettings", staticmethod(fake_gsettings))
    manager = GnomeShortcutManager(python_executable="/tmp/project/.venv/bin/python")

    command = manager.install_selected_text_correction_shortcut(binding="<Primary>space")

    expected_script = Path(sys.prefix) / "bin" / "so-intelligence-tools"
    if expected_script.exists():
        assert command == f"{expected_script} run-selected-text-correction"
    else:
        assert command == "/tmp/project/.venv/bin/python -m so_intelligence_tools run-selected-text-correction"
    assert ("set", "org.gnome.settings-daemon.plugins.media-keys", "custom-keybindings", f"['{SELECTED_TEXT_SHORTCUT_PATH}']") in calls
    assert any(call[2] == "binding" and call[3] == "<Primary>space" for call in calls)


def test_install_selected_text_shortcut_can_enable_debug(monkeypatch):
    def fake_gsettings(action: str, schema: str, key: str, value: str | None = None) -> str:
        if action == "get":
            return "@as []"
        return ""

    monkeypatch.setattr(GnomeShortcutManager, "_gsettings", staticmethod(fake_gsettings))
    manager = GnomeShortcutManager(python_executable="/tmp/project/.venv/bin/python")

    command = manager.install_selected_text_correction_shortcut(
        binding="<Primary>space",
        debug=True,
    )

    assert command.endswith("run-selected-text-correction --debug")
