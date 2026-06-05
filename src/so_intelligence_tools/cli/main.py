from __future__ import annotations

import argparse

from so_intelligence_tools.adapters.testing.fakes import (
    CollectingNotificationAdapter,
    FileScreenshotAdapter,
    InlineTextSelectionAdapter,
    MemoryClipboardAdapter,
    MemoryTextInsertionAdapter,
)
from so_intelligence_tools.application.use_cases.correct_selected_text import (
    correct_selected_text,
)
from so_intelligence_tools.application.use_cases.extract_text_from_image import (
    extract_text_from_image,
)
from so_intelligence_tools.infrastructure.config import get_tool_runner_settings
from so_intelligence_tools.infrastructure.inference_client import LocalInferenceClient
from so_intelligence_tools.infrastructure.logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="so-intelligence-tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    correct_parser = subparsers.add_parser("correct-text")
    correct_parser.add_argument("--text", required=True)
    correct_parser.add_argument("--reasoning-mode", default="off")

    image_parser = subparsers.add_parser("extract-image-text")
    image_parser.add_argument("--image-path", required=True)
    image_parser.add_argument("--reasoning-mode", default="off")

    return parser


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = get_tool_runner_settings()
    inference_client = LocalInferenceClient(settings)
    notifications = CollectingNotificationAdapter()

    if args.command == "correct-text":
        selection = InlineTextSelectionAdapter(args.text)
        insertion = MemoryTextInsertionAdapter()
        result = correct_selected_text(
            inference=inference_client,
            text_selection=selection,
            text_insertion=insertion,
            notifications=notifications,
            reasoning_mode=args.reasoning_mode,
        )
        print(result)
        return 0

    if args.command == "extract-image-text":
        screenshot = FileScreenshotAdapter(args.image_path)
        clipboard = MemoryClipboardAdapter()
        result = extract_text_from_image(
            inference=inference_client,
            screenshot=screenshot,
            clipboard=clipboard,
            notifications=notifications,
            reasoning_mode=args.reasoning_mode,
        )
        print(result)
        return 0

    parser.error("Unsupported command")
    return 2
