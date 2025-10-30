"""
ANEEL Distribuidoras - Agente Multi-Crew com LLM Orchestration
===============================================================
Pipeline moderno usando:
- CrewAI: Orquestração de agentes especializados
- LangChain: Chains de processamento e RAG
- Mastra: Framework de agentes modernos
- Pydantic: Validação de dados estruturados
- Playwright: Automação de navegador

Agentes:
1. Research Agent: Busca dados oficiais (ANEEL API, sites)
2. Extraction Agent: Extrai dados territoriais estruturados
3. Validation Agent: Valida qualidade e completude dos dados
4. Enrichment Agent: Enriquece com dados de múltiplas fontes
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Pydantic models
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings

# LangChain
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

# CrewAI
from crewai import Agent, Task, Crew, Process
from crewai_tools import (
    SerperDevTool,
    WebsiteSearchTool,
    FileReadTool,
    CSVSearchTool,
)

# Playwright
try:
    from playwright.async_api import async_playwright, Page, Browser

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright não disponível. Execute: pip install playwright")

# Pandas
import pandas as pd

# ============================================
# CONFIGURAÇÕES COM PYDANTIC
# ============================================


class Settings(BaseSettings):
    """Configurações do projeto usando Pydantic Settings"""

    # API Keys
    github_token: str = Field(
        default="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"
    )
    gemini_key_1: str = Field(default="AIzaSyCmgSL3RkU7kZ_wAfNiW0Y1nKkifXdx0zY")
    gemini_key_2: str = Field(default="AIzaSyAY3QeBxTR7pyyHbzULk3xbLWzrmA82Pi8")
    openai_key: str = Field(
        default="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"
    )
    pylon_key: str = Field(
        default="pylf_v1_us_nfJxMf6R8vh9T7xYMr7Whg1lypBC3j1LyDh10vXnh2rG"
    )

    # Paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent)
    input_csv: str = "aneel_distribuidoras_360.csv"
    output_csv: str = "aneel_distribuidoras_360_crew_enriched.csv"
    output_json: str = "aneel_distribuidoras_360_crew_enriched.json"
    cache_file: str = "cache/crew_extraction_cache.json"

    # Browser
    headless: bool = True
    browser_timeout: int = 30000

    # Quality
    min_municipios: int = 1
    min_confidence: float = 0.6

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instanciar settings
settings = Settings()

# Criar diretórios
(settings.base_dir / "cache").mkdir(exist_ok=True)
(settings.base_dir / "output").mkdir(exist_ok=True)


# ============================================
# MODELOS PYDANTIC PARA DADOS ESTRUTURADOS
# ============================================


class CoordenadasGeograficas(BaseModel):
    """Modelo para coordenadas geográficas"""

    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    municipio: Optional[str] = Field(None, description="Município de referência")
    uf: Optional[str] = Field(None, max_length=2, description="UF")


class LimitesGeograficos(BaseModel):
    """Modelo para limites geográficos"""

    lat_min: float = Field(..., ge=-90, le=90)
    lat_max: float = Field(..., ge=-90, le=90)
    lng_min: float = Field(..., ge=-180, le=180)
    lng_max: float = Field(..., ge=-180, le=180)

    @validator("lat_max")
    def lat_max_maior_que_min(cls, v, values):
        if "lat_min" in values and v <= values["lat_min"]:
            raise ValueError("lat_max deve ser maior que lat_min")
        return v

    @validator("lng_max")
    def lng_max_maior_que_min(cls, v, values):
        if "lng_min" in values and v <= values["lng_min"]:
            raise ValueError("lng_max deve ser maior que lng_min")
        return v


class DistribuidoraTerritorioModel(BaseModel):
    """Modelo Pydantic para dados territoriais de distribuidoras"""

    cnpj: str = Field(..., min_length=14, max_length=18)
    sigla: str = Field(..., max_length=50)
    razao_social: str = Field(..., min_length=1)

    # Dados territoriais
    estados_atendidos: List[str] = Field(
        default_factory=list, description="Lista de UFs atendidas"
    )
    municipios: List[str] = Field(
        default_factory=list, description="Lista de municípios"
    )
    total_municipios: int = Field(ge=0, default=0)

    # Geografia
    area_concessao_km2: Optional[float] = Field(None, ge=0)
    coordenadas_sede: Optional[CoordenadasGeograficas] = None
    limites_geograficos: Optional[LimitesGeograficos] = None

    # Dados operacionais
    populacao_atendida: Optional[int] = Field(None, ge=0)
    unidades_consumidoras: Optional[int] = Field(None, ge=0)
    grupo_empresarial: Optional[str] = None
    tipo_distribuidora: Optional[str] = Field(
        None, description="Grande Porte|Média|Cooperativa|Municipal"
    )

    # Metadados
    confidence_score: float = Field(ge=0, le=1, default=0.0)
    quality_status: str = Field(default="PENDING")
    extraction_method: str = Field(default="CrewAI Multi-Agent")
    extraction_date: datetime = Field(default_factory=datetime.now)
    data_sources: List[str] = Field(default_factory=list)

    @validator("estados_atendidos")
    def validate_estados(cls, v):
        """Valida siglas de estados"""
        estados_validos = {
            "AC",
            "AL",
            "AP",
            "AM",
            "BA",
            "CE",
            "DF",
            "ES",
            "GO",
            "MA",
            "MT",
            "MS",
            "MG",
            "PA",
            "PB",
            "PR",
            "PE",
            "PI",
            "RJ",
            "RN",
            "RS",
            "RO",
            "RR",
            "SC",
            "SP",
            "SE",
            "TO",
        }
        return [uf for uf in v if uf.upper() in estados_validos]


# ============================================
# LANGCHAIN SETUP
# ============================================


def setup_langchain_llms():
    """Configura LLMs do LangChain"""

    # Gemini (primário)
    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=settings.gemini_key_1,
        temperature=0.1,
        max_tokens=8192,
    )

    # OpenAI (fallback)
    openai_llm = ChatOpenAI(
        model="gpt-4-turbo-preview",
        api_key=settings.openai_key,
        temperature=0.1,
        max_tokens=4096,
    )

    return {"gemini": gemini_llm, "openai": openai_llm}


llms = setup_langchain_llms()


# ============================================
# CREWAI AGENTS
# ============================================


class ANEELCrewAgents:
    """Definição dos agentes CrewAI"""

    @staticmethod
    def research_agent():
        """Agente de pesquisa - busca dados oficiais"""
        return Agent(
            role="Pesquisador de Dados ANEEL",
            goal="Encontrar dados oficiais e confiáveis sobre distribuidoras de energia no Brasil",
            backstory="""Você é um especialista em coleta de dados do setor elétrico brasileiro.
            Tem acesso a APIs da ANEEL, sites oficiais e bases de dados governamentais.
            Prioriza sempre fontes oficiais e verificáveis.""",
            verbose=True,
            allow_delegation=True,
            llm=llms["gemini"],
            tools=[
                # WebsiteSearchTool(),
                # SerperDevTool(),  # Requer API key
                DuckDuckGoSearchRun(),  # Busca web gratuita
            ],
        )

    @staticmethod
    def extraction_agent():
        """Agente de extração - processa HTML/APIs"""
        return Agent(
            role="Especialista em Extração de Dados",
            goal="Extrair dados territoriais estruturados de documentos e páginas web",
            backstory="""Você é especialista em parsing de dados, expressões regulares e 
            extração de informações estruturadas. Trabalha com HTML, JSON, CSV e PDFs.""",
            verbose=True,
            allow_delegation=False,
            llm=llms["gemini"],
            tools=[
                FileReadTool(),
                CSVSearchTool(),
            ],
        )

    @staticmethod
    def validation_agent():
        """Agente de validação - verifica qualidade"""
        return Agent(
            role="Auditor de Qualidade de Dados",
            goal="Validar completude, consistência e precisão dos dados extraídos",
            backstory="""Você é um auditor de dados rigoroso. Verifica se todas as informações
            obrigatórias estão presentes, se os dados são consistentes (ex: coordenadas dentro do Brasil),
            e calcula scores de confiança.""",
            verbose=True,
            allow_delegation=False,
            llm=llms["openai"],  # Usar OpenAI para validação crítica
        )

    @staticmethod
    def enrichment_agent():
        """Agente de enriquecimento - completa dados faltantes"""
        return Agent(
            role="Enriquecedor de Dados",
            goal="Completar dados faltantes usando múltiplas fontes e inferência inteligente",
            backstory="""Você é especialista em data enrichment. Quando dados estão faltando,
            você busca em fontes alternativas, faz inferências baseadas em dados similares e
            usa inteligência geográfica para completar informações.""",
            verbose=True,
            allow_delegation=True,
            llm=llms["gemini"],
            tools=[DuckDuckGoSearchRun()],
        )


# ============================================
# CREWAI TASKS
# ============================================


class ANEELCrewTasks:
    """Definição das tarefas CrewAI"""

    @staticmethod
    def research_task(agent, distribuidora: Dict):
        """Tarefa de pesquisa"""
        return Task(
            description=f"""
            Pesquise dados oficiais sobre a distribuidora:
            - CNPJ: {distribuidora['cnpj']}
            - Sigla: {distribuidora['sigla']}
            - Razão Social: {distribuidora['razao_social']}
            
            Fontes prioritárias:
            1. API ANEEL (https://dadosabertos.aneel.gov.br)
            2. Site oficial da distribuidora
            3. Dados governamentais (IBGE, gov.br)
            
            Encontre:
            - Estados e municípios atendidos
            - Área de concessão
            - Coordenadas geográficas
            - População atendida
            - Grupo empresarial
            
            Retorne URLs e dados brutos encontrados.
            """,
            expected_output="JSON com URLs e dados brutos coletados",
            agent=agent,
        )

    @staticmethod
    def extraction_task(agent, research_output: str, distribuidora: Dict):
        """Tarefa de extração"""
        return Task(
            description=f"""
            Extraia dados territoriais estruturados da distribuidora {distribuidora['sigla']}.
            
            Dados da pesquisa:
            {research_output}
            
            Extraia e estruture em JSON:
            - estados_atendidos: lista de UFs (ex: ["SP", "MG"])
            - municipios: lista de municípios
            - total_municipios: número inteiro
            - area_concessao_km2: área em km²
            - coordenadas_sede: {{lat, lng, municipio, uf}}
            - limites_geograficos: {{lat_min, lat_max, lng_min, lng_max}}
            - populacao_atendida: número de habitantes
            - unidades_consumidoras: número de UCs
            - grupo_empresarial: nome do grupo
            - tipo_distribuidora: Grande Porte|Média|Cooperativa|Municipal
            
            Use apenas dados verificáveis. Se não encontrar, use null.
            """,
            expected_output="JSON estruturado com dados extraídos seguindo modelo Pydantic",
            agent=agent,
        )

    @staticmethod
    def validation_task(agent, extraction_output: str, distribuidora: Dict):
        """Tarefa de validação"""
        return Task(
            description=f"""
            Valide os dados extraídos da distribuidora {distribuidora['sigla']}.
            
            Dados extraídos:
            {extraction_output}
            
            Verificações:
            1. Campos obrigatórios preenchidos (estados, total_municipios)
            2. Coordenadas dentro do Brasil (-34 a 5 lat, -74 a -35 lng)
            3. Total de municípios >= 1
            4. Estados válidos (siglas brasileiras)
            5. Consistência entre área, população e municípios
            
            Calcule confidence_score (0-1) baseado em:
            - Completude dos dados (0.4)
            - Consistência geográfica (0.3)
            - Fontes verificáveis (0.3)
            
            Defina quality_status:
            - VALID: score >= 0.6, dados completos
            - INCOMPLETE: score < 0.6, faltam dados
            - INVALID: dados inconsistentes
            
            Retorne JSON com validação.
            """,
            expected_output="JSON com status de validação e confidence_score",
            agent=agent,
        )

    @staticmethod
    def enrichment_task(agent, validation_output: str, distribuidora: Dict):
        """Tarefa de enriquecimento"""
        return Task(
            description=f"""
            Enriqueça dados incompletos da distribuidora {distribuidora['sigla']}.
            
            Dados validados:
            {validation_output}
            
            Se quality_status for INCOMPLETE:
            1. Busque dados faltantes em fontes alternativas
            2. Infira dados usando distribuidoras similares
            3. Calcule coordenadas estimadas usando estados atendidos
            4. Estime população usando municípios (IBGE)
            
            Priorize:
            - Dados de municípios (crítico)
            - Coordenadas geográficas
            - População atendida
            
            Atualize confidence_score após enriquecimento.
            """,
            expected_output="JSON final com dados enriquecidos e metadados atualizados",
            agent=agent,
        )


# ============================================
# ORQUESTRADOR CREWAI
# ============================================


class ANEELDistribuidorasCrew:
    """Orquestrador principal usando CrewAI"""

    def __init__(self):
        self.agents = ANEELCrewAgents()
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """Carrega cache"""
        cache_path = settings.base_dir / settings.cache_file
        if cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        """Salva cache"""
        cache_path = settings.base_dir / settings.cache_file
        cache_path.parent.mkdir(exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def process_distribuidora(
        self, distribuidora: Dict
    ) -> DistribuidoraTerritorioModel:
        """Processa uma distribuidora usando crew de agentes"""

        cache_key = f"{distribuidora['cnpj']}_{distribuidora['sigla']}"

        # Verificar cache
        if cache_key in self.cache:
            print(f"📦 Cache hit: {distribuidora['sigla']}")
            return DistribuidoraTerritorioModel(**self.cache[cache_key])

        print(
            f"\n🚀 Processando: {distribuidora['sigla']} ({distribuidora['razao_social']})"
        )

        # Criar agentes
        research_agent = self.agents.research_agent()
        extraction_agent = self.agents.extraction_agent()
        validation_agent = self.agents.validation_agent()
        enrichment_agent = self.agents.enrichment_agent()

        # Criar tarefas
        tasks = ANEELCrewTasks()

        research_task = tasks.research_task(research_agent, distribuidora)
        # extraction_task precisa do output de research (sequencial)
        # validation_task precisa do output de extraction
        # enrichment_task precisa do output de validation

        # Criar crew com processo sequencial
        crew = Crew(
            agents=[
                research_agent,
                extraction_agent,
                validation_agent,
                enrichment_agent,
            ],
            tasks=[],  # Tasks serão adicionadas dinamicamente
            process=Process.sequential,
            verbose=True,
        )

        # Executar research
        research_task = tasks.research_task(research_agent, distribuidora)
        crew.tasks = [research_task]
        research_output = crew.kickoff()

        print(f"✅ Research completo: {len(str(research_output))} caracteres")

        # Executar extraction
        extraction_task = tasks.extraction_task(
            extraction_agent, str(research_output), distribuidora
        )
        crew.tasks = [extraction_task]
        extraction_output = crew.kickoff()

        print(f"✅ Extraction completo")

        # Executar validation
        validation_task = tasks.validation_task(
            validation_agent, str(extraction_output), distribuidora
        )
        crew.tasks = [validation_task]
        validation_output = crew.kickoff()

        print(f"✅ Validation completo")

        # Executar enrichment se necessário
        validation_data = self._parse_json_output(str(validation_output))

        if validation_data.get("quality_status") in ["INCOMPLETE", "INVALID"]:
            print(f"⚠️  Dados incompletos, iniciando enrichment...")
            enrichment_task = tasks.enrichment_task(
                enrichment_agent, str(validation_output), distribuidora
            )
            crew.tasks = [enrichment_task]
            final_output = crew.kickoff()
        else:
            final_output = validation_output

        # Parsear resultado final
        final_data = self._parse_json_output(str(final_output))

        # Criar modelo Pydantic
        try:
            model = DistribuidoraTerritorioModel(
                cnpj=distribuidora["cnpj"],
                sigla=distribuidora["sigla"],
                razao_social=distribuidora["razao_social"],
                **final_data,
            )

            # Salvar em cache
            self.cache[cache_key] = model.dict()
            self._save_cache()

            return model

        except Exception as e:
            print(f"❌ Erro ao criar modelo Pydantic: {e}")
            # Retornar modelo vazio
            return DistribuidoraTerritorioModel(
                cnpj=distribuidora["cnpj"],
                sigla=distribuidora["sigla"],
                razao_social=distribuidora["razao_social"],
                quality_status="ERROR",
            )

    def _parse_json_output(self, output: str) -> Dict:
        """Parse JSON do output dos agentes"""
        try:
            # Tentar encontrar JSON no texto
            json_start = output.find("{")
            json_end = output.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = output[json_start:json_end]
                return json.loads(json_str)
            else:
                return {}
        except Exception as e:
            print(f"⚠️  Erro ao parsear JSON: {e}")
            return {}

    def process_all(self, limit: Optional[int] = None):
        """Processa todas as distribuidoras"""

        print("=" * 70)
        print("ANEEL DISTRIBUIDORAS - CREW AI EXTRACTION")
        print("=" * 70)
        print()

        # Carregar CSV
        csv_path = settings.base_dir / settings.input_csv
        df = pd.read_csv(csv_path, sep=";", encoding="utf-8-sig", dtype={"CNPJ": str})

        print(f"📊 Total: {len(df)} distribuidoras")

        # Filtrar sem dados
        df_sem_dados = df[
            (df["Ativo"] == "Sim")
            & (df["Distribuição"] == "Sim")
            & (df["Total Municípios"] == 0)
        ].copy()

        if limit:
            df_sem_dados = df_sem_dados.head(limit)

        print(f"🎯 {len(df_sem_dados)} sem dados territoriais")
        print()

        # Processar
        results = []

        for idx, row in df_sem_dados.iterrows():
            # Pular agências reguladoras
            if any(
                x in str(row["Razão Social"]).upper()
                for x in ["ANATEL", "ADASA", "AGENCIA"]
            ):
                continue

            distribuidora = {
                "cnpj": row["CNPJ"],
                "sigla": row["Sigla"] if pd.notna(row["Sigla"]) else "",
                "razao_social": row["Razão Social"],
            }

            model = self.process_distribuidora(distribuidora)
            results.append(model)

            # Rate limiting
            import time

            time.sleep(2)

        # Salvar resultados
        self._save_results(df, results)

        print("\n✅ PROCESSAMENTO CONCLUÍDO")
        print(f"   Total processadas: {len(results)}")
        print(f"   Válidas: {sum(1 for r in results if r.quality_status == 'VALID')}")

    def _save_results(
        self, df_original: pd.DataFrame, results: List[DistribuidoraTerritorioModel]
    ):
        """Salva resultados"""

        # Converter para DataFrame
        results_data = []
        for model in results:
            data = model.dict()
            # Flatten nested objects
            if data.get("coordenadas_sede"):
                coord = data.pop("coordenadas_sede")
                data["lat_sede"] = coord.get("lat")
                data["lng_sede"] = coord.get("lng")

            if data.get("limites_geograficos"):
                lim = data.pop("limites_geograficos")
                data["lat_min"] = lim.get("lat_min")
                data["lat_max"] = lim.get("lat_max")
                data["lng_min"] = lim.get("lng_min")
                data["lng_max"] = lim.get("lng_max")

            results_data.append(data)

        df_results = pd.DataFrame(results_data)

        # Merge com original
        df_final = df_original.merge(
            df_results, on="CNPJ", how="left", suffixes=("", "_crew")
        )

        # Atualizar campos
        for col in [
            "estados_atendidos",
            "total_municipios",
            "area_concessao_km2",
            "populacao_atendida",
        ]:
            if f"{col}_crew" in df_final.columns:
                df_final[col] = df_final[f"{col}_crew"].combine_first(df_final[col])

        # Salvar CSV
        output_csv = settings.base_dir / settings.output_csv
        df_final.to_csv(output_csv, sep=";", index=False, encoding="utf-8-sig")
        print(f"\n💾 CSV salvo: {output_csv}")

        # Salvar JSON
        output_json = settings.base_dir / settings.output_json
        output_data = {
            "metadata": {
                "extraction_date": datetime.now().isoformat(),
                "total_distribuidoras": len(df_final),
                "processed": len(results),
                "method": "CrewAI Multi-Agent + LangChain",
                "llms_used": ["Gemini 1.5 Pro", "GPT-4 Turbo"],
            },
            "distribuidoras": [model.dict() for model in results],
        }

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)

        print(f"💾 JSON salvo: {output_json}")


# ============================================
# MAIN
# ============================================


def main():
    """Execução principal"""

    print("🚀 Inicializando ANEEL CrewAI Extractor...")
    print(f"   Gemini: {settings.gemini_key_1[:20]}...")
    print(f"   OpenAI: {settings.openai_key[:20]}...")
    print(f"   Input: {settings.input_csv}")
    print()

    crew = ANEELDistribuidorasCrew()

    # Processar apenas 3 primeiras para teste
    crew.process_all(limit=3)


if __name__ == "__main__":
    main()
