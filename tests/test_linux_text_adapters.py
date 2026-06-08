from __future__ import annotations

import subprocess

import pytest

from so_intelligence_tools.adapters.linux.clipboard import LinuxClipboardAdapter
from so_intelligence_tools.adapters.linux.keyboard import LinuxKeyboardAutomationAdapter
from so_intelligence_tools.adapters.linux.text_insertion import LinuxCommandTextInsertionAdapter
from so_intelligence_tools.adapters.linux.text_selection import LinuxCommandTextSelectionAdapter
from so_intelligence_tools.domain.errors import UnsupportedEnvironmentError
from so_intelligence_tools.infrastructure.config import ToolRunnerSettings


class FakeClipboard:
    def __init__(self, initial: str | None) -> None:
        self.current = initial
        self.primary: str | None = None
        self.history: list[str | None] = []

    def get_primary_text(self) -> str | None:
        return self.primary

    def get_text(self) -> str | None:
        return self.current

    def set_text(self, text: str) -> None:
        self.current = text
        self.history.append(text)


class FakeKeyboard:
    def __init__(self, clipboard: FakeClipboard, *, copied_text: str = "texto seleccionado") -> None:
        self.clipboard = clipboard
        self.copied_text = copied_text
        self.copy_calls = 0
        self.paste_calls = 0
        self.typed_texts: list[str] = []

    def trigger_copy_selection(self) -> None:
        self.copy_calls += 1
        self.clipboard.current = self.copied_text

    def trigger_paste(self) -> None:
        self.paste_calls += 1

    def type_text(self, text: str) -> None:
        self.typed_texts.append(text)


def make_settings() -> ToolRunnerSettings:
    return ToolRunnerSettings(
        linux_read_selection_command=None,
        linux_replace_selection_command=None,
    )


def test_text_selection_adapter_prefers_primary_selection_before_clipboard_roundtrip():
    clipboard = FakeClipboard("clipboard original")
    clipboard.primary = "texto primario x11"
    keyboard = FakeKeyboard(clipboard, copied_text="texto desde foco")
    adapter = LinuxCommandTextSelectionAdapter(
        make_settings(),
        clipboard=clipboard,
        keyboard=keyboard,
    )

    result = adapter.get_selected_text()

    assert result == "texto primario x11"
    assert keyboard.copy_calls == 0


def test_text_selection_adapter_uses_clipboard_roundtrip_when_primary_is_empty():
    clipboard = FakeClipboard("clipboard original")
    keyboard = FakeKeyboard(clipboard, copied_text="texto desde foco")
    adapter = LinuxCommandTextSelectionAdapter(
        make_settings(),
        clipboard=clipboard,
        keyboard=keyboard,
    )

    result = adapter.get_selected_text()

    assert result == "texto desde foco"
    assert keyboard.copy_calls == 1
    assert clipboard.current == "clipboard original"


def test_text_selection_adapter_returns_none_when_copy_does_not_update_clipboard():
    clipboard = FakeClipboard("clipboard original")
    keyboard = FakeKeyboard(clipboard)

    def no_op_copy() -> None:
        keyboard.copy_calls += 1

    keyboard.trigger_copy_selection = no_op_copy  # type: ignore[method-assign]
    adapter = LinuxCommandTextSelectionAdapter(
        make_settings(),
        clipboard=clipboard,
        keyboard=keyboard,
    )

    result = adapter.get_selected_text()

    assert result is None
    assert keyboard.copy_calls == 1
    assert clipboard.current == "clipboard original"


