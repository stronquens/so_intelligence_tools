from __future__ import annotations

import json
import threading

from so_intelligence_tools.local_tts.codex_events import (
    CodexVisibleEventExtractor,
    clean_visible_text,
    parse_visible_text_from_codex_event,
)
from so_intelligence_tools.local_tts.codex_voice import run_codex_visible_event_listener


class CollectingClient:
    def __init__(self) -> None:
        self.spoken: list[str] = []

    def speak(self, text: str):
        self.spoken.append(text)


class BlockingClient:
    def __init__(self) -> None:
        self.spoken: list[str] = []
        self.started = threading.Event()
        self.release = threading.Event()

    def speak(self, text: str):
        self.spoken.append(text)
        self.started.set()
        self.release.wait(timeout=2)


def test_parse_codex_exec_agent_message():
    text = parse_visible_text_from_codex_event(
        {
            "type": "item.completed",
            "item": {"type": "agent_message", "text": "Mensaje visible."},
        }
    )

    assert text == "Mensaje visible."


def test_parse_codex_event_never_speaks_reasoning():
    text = parse_visible_text_from_codex_event(
        {
            "type": "item.completed",
            "item": {"type": "reasoning", "text": "razonamiento privado"},
        },
        include_progress=True,
    )

    assert text is None


def test_parse_codex_event_announces_command_lifecycle_without_payload():
    started = parse_visible_text_from_codex_event(
        {
            "type": "item.started",
            "item": {"type": "command_execution", "command": "cat secret.txt"},
        },
        include_progress=True,
    )
    completed = parse_visible_text_from_codex_event(
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "cat secret.txt",
                "output": "contenido privado",
                "exit_code": 0,
            },
        },
        include_progress=True,
    )

    assert started == "Ejecutando comando."
    assert completed == "Comando terminado."


def test_parse_codex_event_announces_tool_lifecycle_without_arguments():
    started = parse_visible_text_from_codex_event(
        {
            "type": "item.started",
            "item": {
                "type": "tool_call",
                "name": "functions.exec_command",
                "arguments": {"cmd": "cat secret.txt"},
            },
        },
        include_progress=True,
    )
    completed = parse_visible_text_from_codex_event(
        {
            "type": "item.completed",
            "item": {
                "type": "tool_call",
                "name": "functions.exec_command",
                "output": "contenido privado",
            },
        },
        include_progress=True,
    )

    assert started == "Usando herramienta functions.exec_command."
    assert completed == "Herramienta terminada."


def test_minimal_detail_only_speaks_task_boundaries():
    extractor = CodexVisibleEventExtractor(
        include_progress=True, speech_detail="minimal"
    )

    assert extractor.feed({"method": "turn/started", "params": {}}) == [
        "Inicio de tarea."
    ]
    assert (
        extractor.feed(
            {"method": "item/agentMessage/delta", "params": {"delta": "Hola."}}
        )
        == []
    )
    assert (
        extractor.feed(
            {
                "type": "item.started",
                "item": {"type": "command_execution", "command": "pytest"},
            }
        )
        == []
    )
    assert (
        extractor.feed(
            {
                "method": "item/completed",
                "params": {"item": {"type": "agent_message", "text": "Hola."}},
            }
        )
        == []
    )
    assert extractor.feed({"method": "turn/completed", "params": {}}) == [
        "Fin de tarea."
    ]


def test_extractor_deduplicates_repeated_turn_start_events():
    extractor = CodexVisibleEventExtractor(
        include_progress=True, speech_detail="actions"
    )

    assert extractor.feed({"method": "turn/started", "params": {}}) == [
        "Inicio de tarea."
    ]
    assert extractor.feed({"method": "turn/started", "params": {}}) == []
    assert extractor.feed({"type": "turn.started"}) == []


def test_actions_detail_speaks_boundaries_and_tool_calls_not_messages():
    extractor = CodexVisibleEventExtractor(
        include_progress=True, speech_detail="actions"
    )

    assert extractor.feed(
        {
            "type": "item.started",
            "item": {"type": "tool_call", "name": "functions.exec_command"},
        }
    ) == ["Usando herramienta functions.exec_command."]
    assert (
        extractor.feed(
            {"method": "item/agentMessage/delta", "params": {"delta": "Hola."}}
        )
        == []
    )


