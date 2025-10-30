"""Dependency Injection para Pipeline INMETRO usando FastAPI DI."""

import json
from functools import lru_cache
import logging
from pathlib import Path
import sys
from typing import AsyncGenerator, Generator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Adicionar validators ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from validators.inmetro.crawler import InmetroCrawler
from validators.inmetro.llm import MockLLMAgent, LLMInterface
from validators.inmetro.pipeline import InmetroExtractor, InmetroPipeline
from validators.inmetro.database_repository import DatabaseInmetroRepository
from validators.inmetro.validator import RecordValidator
from validators.inmetro.schema_loader import load_datasheet_schema

from app.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)


# Dependency para LLM Interface
@lru_cache(maxsize=1)
def get_llm_interface() -> LLMInterface:
    """Dependency para interface LLM baseada na configuração."""
    # Prioridade: Anthropic > OpenAI > Ollama > Mock
    priority = settings.LLM_PROVIDER_PRIORITY

    for provider in priority:
        try:
            if (
                provider == "anthropic"
                and settings.ANTHROPIC_ENABLED
                and settings.ANTHROPIC_API_KEY
            ):
                logger.info(f"Usando Anthropic: {settings.ANTHROPIC_MODEL}")
                return _create_anthropic_llm()

            elif (
                provider == "openai"
                and settings.OPENAI_ENABLED
                and settings.OPENAI_API_KEY
            ):
                logger.info(f"Usando OpenAI: {settings.OPENAI_MODEL}")
                return _create_openai_llm()

            elif provider == "ollama" and settings.OLLAMA_ENABLED:
                logger.info(f"Usando Ollama: {settings.OLLAMA_MODEL}")
                return _create_ollama_llm()

        except Exception as e:
            logger.warning(f"Falha ao inicializar {provider}: {e}")
            continue

    # Fallback para MockLLM
    logger.warning("Usando MockLLM - nenhum provedor real disponível")
    return MockLLMAgent()


def _create_anthropic_llm() -> LLMInterface:
    """Cria instância Anthropic Claude."""
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise RuntimeError("Biblioteca 'anthropic' necessária para Anthropic") from exc

    class AnthropicAdapter(LLMInterface):
        def __init__(self):
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.ANTHROPIC_MODEL
            self.temperature = settings.ANTHROPIC_TEMPERATURE
            self.max_tokens = settings.ANTHROPIC_MAX_TOKENS

        def structured_extract(self, system_prompt: str, user_prompt: str) -> dict:
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )

                content = response.content[0].text if response.content else ""
                return _parse_json_response(content)

            except Exception as exc:
                raise RuntimeError(f"Falha na API Anthropic: {exc}") from exc

    return AnthropicAdapter()


def _create_openai_llm() -> LLMInterface:
    """Cria instância OpenAI GPT."""
    try:
        from validators.inmetro.llm import OpenAICodexAgent

        return OpenAICodexAgent(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=settings.OPENAI_TEMPERATURE,
        )
    except ImportError as exc:
        raise RuntimeError("OpenAI não configurado") from exc


def _create_ollama_llm() -> LLMInterface:
    """Cria instância Ollama."""
    try:
        from validators.inmetro.llm import OllamaLLMAgent

        return OllamaLLMAgent(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            timeout=settings.OLLAMA_TIMEOUT,
            temperature=settings.OLLAMA_TEMPERATURE,
        )
    except ImportError as exc:
        raise RuntimeError("Ollama não configurado") from exc


