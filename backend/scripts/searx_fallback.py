"""SearxNG Fallback - Busca FOSS para URLs de produtos.

Recursos avançados:
- Scoring de relevância baseado em posição e título
- Filtros por categoria, data e tipo de conteúdo
- Cache de resultados com TTL
- Fallback multi-engine (DuckDuckGo, Brave, Google)
- Métricas de performance
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from datetime import datetime
from typing import NamedTuple

import requests

# Configurar logging estruturado com Loki
try:
    from scripts.structured_logging import setup_structured_logging

    logger = setup_structured_logging("searx-fallback")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("structured_logging não disponível, usando logger padrão")

DEFAULT_SEARX_URL = "http://searxng:8080"
DEFAULT_CACHE_TTL = int(os.getenv("SEARX_CACHE_TTL", "1800"))


class SearchResult(NamedTuple):
    """Resultado de busca estruturado."""

    url: str
    title: str
    score: float
    engine: str
    category: str = "general"


class SearxFallback:
    """Cliente avançado para consultas ao SearxNG.

    Features:
    - Scoring de relevância (posição, título match)
    - Cache de resultados
    - Filtros avançados
    - Fallback entre múltiplos engines
    - Métricas
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int = 15,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        enable_cache: bool = True,
    ):
        self.base_url = base_url or os.getenv("SEARXNG_URL", DEFAULT_SEARX_URL)
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.enable_cache = enable_cache

        # Cache: {hash: (results, timestamp)}
        self._cache: dict[str, tuple[list[SearchResult], datetime]] = {}

        # Métricas
        self._metrics: dict[str, int | float] = {
            "total_requests": 0,
            "cache_hits": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_latency_ms": 0.0,
        }

    def _get_cache_key(
        self, query: str, site: str | None, filters: dict[str, str]
    ) -> str:
        """Gera hash para cache."""
        content = f"{query}|{site or ''}|{filters}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _get_from_cache(self, cache_key: str) -> list[SearchResult] | None:
        """Recupera resultados do cache se válidos."""
        if not self.enable_cache or cache_key not in self._cache:
            return None

        results, timestamp = self._cache[cache_key]
        age = (datetime.now() - timestamp).total_seconds()

        if age > self.cache_ttl:
            del self._cache[cache_key]
            return None

        self._metrics["cache_hits"] += 1
        logger.debug(f"Cache hit: {cache_key[:8]}...")
        return results

    def _set_cache(self, cache_key: str, results: list[SearchResult]) -> None:
        """Armazena resultados no cache."""
        if self.enable_cache:
            self._cache[cache_key] = (results, datetime.now())

    def _calculate_score(
        self,
        position: int,
        title: str,
        query: str,
        total_results: int,
    ) -> float:
        """Calcula score de relevância.

        Fatores:
        - Posição no ranking (peso maior)
        - Match de palavras do query no título
        - Normalizado 0-1
        """
        # Score de posição (decai exponencialmente)
        position_score = 1.0 / (position + 1)

        # Score de título (% de palavras que matcham)
        query_terms = set(query.lower().split())
        title_terms = set(title.lower().split())
        if query_terms:
            title_score = len(query_terms & title_terms) / len(query_terms)
        else:
            title_score = 0.0

        # Combinação ponderada (70% posição, 30% título)
        combined_score = 0.7 * position_score + 0.3 * title_score

        return min(combined_score, 1.0)

    def search(
        self,
        query: str,
        site: str | None = None,
        language: str = "pt",
        max_results: int = 10,
        engines: list[str] | None = None,
        category: str = "general",
        time_range: str | None = None,
    ) -> list[SearchResult]:
        """Executa uma busca no SearxNG e retorna URLs ranqueadas.

        Args:
            query: Termo de busca
            site: Limitar a domínio específico
            language: Idioma da busca
            max_results: Número máximo de resultados
            engines: Lista de engines (None = todos)
            category: Categoria (general, files, images, etc)
            time_range: Filtro temporal (day, week, month, year)

        Returns:
            Lista de SearchResult ordenada por score
        """
        self._metrics["total_requests"] += 1
        start_time = time.time()

        filters = {
            "language": language,
            "category": category,
        }
        if time_range:
            filters["time_range"] = time_range

        # Verifica cache
        cache_key = self._get_cache_key(query, site, filters)
        cached_results = self._get_from_cache(cache_key)
        if cached_results:
            return cached_results[:max_results]

        # Constrói query final
        if site:
            query = f"site:{site} {query}"

        params: dict[str, str | int] = {
            "q": query,
            "format": "json",
            "language": language,
            "safesearch": "1",
            "categories": category,
        }

        if engines:
            params["engines"] = ",".join(engines)
        else:
            params["engines"] = "duckduckgo,brave,google"

        if time_range:
            params["time_range"] = time_range

        try:
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error(f"Erro ao consultar SearxNG: {exc}")
            self._metrics["failed_calls"] += 1
            return []

        # Parseia resultados
        data = response.json()
        raw_results = data.get("results", [])

        # Cria SearchResults com scores
        results: list[SearchResult] = []
        for i, item in enumerate(raw_results):
            if not item.get("url"):
                continue

            score = self._calculate_score(
                position=i,
                title=item.get("title", ""),
                query=query,
                total_results=len(raw_results),
            )

            results.append(
                SearchResult(
                    url=item["url"],
                    title=item.get("title", ""),
                    score=score,
                    engine=item.get("engine", "unknown"),
                    category=item.get("category", "general"),
                )
            )

        # Ordena por score
        results.sort(key=lambda x: x.score, reverse=True)

        # Atualiza métricas
        latency_ms = (time.time() - start_time) * 1000
        self._metrics["total_latency_ms"] += latency_ms
        self._metrics["successful_calls"] += 1

        # Cacheia
        self._set_cache(cache_key, results)

        # Log estruturado para Loki
        avg_score = sum(r.score for r in results) / len(results) if results else 0
        logger.info(
            f"SearxNG: {len(results)} resultados (avg score={avg_score:.3f})",
            extra={
                "fallback_layer": "searx",
                "query": query,
                "latency_ms": latency_ms,
                "score": avg_score,
                "status": "success" if results else "no_results",
            },
        )

        return results[:max_results]

    def search_urls_only(
        self,
        query: str,
        site: str | None = None,
        language: str = "pt",
        max_results: int = 5,
    ) -> list[str]:
        """Versão simplificada retornando apenas URLs."""
        results = self.search(
            query=query,
            site=site,
            language=language,
            max_results=max_results,
        )
        return [r.url for r in results]

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
        }

    def clear_cache(self) -> None:
        """Limpa cache."""
        self._cache.clear()
        logger.info("Cache SearxNG limpo")
