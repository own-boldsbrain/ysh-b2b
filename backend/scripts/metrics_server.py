"""Metrics HTTP Server para Prometheus.

Expõe métricas do sistema de fallbacks inteligente:
- Requisições por camada
- Taxa de sucesso
- Latência média
- Cache hit rate
- Status de circuit breakers

Endpoint: http://localhost:9090/metrics
"""

import logging
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from typing import Optional

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Coletor de métricas do sistema de fallbacks."""

    def __init__(self, kb_dir: str = "../output/knowledge_bases"):
        self._orchestrator = None
        self._kb_dir = kb_dir
        self._last_update = time.time()

    def _get_orchestrator(self):
        """Lazy load orchestrator."""
        if self._orchestrator is None:
            try:
                from intelligent_fallback_orchestrator import (
                    IntelligentFallbackOrchestrator,
                )

                self._orchestrator = IntelligentFallbackOrchestrator(
                    kb_dir=self._kb_dir,
                    circuit_threshold=5,
                    enable_adaptive=True,
                )
            except ImportError:
                logger.warning("Orchestrator não disponível")
        return self._orchestrator

    def collect_metrics(self) -> str:
        """Coleta métricas e retorna em formato Prometheus."""
        orchestrator = self._get_orchestrator()
        if not orchestrator:
            return "# Orchestrator unavailable\n"

        metrics = orchestrator.get_metrics()
        config = orchestrator.get_config()
        health = orchestrator.health_check()

        lines = [
            "# HELP fallback_requests_total Total de requisições por camada",
            "# TYPE fallback_requests_total counter",
        ]

        for layer, m in metrics.items():
            lines.append(
                f'fallback_requests_total{{layer="{layer}"}} ' f'{m["total_requests"]}'
            )

        lines.extend(
            [
                "",
                "# HELP fallback_success_rate Taxa de sucesso por camada (0-1)",
                "# TYPE fallback_success_rate gauge",
            ]
        )

        for layer, m in metrics.items():
            lines.append(
                f'fallback_success_rate{{layer="{layer}"}} ' f'{m["success_rate"]:.4f}'
            )

        lines.extend(
            [
                "",
                "# HELP fallback_latency_ms Latência média em ms",
                "# TYPE fallback_latency_ms gauge",
            ]
        )

        for layer, m in metrics.items():
            lines.append(
                f'fallback_latency_ms{{layer="{layer}"}} ' f'{m["avg_latency_ms"]:.2f}'
            )

        lines.extend(
            [
                "",
                "# HELP fallback_circuit_open Circuit breaker status (1=open)",
                "# TYPE fallback_circuit_open gauge",
            ]
        )

        for layer, m in metrics.items():
            lines.append(
                f'fallback_circuit_open{{layer="{layer}"}} '
                f'{1 if m["circuit_open"] else 0}'
            )

        lines.extend(
            [
                "",
                "# HELP fallback_health Saúde da camada (1=healthy, 0=unhealthy)",
                "# TYPE fallback_health gauge",
            ]
        )

        for layer, healthy in health.items():
            lines.append(
                f'fallback_health{{layer="{layer}"}} ' f"{1 if healthy else 0}"
            )

        lines.extend(
            [
                "",
                "# HELP fallback_threshold_adaptive Threshold adaptativo atual",
                "# TYPE fallback_threshold_adaptive gauge",
                f'fallback_threshold_adaptive{{layer="rag"}} '
                f'{config["rag_min_score"]:.4f}',
                f'fallback_threshold_adaptive{{layer="searx"}} '
                f'{config["searx_min_score"]:.4f}',
            ]
        )

        lines.extend(
            [
                "",
                "# HELP fallback_adaptive_samples Número de samples no histórico",
                "# TYPE fallback_adaptive_samples gauge",
                f'fallback_adaptive_samples{{layer="rag"}} ' f'{config["rag_samples"]}',
                f'fallback_adaptive_samples{{layer="searx"}} '
                f'{config["searx_samples"]}',
            ]
        )

        return "\n".join(lines) + "\n"


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler para endpoint /metrics."""

    collector: Optional[MetricsCollector] = None

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()

            if self.collector:
                metrics = self.collector.collect_metrics()
                self.wfile.write(metrics.encode())
            else:
                self.wfile.write(b"# Collector not initialized\n")

        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "healthy"}')

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suprime logs padrão do HTTP server."""
        pass


class MetricsServer:
    """Servidor HTTP de métricas para Prometheus."""

    def __init__(
        self,
        port: int = 9090,
        kb_dir: str = "../output/knowledge_bases",
    ):
        self.port = port
        self.collector = MetricsCollector(kb_dir=kb_dir)
        self.server: Optional[HTTPServer] = None
        self._thread: Optional[Thread] = None

    def start(self):
        """Inicia servidor em thread separada."""
        MetricsHandler.collector = self.collector

        self.server = HTTPServer(("0.0.0.0", self.port), MetricsHandler)

        self._thread = Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()

        logger.info(f"📊 Metrics server rodando em http://0.0.0.0:{self.port}/metrics")

    def stop(self):
        """Para servidor."""
        if self.server:
            self.server.shutdown()
            logger.info("Metrics server parado")


if __name__ == "__main__":
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9090

    server = MetricsServer(port=port)
    server.start()

    print(f"\n✅ Metrics endpoint disponível:")
    print(f"   http://localhost:{port}/metrics")
    print(f"   http://localhost:{port}/health")
    print("\nPressione Ctrl+C para parar\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nParando servidor...")
        server.stop()
