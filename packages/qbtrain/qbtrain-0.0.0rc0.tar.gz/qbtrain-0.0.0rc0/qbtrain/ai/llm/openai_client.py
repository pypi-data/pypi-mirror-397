# qbtrain/ai/llm/openai_client.py
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, Generator, List, Optional, Type, TypeVar, cast

from openai import OpenAI
from pydantic import BaseModel

from .base_llm_client import LLMClient, Message

R = TypeVar("R")
MessageList = Optional[List[Message]]


def _enforce_openai_guardrails(fn: Callable[..., R]) -> Callable[..., R]:
    """
    Validate:
      - model is available (if gated)
      - unsupported params for Responses API (top_k, presence/frequency penalties)
    """
    @wraps(fn)
    def wrapper(self: "OpenAIClient", *args: Any, **kwargs: Any) -> R:
        model = cast(str, kwargs.get("model"))
        if not model:
            raise ValueError("model is required (pass by keyword)")

        if self.available_models and model not in self.available_models:
            raise ValueError(f"Model {model} is not supported by OpenAIClient.")

        if int(kwargs.get("top_k", 1)) != 1:
            raise ValueError("OpenAI Responses API does not support top_k != 1.")
        if float(kwargs.get("presence_penalty", 0.0)) != 0.0:
            raise ValueError("OpenAI Responses API does not support presence_penalty.")
        if float(kwargs.get("frequency_penalty", 0.0)) != 0.0:
            raise ValueError("OpenAI Responses API does not support frequency_penalty.")

        return fn(self, *args, **kwargs)

    return wrapper


class OpenAIClient(LLMClient):
    client_id = "openai"
    display_name = "OpenAI"
    available_models = ["gpt-4o", "gpt-4o-mini"]
    param_display_names = {"api_key": "API Key"}

    def __init__(self, api_key: str):
        # Do not persist secrets elsewhere; only kept inside client instance.
        self.client = OpenAI(api_key=api_key)

    @staticmethod
    def _build_input(prompt: str, conversation_history: MessageList) -> List[Message]:
        items: List[Message] = []
        if conversation_history:
            items.extend(conversation_history)
        items.append({"role": "user", "content": prompt})
        return items

    @_enforce_openai_guardrails
    def response(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        conversation_history: MessageList = None,
        top_k: int = 1,
        top_p: float = 1.0,
        temperature: float = 0.7,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        max_output_tokens: int = 1024,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        rsp = self.client.responses.create(
            model=model,
            input=self._build_input(prompt, conversation_history),
            instructions=system_prompt or None,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            **kwargs,
        )
        return rsp.output_text

    @_enforce_openai_guardrails
    def json_response(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        schema: Type[BaseModel],
        conversation_history: MessageList = None,
        top_k: int = 1,
        top_p: float = 1.0,
        temperature: float = 0.7,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        max_output_tokens: int = 1024,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        rsp = self.client.responses.parse(
            model=model,
            input=self._build_input(prompt, conversation_history),
            instructions=system_prompt or None,
            text_format=schema,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            **kwargs,
        )
        parsed = rsp.output_parsed
        if isinstance(parsed, BaseModel):
            return parsed.model_dump()
        if isinstance(parsed, dict):
            return parsed
        return {"value": parsed}

    @_enforce_openai_guardrails
    def response_stream(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        conversation_history: MessageList = None,
        top_k: int = 1,
        top_p: float = 1.0,
        temperature: float = 0.7,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        max_output_tokens: int = 1024,
        *args: Any,
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        with self.client.responses.stream(
            model=model,
            input=self._build_input(prompt, conversation_history),
            instructions=system_prompt or None,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            **kwargs,
        ) as stream:
            for event in stream:
                et = getattr(event, "type", None)
                if et in ("response.output_text.delta", "response.refusal.delta"):
                    yield getattr(event, "delta", "")
                elif et in ("response.error", "error"):
                    err = getattr(event, "error", None)
                    raise RuntimeError(str(err) if err is not None else "OpenAI streaming error")
