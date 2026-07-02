from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Iterable
from urllib.parse import unquote, urlparse


HIDDEN_ITEM_TYPES = {
    "reasoning",
    "internal_reasoning",
    "chain_of_thought",
}

VISIBLE_PROGRESS_TYPES = {
    "command_execution",
    "mcp_tool_call",
    "plan_update",
    "tool_call",
    "web_search",
    "file_change",
}

FENCED_CODE_BLOCK_RE = re.compile(r"```([^\n`]*)\n?(.*?)```", flags=re.DOTALL)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
RAW_URL_RE = re.compile(r"(?<!\w)(https?://[^\s<>)]+)")
SPEECH_DETAIL_ALIASES = {
    "default": "standard",
    "messages": "standard",
    "normal": "standard",
    "verbose": "full",
    "exhaustive": "full",
}
SPEECH_DETAILS = {"minimal", "actions", "standard", "no-code", "full"}


@dataclass(slots=True)
class CodexVisibleEventExtractor:
    include_progress: bool = False
    speech_detail: str = "standard"
    max_segment_chars: int = 500
    skip_code_blocks: bool = True
    _delta_buffer: str = field(default="", init=False)
    _saw_agent_delta: bool = field(default=False, init=False)

    def feed_line(self, line: str) -> list[str]:
        stripped = line.strip()
        if not stripped:
            return []
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            return []
        return self.feed(payload)

    def feed(self, payload: dict[str, Any]) -> list[str]:
        method = str(payload.get("method") or "")
        event_type = str(payload.get("type") or "")
        if method == "item/agentMessage/delta":
            if not _detail_allows_messages(self.speech_detail):
                return []
            return self._feed_delta(_extract_text(payload.get("params")))
        if method in {"turn/completed", "turn/failed"} or event_type in {
            "turn.completed",
            "turn.failed",
        }:
            segments = self.flush()
            if self.include_progress and _detail_allows_lifecycle(self.speech_detail):
                completion_text = _turn_completion_text(method, event_type)
                if completion_text:
                    segments.extend(self._prepare_text(completion_text))
            self._saw_agent_delta = False
            return segments

        if self._saw_agent_delta and _is_completed_agent_message(payload):
            return self.flush()
        text = parse_visible_text_from_codex_event(
            payload,
            include_progress=self.include_progress,
            speech_detail=self.speech_detail,
        )
        if not text:
            return []
        return self._prepare_text(text)

    def flush(self) -> list[str]:
        if not self._delta_buffer.strip():
            self._delta_buffer = ""
            return []
        text = self._delta_buffer
        self._delta_buffer = ""
        return self._prepare_text(text)

    def _feed_delta(self, delta: str) -> list[str]:
        if not delta:
            return []
        self._saw_agent_delta = True
        self._delta_buffer += delta
        ready, remainder = _split_ready_sentences(self._delta_buffer)
        self._delta_buffer = remainder
        if not ready:
            return []
        return self._prepare_text(" ".join(ready))

    def _prepare_text(self, text: str) -> list[str]:
        cleaned = clean_visible_text(
            text,
            skip_code_blocks=self.skip_code_blocks,
            code_block_mode=_code_block_mode_for_detail(self.speech_detail),
            shorten_urls=self.speech_detail != "full",
        )
        if not cleaned:
            return []
        return list(chunk_text(cleaned, max_chars=self.max_segment_chars))


def parse_visible_text_from_codex_event(
    payload: dict[str, Any],
    *,
    include_progress: bool = False,
    speech_detail: str = "standard",
) -> str | None:
    speech_detail = normalize_speech_detail(speech_detail)
    event_type = str(payload.get("type") or "")
    method = str(payload.get("method") or "")
    item = _extract_item(payload)
    item_type = str(item.get("type") or "")
    if item_type in HIDDEN_ITEM_TYPES:
        return None
    if include_progress:
        progress_text = _extract_progress_text(
            event_type,
            method,
            item,
            payload,
            speech_detail=speech_detail,
        )
        if progress_text:
            return progress_text
    if event_type == "item.completed" or method == "item/completed":
        if item_type == "agent_message" and _detail_allows_messages(speech_detail):
            return _extract_text(item)
    if (
        event_type == "assistant_message" or method == "assistant/message"
    ) and _detail_allows_messages(speech_detail):
        return _extract_text(payload.get("params") or payload)
    if (
        include_progress
        and _detail_allows_status(speech_detail)
        and event_type in {"status", "progress"}
    ):
        return _extract_text(payload)
    return None


def normalize_speech_detail(value: str | None) -> str:
    normalized = (value or "standard").strip().lower()
    normalized = SPEECH_DETAIL_ALIASES.get(normalized, normalized)
    return normalized if normalized in SPEECH_DETAILS else "standard"


