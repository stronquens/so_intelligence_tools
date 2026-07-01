from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from so_intelligence_tools.infrastructure.config import ToolRunnerSettings


ShortcutPlatform = Literal["linux", "windows", "desktop"]


@dataclass(frozen=True, slots=True)
class ShortcutMapEntry:
    feature: str
    platform: ShortcutPlatform
    shortcut: str
    env_var: str
    mechanism: str
    status: str
    notes: str = ""


def build_shortcut_map(settings: ToolRunnerSettings) -> list[ShortcutMapEntry]:
    return [
        ShortcutMapEntry(
            feature="Selected text correction",
            platform="linux",
            shortcut=settings.gnome_selected_text_correction_binding,
            env_var="GNOME_SELECTED_TEXT_CORRECTION_BINDING",
            mechanism="GNOME custom shortcut",
            status="active",
            notes="Installed by install-linux-desktop-integration.",
        ),
        ShortcutMapEntry(
            feature="System audio translation",
            platform="linux",
            shortcut=settings.gnome_system_audio_translation_binding,
            env_var="GNOME_SYSTEM_AUDIO_TRANSLATION_BINDING",
            mechanism="GNOME custom shortcut",
            status="active",
            notes="Toggle action.",
        ),
        ShortcutMapEntry(
            feature="Voice translation virtual microphone",
            platform="linux",
            shortcut=settings.gnome_voice_translation_binding,
            env_var="GNOME_VOICE_TRANSLATION_BINDING",
            mechanism="GNOME custom shortcut",
            status="active",
            notes="Toggle action.",
        ),
        ShortcutMapEntry(
            feature="Push-to-talk dictation",
            platform="linux",
            shortcut=settings.push_to_talk_dictation_shortcut,
            env_var="PUSH_TO_TALK_DICTATION_SHORTCUT",
            mechanism="press-and-hold listener service",
            status="active",
            notes="Service installed by install-push-to-talk-dictation-service.",
        ),
        ShortcutMapEntry(
            feature="Open overlay",
            platform="windows",
            shortcut="Ctrl + Alt + A",
            env_var="Windows shell shortcut",
            mechanism="Electron desktop launcher",
            status="active",
            notes="Launches the app; Electron single-instance handling toggles the overlay.",
        ),
        ShortcutMapEntry(
            feature="Selected text correction",
            platform="windows",
            shortcut=settings.windows_selected_text_correction_shortcut,
            env_var="WINDOWS_SELECTED_TEXT_CORRECTION_SHORTCUT",
            mechanism="Windows global shortcut listener",
            status="active",
            notes="Started by listen-shortcuts or Windows Startup launcher.",
        ),
        ShortcutMapEntry(
            feature="Push-to-talk dictation",
            platform="windows",
            shortcut=settings.windows_push_to_talk_dictation_shortcut,
            env_var="WINDOWS_PUSH_TO_TALK_DICTATION_SHORTCUT",
            mechanism="press-and-hold listener",
            status="active",
            notes="Default uses Ctrl+Shift+Space to avoid common Ctrl+Space OS shortcut collisions.",
        ),
        ShortcutMapEntry(
            feature="Open overlay",
            platform="desktop",
            shortcut="Ctrl + Alt + A",
            env_var="desktop-settings.json",
            mechanism="Electron desktop setting",
            status="ui-setting",
            notes="Matches the Windows launcher hotkey on the current desktop setup.",
        ),
        ShortcutMapEntry(
            feature="Selected text correction",
            platform="desktop",
            shortcut="Ctrl + Alt + C",
            env_var="desktop-settings.json",
            mechanism="Electron desktop setting",
            status="ui-setting",
            notes="Visible in overlay settings; OS listener uses platform env vars.",
        ),
        ShortcutMapEntry(
            feature="Screenshot OCR",
            platform="desktop",
            shortcut="Ctrl + Alt + O",
            env_var="desktop-settings.json",
            mechanism="Electron desktop setting",
            status="planned",
            notes="Visible in overlay settings; tool is not wired as an OS shortcut yet.",
        ),
        ShortcutMapEntry(
            feature="System audio translation",
            platform="desktop",
            shortcut="Ctrl + Alt + T",
            env_var="desktop-settings.json",
            mechanism="Electron desktop setting",
            status="ui-setting",
            notes="OS shortcut uses GNOME_SYSTEM_AUDIO_TRANSLATION_BINDING on Linux.",
        ),
        ShortcutMapEntry(
            feature="Voice translation virtual microphone",
            platform="desktop",
            shortcut="Ctrl + Alt + M",
            env_var="desktop-settings.json",
            mechanism="Electron desktop setting",
            status="ui-setting",
            notes="OS shortcut uses GNOME_VOICE_TRANSLATION_BINDING on Linux.",
        ),
        ShortcutMapEntry(
            feature="Push-to-talk dictation",
            platform="desktop",
            shortcut="Ctrl + Shift + Space",
            env_var="desktop-settings.json",
            mechanism="Electron desktop setting",
            status="planned",
            notes="Visible in overlay settings; OS listener uses platform env vars.",
        ),
        ShortcutMapEntry(
            feature="Assistant",
            platform="desktop",
            shortcut="Sin asignar",
            env_var="desktop-settings.json",
            mechanism="Electron desktop setting",
            status="planned",
            notes="Ctrl+Alt+A is reserved for opening the main overlay.",
        ),
        ShortcutMapEntry(
            feature="Summary",
            platform="desktop",
            shortcut="Ctrl + Alt + R",
            env_var="desktop-settings.json",
            mechanism="Electron desktop setting",
            status="planned",
        ),
        ShortcutMapEntry(
            feature="Intelligent capture",
            platform="desktop",
            shortcut="Ctrl + Alt + I",
            env_var="desktop-settings.json",
            mechanism="Electron desktop setting",
            status="planned",
        ),
    ]


def filter_shortcut_map(
    entries: list[ShortcutMapEntry],
    platform: ShortcutPlatform | None,
) -> list[ShortcutMapEntry]:
    if platform is None:
        return entries
    return [entry for entry in entries if entry.platform == platform]


def format_shortcut_map(entries: list[ShortcutMapEntry]) -> str:
    headers = ["Platform", "Feature", "Shortcut", "Config", "Mechanism", "Status"]
    rows = [
        [
            entry.platform,
            entry.feature,
            entry.shortcut,
            entry.env_var,
            entry.mechanism,
            entry.status,
        ]
        for entry in entries
    ]
    return _format_table(headers, rows)


def _format_table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [
        max(len(str(value)) for value in column)
        for column in zip(headers, *rows, strict=False)
    ]
    header_line = "  ".join(
        value.ljust(width) for value, width in zip(headers, widths, strict=False)
    )
    separator = "  ".join("-" * width for width in widths)
    row_lines = [
        "  ".join(value.ljust(width) for value, width in zip(row, widths, strict=False))
        for row in rows
    ]
    return "\n".join([header_line, separator, *row_lines])
