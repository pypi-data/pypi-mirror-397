# qbtrain/ai/llm/azure_foundry_client.py
from __future__ import annotations

from functools import wraps
from typing import Any, Dict, Generator, List, Optional, Type

from openai import AzureOpenAI
from pydantic import BaseModel

from .base_llm_client import LLMClient, Message

MessageList = Optional[List[Message]]


def _azure_guardrails(fn):
    @wraps(fn)
    def wrapper(self: "AzureFoundryClient", *args, **kwargs):
        if kwargs.get("top_k", 1) != 1:
            raise ValueError("Azure chat completions do not support top_k != 1.")
        return fn(self, *args, **kwargs)
    return wrapper


class AzureFoundryClient(LLMClient):
    client_id = "azure_foundry"
    display_name = "Azure OpenAI (Foundry)"
    # Include a 'default_deployment' convenience for forms (optional).
    param_display_names = {
        "api_key": "Secret (API Key)",
        "endpoint": "Endpoint URL",
        "api_version": "API Version",
        "default_deployment": "Default Deployment (optional)",
    }

    def __init__(self, api_key: str, endpoint: str, api_version: str, default_deployment: Optional[str] = None):
        self.client = AzureOpenAI(api_key=api_key, azure_endpoint=endpoint, api_version=api_version)
        self.default_deployment = default_deployment

    @staticmethod
    def _build_messages(
        prompt: str,
        system_prompt: str,
        conversation_history: MessageList,
    ) -> List[Dict[str, str]]:
        msgs: List[Dict[str, str]] = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        if conversation_history:
            for m in conversation_history:
                role = m.get("role", "user")
                content = m.get("content", "")
                role = "assistant" if role == "assistant" else "user"
                msgs.append({"role": role, "content": content})
        msgs.append({"role": "user", "content": prompt})
        return msgs

    @_azure_guardrails
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
        deployment = model or self.default_deployment or ""
        if not deployment:
            raise ValueError("AzureFoundryClient requires a deployment name as `model` or `default_deployment`.")
        r = self.client.chat.completions.create(
            model=deployment,
            messages=self._build_messages(prompt, system_prompt, conversation_history),
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            max_tokens=max_output_tokens,
            **kwargs,
        )
        return (r.choices[0].message.content or "").strip()

    @_azure_guardrails
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
        deployment = model or self.default_deployment or ""
        if not deployment:
            raise ValueError("AzureFoundryClient requires a deployment name as `model` or `default_deployment`.")
        r = self.client.chat.completions.create(
            model=deployment,
            messages=self._build_messages(prompt, system_prompt, conversation_history),
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            max_tokens=max_output_tokens,
            response_format={"type": "json_object"},
            **kwargs,
        )
        txt = (r.choices[0].message.content or "").strip()
        obj = schema.model_validate_json(txt)
        return obj.model_dump()

    @_azure_guardrails
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
        deployment = model or self.default_deployment or ""
        if not deployment:
            raise ValueError("AzureFoundryClient requires a deployment name as `model` or `default_deployment`.")
        stream = self.client.chat.completions.create(
            model=deployment,
            messages=self._build_messages(prompt, system_prompt, conversation_history),
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            max_tokens=max_output_tokens,
            stream=True,
            **kwargs,
        )
        for chunk in stream:
            delta = ""
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta
