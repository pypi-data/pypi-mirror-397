# qbtrain/ai/llm/ollama_client.py
from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, Generator, List, Optional, Type

import ollama
from pydantic import BaseModel

from .base_llm_client import LLMClient, Message

MessageList = Optional[List[Message]]


def _ollama_guardrails(top_k: int) -> None:
    if top_k is not None and top_k < 1:
        raise ValueError("top_k must be >= 1 for Ollama.")


@dataclass
class PullTask:
    model: str
    status: str = "queued"  # queued | pulling | completed | failed
    progress: float = 0.0
    message: str = ""


class OllamaClient(LLMClient):
    client_id = "ollama"
    display_name = "Ollama (local)"
    param_display_names = {"host": "Server URL (http://127.0.0.1:11434)"}

    _LOCK = threading.RLock()
    _QUEUE: Deque[PullTask] = deque()
    _CURRENT: Optional[PullTask] = None
    _WORKER: Optional[threading.Thread] = None

    def __init__(self, host: str = "http://127.0.0.1:11434"):
        self.client = ollama.Client(host=host)

    # ---- Pull manager ----
    @classmethod
    def _ensure_worker(cls):
        with cls._LOCK:
            if cls._WORKER is None or not cls._WORKER.is_alive():
                cls._WORKER = threading.Thread(target=cls._worker_loop, daemon=True)
                cls._WORKER.start()

    @classmethod
    def _worker_loop(cls):
        while True:
            with cls._LOCK:
                if not cls._QUEUE:
                    cls._CURRENT = None
                    break
                task = cls._QUEUE.popleft()
                cls._CURRENT = task
                task.status = "pulling"

            try:
                for ev in ollama.pull(model=task.model, stream=True):
                    total = ev.get("total", 0) or 0
                    completed = ev.get("completed", 0) or 0
                    if total > 0:
                        prog = (completed / total) * 100.0
                        with cls._LOCK:
                            task.progress = prog
                    status = ev.get("status", "")
                    with cls._LOCK:
                        task.message = status
                with cls._LOCK:
                    task.progress = 100.0
                    task.status = "completed"
            except Exception as e:
                with cls._LOCK:
                    task.status = "failed"
                    task.message = str(e)
            finally:
                with cls._LOCK:
                    cls._CURRENT = None

    @classmethod
    def request_download(cls, model: str) -> None:
        with cls._LOCK:
            cls._QUEUE.append(PullTask(model=model))
        cls._ensure_worker()

    @classmethod
    def download_status(cls) -> Dict[str, Any]:
        with cls._LOCK:
            queue_list = [{"model": t.model, "status": t.status, "progress": round(t.progress, 2)} for t in cls._QUEUE]
            current = None
            if cls._CURRENT:
                current = {
                    "model": cls._CURRENT.model,
                    "status": cls._CURRENT.status,
                    "progress": round(cls._CURRENT.progress, 2),
                    "message": cls._CURRENT.message,
                }
            return {"current": current, "queue": queue_list}

    def list_models(self) -> List[str]:
        res = self.client.list()
        return [m["model"] for m in res.get("models", [])]

    def delete_model(self, model: str) -> None:
        self.client.delete(model=model)

    # ---- Inference ----
    def response(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        conversation_history: MessageList = None,
        top_k: int = 50,
        top_p: float = 1.0,
        temperature: float = 0.7,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        max_output_tokens: int = 256,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        _ollama_guardrails(top_k)
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if conversation_history:
            for m in conversation_history:
                role = "assistant" if m.get("role") == "assistant" else "user"
                messages.append({"role": role, "content": m.get("content", "")})
        messages.append({"role": "user", "content": prompt})

        r = self.client.chat(
            model=model,
            messages=messages,
            options={
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "presence_penalty": presence_penalty,
                "frequency_penalty": frequency_penalty,
                "num_predict": max_output_tokens,
            },
            stream=False,
        )
        return r.get("message", {}).get("content", "")

    def json_response(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        schema: Type[BaseModel],
        conversation_history: MessageList = None,
        top_k: int = 50,
        top_p: float = 1.0,
        temperature: float = 0.7,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        max_output_tokens: int = 256,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        txt = self.response(
            prompt=f"{prompt}\n\nReturn only a strict JSON object.",
            system_prompt=system_prompt,
            model=model,
            conversation_history=conversation_history,
            top_k=top_k,
            top_p=top_p,
            temperature=temperature,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            max_output_tokens=max_output_tokens,
        )
        obj = schema.model_validate_json(txt)
        return obj.model_dump()

    def response_stream(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        conversation_history: MessageList = None,
        top_k: int = 50,
        top_p: float = 1.0,
        temperature: float = 0.7,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        max_output_tokens: int = 256,
        *args: Any,
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        _ollama_guardrails(top_k)
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if conversation_history:
            for m in conversation_history:
                role = "assistant" if m.get("role") == "assistant" else "user"
                messages.append({"role": role, "content": m.get("content", "")})
        messages.append({"role": "user", "content": prompt})

        for chunk in self.client.chat(
            model=model,
            messages=messages,
            options={
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "presence_penalty": presence_penalty,
                "frequency_penalty": frequency_penalty,
                "num_predict": max_output_tokens,
            },
            stream=True,
        ):
            delta = chunk.get("message", {}).get("content", "") or ""
            if delta:
                yield delta
