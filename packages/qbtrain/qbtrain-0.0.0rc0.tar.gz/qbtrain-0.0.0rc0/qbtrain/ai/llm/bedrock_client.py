# qbtrain/ai/llm/bedrock_client.py
from __future__ import annotations

from functools import wraps
from typing import Any, Dict, Generator, List, Optional, Type

import boto3
from pydantic import BaseModel

from .base_llm_client import LLMClient, Message

MessageList = Optional[List[Message]]


def _bedrock_guardrails(fn):
    @wraps(fn)
    def wrapper(self: "BedrockClient", *args, **kwargs):
        if kwargs.get("top_k", 1) != 1:
            raise ValueError("Bedrock Converse does not support top_k != 1.")
        if kwargs.get("presence_penalty", 0.0) != 0.0:
            raise ValueError("Bedrock does not support presence_penalty.")
        if kwargs.get("frequency_penalty", 0.0) != 0.0:
            raise ValueError("Bedrock does not support frequency_penalty.")
        return fn(self, *args, **kwargs)
    return wrapper


class BedrockClient(LLMClient):
    client_id = "aws_bedrock"
    display_name = "AWS Bedrock"
    param_display_names = {"region_name": "AWS Region (e.g., us-east-1)"}

    def __init__(self, region_name: str, **session_kwargs: Any):
        self.client = boto3.client("bedrock-runtime", region_name=region_name, **session_kwargs)

    @staticmethod
    def _messages(prompt: str, system_prompt: str, conversation_history: MessageList) -> Dict[str, Any]:
        msgs: List[Dict[str, Any]] = []
        if conversation_history:
            for m in conversation_history:
                role = "assistant" if m.get("role") == "assistant" else "user"
                msgs.append({"role": role, "content": [{"text": m.get("content", "")}]})
        msgs.append({"role": "user", "content": [{"text": prompt}]})
        sys = [{"text": system_prompt}] if system_prompt else None
        return {"messages": msgs, "system": sys}

    @_bedrock_guardrails
    def response(
        self,
        prompt: str,
        system_prompt: str,
        model: str,  # modelId
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
        payload = self._messages(prompt, system_prompt, conversation_history)
        r = self.client.converse(
            modelId=model,
            messages=payload["messages"],
            system=payload["system"],
            inferenceConfig={"temperature": temperature, "topP": top_p, "maxTokens": max_output_tokens},
            **kwargs,
        )
        parts = r.get("output", {}).get("message", {}).get("content", [])
        if parts and "text" in parts[0]:
            return parts[0]["text"]
        return ""

    @_bedrock_guardrails
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
        hint = "Return only a strict JSON object."
        payload = self._messages(f"{prompt}\n\n{hint}", system_prompt, conversation_history)
        r = self.client.converse(
            modelId=model,
            messages=payload["messages"],
            system=payload["system"],
            inferenceConfig={"temperature": temperature, "topP": top_p, "maxTokens": max_output_tokens},
            **kwargs,
        )
        parts = r.get("output", {}).get("message", {}).get("content", [])
        txt = parts[0]["text"] if parts and "text" in parts[0] else "{}"
        obj = schema.model_validate_json(txt)
        return obj.model_dump()

    @_bedrock_guardrails
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
        payload = self._messages(prompt, system_prompt, conversation_history)
        stream = self.client.converse_stream(
            modelId=model,
            messages=payload["messages"],
            system=payload["system"],
            inferenceConfig={"temperature": temperature, "topP": top_p, "maxTokens": max_output_tokens},
            **kwargs,
        )
        for event in stream.get("stream", []):
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"]["delta"].get("text", "")
                if delta:
                    yield delta
            elif "messageStop" in event:
                break