def test_extractor_does_not_end_turn_for_premature_completion_before_tool_call():
    extractor = CodexVisibleEventExtractor(
        include_progress=True, speech_detail="actions"
    )

    assert extractor.feed({"method": "turn/started", "params": {}}) == [
        "Inicio de tarea."
    ]
    assert extractor.feed({"method": "turn/completed", "params": {}}) == []
    assert extractor.feed(
        {
            "method": "item/started",
            "params": {"item": {"type": "tool_call", "name": "functions.exec_command"}},
        }
    ) == ["Usando herramienta functions.exec_command."]
    assert extractor.feed(
        {
            "method": "item/completed",
            "params": {"item": {"type": "tool_call", "name": "functions.exec_command"}},
        }
    ) == ["Herramienta terminada."]
    assert (
        extractor.feed(
            {"method": "item/agentMessage/delta", "params": {"delta": "He terminado."}}
        )
        == []
    )
    assert extractor.feed({"method": "turn/completed", "params": {}}) == [
        "Fin de tarea."
    ]


def test_extractor_ignores_completion_for_another_correlated_turn():
    extractor = CodexVisibleEventExtractor(
        include_progress=True, speech_detail="actions"
    )

    assert extractor.feed(_turn_started("thread-a", "turn-a")) == ["Inicio de tarea."]
    assert extractor.feed(_agent_delta("thread-a", "turn-a", "Voy a revisarlo.")) == []
    assert extractor.feed(_turn_completed("thread-b", "turn-b")) == []
    assert extractor.feed(_turn_completed("thread-a", "turn-a")) == ["Fin de tarea."]


def test_extractor_deduplicates_correlated_completion():
    extractor = CodexVisibleEventExtractor(
        include_progress=True, speech_detail="actions"
    )

    assert extractor.feed(_turn_started("thread-a", "turn-a")) == ["Inicio de tarea."]
    assert extractor.feed(_turn_completed("thread-a", "turn-a")) == ["Fin de tarea."]
    assert extractor.feed(_turn_completed("thread-a", "turn-a")) == []


def test_extractor_deduplicates_correlated_completion_without_start():
    extractor = CodexVisibleEventExtractor(
        include_progress=True, speech_detail="actions"
    )

    assert extractor.feed(_turn_completed("thread-a", "turn-a")) == ["Fin de tarea."]
    assert extractor.feed(_turn_completed("thread-a", "turn-a")) == []


def test_extractor_ignores_background_progress_for_another_turn():
    extractor = CodexVisibleEventExtractor(
        include_progress=True, speech_detail="actions"
    )

    assert extractor.feed(_turn_started("thread-a", "turn-a")) == ["Inicio de tarea."]
    assert (
        extractor.feed(
            _item_started("thread-b", "turn-b", item_type="command_execution")
        )
        == []
    )
    assert extractor.feed(
        _item_started("thread-a", "turn-a", item_type="command_execution")
    ) == ["Ejecutando comando."]


def test_extractor_does_not_flush_text_for_unrelated_completion():
    extractor = CodexVisibleEventExtractor(
        include_progress=True, speech_detail="standard"
    )

    assert extractor.feed(_turn_started("thread-a", "turn-a")) == ["Inicio de tarea."]
    assert (
        extractor.feed(_agent_delta("thread-a", "turn-a", "Mensaje sin punto final"))
        == []
    )
    assert extractor.feed(_turn_completed("thread-b", "turn-b")) == []
    assert extractor.feed(_turn_completed("thread-a", "turn-a")) == [
        "Mensaje sin punto final",
        "Fin de tarea.",
    ]


def test_extractor_uses_terminal_turn_status_for_completion_speech():
    extractor = CodexVisibleEventExtractor(
        include_progress=True, speech_detail="actions"
    )

    assert extractor.feed(_turn_started("thread-a", "turn-a")) == ["Inicio de tarea."]
    assert extractor.feed(_turn_completed("thread-a", "turn-a", status="failed")) == [
        "Fin de tarea con error."
    ]


def test_extractor_preserves_identifierless_legacy_fallback():
    extractor = CodexVisibleEventExtractor(
        include_progress=True, speech_detail="actions"
    )

    assert extractor.feed({"method": "turn/started", "params": {}}) == [
        "Inicio de tarea."
    ]
    assert extractor.feed({"method": "turn/completed", "params": {}}) == []
    assert (
        extractor.feed(
            {"method": "item/agentMessage/delta", "params": {"delta": "Listo."}}
        )
        == []
    )
    assert extractor.feed({"method": "turn/completed", "params": {}}) == [
        "Fin de tarea."
    ]


def test_extractor_correlates_snake_case_legacy_alias_identifiers():
    extractor = CodexVisibleEventExtractor(
        include_progress=True, speech_detail="actions"
    )

    assert extractor.feed(
        {
            "type": "codex/event/task_started",
            "thread_id": "thread-a",
            "turn_id": "turn-a",
        }
    ) == ["Inicio de tarea."]
    assert (
        extractor.feed(
            {
                "type": "codex/event/task_complete",
                "thread_id": "thread-b",
                "turn_id": "turn-b",
            }
        )
        == []
    )
    assert extractor.feed(
        {
            "type": "codex/event/task_complete",
            "thread_id": "thread-a",
            "turn_id": "turn-a",
        }
    ) == ["Fin de tarea."]


