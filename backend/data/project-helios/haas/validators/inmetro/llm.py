"""Interfaces e implementações para agentes LLM (Codex/OpenAI)."""

import json
import logging
from typing import Any, Dict, Optional, Protocol

logger = logging.getLogger(__name__)


class LLMExtractionError(RuntimeError):
    """Erro ao tentar obter resposta estruturada do LLM."""


class LLMInterface(Protocol):
    """Interface base para agentes LLM utilizados no pipeline."""

    def structured_extract(
        self, system_prompt: str, user_prompt: str
    ) -> Dict[str, Any]:
        """Recebe prompts e devolve um objeto JSON estruturado."""


class OpenAICodexAgent(LLMInterface):
    """Agente que utiliza a API OpenAI para produzir respostas JSON."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        temperature: float = 0.0,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - dependência opcional
            raise RuntimeError(
                "A biblioteca 'openai' é necessária para usar " "o OpenAICodexAgent"
            ) from exc

        kwargs: Dict[str, Any] = {}
        if api_key:
            kwargs["api_key"] = api_key
        if organization:
            kwargs["organization"] = organization

        self._client: Any = OpenAI(**kwargs)
        self._model: str = model
        self._temperature: float = temperature

    def structured_extract(
        self, system_prompt: str, user_prompt: str
    ) -> Dict[str, Any]:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                temperature=self._temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
        except Exception as exc:  # pragma: no cover - apenas logamos
            raise LLMExtractionError("Falha ao consultar a API OpenAI") from exc

        try:
            # Extrair conteúdo da resposta
            raw_text = response.choices[0].message.content
            if not raw_text:
                raise LLMExtractionError("Resposta vazia da OpenAI")
        except Exception as exc:  # pragma: no cover - defensivo
            raise LLMExtractionError(
                "Não foi possível interpretar a resposta do LLM"
            ) from exc

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as exc:
            logger.exception("Resposta inválida do LLM: %s", raw_text)
            raise LLMExtractionError("Resposta do LLM não é um JSON válido") from exc


class OllamaLLMAgent(LLMInterface):
    """Agente que utiliza Ollama local para produzir respostas JSON."""

    def __init__(
        self,
        model: str = "smollm2:latest",
        base_url: str = "http://localhost:11434",
        timeout: int = 30,
        temperature: float = 0.0,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._temperature = temperature
        logger.info(f"OllamaLLMAgent inicializado: modelo={model}, url={base_url}")

    def structured_extract(
        self, system_prompt: str, user_prompt: str
    ) -> Dict[str, Any]:
        """Extrai dados estruturados via Ollama API."""
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError(
                "A biblioteca 'requests' é necessária para OllamaLLMAgent"
            ) from exc

        # Combinar prompts
        full_prompt = f"{system_prompt}\n\n{user_prompt}\n\nRetorne APENAS um objeto JSON válido, sem explicações adicionais."

        payload = {
            "model": self._model,
            "prompt": full_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": self._temperature,
            },
        }

        try:
            logger.debug(f"Chamando Ollama API: {self._base_url}/api/generate")
            response = requests.post(
                f"{self._base_url}/api/generate",
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            logger.error(f"Erro ao chamar Ollama API: {exc}")
            raise LLMExtractionError(
                f"Falha ao consultar Ollama ({self._base_url}): {exc}"
            ) from exc

        try:
            result = response.json()
            raw_text = result.get("response", "")

            if not raw_text:
                raise LLMExtractionError("Resposta vazia do Ollama")

            logger.debug(f"Resposta Ollama (primeiros 200 chars): {raw_text[:200]}")

        except Exception as exc:
            raise LLMExtractionError(
                "Não foi possível interpretar a resposta do Ollama"
            ) from exc

        try:
            # Tentar parse direto
            return json.loads(raw_text)
        except json.JSONDecodeError:
            # Tentar extrair JSON de markdown code blocks
            import re

            json_match = re.search(r"```(?:json)?\s*({.*?})\s*```", raw_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Última tentativa: procurar objeto JSON no texto
            json_match = re.search(r"({.*})", raw_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            logger.exception("Resposta inválida do Ollama: %s", raw_text)
            raise LLMExtractionError(
                f"Resposta do Ollama não é um JSON válido: {raw_text[:200]}"
            )


class MockLLMAgent:
    """Implementação simples para testes unitários e execuções offline."""

    def __init__(self, payload: Optional[Dict[str, Any]] = None) -> None:
        self._payload = payload or {}

    def structured_extract(
        self, system_prompt: str, user_prompt: str
    ) -> Dict[str, Any]:
        if not self._payload:
            raise LLMExtractionError("Payload de teste não configurado")
        return self._payload
