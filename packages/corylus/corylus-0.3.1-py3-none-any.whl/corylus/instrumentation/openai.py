__all__ = ['instrument_openai_logging', 'uninstrument_openai_logging']

from __future__ import annotations

import functools
import json
from typing import Any, Callable, Optional

from ..log import getLogger

log = getLogger(__name__)

# We keep these as module-level so we can restore them in uninstrument_openai_logging.
_ORIGINAL_CHAT_COMPLETIONS_CREATE: Optional[Callable[..., Any]] = None
_ORIGINAL_RESPONSES_CREATE: Optional[Callable[..., Any]] = None

# We also keep a reference to the OpenAI class once imported, to avoid
# re-importing and to allow uninstrumentation to work cleanly.
_OpenAIClass: Optional[type] = None


def _lazy_import_openai() -> type:
    """
    Import and return the OpenAI client class lazily.

    Raises ImportError if openai is not installed.
    """
    global _OpenAIClass
    if _OpenAIClass is not None:
        return _OpenAIClass

    try:
        from openai import OpenAI  # type: ignore[import]
    except ImportError as e:
        # Do not raise at module import; only here when instrumentation is requested.
        raise ImportError(
            "openai package is required to instrument OpenAI, "
            "but it is not installed."
        ) from e

    _OpenAIClass = OpenAI
    return OpenAI


