from __future__ import annotations

from dataclasses import dataclass

from so_intelligence_tools.adapters.linux.clipboard import LinuxClipboardAdapter
from so_intelligence_tools.adapters.linux.notification import LinuxNotificationAdapter
from so_intelligence_tools.adapters.linux.screenshot import LinuxScreenshotAdapter
from so_intelligence_tools.adapters.linux.text_insertion import LinuxCommandTextInsertionAdapter
from so_intelligence_tools.adapters.linux.text_selection import LinuxCommandTextSelectionAdapter
from so_intelligence_tools.infrastructure.config import (
    ToolRunnerSettings,
    get_tool_runner_settings,
)
from so_intelligence_tools.infrastructure.inference_client import LocalInferenceClient


@dataclass(slots=True)
class LinuxRuntime:
    inference_client: LocalInferenceClient
    clipboard: LinuxClipboardAdapter
    notifications: LinuxNotificationAdapter
    screenshot: LinuxScreenshotAdapter
    text_selection: LinuxCommandTextSelectionAdapter
    text_insertion: LinuxCommandTextInsertionAdapter


def build_linux_runtime(settings: ToolRunnerSettings | None = None) -> LinuxRuntime:
    runtime_settings = settings or get_tool_runner_settings()
    return LinuxRuntime(
        inference_client=LocalInferenceClient(runtime_settings),
        clipboard=LinuxClipboardAdapter(),
        notifications=LinuxNotificationAdapter(runtime_settings),
        screenshot=LinuxScreenshotAdapter(),
        text_selection=LinuxCommandTextSelectionAdapter(runtime_settings),
        text_insertion=LinuxCommandTextInsertionAdapter(runtime_settings),
    )
