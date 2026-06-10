from __future__ import annotations

from so_intelligence_tools.infrastructure.shortcut_actions import ShortcutActionRegistry


def test_shortcut_action_registry_registers_and_executes_action():
    registry = ShortcutActionRegistry()
    called: list[str] = []

    registry.register("selected-text-correction", lambda: called.append("ok") or "done")

    result = registry.execute("selected-text-correction")

    assert registry.has_action("selected-text-correction") is True
    assert called == ["ok"]
    assert result == "done"