def _safe_model_dump(obj: Any) -> Any:
    """
    Try model_dump (Pydantic-style) first, fall back to dict/attrs/plain obj.
    """
    for attr in ("model_dump", "dict"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                pass
    try:
        return obj.__dict__
    except Exception:
        return obj


def _shorten(text: Any, max_len: int = 100_000) -> str:
    """
    Avoid dumping megabytes to logs; truncate and annotate.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    if max_len <= 0 or len(text) <= max_len:
        return text
    return text[:max_len] + f"... [truncated, total_length={len(text)}]"


def instrument_openai_logging(
    log_requests: bool = True,
    log_responses: bool = True,
    include_raw_json: bool = False,
    truncate_content: int = 800,
) -> None:
    """
    Globally instrument the OpenAI Python client to log requests and responses
    via corylus.log.

    This is a NO-OP until you call it. If the 'openai' package is not installed,
    this function will raise ImportError.

    Typical usage:

        from corylus.instrumentation.openai import instrument_openai_logging
        instrument_openai_logging()

        from openai import OpenAI
        client = OpenAI()
        # All client.chat.completions.create / client.responses.create
        # calls in this process are now logged.

    Parameters
    ----------
    log_requests : bool
        Log outbound request payload (model, messages/input).
    log_responses : bool
        Log response payload (id, content/choices, usage).
    include_raw_json : bool
        If True, include full JSON-like payloads in logs (can be very large).
    truncate_content : int
        Maximum length for content snippets in logs; 0 disables truncation.
    """
    global _ORIGINAL_CHAT_COMPLETIONS_CREATE, _ORIGINAL_RESPONSES_CREATE

    OpenAI = _lazy_import_openai()  # Raises if openai not installed.

    # Idempotency for chat.completions.create
    if _ORIGINAL_CHAT_COMPLETIONS_CREATE is None:
        _ORIGINAL_CHAT_COMPLETIONS_CREATE = OpenAI.chat.completions.create

        @functools.wraps(_ORIGINAL_CHAT_COMPLETIONS_CREATE)
        def _wrapped_chat_completions_create(self, *args, **kwargs):
            model = kwargs.get("model", None)
            messages = kwargs.get("messages", None)

            if log_requests:
                try:
                    simple_msgs = []
                    if isinstance(messages, list):
                        for m in messages:
                            if not isinstance(m, dict):
                                simple_msgs.append(str(m))
                                continue
                            role = m.get("role")
                            content = m.get("content")
                            if isinstance(content, list):
                                # Multi-part content (e.g. image + text); flatten into a string.
                                content = " ".join(
                                    part.get("text", "") if isinstance(part, dict) else str(part)
                                    for part in content
                                )
                            simple_msgs.append(
                                {
                                    "role": role,
                                    "content": _shorten(content, truncate_content),
                                }
                            )

                    # Your `corylus.log` can decide how to handle structured extra.
                    log.info(
                        "openai.chat.completions.create request",
                        extra={
                            "event": "openai_request",
                            "api": "chat.completions.create",
                            "model": model,
                            "messages": simple_msgs,
                        },
                    )
                except Exception:
                    log.exception("Failed to log OpenAI chat request")

            resp = _ORIGINAL_CHAT_COMPLETIONS_CREATE(self, *args, **kwargs)

            if log_responses:
                try:
                    resp_id = getattr(resp, "id", None)
                    choices = getattr(resp, "choices", []) or []
                    usage = getattr(resp, "usage", None)

                    assistant_texts = []
                    for ch in choices:
                        msg = getattr(ch, "message", None)
                        if msg is None:
                            continue
                        content = getattr(msg, "content", None)
                        assistant_texts.append(
                            {
                                "role": getattr(msg, "role", "assistant"),
                                "content": _shorten(content, truncate_content),
                            }
                        )

                    payload: dict[str, Any] = {
                        "event": "openai_response",
                        "api": "chat.completions.create",
                        "id": resp_id,
                        "model": model,
                        "choices": assistant_texts,
                    }
                    if usage is not None:
                        try:
                            payload["usage"] = _safe_model_dump(usage)
                        except Exception:
                            payload["usage"] = str(usage)

                    if include_raw_json:
                        payload["raw"] = _safe_model_dump(resp)

                    # If your logging backend prefers flat logs, you can change this
                    # to encode payload as JSON string.
                    log.info(
                        "openai.chat.completions.create response: %s",
                        json.dumps(payload, ensure_ascii=False),
                    )
                except Exception:
                    log.exception("Failed to log OpenAI chat response")

            return resp

        OpenAI.chat.completions.create = _wrapped_chat_completions_create
        log.debug("Instrumented OpenAI.chat.completions.create")

    else:
        log.debug("OpenAI.chat.completions.create already instrumented; skipping")

    # Idempotency for responses.create
    # Not all versions of openai have `responses`, so guard it.
    if _ORIGINAL_RESPONSES_CREATE is not None:
        log.debug("OpenAI.responses.create already instrumented; skipping")
        return

    responses_attr = getattr(OpenAI, "responses", None)
    if responses_attr is None or not hasattr(responses_attr, "create"):
        log.debug("OpenAI client has no .responses.create; skipping responses instrumentation")
        return

    _ORIGINAL_RESPONSES_CREATE = OpenAI.responses.create

    @functools.wraps(_ORIGINAL_RESPONSES_CREATE)
    def _wrapped_responses_create(self, *args, **kwargs):
        model = kwargs.get("model", None)
        input_data = kwargs.get("input", None)

        if log_requests:
            try:
                text = _shorten(input_data, truncate_content)
                log.info(
                    "openai.responses.create request",
                    extra={
                        "event": "openai_request",
                        "api": "responses.create",
                        "model": model,
                        "input": text,
                    },
                )
            except Exception:
                log.exception("Failed to log OpenAI responses.create request")

        resp = _ORIGINAL_RESPONSES_CREATE(self, *args, **kwargs)

        if log_responses:
            try:
                resp_id = getattr(resp, "id", None)
                usage = getattr(resp, "usage", None)

                text_outputs: list[str] = []
                output = getattr(resp, "output", None) or []
                for item in output:
                    content = getattr(item, "content", None) or []
                    for part in content:
                        part_type = getattr(part, "type", None)
                        if part_type == "output_text":
                            txt_obj = getattr(part, "text", None)
                            if txt_obj is None:
                                continue
                            # Some clients use .value, some use .text; we try both.
                            txt_val = getattr(txt_obj, "value", None) or getattr(
                                txt_obj, "text", None
                            ) or str(txt_obj)
                            text_outputs.append(_shorten(txt_val, truncate_content))

                payload = {
                    "event": "openai_response",
                    "api": "responses.create",
                    "id": resp_id,
                    "model": model,
                    "outputs": text_outputs,
                }
                if usage is not None:
                    payload["usage"] = _safe_model_dump(usage)
                if include_raw_json:
                    payload["raw"] = _safe_model_dump(resp)

                log.info(
                    "openai.responses.create response: %s",
                    json.dumps(payload, ensure_ascii=False),
                )
            except Exception:
                log.exception("Failed to log OpenAI responses.create response")

        return resp

    OpenAI.responses.create = _wrapped_responses_create
    log.debug("Instrumented OpenAI.responses.create")


def uninstrument_openai_logging() -> None:
    """
    Restore the original OpenAI methods, undoing global instrumentation.

    Safe to call even if instrumentation was never applied.
    """
    global _ORIGINAL_CHAT_COMPLETIONS_CREATE, _ORIGINAL_RESPONSES_CREATE

    if _OpenAIClass is None:
        # OpenAI was never imported via this instrumentation; nothing to unpatch.
        return

    OpenAI = _OpenAIClass

    if _ORIGINAL_CHAT_COMPLETIONS_CREATE is not None:
        try:
            OpenAI.chat.completions.create = _ORIGINAL_CHAT_COMPLETIONS_CREATE
            log.debug("Restored OpenAI.chat.completions.create")
        except Exception:
            log.exception("Failed to restore OpenAI.chat.completions.create")
        finally:
            _ORIGINAL_CHAT_COMPLETIONS_CREATE = None

    if _ORIGINAL_RESPONSES_CREATE is not None:
        try:
            OpenAI.responses.create = _ORIGINAL_RESPONSES_CREATE
            log.debug("Restored OpenAI.responses.create")
        except Exception:
            log.exception("Failed to restore OpenAI.responses.create")
        finally:
            _ORIGINAL_RESPONSES_CREATE = None
