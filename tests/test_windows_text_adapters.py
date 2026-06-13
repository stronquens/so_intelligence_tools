from __future__ import annotations

import sys

import pytest

from so_intelligence_tools.adapters.windows.clipboard import WindowsClipboardAdapter
from so_intelligence_tools.adapters.windows.text_insertion import (
    WindowsCommandTextInsertionAdapter,
)
from so_intelligence_tools.adapters.windows.text_selection import (
    WindowsCommandTextSelectionAdapter,
)
from so_intelligence_tools.domain.errors import UnsupportedEnvironmentError
from so_intelligence_tools.infrastructure import runtime as runtime_module


class FakeClipboard:
    def __init__(self, initial: str | None) -> None:
        self.current = initial
        self.history: list[str | None] = []
        self.cleared = False

    def get_text(self) -> str | None:
        return self.current

    def set_text(self, text: str) -> None:
        self.current = text
        self.history.append(text)

    def clear_text(self) -> None:
        self.current = None
        self.cleared = True


class FakeKeyboard:
    def __init__(
        self,
        clipboard: FakeClipboard,
        *,
        copied_text: str = "selected text",
        select_all_text: str = "all input text",
        select_all_copy_results: list[str] | None = None,
    ) -> None:
        self.clipboard = clipboard
        self.copied_text = copied_text
        self.select_all_text = select_all_text
        self.select_all_copy_results = list(select_all_copy_results or [])
        self.copy_calls = 0
        self.select_all_calls = 0
        self.paste_calls = 0
        self._select_all_active = False

    def trigger_copy_selection(self) -> None:
        self.copy_calls += 1
        if self._select_all_active:
            if self.select_all_copy_results:
                self.clipboard.current = self.select_all_copy_results.pop(0)
            else:
                self.clipboard.current = self.select_all_text
            return
        self.clipboard.current = self.copied_text

    def trigger_select_all(self) -> None:
        self.select_all_calls += 1
        self._select_all_active = True

    def trigger_paste(self) -> None:
        self.paste_calls += 1


def test_windows_text_selection_uses_clipboard_roundtrip_and_restores_previous_text():
    clipboard = FakeClipboard("previous clipboard")
    keyboard = FakeKeyboard(clipboard, copied_text="texto seleccionado")
    adapter = WindowsCommandTextSelectionAdapter(
        clipboard=clipboard,
        keyboard=keyboard,
    )

    result = adapter.get_selected_text()

    assert result == "texto seleccionado"
    assert keyboard.copy_calls == 1
    assert keyboard.select_all_calls == 0
    assert clipboard.current == "previous clipboard"
    assert clipboard.history[-1] == "previous clipboard"


def test_windows_text_selection_clears_probe_when_clipboard_was_empty():
    clipboard = FakeClipboard(None)
    keyboard = FakeKeyboard(clipboard, copied_text="texto seleccionado")
    adapter = WindowsCommandTextSelectionAdapter(
        clipboard=clipboard,
        keyboard=keyboard,
    )

    assert adapter.get_selected_text() == "texto seleccionado"
    assert clipboard.current is None
    assert clipboard.cleared is True


def test_windows_text_selection_selects_all_focused_input_when_no_text_is_selected():
    clipboard = FakeClipboard("previous clipboard")
    keyboard = FakeKeyboard(clipboard, copied_text="", select_all_text="todo el input")
    adapter = WindowsCommandTextSelectionAdapter(
        clipboard=clipboard,
        keyboard=keyboard,
    )

    result = adapter.get_selected_text()

    assert result == "todo el input"
    assert keyboard.copy_calls == 2
    assert keyboard.select_all_calls == 1
    assert clipboard.current == "previous clipboard"


def test_windows_text_selection_retries_copy_after_select_all_if_first_copy_is_empty():
    clipboard = FakeClipboard("previous clipboard")
    keyboard = FakeKeyboard(
        clipboard,
        copied_text="",
        select_all_copy_results=["", "todo el input"],
    )
    adapter = WindowsCommandTextSelectionAdapter(
        clipboard=clipboard,
        keyboard=keyboard,
    )

    result = adapter.get_selected_text()

    assert result == "todo el input"
    assert keyboard.copy_calls == 3
    assert keyboard.select_all_calls == 1
    assert clipboard.current == "previous clipboard"


def test_windows_text_insertion_sets_clipboard_and_pastes():
    clipboard = FakeClipboard("old")
    keyboard = FakeKeyboard(clipboard)
    adapter = WindowsCommandTextInsertionAdapter(
        clipboard=clipboard,
        keyboard=keyboard,
    )

    adapter.replace_selected_text("new text")

    assert clipboard.current == "new text"
    assert keyboard.paste_calls == 1


def test_windows_clipboard_rejects_non_windows_platform(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    adapter = WindowsClipboardAdapter()

    with pytest.raises(UnsupportedEnvironmentError, match="solo funciona en Windows"):
        adapter.get_text()


def test_build_runtime_selects_linux(monkeypatch):
    linux_runtime = object()
    monkeypatch.setattr(runtime_module, "build_linux_runtime", lambda settings=None: linux_runtime)

    assert runtime_module.build_runtime(platform_name="linux") is linux_runtime


def test_build_runtime_selects_windows(monkeypatch):
    windows_runtime = object()
    monkeypatch.setattr(
        runtime_module,
        "build_windows_runtime",
        lambda settings=None: windows_runtime,
    )

    assert runtime_module.build_runtime(platform_name="win32") is windows_runtime


def test_build_runtime_rejects_unsupported_platform():
    with pytest.raises(UnsupportedEnvironmentError, match="No hay runtime"):
        runtime_module.build_runtime(platform_name="darwin")
