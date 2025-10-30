#!/usr/bin/env python3
"""
Script para testar o Celery worker do INMETRO.
"""

import sys
import os
import logging

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tasks.inmetro_tasks import health_check_task, validate_equipment_task
from app.services.inmetro_store import InmetroValidationStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_health_check():
    """Testa o health check do Celery."""
    logger.info("Testando health check do Celery...")

    try:
        result = health_check_task.delay()
        logger.info(f"Task ID: {result.id}")

        # Aguardar resultado (síncrono para teste)
        response = result.get(timeout=10)
        logger.info(f"Health check result: {response}")

        return True
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return False


def test_validate_equipment():
    """Testa validação de equipamento via Celery."""
    logger.info("Testando validação de equipamento via Celery...")

    try:
        # Dados de teste
        equipment_data = {
            "categoria": "inversores",
            "fabricante": "Fronius",
            "modelo": "Primo 8.2-1",
            "registry_id": None
        }

        # Criar request_id
        from uuid import uuid4
        request_id = f"test_{uuid4().hex[:8]}"

        # Agendar task
        result = validate_equipment_task.delay(
            request_id=request_id,
            equipment_data=equipment_data
        )

        logger.info(f"Task ID: {result.id}")

        # Aguardar resultado (síncrono para teste)
        response = result.get(timeout=30)
        logger.info(f"Validation result: {response}")

        # Verificar status no Redis
        status = InmetroValidationStore.get(request_id)
        if status:
            logger.info(f"Status final: {status.status} - Valid: {status.valid}")
        else:
            logger.warning("Status não encontrado no Redis")

        return True
    except Exception as e:
        logger.error(f"Erro na validação: {e}")
        return False


def main():
    """Função principal."""
    logger.info("Iniciando testes do Celery...")

    # Testar health check
    if not test_health_check():
        logger.error("Health check falhou!")
        return 1

    # Testar validação
    if not test_validate_equipment():
        logger.error("Validação falhou!")
        return 1

    logger.info("Todos os testes passaram!")
    return 0


if __name__ == "__main__":
    sys.exit(main())