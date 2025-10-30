"""Logging estruturado com handler para Loki.

Envia logs estruturados (JSON) para Loki via HTTP push API.
Contexto: fallback_layer, query, latency_ms, etc.

Configuração:
    LOKI_URL=http://loki:3100
"""

import json
import logging
import os
import socket
import time
from datetime import datetime
from logging import Handler, LogRecord

import requests


class LokiHandler(Handler):
    """Handler que envia logs estruturados ao Loki via HTTP."""

    def __init__(
        self,
        url: str | None = None,
        labels: dict[str, str] | None = None,
        timeout: int = 5,
    ):
        super().__init__()
        self.url = url or os.getenv("LOKI_URL", "http://loki:3100")
        self.push_url = f"{self.url}/loki/api/v1/push"
        self.timeout = timeout

        # Labels padrão
        self.labels = labels or {}
        self.labels.setdefault("job", "intelligent-fallback")
        self.labels.setdefault("host", socket.gethostname())

    def emit(self, record: LogRecord) -> None:
        """Envia log record para Loki."""
        try:
            # Extrai contexto estruturado
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }

            # Adiciona campos extras do record
            if hasattr(record, "fallback_layer"):
                log_entry["fallback_layer"] = record.fallback_layer
            if hasattr(record, "query"):
                log_entry["query"] = record.query
            if hasattr(record, "latency_ms"):
                log_entry["latency_ms"] = record.latency_ms
            if hasattr(record, "score"):
                log_entry["score"] = record.score

            # Timestamp em nanosegundos (Loki exige)
            ts_ns = str(int(time.time() * 1e9))

            # Payload Loki
            payload = {
                "streams": [
                    {"stream": self.labels, "values": [[ts_ns, json.dumps(log_entry)]]}
                ]
            }

            # Envia para Loki
            response = requests.post(
                self.push_url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code not in (200, 204):
                print(
                    f"⚠️  Loki push failed: {response.status_code} - " f"{response.text}"
                )

        except Exception as e:
            # Não quebra aplicação se Loki falhar
            print(f"⚠️  Erro ao enviar log para Loki: {e}")


def setup_structured_logging(
    app_name: str = "intelligent-fallback",
    loki_url: str | None = None,
    console_level: int = logging.INFO,
    loki_level: int = logging.WARNING,
) -> logging.Logger:
    """Configura logging estruturado com console + Loki.

    Args:
        app_name: Nome da aplicação
        loki_url: URL do Loki (default: LOKI_URL env var)
        console_level: Nível de log para console
        loki_level: Nível de log para Loki

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)

    # Remove handlers existentes
    logger.handlers.clear()

    # Console handler (formato legível)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Loki handler (JSON estruturado)
    try:
        loki_handler = LokiHandler(
            url=loki_url,
            labels={
                "job": app_name,
                "environment": os.getenv("ENV", "development"),
            },
        )
        loki_handler.setLevel(loki_level)
        logger.addHandler(loki_handler)
        logger.info(f"✅ Loki logging habilitado: {loki_handler.push_url}")
    except Exception as e:
        logger.warning(f"⚠️  Loki handler não disponível: {e}")

    return logger


# Logger padrão para módulo
_logger = setup_structured_logging()


def log_fallback_request(
    layer: str,
    query: str,
    latency_ms: float,
    score: float | None = None,
    status: str = "success",
) -> None:
    """Helper para logar requisições de fallback com contexto."""
    extra = {
        "fallback_layer": layer,
        "query": query,
        "latency_ms": latency_ms,
        "status": status,
    }
    if score is not None:
        extra["score"] = score

    if status == "success":
        _logger.info(
            f"{layer} fallback: {query[:50]} "
            f"(score={score:.3f if score else 'N/A'}, "
            f"{latency_ms:.0f}ms)",
            extra=extra,
        )
    else:
        _logger.warning(
            f"{layer} fallback failed: {query[:50]} ({status})",
            extra=extra,
        )


def log_circuit_breaker(layer: str, action: str, failure_count: int) -> None:
    """Helper para logar eventos de circuit breaker."""
    extra = {
        "fallback_layer": layer,
        "circuit_action": action,
        "failure_count": failure_count,
    }

    if action == "opened":
        _logger.error(
            f"Circuit breaker ABERTO para {layer} " f"após {failure_count} falhas",
            extra=extra,
        )
    elif action == "closed":
        _logger.info(
            f"Circuit breaker FECHADO para {layer}",
            extra=extra,
        )


if __name__ == "__main__":
    # Teste do handler
    logger = setup_structured_logging(
        loki_url="http://localhost:3100",
        console_level=logging.DEBUG,
        loki_level=logging.INFO,
    )

    logger.debug("Debug message (não vai para Loki)")
    logger.info("Info message (vai para Loki)")

    # Log com contexto estruturado
    log_fallback_request(
        layer="rag",
        query="Jinko Tiger Neo 585W",
        latency_ms=123.45,
        score=0.876,
        status="success",
    )

    log_fallback_request(
        layer="searx",
        query="Deye SUN-8K datasheet",
        latency_ms=567.89,
        status="not_found",
    )

    log_circuit_breaker(
        layer="ollama",
        action="opened",
        failure_count=5,
    )

    print("\n✅ Logs enviados para console e Loki")
    print("Verifique em Grafana -> Explore -> Loki")
