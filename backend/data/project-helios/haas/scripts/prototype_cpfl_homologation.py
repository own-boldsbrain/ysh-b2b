#!/usr/bin/env python3
"""
Protótipo de Cenário de Homologação CPFL
Demonstra o uso dos agentes Helios para automatizar o processo de homologação
junto à CPFL (Companhia Paulista de Força e Luz).
"""

import asyncio
import logging
from pathlib import Path

# Adicionar os diretórios ao PYTHONPATH
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))  # haas
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # root

from app.services.agent_integration_service import AgentIntegrationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def prototype_cpfl_homologation():
    """Executa protótipo de homologação CPFL usando agentes."""

    # Inicializar serviço de integração de agentes
    service = AgentIntegrationService()

    # Listar workflows suportados para CPFL
    workflows = await service.list_supported_workflows("CPFL")
    logger.info(f"Workflows suportados para CPFL: {workflows}")

    # Contexto de exemplo para homologação
    context = {
        "project_data": {
            "nome_projeto": "Sistema Fotovoltaico Residencial - São Paulo",
            "potencia_instalada": 5.0,  # kWp
            "tipo_conexao": "residencial",
            "endereco": {
                "logradouro": "Rua das Flores, 123",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01234-567"
            }
        },
        "empresa": {
            "cnpj": "12.345.678/0001-90",
            "nome": "Empresa Solar Ltda",
            "contato": {
                "nome": "João Silva",
                "email": "joao.silva@empresasolar.com.br",
                "telefone": "(11) 99999-9999"
            }
        },
        "documentos": [
            {
                "tipo": "projeto_tecnico",
                "arquivo": "projeto_tecnico.pdf",
                "status": "pronto"
            },
            {
                "tipo": "art",
                "arquivo": "art.pdf",
                "status": "pronto"
            },
            {
                "tipo": "certificado_inmetro",
                "arquivo": "certificado_inmetro.pdf",
                "status": "pronto"
            }
        ],
        "configuracao_agente": {
            "modo_execucao": "SIMULATED",  # ou "REAL" para execução real
            "timeout": 300,  # 5 minutos
            "max_tentativas": 3
        }
    }

    # Executar workflow de solicitação de acesso
    logger.info("Iniciando workflow de solicitação de acesso...")
    task_id = await service.run_workflow(
        utility_code="CPFL",
        workflow="solicitacao_acesso",
        payload={
            "context": context,
            "session_id": "prototype_cpfl_001"
        }
    )

    logger.info(f"Workflow iniciado com task_id: {task_id}")

    # Verificar status da tarefa
    status = await service.get_task_status(task_id)
    logger.info(f"Status da tarefa: {status}")

    # Simular verificação periódica do status
    for i in range(3):
        await asyncio.sleep(2)  # Simular delay
        status = await service.get_task_status(task_id)
        logger.info(f"Status atualizado ({i+1}): {status}")

    logger.info("Protótipo de homologação CPFL concluído!")


if __name__ == "__main__":
    asyncio.run(prototype_cpfl_homologation())