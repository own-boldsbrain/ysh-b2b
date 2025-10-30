"""
Gerenciador de Agentes de IA

Este módulo decide qual modelo de IA usar com base na disponibilidade da API e na configuração.
Ele alterna entre as APIs da OpenAI/Gemini e os modelos locais do Docker.
"""

import os
import docker
import openai
import google.generativeai as genai

# Carrega as configurações do config.py
from config import (
    GEMINI_API_KEYS,
    OPENAI_API_KEY,
    DOCKER_MODELS,
    MAX_RETRIES,
    BACKOFF_FACTOR,
)


class AgentManager:
    def __init__(self):
        self.gemini_key_index = 0
        self.openai_key_index = 0  # Placeholder for multiple keys if needed
        self.docker_client = None
        self._configure_apis()

    def _configure_apis(self):
        """Configura os clientes das APIs."""
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY

        if GEMINI_API_KEYS:
            genai.configure(api_key=GEMINI_API_KEYS[self.gemini_key_index])

    def _connect_docker(self):
        """Inicia a conexão com o Docker se ainda não estiver conectada."""
        if not self.docker_client:
            try:
                self.docker_client = docker.from_env()
                print("✅ Conectado ao Docker com sucesso.")
            except docker.errors.DockerException as e:
                print(f"❌ Erro ao conectar ao Docker: {e}")
                print("⚠️  Modelos locais não estarão disponíveis.")
                self.docker_client = None

    def get_agent(self, preference="gemini"):
        """
        Obtém o próximo agente disponível, começando com as APIs externas.
        Se as APIs falharem ou os limites forem atingidos, tenta usar os modelos do Docker.
        """
        # Tenta primeiro as APIs externas
        if preference == "gemini" and self._is_gemini_available():
            print("🤖 Usando agente: Gemini Pro")
            return self._get_gemini_agent()

        if self._is_openai_available():
            print("🤖 Usando agente: OpenAI GPT-4")
            return self._get_openai_agent()

        # Fallback para modelos Docker
        print(
            "⚠️ APIs externas indisponíveis ou limites atingidos. Tentando modelos Docker..."
        )
        self._connect_docker()
        if self.docker_client:
            for model_name in DOCKER_MODELS:
                if self._is_docker_model_running(model_name):
                    print(f"🐳 Usando modelo Docker: {model_name}")
                    return self._get_docker_agent(model_name)

        print("❌ Nenhum agente de IA disponível.")
        return None

    def _is_gemini_available(self):
        # Lógica para verificar se a API do Gemini está respondendo
        # (Pode ser um simples ping ou uma verificação de status)
        return self.gemini_key_index < len(GEMINI_API_KEYS)

    def _is_openai_available(self):
        # Lógica para verificar a API da OpenAI
        return bool(OPENAI_API_KEY)

    def _is_docker_model_running(self, model_name):
        """Verifica se um container com o nome do modelo está em execução."""
        try:
            containers = self.docker_client.containers.list(
                filters={"name": model_name}
            )
            return len(containers) > 0
        except Exception as e:
            print(f"❌ Erro ao verificar container Docker '{model_name}': {e}")
            return False

    def _get_gemini_agent(self):
        # Retorna uma função ou classe que interage com o Gemini
        # A implementação real da consulta seria feita em 'image_scraper.py'
        return "gemini"

    def _get_openai_agent(self):
        # Retorna uma função ou classe que interage com a OpenAI
        return "openai"

    def _get_docker_agent(self, model_name):
        # Retorna uma função ou classe para interagir com o modelo Docker
        return f"docker:{model_name}"

    def report_api_failure(self, agent_type):
        """Chamado quando uma API atinge seu limite para tentar a próxima chave ou fazer fallback."""
        if agent_type == "gemini":
            self.gemini_key_index += 1
            if self.gemini_key_index < len(GEMINI_API_KEYS):
                print(
                    f"🔄 Trocando para a próxima chave Gemini (índice {self.gemini_key_index})."
                )
                genai.configure(api_key=GEMINI_API_KEYS[self.gemini_key_index])
            else:
                print("🚫 Todas as chaves Gemini foram esgotadas.")


# Exemplo de uso
if __name__ == "__main__":
    manager = AgentManager()

    # Simula o uso
    agent = manager.get_agent()
    print(f"Agente selecionado: {agent}")

    # Simula falha da Gemini
    manager.report_api_failure("gemini")
    agent = manager.get_agent(preference="openai")  # Tenta OpenAI
    print(f"Agente selecionado: {agent}")

    # Simula falha da segunda chave Gemini
    manager.report_api_failure("gemini")
    agent = manager.get_agent()
    print(f"Agente selecionado: {agent}")