def clean_visible_text(
    text: str,
    *,
    skip_code_blocks: bool = True,
    code_block_mode: str | None = None,
    shorten_urls: bool = True,
) -> str:
    value = text.strip()
    if not value:
        return ""
    mode = code_block_mode or ("announce" if skip_code_blocks else "preserve")
    if mode == "announce":
        value = FENCED_CODE_BLOCK_RE.sub(_spoken_fenced_code_block, value)
        value = re.sub(r"`([^`]{80,})`", " código omitido ", value)
    elif mode == "drop":
        value = FENCED_CODE_BLOCK_RE.sub(" ", value)
        value = re.sub(r"`([^`]{80,})`", " ", value)
    elif mode == "preserve":
        value = FENCED_CODE_BLOCK_RE.sub(_preserved_fenced_code_block, value)
    if shorten_urls:
        value = MARKDOWN_LINK_RE.sub(_spoken_markdown_link, value)
        value = RAW_URL_RE.sub(_spoken_raw_url, value)
    else:
        value = MARKDOWN_LINK_RE.sub(r"\1, \2", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def chunk_text(text: str, *, max_chars: int = 500) -> Iterable[str]:
    if len(text) <= max_chars:
        yield text
        return
    sentences = re.split(r"(?<=[.!?¿¡])\s+", text)
    chunk = ""
    for sentence in sentences:
        if not sentence:
            continue
        if chunk and len(chunk) + len(sentence) + 1 > max_chars:
            yield chunk.strip()
            chunk = sentence
        else:
            chunk = f"{chunk} {sentence}".strip()
    if chunk:
        yield chunk.strip()


def _extract_item(payload: dict[str, Any]) -> dict[str, Any]:
    item = payload.get("item")
    if isinstance(item, dict):
        return item
    params = payload.get("params")
    if isinstance(params, dict):
        nested = params.get("item")
        if isinstance(nested, dict):
            return nested
    return {}


def _is_completed_agent_message(payload: dict[str, Any]) -> bool:
    event_type = str(payload.get("type") or "")
    method = str(payload.get("method") or "")
    if event_type != "item.completed" and method != "item/completed":
        return False
    return str(_extract_item(payload).get("type") or "") == "agent_message"


def _extract_progress_text(
    event_type: str,
    method: str,
    item: dict[str, Any],
    payload: dict[str, Any],
    *,
    speech_detail: str,
) -> str | None:
    item_type = str(item.get("type") or "")
    started = event_type == "item.started" or method == "item/started"
    completed = event_type == "item.completed" or method == "item/completed"
    failed = event_type == "item.failed" or method == "item/failed"

    if started:
        return _started_progress_text(item_type, item, speech_detail=speech_detail)
    if completed or failed:
        return _completed_progress_text(
            item_type,
            item,
            failed=failed,
            speech_detail=speech_detail,
        )
    if item_type in VISIBLE_PROGRESS_TYPES and _detail_allows_status(speech_detail):
        return _extract_text(item)
    if (
        event_type == "turn.started" or method == "turn/started"
    ) and _detail_allows_lifecycle(speech_detail):
        return "Inicio de tarea."
    if (
        event_type == "turn.failed" or method == "turn/failed"
    ) and _detail_allows_lifecycle(speech_detail):
        return "El turno terminó con error."
    if _detail_allows_status(speech_detail):
        return _extract_status_progress_text(event_type, method, payload)
    return None


def _turn_completion_text(method: str, event_type: str) -> str | None:
    if method == "turn/completed" or event_type == "turn.completed":
        return "Fin de tarea."
    if method == "turn/failed" or event_type == "turn.failed":
        return "Fin de tarea con error."
    return None


def _started_progress_text(
    item_type: str,
    item: dict[str, Any],
    *,
    speech_detail: str,
) -> str | None:
    if not _detail_allows_actions(speech_detail):
        return None
    if item_type == "command_execution":
        return "Ejecutando comando."
    if item_type in {"tool_call", "mcp_tool_call"}:
        tool_name = _safe_label(
            item.get("name")
            or item.get("tool_name")
            or item.get("tool")
            or item.get("raw_name")
        )
        return f"Usando herramienta {tool_name}." if tool_name else "Usando herramienta."
    if item_type == "web_search":
        return "Buscando en la web."
    if item_type == "file_change":
        return "Preparando cambios de archivos."
    if item_type == "plan_update":
        return "Actualizando el plan."
    return None


def _completed_progress_text(
    item_type: str,
    item: dict[str, Any],
    *,
    failed: bool,
    speech_detail: str,
) -> str | None:
    if not _detail_allows_actions(speech_detail):
        return None
    if item_type == "command_execution":
        exit_code = item.get("exit_code")
        status = str(item.get("status") or "").lower()
        if failed or status in {"failed", "error"} or _nonzero_exit_code(exit_code):
            return "El comando terminó con error."
        return "Comando terminado."
    if item_type in {"tool_call", "mcp_tool_call"}:
        return "La herramienta terminó con error." if failed else "Herramienta terminada."
    if item_type == "web_search":
        return "Búsqueda web completada."
    if item_type == "file_change":
        return "Cambios de archivos registrados."
    if item_type == "plan_update":
        return _extract_text(item) or "Plan actualizado."
    return None


def _extract_status_progress_text(
    event_type: str,
    method: str,
    payload: dict[str, Any],
) -> str | None:
    if event_type in {"status", "progress"} or method in {"status", "progress"}:
        return _extract_text(payload.get("params") or payload)
    return None


def _detail_allows_lifecycle(speech_detail: str) -> bool:
    return normalize_speech_detail(speech_detail) in {
        "minimal",
        "actions",
        "standard",
        "no-code",
        "full",
    }


def _detail_allows_actions(speech_detail: str) -> bool:
    return normalize_speech_detail(speech_detail) in {
        "actions",
        "standard",
        "no-code",
        "full",
    }


def _detail_allows_status(speech_detail: str) -> bool:
    return normalize_speech_detail(speech_detail) in {"standard", "no-code", "full"}


def _detail_allows_messages(speech_detail: str) -> bool:
    return normalize_speech_detail(speech_detail) in {"standard", "no-code", "full"}


def _code_block_mode_for_detail(speech_detail: str) -> str:
    detail = normalize_speech_detail(speech_detail)
    if detail == "no-code":
        return "drop"
    if detail == "full":
        return "preserve"
    return "announce"


def _nonzero_exit_code(exit_code: Any) -> bool:
    if isinstance(exit_code, int):
        return exit_code != 0
    if isinstance(exit_code, str) and exit_code.strip().lstrip("-").isdigit():
        return int(exit_code) != 0
    return False


def _safe_label(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    label = re.sub(r"[^A-Za-z0-9_.:-]+", " ", value).strip()
    return label[:60].strip()


def _spoken_fenced_code_block(match: re.Match[str]) -> str:
    language = match.group(1).strip().lower().split(maxsplit=1)[0]
    label = f" {language}" if language else ""
    return f" Bloque de código{label} omitido. "


def _preserved_fenced_code_block(match: re.Match[str]) -> str:
    language = match.group(1).strip().lower().split(maxsplit=1)[0]
    body = match.group(2).strip()
    label = f" {language}" if language else ""
    if not body:
        return f" Bloque de código{label} vacío. "
    return f" Bloque de código{label}. {body}. Fin del bloque de código. "


def _spoken_markdown_link(match: re.Match[str]) -> str:
    label = match.group(1).strip()
    url = match.group(2).strip()
    tail = _url_tail(url)
    if not label:
        return f"URL {tail}"
    return f"{label}, URL {tail}"


def _spoken_raw_url(match: re.Match[str]) -> str:
    return f"URL {_url_tail(match.group(1))}"


def _url_tail(url: str) -> str:
    parsed = urlparse(url)
    path = unquote(parsed.path or "").rstrip("/")
    tail = path.rsplit("/", 1)[-1] if path else ""
    if not tail:
        tail = parsed.hostname or "enlace"
    if parsed.fragment and not path:
        tail = unquote(parsed.fragment.rsplit("/", 1)[-1]) or tail
    return _safe_spoken_url_tail(tail)


def _safe_spoken_url_tail(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._~+-]+", " ", value).strip()
    return cleaned[:80] if cleaned else "enlace"


def _extract_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if not isinstance(payload, dict):
        return ""
    for key in ("text", "delta", "message", "content", "summary"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""


def _split_ready_sentences(text: str) -> tuple[list[str], str]:
    boundaries = _ready_boundaries(text)
    if not boundaries:
        return [], text
    ready: list[str] = []
    start = 0
    for boundary in boundaries:
        segment = text[start:boundary].strip()
        if segment:
            ready.append(segment)
        start = boundary
    remainder = text[start:].lstrip()
    return ready, remainder


def _ready_boundaries(text: str) -> list[int]:
    boundaries: list[int] = []
    in_fence = False
    index = 0
    while index < len(text):
        if text.startswith("```", index):
            in_fence = not in_fence
            index += 3
            continue
        char = text[index]
        if not in_fence and char in ".!?":
            next_index = index + 1
            if next_index == len(text) or text[next_index].isspace():
                boundaries.append(_consume_following_space(text, next_index))
                index = boundaries[-1]
                continue
        if not in_fence and char == "\n":
            boundaries.append(index + 1)
        index += 1
    return _dedupe_sorted_boundaries(boundaries)


def _consume_following_space(text: str, index: int) -> int:
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def _dedupe_sorted_boundaries(boundaries: list[int]) -> list[int]:
    deduped: list[int] = []
    for boundary in boundaries:
        if boundary > 0 and (not deduped or boundary > deduped[-1]):
            deduped.append(boundary)
    return deduped