def _parse_json_response(content: str) -> dict:
    """Parse JSON response from LLM."""
    import json
    import re

    try:
        return json.loads(content.strip())
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown code blocks
    json_match = re.search(r"```(?:json)?\s*({.*?})\s*```", content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find JSON object in text
    json_match = re.search(r"({.*})", content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Não foi possível parsear JSON da resposta: {content[:200]}")


# Dependency para Schema de Validação
@lru_cache(maxsize=1)
def get_validation_schema() -> dict:
    """Dependency para schema de validação JSON."""
    return load_datasheet_schema()


# Dependency para InmetroCrawler
def get_inmetro_crawler() -> InmetroCrawler:
    """Dependency para crawler INMETRO."""
    return InmetroCrawler()


# Dependency para InmetroExtractor
def get_inmetro_extractor(
    llm: LLMInterface = Depends(get_llm_interface),
) -> InmetroExtractor:
    """Dependency para extractor INMETRO."""
    return InmetroExtractor(
        llm=llm,
        system_prompt=(
            "Você é um agente especializado em homologação de equipamentos. "
            "Extraia dados do portal INMETRO e responda sempre com um único JSON."
        ),
        max_prompt_chars=12000,
        html_excerpt_chars=4000,
    )


# Dependency para RecordValidator
def get_record_validator(
    schema: dict = Depends(get_validation_schema),
) -> RecordValidator:
    """Dependency para validador de registros."""
    return RecordValidator(schema)


# Dependency para InmetroRepository (PostgreSQL)
def get_inmetro_repository() -> "DatabaseInmetroRepository":
    """Dependency para repositório INMETRO com PostgreSQL."""
    from validators.inmetro.database_repository import DatabaseInmetroRepository

    return DatabaseInmetroRepository()


# Dependency principal para InmetroPipeline
@lru_cache(maxsize=1)
def get_inmetro_pipeline(
    crawler: InmetroCrawler = Depends(get_inmetro_crawler),
    extractor: InmetroExtractor = Depends(get_inmetro_extractor),
    validator: RecordValidator = Depends(get_record_validator),
    repository: DatabaseInmetroRepository = Depends(get_inmetro_repository),
) -> InmetroPipeline:
    """
    Dependency principal para InmetroPipeline usando FastAPI DI.

    Componentes injetados:
    - InmetroCrawler: Scraping do portal INMETRO
    - InmetroExtractor: Transformação HTML → EquipmentRecord
    - RecordValidator: Validação contra schema JSON
    - InmetroRepository: Persistência PostgreSQL
    """
    logger.info("✅ InmetroPipeline inicializado com FastAPI Dependency Injection")

    return InmetroPipeline(
        crawler=crawler,
        extractor=extractor,
        validator=validator,
        repository=repository,
    )


# Dependency para InmetroService
@lru_cache(maxsize=1)
def get_inmetro_service(
    pipeline: InmetroPipeline = Depends(get_inmetro_pipeline),
) -> "InmetroService":
    """Dependency para InmetroService usando pipeline injetado."""
    from app.services.inmetro_service import InmetroService

    # Injetar pipeline no serviço
    service = InmetroService()
    service._pipeline = pipeline
    return service


# Legacy functions para compatibilidade
@lru_cache(maxsize=1)
def get_inmetro_pipeline_legacy() -> InmetroPipeline:
    """Função legada para compatibilidade - será removida."""
    logger.warning("Usando função legada get_inmetro_pipeline_legacy - migrar para DI")
    return get_inmetro_pipeline()


@lru_cache(maxsize=1)
def get_inmetro_repository_legacy() -> DatabaseInmetroRepository:
    """Função legada para compatibilidade - será removida."""
    logger.warning(
        "Usando função legada get_inmetro_repository_legacy - migrar para DI"
    )
    return get_inmetro_repository()


import json
from functools import lru_cache
import logging
from pathlib import Path
import sys

# Adicionar validators ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from validators.inmetro.crawler import InmetroCrawler
from validators.inmetro.llm import MockLLMAgent
from validators.inmetro.pipeline import InmetroExtractor, InmetroPipeline
from validators.inmetro.repository import InmetroRepository
from validators.inmetro.validator import RecordValidator

logger = logging.getLogger(__name__)


def load_json_schema(schema_path: Path) -> dict:
    """Load JSON schema from file."""
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)
