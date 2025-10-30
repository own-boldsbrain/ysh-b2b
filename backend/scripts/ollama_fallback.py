"""Fallback para sugerir URLs usando modelos locais via Ollama.

Recursos avançados:
- Cache de respostas para evitar chamadas duplicadas
- Retry exponencial com backoff configurável
- Validação de URLs sugeridas
- Métricas de performance (latência, taxa de sucesso)
- Circuit breaker para falhas consecutivas
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Union
from urllib.parse import urlparse

import requests

# Configurar logging estruturado com Loki
try:
    from scripts.structured_logging import setup_structured_logging

    logger = setup_structured_logging("ollama-fallback")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("structured_logging não disponível, usando logger padrão")

DEFAULT_OLLAMA_URL = "http://ollama:11434"
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
DEFAULT_CACHE_TTL = int(os.getenv("OLLAMA_CACHE_TTL", "3600"))
DEFAULT_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
DEFAULT_CIRCUIT_THRESHOLD = int(os.getenv("OLLAMA_CIRCUIT_THRESHOLD", "5"))

JsonPrimitive = Union[str, int, float, bool, None]
JsonType = Union[JsonPrimitive, "JsonDict", "JsonList"]
JsonDict = dict[str, JsonType]
JsonList = list[JsonType]


class OllamaFallback:
    """Wrapper avançado para consultar a API do Ollama.

    Features:
    - Cache com TTL configurável
    - Retry com backoff exponencial
    - Validação de URLs
    - Circuit breaker
    - Métricas de performance
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str = DEFAULT_MODEL,
        timeout: int = 30,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        max_retries: int = DEFAULT_MAX_RETRIES,
        enable_cache: bool = True,
    ) -> None:
        host_override = os.getenv("OLLAMA_HOST")
        resolved_base = base_url or host_override or DEFAULT_OLLAMA_URL
        self.base_url: str = resolved_base
        self.model: str = model
        self.timeout: int = timeout
        self.cache_ttl: int = cache_ttl
        self.max_retries: int = max_retries
        self.enable_cache: bool = enable_cache

        # Cache: {hash: (url, timestamp)}
        self._cache: dict[str, tuple[str, datetime]] = {}

        # Circuit breaker
        self._failure_count: int = 0
        self._circuit_open: bool = False
        self._circuit_threshold: int = DEFAULT_CIRCUIT_THRESHOLD

        # Métricas
        self._metrics: dict[str, int | float] = {
            "total_requests": 0,
            "cache_hits": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_latency_ms": 0.0,
        }

    def _get_cache_key(
        self, base_domain: str, product_name: str, context: str | None
    ) -> str:
        """Gera hash para cache."""
        content = f"{base_domain}|{product_name}|{context or ''}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _get_from_cache(self, cache_key: str) -> str | None:
        """Recupera URL do cache se válida."""
        if not self.enable_cache or cache_key not in self._cache:
            return None

        url, timestamp = self._cache[cache_key]
        age = datetime.now() - timestamp

        if age.total_seconds() > self.cache_ttl:
            del self._cache[cache_key]
            return None

        self._metrics["cache_hits"] += 1
        logger.debug(f"Cache hit: {cache_key[:8]}...")
        return url

    def _set_cache(self, cache_key: str, url: str) -> None:
        """Armazena URL no cache."""
        if self.enable_cache:
            self._cache[cache_key] = (url, datetime.now())

    def _validate_url(self, url: str, base_domain: str) -> bool:
        """Valida se URL é bem formada e pertence ao domínio."""
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return False

            domain_clean = (
                base_domain.replace("https://", "").replace("http://", "").split("/")[0]
            )
            return domain_clean in parsed.netloc
        except Exception:
            return False

    def _call_ollama_with_retry(self, payload: dict[str, JsonType]) -> JsonType | None:
        """Chama API com retry exponencial."""
        for attempt in range(self.max_retries):
            try:
                wait_time = 2**attempt
                if attempt > 0:
                    logger.debug(
                        f"Retry {attempt}/{self.max_retries} " f"após {wait_time}s"
                    )
                    time.sleep(wait_time)

                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                parsed: JsonType = json.loads(response.text)
                return parsed

            except requests.RequestException as exc:
                if attempt == self.max_retries - 1:
                    logger.error(
                        f"Ollama falhou após {self.max_retries} " f"tentativas: {exc}"
                    )
                    return None
            except json.JSONDecodeError:
                logger.error("Resposta Ollama não é JSON válido")
                return None

        return None

    def suggest_url(
        self,
        base_domain: str,
        product_name: str,
        product_context: str | None = None,
    ) -> str | None:
        """Usa o modelo local para inferir uma URL provável.

        Args:
            base_domain: Domínio do fabricante
            product_name: Nome do produto
            product_context: Contexto adicional

        Returns:
            URL sugerida ou None
        """
        self._metrics["total_requests"] += 1
        start_time = time.time()

        # Circuit breaker
        if self._circuit_open:
            logger.warning("Circuit breaker aberto, pulando chamada Ollama")
            self._metrics["failed_calls"] += 1
            return None

        # Verifica cache
        cache_key = self._get_cache_key(base_domain, product_name, product_context)
        cached_url = self._get_from_cache(cache_key)
        if cached_url:
            return cached_url

        # Constrói prompt
        prompt_parts = [
            "Você é um especialista em catálogos solares.",
            " Dado o domínio da fabricante e as informações do produto,",
            " gere APENAS uma URL completa onde o produto " "provavelmente está",
            " listado no site oficial.",
            "\n\nDomínio base:",
            f" {base_domain}",
            "\nProduto:",
            f" {product_name}",
        ]

        if product_context:
            prompt_parts.append(f"\nContexto extra: {product_context}")

        prompt_parts.append("\n\nRegras:")
        prompt_parts.append("\n- Responda SOMENTE com uma URL completa (https://...).")
        prompt_parts.append("\n- Se não souber, responda com a palavra 'NONE'.")

        payload = {
            "model": self.model,
            "prompt": "".join(prompt_parts),
            "stream": False,
            "options": {"temperature": 0.2},
        }

        # Chama Ollama com retry
        parsed = self._call_ollama_with_retry(payload)

        # Atualiza latência
        latency_ms = (time.time() - start_time) * 1000
        self._metrics["total_latency_ms"] += latency_ms

        if not parsed or not isinstance(parsed, dict):
            self._handle_failure()
            logger.warning(
                "Ollama fallback failed",
                extra={
                    "fallback_layer": "ollama",
                    "query": product_name,
                    "latency_ms": latency_ms,
                    "status": "invalid_response",
                },
            )
            return None

        response_field = parsed.get("response")
        if not isinstance(response_field, str):
            self._handle_failure()
            return None

        suggestion = response_field.strip()

        # Valida resposta
        if suggestion.upper() == "NONE" or not suggestion.startswith("http"):
            self._handle_failure()
            return None

        # Valida URL
        if not self._validate_url(suggestion, base_domain):
            logger.warning(f"URL sugerida inválida: {suggestion}")
            self._handle_failure()
            return None

        # Sucesso
        self._handle_success()
        logger.info(
            f"Ollama URL suggestion: {suggestion}",
            extra={
                "fallback_layer": "ollama",
                "query": product_name,
                "latency_ms": latency_ms,
                "status": "success",
            },
        )
        self._set_cache(cache_key, suggestion)
        logger.debug(f"Ollama sugeriu URL em {latency_ms:.0f}ms: {suggestion}")

        return suggestion

    def _handle_failure(self) -> None:
        """Registra falha e atualiza circuit breaker."""
        self._metrics["failed_calls"] += 1
        self._failure_count += 1

        if self._failure_count >= self._circuit_threshold:
            self._circuit_open = True
            logger.error(
                f"Circuit breaker aberto após " f"{self._failure_count} falhas"
            )

    def _handle_success(self) -> None:
        """Registra sucesso e reseta circuit breaker."""
        self._metrics["successful_calls"] += 1
        self._failure_count = 0
        self._circuit_open = False

    def get_metrics(self) -> dict[str, int | float]:
        """Retorna métricas de performance."""
        total = self._metrics["total_requests"]
        if total == 0:
            return self._metrics

        return {
            **self._metrics,
            "cache_hit_rate": self._metrics["cache_hits"] / total,
            "success_rate": (self._metrics["successful_calls"] / total),
            "avg_latency_ms": (self._metrics["total_latency_ms"] / total),
            "circuit_open": self._circuit_open,
        }

    def reset_circuit(self) -> None:
        """Reseta circuit breaker manualmente."""
        self._circuit_open = False
        self._failure_count = 0
        logger.info("Circuit breaker resetado manualmente")

    def clear_cache(self) -> None:
        """Limpa cache."""
        self._cache.clear()
        logger.info("Cache limpo")