def test_text_selection_adapter_reads_wayland_primary_selection(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    clipboard = FakeClipboard("clipboard original")
    clipboard.primary = "texto primario"
    keyboard = FakeKeyboard(clipboard)
    adapter = LinuxCommandTextSelectionAdapter(
        make_settings(),
        clipboard=clipboard,
        keyboard=keyboard,
    )

    result = adapter.get_selected_text()

    assert result == "texto primario"
    assert keyboard.copy_calls == 0


def test_text_insertion_adapter_leaves_corrected_text_in_clipboard_on_x11():
    os_session = __import__("os").environ.get("XDG_SESSION_TYPE")
    clipboard = FakeClipboard("clipboard original")
    keyboard = FakeKeyboard(clipboard)
    adapter = LinuxCommandTextInsertionAdapter(
        make_settings(),
        clipboard=clipboard,
        keyboard=keyboard,
    )
    try:
        __import__("os").environ["XDG_SESSION_TYPE"] = "x11"
        adapter.replace_selected_text("texto nuevo")
    finally:
        if os_session is None:
            __import__("os").environ.pop("XDG_SESSION_TYPE", None)
        else:
            __import__("os").environ["XDG_SESSION_TYPE"] = os_session

    assert keyboard.paste_calls == 1
    assert clipboard.history == ["texto nuevo"]
    assert clipboard.current == "texto nuevo"


def test_text_insertion_adapter_pastes_clipboard_text_on_wayland(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    clipboard = FakeClipboard("clipboard original")
    keyboard = FakeKeyboard(clipboard)
    adapter = LinuxCommandTextInsertionAdapter(
        make_settings(),
        clipboard=clipboard,
        keyboard=keyboard,
    )

    adapter.replace_selected_text("texto nuevo")

    assert clipboard.history == ["texto nuevo"]
    assert keyboard.paste_calls == 1


def test_wayland_clipboard_requires_wl_clipboard(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setattr("shutil.which", lambda _: None)
    adapter = LinuxClipboardAdapter()

    with pytest.raises(UnsupportedEnvironmentError):
        adapter.get_text()


def test_x11_clipboard_prefers_xclip_even_if_wl_clipboard_is_installed(monkeypatch):
    calls: list[list[str]] = []

    def fake_which(command: str) -> str | None:
        if command in {"wl-copy", "wl-paste", "xclip"}:
            return f"/usr/bin/{command}"
        return None

    def fake_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "texto", "")

    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.setattr("shutil.which", fake_which)
    monkeypatch.setattr("subprocess.run", fake_run)
    adapter = LinuxClipboardAdapter()

    assert adapter.get_text() == "texto"
    adapter.set_text("nuevo texto")

    assert calls == [
        ["xclip", "-selection", "clipboard", "-o"],
        ["xclip", "-selection", "clipboard"],
    ]


def test_wayland_keyboard_requires_system_keyboard_automation(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setattr("shutil.which", lambda _: None)
    adapter = LinuxKeyboardAutomationAdapter()

    with pytest.raises(UnsupportedEnvironmentError):
        adapter.type_text("hola")


def test_wayland_keyboard_prefers_ydotool(monkeypatch):
    calls: list[list[str]] = []

    def fake_which(command: str) -> str | None:
        return f"/usr/bin/{command}" if command == "ydotool" else None

    def fake_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setattr("shutil.which", fake_which)
    monkeypatch.setattr("subprocess.run", fake_run)

    adapter = LinuxKeyboardAutomationAdapter()
    adapter.trigger_copy_selection()
    adapter.trigger_paste()
    adapter.type_text("hola")

    assert calls == [
        ["ydotool", "key", "29:1", "46:1", "46:0", "29:0"],
        ["ydotool", "key", "29:1", "47:1", "47:0", "29:0"],
        ["ydotool", "type", "hola"],
    ]


def test_ydotool_uses_tmp_socket_when_inherited_socket_is_missing(monkeypatch):
    captured_envs: list[dict[str, str]] = []

    def fake_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        captured_envs.append(kwargs["env"])
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setenv("YDOTOOL_SOCKET", "/run/user/1001/.ydotool_socket")
    monkeypatch.setattr("os.path.exists", lambda path: path == "/tmp/.ydotool_socket")
    monkeypatch.setattr("subprocess.run", fake_run)

    LinuxKeyboardAutomationAdapter._run_ydotool_key(["29:1", "46:1", "46:0", "29:0"])

    assert captured_envs[0]["YDOTOOL_SOCKET"] == "/tmp/.ydotool_socket"


def test_wayland_keyboard_reports_wtype_compositor_rejection(monkeypatch):
    def fake_which(command: str) -> str | None:
        return f"/usr/bin/{command}" if command == "wtype" else None

    def fake_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            command,
            1,
            "",
            "Compositor does not support the virtual keyboard protocol",
        )

    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setattr("shutil.which", fake_which)
    monkeypatch.setattr("subprocess.run", fake_run)

    adapter = LinuxKeyboardAutomationAdapter()

    with pytest.raises(UnsupportedEnvironmentError, match="GNOME Wayland"):
        adapter.trigger_copy_selection()
