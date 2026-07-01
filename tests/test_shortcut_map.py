from __future__ import annotations

from so_intelligence_tools.cli import main as cli_main
from so_intelligence_tools.infrastructure.config import ToolRunnerSettings
from so_intelligence_tools.infrastructure.shortcut_map import (
    build_shortcut_map,
    filter_shortcut_map,
    format_shortcut_map,
)


def test_shortcut_map_uses_effective_settings_values():
    settings = ToolRunnerSettings(
        _env_file=None,
        gnome_selected_text_correction_binding="<Primary><Alt>k",
        windows_push_to_talk_dictation_shortcut="<ctrl>+<alt>+x",
    )

    entries = build_shortcut_map(settings)

    assert any(
        entry.platform == "linux"
        and entry.feature == "Selected text correction"
        and entry.shortcut == "<Primary><Alt>k"
        and entry.env_var == "GNOME_SELECTED_TEXT_CORRECTION_BINDING"
        for entry in entries
    )
    assert any(
        entry.platform == "windows"
        and entry.feature == "Push-to-talk dictation"
        and entry.shortcut == "<ctrl>+<alt>+x"
        and entry.env_var == "WINDOWS_PUSH_TO_TALK_DICTATION_SHORTCUT"
        for entry in entries
    )
    assert any(
        entry.platform == "linux"
        and entry.feature == "Push-to-talk dictation"
        and entry.shortcut == "<ctrl>+<shift>+<space>"
        and entry.env_var == "PUSH_TO_TALK_DICTATION_SHORTCUT"
        for entry in build_shortcut_map(ToolRunnerSettings(_env_file=None))
    )


def test_shortcut_map_can_filter_by_platform():
    settings = ToolRunnerSettings(_env_file=None)

    entries = filter_shortcut_map(build_shortcut_map(settings), "windows")

    assert entries
    assert {entry.platform for entry in entries} == {"windows"}
    assert any(
        entry.feature == "Open overlay"
        and entry.shortcut == "Ctrl + Alt + A"
        and entry.status == "active"
        for entry in entries
    )


def test_format_shortcut_map_outputs_readable_table():
    settings = ToolRunnerSettings(_env_file=None)

    output = format_shortcut_map(filter_shortcut_map(build_shortcut_map(settings), "linux"))

    assert "Platform" in output
    assert "Selected text correction" in output
    assert "GNOME_SELECTED_TEXT_CORRECTION_BINDING" in output


def test_show_shortcuts_cli_prints_filtered_map(monkeypatch, capsys):
    monkeypatch.setattr(
        cli_main,
        "get_tool_runner_settings",
        lambda: ToolRunnerSettings(_env_file=None),
    )

    exit_code = cli_main.main(["show-shortcuts", "--platform", "windows"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Open overlay" in captured.out
    assert "Ctrl + Alt + A" in captured.out
    assert "WINDOWS_SELECTED_TEXT_CORRECTION_SHORTCUT" in captured.out
    assert "GNOME_SELECTED_TEXT_CORRECTION_BINDING" not in captured.out
