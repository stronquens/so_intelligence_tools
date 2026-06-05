from __future__ import annotations

import pytest

from so_intelligence_tools.adapters.testing.fakes import (
    CollectingNotificationAdapter,
    FakeInferenceAdapter,
    InlineTextSelectionAdapter,
    MemoryClipboardAdapter,
    MemoryTextInsertionAdapter,
    StaticImageScreenshotAdapter,
)
from so_intelligence_tools.application.use_cases.correct_selected_text import (
    correct_selected_text,
)
from so_intelligence_tools.application.use_cases.extract_text_from_image import (
    extract_text_from_image,
)
from so_intelligence_tools.domain.errors import NoSelectionError


def test_correct_selected_text_replaces_text_and_notifies():
    inference = FakeInferenceAdapter(text_response="Texto corregido.")
    selection = InlineTextSelectionAdapter("Texto corrregido.")
    insertion = MemoryTextInsertionAdapter()
    notifications = CollectingNotificationAdapter()

    result = correct_selected_text(
        inference=inference,
        text_selection=selection,
        text_insertion=insertion,
        notifications=notifications,
    )

    assert result == "Texto corregido."
    assert insertion.last_text == "Texto corregido."
    assert notifications.messages[-1].level == "success"
    assert inference.last_text_prompt == "Texto corrregido."


def test_correct_selected_text_reports_missing_selection():
    inference = FakeInferenceAdapter()
    selection = InlineTextSelectionAdapter(None)
    insertion = MemoryTextInsertionAdapter()
    notifications = CollectingNotificationAdapter()

    with pytest.raises(NoSelectionError):
        correct_selected_text(
            inference=inference,
            text_selection=selection,
            text_insertion=insertion,
            notifications=notifications,
        )

    assert notifications.messages[-1].level == "warning"


def test_extract_text_from_image_copies_result_to_clipboard():
    inference = FakeInferenceAdapter(image_response="Test 123")
    screenshot = StaticImageScreenshotAdapter(b"fake-image")
    clipboard = MemoryClipboardAdapter()
    notifications = CollectingNotificationAdapter()

    result = extract_text_from_image(
        inference=inference,
        screenshot=screenshot,
        clipboard=clipboard,
        notifications=notifications,
    )

    assert result == "Test 123"
    assert clipboard.last_text == "Test 123"
    assert notifications.messages[-1].level == "success"
    assert inference.last_image_bytes == b"fake-image"
