from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Protocol

from so_intelligence_tools.adapters.linux.clipboard import LinuxClipboardAdapter
from so_intelligence_tools.adapters.linux.keyboard import LinuxKeyboardAutomationAdapter
from so_intelligence_tools.adapters.linux.notification import LinuxNotificationAdapter
from so_intelligence_tools.adapters.linux.screenshot import LinuxScreenshotAdapter
from so_intelligence_tools.adapters.linux.text_insertion import LinuxCommandTextInsertionAdapter
from so_intelligence_tools.adapters.linux.text_selection import LinuxCommandTextSelectionAdapter
from so_intelligence_tools.domain.errors import UnsupportedEnvironmentError
from so_intelligence_tools.infrastructure.config import (
    ToolRunnerSettings,
    get_tool_runner_settings,
)
from so_intelligence_tools.infrastructure.inference_client import LocalInferenceClient
from so_intelligence_tools.ports.clipboard import ClipboardPort
from so_intelligence_tools.ports.inference import InferencePort
from so_intelligence_tools.ports.notification import NotificationPort
from so_intelligence_tools.ports.text_insertion import TextInsertionPort
from so_intelligence_tools.ports.text_selection import TextSelectionPort


class ToolRuntime(Protocol):
    inference_client: InferencePort
    clipboard: ClipboardPort
    notifications: NotificationPort
    text_selection: TextSelectionPort
    text_insertion: TextInsertionPort


@dataclass(slots=True)
class LinuxRuntime:
    inference_client: LocalInferenceClient
    clipboard: LinuxClipboardAdapter
    keyboard: LinuxKeyboardAutomationAdapter
    notifications: LinuxNotificationAdapter
    screenshot: LinuxScreenshotAdapter
    text_selection: LinuxCommandTextSelectionAdapter
    text_insertion: LinuxCommandTextInsertionAdapter


@dataclass(slots=True)
class WindowsRuntime:
    inference_client: LocalInferenceClient
    clipboard: ClipboardPort
    notifications: NotificationPort
    text_selection: TextSelectionPort
    text_insertion: TextInsertionPort


def build_linux_runtime(settings: ToolRunnerSettings | None = None) -> LinuxRuntime:
    runtime_settings = settings or get_tool_runner_settings()
    clipboard = LinuxClipboardAdapter()
    keyboard = LinuxKeyboardAutomationAdapter()
    return LinuxRuntime(
        inference_client=LocalInferenceClient(runtime_settings),
        clipboard=clipboard,
        keyboard=keyboard,
        notifications=LinuxNotificationAdapter(runtime_settings),
        screenshot=LinuxScreenshotAdapter(),
        text_selection=LinuxCommandTextSelectionAdapter(
            runtime_settings, clipboard=clipboard, keyboard=keyboard
        ),
        text_insertion=LinuxCommandTextInsertionAdapter(
            runtime_settings, clipboard=clipboard, keyboard=keyboard
        ),
    )


def build_windows_runtime(settings: ToolRunnerSettings | None = None) -> WindowsRuntime:
    from so_intelligence_tools.adapters.windows.clipboard import WindowsClipboardAdapter
    from so_intelligence_tools.adapters.windows.keyboard import WindowsKeyboardAutomationAdapter
    from so_intelligence_tools.adapters.windows.notification import WindowsNotificationAdapter
    from so_intelligence_tools.adapters.windows.text_insertion import (
        WindowsCommandTextInsertionAdapter,
    )
    from so_intelligence_tools.adapters.windows.text_selection import (
        WindowsCommandTextSelectionAdapter,
    )

    runtime_settings = settings or get_tool_runner_settings()
    clipboard = WindowsClipboardAdapter()
    keyboard = WindowsKeyboardAutomationAdapter()
    return WindowsRuntime(
        inference_client=LocalInferenceClient(runtime_settings),
        clipboard=clipboard,
        notifications=WindowsNotificationAdapter(),
        text_selection=WindowsCommandTextSelectionAdapter(
            clipboard=clipboard,
            keyboard=keyboard,
        ),
        text_insertion=WindowsCommandTextInsertionAdapter(
            clipboard=clipboard,
            keyboard=keyboard,
        ),
    )


def build_runtime(
    settings: ToolRunnerSettings | None = None,
    *,
    platform_name: str | None = None,
) -> ToolRuntime:
    detected_platform = platform_name or sys.platform
    if detected_platform.startswith("linux"):
        return build_linux_runtime(settings)
    if detected_platform == "win32":
        return build_windows_runtime(settings)
    raise UnsupportedEnvironmentError(
        f"No hay runtime de escritorio soportado para la plataforma: {detected_platform}"
    )
