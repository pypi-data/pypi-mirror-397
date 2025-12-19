# qbtrain/ai/llm/base.py
from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List, Optional, Type

from pydantic import BaseModel

Message = Dict[str, Any]


class LLMClient(ABC):
    """
    Minimal provider-agnostic interface matching your earlier signature.
    Each subclass MUST set `client_id` and SHOULD set `display_name` and `param_display_names`.
    """

    # ---- identity & metadata (override in subclasses) ----
    client_id: str = "base"
    display_name: str = "Base LLM"
    available_models: Optional[List[str]] = None
    # Map of __init__ parameter -> human-friendly label
    param_display_names: Dict[str, str] = {}

    # ---- properties with defaults/fallbacks ----
    @property
    def name(self) -> str:
        """Frontend display name."""
        return getattr(self, "display_name", self.__class__.__name__)

    @property
    def id(self) -> str:
        """Stable identifier used by the frontend/registry."""
        cid = getattr(self, "client_id", None)
        return cid or f"{self.__class__.__module__}.{self.__class__.__name__}"

    @property
    def params_display(self) -> Dict[str, str]:
        """
        Display labels for __init__ parameters.
        If subclass didn't provide, auto-generate from the __init__ signature.
        """
        labels = getattr(self, "param_display_names", None)
        if labels:
            return dict(labels)

        sig = inspect.signature(self.__init__)
        out: Dict[str, str] = {}
        for name, p in sig.parameters.items():
            if name == "self":
                continue
            # Title-case fallback (e.g., api_key -> API Key)
            label = name.replace("_", " ").title()
            out[name] = label
        return out

    # ---- core interface (match your original minimal set) ----
    @abstractmethod
    def response(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        conversation_history: Optional[List[Message]] = None,
        top_k: int = 1,
        top_p: float = 1.0,
        temperature: float = 0.7,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        max_output_tokens: int = 1024,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def json_response(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        schema: Type[BaseModel],
        conversation_history: Optional[List[Message]] = None,
        top_k: int = 1,
        top_p: float = 1.0,
        temperature: float = 0.7,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        max_output_tokens: int = 1024,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def response_stream(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        conversation_history: Optional[List[Message]] = None,
        top_k: int = 1,
        top_p: float = 1.0,
        temperature: float = 0.7,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        max_output_tokens: int = 1024,
        *args: Any,
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        raise NotImplementedError