def test_no_code_detail_drops_code_blocks():
    extractor = CodexVisibleEventExtractor(speech_detail="no-code")

    assert extractor.feed(
        {
            "type": "item.completed",
            "item": {
                "type": "agent_message",
                "text": "Antes. ```bash\npoetry run pytest\n``` Después.",
            },
        }
    ) == ["Antes. Después."]


def test_full_detail_preserves_code_and_full_urls():
    text = clean_visible_text(
        "Mira https://developers.openai.com/codex/app-server.md\n"
        "```bash\npoetry run pytest\n```",
        code_block_mode="preserve",
        shorten_urls=False,
    )

    assert "https://developers.openai.com/codex/app-server.md" in text
    assert "poetry run pytest" in text
    assert "Fin del bloque de código." in text


def test_extractor_speaks_app_server_deltas_when_sentence_completes():
    extractor = CodexVisibleEventExtractor()

    assert (
        extractor.feed(
            {"method": "item/agentMessage/delta", "params": {"delta": "Hola"}}
        )
        == []
    )
    assert extractor.feed(
        {"method": "item/agentMessage/delta", "params": {"delta": " mundo."}}
    ) == ["Hola mundo."]


def test_extractor_does_not_repeat_completed_message_after_deltas():
    extractor = CodexVisibleEventExtractor()

    assert extractor.feed(
        {"method": "item/agentMessage/delta", "params": {"delta": "Hola mundo."}}
    ) == ["Hola mundo."]
    assert (
        extractor.feed(
            {
                "method": "item/completed",
                "params": {"item": {"type": "agent_message", "text": "Hola mundo."}},
            }
        )
        == []
    )


def test_extractor_flushes_unfinished_delta_on_completed_message():
    extractor = CodexVisibleEventExtractor()

    assert (
        extractor.feed(
            {
                "method": "item/agentMessage/delta",
                "params": {"delta": "Hola sin punto final"},
            }
        )
        == []
    )
    assert extractor.feed(
        {
            "method": "item/completed",
            "params": {
                "item": {
                    "type": "agent_message",
                    "text": "Hola sin punto final",
                }
            },
        }
    ) == ["Hola sin punto final"]


def test_extractor_announces_turn_completion_when_progress_enabled():
    extractor = CodexVisibleEventExtractor(include_progress=True)

    assert (
        extractor.feed(
            {"method": "item/agentMessage/delta", "params": {"delta": "Listo"}}
        )
        == []
    )
    assert extractor.feed({"method": "turn/completed", "params": {}}) == [
        "Listo",
        "Fin de tarea.",
    ]


def test_extractor_does_not_announce_turn_completion_without_progress():
    extractor = CodexVisibleEventExtractor(include_progress=False)

    assert extractor.feed({"method": "turn/completed", "params": {}}) == []


def test_clean_visible_text_summarizes_non_shell_code_blocks():
    text = clean_visible_text("Lee esto. ```python\nprint('no')\n``` Fin.")

    assert "print" not in text
    assert text == "Lee esto. Bloque de código python omitido. Fin."


def test_clean_visible_text_announces_bash_code_blocks_without_reading_commands():
    text = clean_visible_text(
        "Ejecuta esto:\n```bash\npoetry run pytest\n"
        "docker compose up -d && curl http://127.0.0.1:9011/health\n```"
    )

    assert text == "Ejecuta esto: Bloque de código bash omitido."
    assert "poetry run pytest" not in text
    assert "docker compose" not in text


def test_clean_visible_text_summarizes_raw_urls_with_tail_only():
    text = clean_visible_text(
        "Mira https://developers.openai.com/codex/app-server.md y seguimos."
    )

    assert text == "Mira URL app-server.md y seguimos."
    assert "developers.openai.com/codex" not in text


def test_clean_visible_text_summarizes_markdown_links_with_label_and_tail():
    text = clean_visible_text(
        "Consulta [la guía](https://developers.openai.com/codex/ide/settings.md)."
    )

    assert text == "Consulta la guía, URL settings.md."


def test_extractor_speaks_complete_lines_without_waiting_for_periods():
    extractor = CodexVisibleEventExtractor()

    assert extractor.feed(
        {"method": "item/agentMessage/delta", "params": {"delta": "Pasos:\n"}}
    ) == ["Pasos:"]
    assert extractor.feed(
        {"method": "item/agentMessage/delta", "params": {"delta": "- ejecutar tests\n"}}
    ) == ["- ejecutar tests"]


