"""Orquestrador Inteligente de Fallbacks com Adaptive Thresholds.

Pipeline multinível:
1. RAG (TF-IDF) - Busca primária em knowledge base
2. SearxNG - Busca FOSS em múltiplos engines
3. Ollama - LLM local para inferência de URLs

Recursos:
- Adaptive threshold baseado em histórico
- Circuit breaker por camada
- Métricas agregadas e por camada
- Health checks e auto-recovery
- Logging estruturado
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from rag_finder import RAGFinder
    from searx_fallback import SearxFallback
    from ollama_fallback import OllamaFallback

# Configurar logging estruturado com Loki
try:
    from scripts.structured_logging import setup_structured_logging, log_circuit_breaker

    logger = setup_structured_logging("intelligent-fallback-orchestrator")
except ImportError:
    logger = logging.getLogger(__name__)
    log_circuit_breaker = None  # type: ignore
    logger.warning("structured_logging não disponível, usando logger padrão")


class FallbackLayer(Enum):
    """Camadas do pipeline de fallback."""

    RAG = "rag"
    SEARX = "searx"
    OLLAMA = "ollama"


class SearchResult(NamedTuple):
    """Resultado consolidado de busca."""

    url: str
    score: float
    layer: FallbackLayer
    metadata: dict[str, str | float] = {}


@dataclass
class LayerMetrics:
    """Métricas por camada."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    circuit_open: bool = False
    failure_count: int = 0

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def avg_latency_ms(self) -> float:
        """Latência média."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests


@dataclass
class AdaptiveConfig:
    """Configuração adaptativa baseada em performance."""

    rag_min_score: float = 0.3
    searx_min_score: float = 0.4
    ollama_enabled: bool = True

    # Limites dinâmicos
    rag_score_history: list[float] = field(default_factory=list)
    searx_score_history: list[float] = field(default_factory=list)

    max_history: int = 50

    def update_rag_threshold(self, score: float) -> None:
        """Atualiza threshold do RAG baseado em histórico."""
        self.rag_score_history.append(score)
        if len(self.rag_score_history) > self.max_history:
            self.rag_score_history.pop(0)

        # Calcula percentil 25 (conservador)
        if len(self.rag_score_history) >= 10:
            sorted_scores = sorted(self.rag_score_history)
            p25_idx = len(sorted_scores) // 4
            self.rag_min_score = max(0.2, sorted_scores[p25_idx])

    def update_searx_threshold(self, score: float) -> None:
        """Atualiza threshold do SearxNG."""
        self.searx_score_history.append(score)
        if len(self.searx_score_history) > self.max_history:
            self.searx_score_history.pop(0)

        if len(self.searx_score_history) >= 10:
            sorted_scores = sorted(self.searx_score_history)
            p25_idx = len(sorted_scores) // 4
            self.searx_min_score = max(0.3, sorted_scores[p25_idx])


class IntelligentFallbackOrchestrator:
    """Orquestrador inteligente com múltiplas camadas de fallback."""

    def __init__(
        self,
        kb_dir: str | Path,
        circuit_threshold: int = 5,
        enable_adaptive: bool = True,
    ):
        """Inicializa orquestrador.

        Args:
            kb_dir: Diretório com knowledge bases
            circuit_threshold: Falhas consecutivas para abrir circuit
            enable_adaptive: Ativa adaptive thresholds
        """
        from rag_finder import RAGFinder
        from searx_fallback import SearxFallback
        from ollama_fallback import OllamaFallback

        self.rag = RAGFinder(str(kb_dir))
        self.searx = SearxFallback()
        self.ollama = OllamaFallback()

        self.circuit_threshold = circuit_threshold
        self.enable_adaptive = enable_adaptive

        # Configuração adaptativa
        self.config = AdaptiveConfig()

        # Métricas por camada
        self.metrics: dict[FallbackLayer, LayerMetrics] = {
            FallbackLayer.RAG: LayerMetrics(),
            FallbackLayer.SEARX: LayerMetrics(),
            FallbackLayer.OLLAMA: LayerMetrics(),
        }

    def search(
        self,
        manufacturer: str,
        product_name: str,
        base_domain: str,
        queries: list[str] | None = None,
        product_context: str | None = None,
    ) -> SearchResult | None:
        """Busca inteligente com fallback multinível.

        Args:
            manufacturer: Nome do fabricante (para RAG)
            product_name: Nome do produto
            base_domain: Domínio base do fabricante
            queries: Múltiplas queries (para RAG)
            product_context: Contexto adicional (para Ollama)

        Returns:
            SearchResult ou None
        """
        logger.info(f"Iniciando busca para {manufacturer} / {product_name}")

        # Camada 1: RAG
        result = self._try_rag(manufacturer, queries or [product_name])
        if result:
            return result

        # Camada 2: SearxNG
        result = self._try_searx(product_name, base_domain)
        if result:
            return result

        # Camada 3: Ollama (LLM local)
        if self.config.ollama_enabled:
            result = self._try_ollama(base_domain, product_name, product_context)
            if result:
                return result

        logger.warning(f"Nenhuma camada retornou resultado para {product_name}")
        return None

    def _try_rag(self, manufacturer: str, queries: list[str]) -> SearchResult | None:
        """Tenta busca via RAG."""
        layer = FallbackLayer.RAG
        metrics = self.metrics[layer]

        if metrics.circuit_open:
            logger.warning(f"Circuit breaker aberto: {layer.value}")
            return None

        metrics.total_requests += 1
        start_time = time.time()

        try:
            result = self.rag.multi_query_search(manufacturer, queries, top_k=5)

            latency_ms = (time.time() - start_time) * 1000
            metrics.total_latency_ms += latency_ms

            if not result or not result.get("best_url"):
                self._handle_layer_failure(layer)
                return None

            score = result["score"]

            # Atualiza threshold adaptativo
            if self.enable_adaptive:
                self.config.update_rag_threshold(score)

            # Verifica threshold
            if score < self.config.rag_min_score:
                logger.info(
                    f"RAG score {score:.3f} < "
                    f"threshold {self.config.rag_min_score:.3f}"
                )
                self._handle_layer_failure(layer)
                return None

            # Sucesso
            self._handle_layer_success(layer)
            logger.info(
                f"RAG encontrou URL (score={score:.3f}, {latency_ms:.0f}ms)",
                extra={
                    "fallback_layer": "rag",
                    "query": ", ".join(queries[:2]),
                    "latency_ms": latency_ms,
                    "score": score,
                    "status": "success",
                },
            )

            return SearchResult(
                url=result["best_url"],
                score=score,
                layer=layer,
                metadata={
                    "queries_matched": result.get("queries_matched", 0),
                    "latency_ms": latency_ms,
                },
            )

        except Exception as exc:
            logger.error(f"Erro no RAG: {exc}")
            self._handle_layer_failure(layer)
            return None

    def _try_searx(self, product_name: str, base_domain: str) -> SearchResult | None:
        """Tenta busca via SearxNG."""
        layer = FallbackLayer.SEARX
        metrics = self.metrics[layer]

        if metrics.circuit_open:
            logger.warning(f"Circuit breaker aberto: {layer.value}")
            return None

        metrics.total_requests += 1
        start_time = time.time()

        try:
            site_clean = (
                base_domain.replace("https://", "").replace("http://", "").split("/")[0]
            )

            results = self.searx.search(
                query=product_name,
                site=site_clean,
                max_results=5,
            )

            latency_ms = (time.time() - start_time) * 1000
            metrics.total_latency_ms += latency_ms

            if not results:
                self._handle_layer_failure(layer)
                return None

            # Pega resultado com maior score
            best = results[0]

            # Atualiza threshold
            if self.enable_adaptive:
                self.config.update_searx_threshold(best.score)

            # Verifica threshold
            if best.score < self.config.searx_min_score:
                logger.info(
                    f"SearxNG score {best.score:.3f} < "
                    f"threshold {self.config.searx_min_score:.3f}"
                )
                self._handle_layer_failure(layer)
                return None

            # Sucesso
            self._handle_layer_success(layer)
            logger.info(
                f"SearxNG encontrou URL (score={best.score:.3f})",
                extra={
                    "fallback_layer": "searx",
                    "query": product_name,
                    "latency_ms": latency_ms,
                    "score": best.score,
                    "status": "success",
                },
            )

            return SearchResult(
                url=best.url,
                score=best.score,
                layer=layer,
                metadata={
                    "title": best.title,
                    "engine": best.engine,
                    "latency_ms": latency_ms,
                },
            )

        except Exception as exc:
            logger.error(f"Erro no SearxNG: {exc}")
            self._handle_layer_failure(layer)
            return None

    def _try_ollama(
        self,
        base_domain: str,
        product_name: str,
        context: str | None,
    ) -> SearchResult | None:
        """Tenta sugestão via Ollama."""
        layer = FallbackLayer.OLLAMA
        metrics = self.metrics[layer]

        if metrics.circuit_open:
            logger.warning(f"Circuit breaker aberto: {layer.value}")
            return None

        metrics.total_requests += 1
        start_time = time.time()

        try:
            url = self.ollama.suggest_url(base_domain, product_name, context)

            latency_ms = (time.time() - start_time) * 1000
            metrics.total_latency_ms += latency_ms

            if not url:
                self._handle_layer_failure(layer)
                return None

            # Sucesso (Ollama não tem score interno)
            self._handle_layer_success(layer)
            logger.info(
                f"Ollama sugeriu URL: {url}",
                extra={
                    "fallback_layer": "ollama",
                    "query": product_name,
                    "latency_ms": latency_ms,
                    "status": "success",
                },
            )

            return SearchResult(
                url=url,
                score=0.5,  # Score fixo (Ollama não ranqueia)
                layer=layer,
                metadata={"latency_ms": latency_ms},
            )

        except Exception as exc:
            logger.error(f"Erro no Ollama: {exc}")
            self._handle_layer_failure(layer)
            return None

    def _handle_layer_failure(self, layer: FallbackLayer) -> None:
        """Registra falha e atualiza circuit breaker."""
        metrics = self.metrics[layer]
        metrics.failed_requests += 1
        metrics.failure_count += 1

        if metrics.failure_count >= self.circuit_threshold:
            metrics.circuit_open = True
            if log_circuit_breaker:
                log_circuit_breaker(
                    layer=layer.value,
                    action="opened",
                    failure_count=metrics.failure_count,
                )
            else:
                logger.error(
                    "Circuit breaker aberto para %s após %d falhas",
                    layer.value,
                    metrics.failure_count,
                )

    def _handle_layer_success(self, layer: FallbackLayer) -> None:
        """Registra sucesso e reseta circuit breaker."""
        metrics = self.metrics[layer]
        metrics.successful_requests += 1
        metrics.failure_count = 0
        metrics.circuit_open = False

    def get_metrics(self) -> dict[str, dict[str, float | bool]]:
        """Retorna métricas agregadas."""
        return {
            layer.value: {
                "total_requests": metrics.total_requests,
                "success_rate": metrics.success_rate,
                "avg_latency_ms": metrics.avg_latency_ms,
                "circuit_open": metrics.circuit_open,
            }
            for layer, metrics in self.metrics.items()
        }

    def get_config(self) -> dict[str, float | bool]:
        """Retorna configuração adaptativa atual."""
        return {
            "rag_min_score": self.config.rag_min_score,
            "searx_min_score": self.config.searx_min_score,
            "ollama_enabled": self.config.ollama_enabled,
            "rag_samples": len(self.config.rag_score_history),
            "searx_samples": len(self.config.searx_score_history),
        }

    def reset_circuits(self) -> None:
        """Reseta todos os circuit breakers."""
        for metrics in self.metrics.values():
            metrics.circuit_open = False
            metrics.failure_count = 0
        logger.info("Todos circuit breakers resetados")

    def health_check(self) -> dict[str, bool]:
        """Verifica saúde de cada camada."""
        return {
            "rag": not self.metrics[FallbackLayer.RAG].circuit_open,
            "searx": not self.metrics[FallbackLayer.SEARX].circuit_open,
            "ollama": not self.metrics[FallbackLayer.OLLAMA].circuit_open,
        }