def test_extractor_waits_for_closing_code_fence_before_speaking_bash_block():
    extractor = CodexVisibleEventExtractor()

    assert (
        extractor.feed(
            {"method": "item/agentMessage/delta", "params": {"delta": "```bash\n"}}
        )
        == []
    )
    assert (
        extractor.feed(
            {
                "method": "item/agentMessage/delta",
                "params": {"delta": "poetry run pytest\n"},
            }
        )
        == []
    )
    assert extractor.feed(
        {"method": "item/agentMessage/delta", "params": {"delta": "```\n"}}
    ) == ["Bloque de código bash omitido."]


def test_listener_reads_jsonl_visible_messages():
    client = CollectingClient()
    lines = [
        json.dumps(
            {
                "type": "item.completed",
                "item": {"type": "agent_message", "text": "Respuesta visible."},
            }
        )
        + "\n",
        json.dumps(
            {
                "type": "item.completed",
                "item": {"type": "reasoning", "text": "no leer"},
            }
        )
        + "\n",
    ]

    result = run_codex_visible_event_listener(lines=lines, client=client)

    assert result == 0
    assert client.spoken == ["Respuesta visible."]


def test_listener_reads_visible_cycle_when_progress_enabled():
    client = CollectingClient()
    lines = [
        json.dumps(
            {
                "type": "item.started",
                "item": {"type": "command_execution", "command": "cat secret.txt"},
            }
        )
        + "\n",
        json.dumps(
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "cat secret.txt",
                    "output": "contenido privado",
                    "exit_code": 0,
                },
            }
        )
        + "\n",
    ]

    result = run_codex_visible_event_listener(
        lines=lines,
        client=client,
        include_progress=True,
    )

    assert result == 0
    assert client.spoken == ["Ejecutando comando.", "Comando terminado."]


def test_listener_prioritizes_turn_completion_over_queued_message_segments():
    client = BlockingClient()
    first_line = (
        json.dumps(
            {
                "method": "item/agentMessage/delta",
                "params": {"delta": "Primer segmento.\n"},
            }
        )
        + "\n"
    )
    remaining_lines = [
        json.dumps(
            {
                "method": "item/agentMessage/delta",
                "params": {"delta": "Segmento que debe limpiarse.\n"},
            }
        )
        + "\n",
        json.dumps({"method": "turn/completed", "params": {}}) + "\n",
    ]

    def line_source():
        yield first_line
        assert client.started.wait(timeout=2)
        yield from remaining_lines

    listener = threading.Thread(
        target=run_codex_visible_event_listener,
        kwargs={"lines": line_source(), "client": client, "include_progress": True},
    )
    listener.start()
    assert client.started.wait(timeout=2)
    client.release.set()
    listener.join(timeout=2)

    assert client.spoken == ["Primer segmento.", "Fin de tarea."]


def test_listener_does_not_clear_queue_for_unrelated_completion():
    client = BlockingClient()
    first_line = (
        json.dumps(_agent_delta("thread-a", "turn-a", "Primer segmento.\n")) + "\n"
    )
    remaining_lines = [
        json.dumps(_agent_delta("thread-a", "turn-a", "Segundo segmento.\n")) + "\n",
        json.dumps(_turn_completed("thread-b", "turn-b")) + "\n",
    ]

    def line_source():
        yield first_line
        assert client.started.wait(timeout=2)
        yield from remaining_lines

    listener = threading.Thread(
        target=run_codex_visible_event_listener,
        kwargs={"lines": line_source(), "client": client, "include_progress": True},
    )
    listener.start()
    assert client.started.wait(timeout=2)
    client.release.set()
    listener.join(timeout=2)

    assert client.spoken == ["Primer segmento.", "Segundo segmento."]


def _turn_started(thread_id: str, turn_id: str) -> dict:
    return {
        "method": "turn/started",
        "params": {
            "threadId": thread_id,
            "turn": {"id": turn_id, "status": "inProgress", "items": []},
        },
    }


def _turn_completed(thread_id: str, turn_id: str, *, status: str = "completed") -> dict:
    return {
        "method": "turn/completed",
        "params": {
            "threadId": thread_id,
            "turn": {"id": turn_id, "status": status, "items": []},
        },
    }


def _agent_delta(thread_id: str, turn_id: str, delta: str) -> dict:
    return {
        "method": "item/agentMessage/delta",
        "params": {
            "threadId": thread_id,
            "turnId": turn_id,
            "itemId": "message-1",
            "delta": delta,
        },
    }


def _item_started(thread_id: str, turn_id: str, *, item_type: str) -> dict:
    return {
        "method": "item/started",
        "params": {
            "threadId": thread_id,
            "turnId": turn_id,
            "startedAtMs": 1,
            "item": {"id": "item-1", "type": item_type},
        },
    }
