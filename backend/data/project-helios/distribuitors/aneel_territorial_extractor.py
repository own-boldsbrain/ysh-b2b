"""
ANEEL Distribuidoras - Agente de Captura Territorial com LLM
==============================================================
Extrai dados de operações territoriais uma a uma utilizando:
- Playwright para automação de navegador (Chromium)
- LLMs (Gemini → OpenAI → Docker models) para enriquecimento semântico
- RAG e fuzzy matching para validação de dados
"""

import os
import sys
import json
import time
import asyncio
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Playwright para automação de navegador
try:
    from playwright.async_api import async_playwright, Page, Browser

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    print(
        "⚠️  Playwright não instalado. Execute: pip install playwright && playwright install chromium"
    )
    PLAYWRIGHT_AVAILABLE = False

# LLMs
try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    print(
        "⚠️  Google Generative AI não instalado. Execute: pip install google-generativeai"
    )
    GEMINI_AVAILABLE = False

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    print("⚠️  OpenAI não instalado. Execute: pip install openai")
    OPENAI_AVAILABLE = False

try:
    import docker

    DOCKER_AVAILABLE = True
except ImportError:
    print("⚠️  Docker SDK não instalado. Execute: pip install docker")
    DOCKER_AVAILABLE = False

# Bibliotecas auxiliares
from bs4 import BeautifulSoup
import requests
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Carregar variáveis de ambiente
load_dotenv()

# ==========================================
# CONFIGURAÇÕES
# ==========================================


class Config:
    """Configurações centralizadas"""

    # API Keys
    GEMINI_KEY_1 = os.getenv("GEMINI_API_KEY_1")
    GEMINI_KEY_2 = os.getenv("GEMINI_API_KEY_2")
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")

    # Docker Models
    DOCKER_MODELS = os.getenv("DOCKER_MODELS", "ai/gemma3-qat:latest").split(",")

    # Browser
    HEADLESS = os.getenv("HEADLESS_BROWSER", "true").lower() == "true"
    TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    USER_AGENT = os.getenv(
        "USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    # Rate Limiting
    MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_SECOND", "3"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))

    # Paths
    BASE_DIR = Path(__file__).parent
    OUTPUT_DIR = BASE_DIR / "output"
    CACHE_DIR = BASE_DIR / "cache"

    # Datasets
    INPUT_CSV = BASE_DIR / "aneel_distribuidoras_360.csv"
    OUTPUT_CSV = BASE_DIR / "aneel_distribuidoras_360_territorial_enriched.csv"
    OUTPUT_JSON = BASE_DIR / "aneel_distribuidoras_360_territorial_enriched.json"
    CACHE_FILE = CACHE_DIR / "territorial_extraction_cache.json"

    # Quality Thresholds
    MIN_MUNICIPIOS = 1  # Mínimo de municípios para considerar válido
    MIN_CONFIDENCE_SCORE = 0.6  # Score mínimo de confiança (0-1)

    @classmethod
    def setup_dirs(cls):
        """Cria diretórios necessários"""
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.CACHE_DIR.mkdir(exist_ok=True)


# ==========================================
# GERENCIADOR DE AGENTES LLM
# ==========================================


class LLMAgentManager:
    """Gerencia failover entre Gemini → OpenAI → Docker models"""

    def __init__(self):
        self.gemini_clients = []
        self.openai_client = None
        self.docker_client = None
        self.current_provider = None

        # Inicializar Gemini
        if GEMINI_AVAILABLE and Config.GEMINI_KEY_1:
            try:
                genai.configure(api_key=Config.GEMINI_KEY_1)
                self.gemini_clients.append(genai.GenerativeModel("gemini-pro"))
                print("✅ Gemini Key 1 configurado")
            except Exception as e:
                print(f"⚠️  Erro ao configurar Gemini Key 1: {e}")

        if GEMINI_AVAILABLE and Config.GEMINI_KEY_2:
            try:
                # Criar segundo cliente (precisa de instância separada)
                self.gemini_clients.append(
                    {"api_key": Config.GEMINI_KEY_2, "model": "gemini-pro"}
                )
                print("✅ Gemini Key 2 configurado")
            except Exception as e:
                print(f"⚠️  Erro ao configurar Gemini Key 2: {e}")

        # Inicializar OpenAI
        if OPENAI_AVAILABLE and Config.OPENAI_KEY:
            try:
                openai.api_key = Config.OPENAI_KEY
                self.openai_client = openai
                print("✅ OpenAI configurado")
            except Exception as e:
                print(f"⚠️  Erro ao configurar OpenAI: {e}")

        # Inicializar Docker
        if DOCKER_AVAILABLE:
            try:
                self.docker_client = docker.from_env()
                print("✅ Docker client configurado")
            except Exception as e:
                print(f"⚠️  Erro ao configurar Docker: {e}")

    async def generate_content(self, prompt: str, context: str = "") -> Optional[str]:
        """
        Gera conteúdo usando LLM com failover automático

        Args:
            prompt: Prompt principal
            context: Contexto adicional (HTML, texto extraído, etc.)

        Returns:
            Resposta do LLM ou None em caso de falha total
        """
        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        # Tentar Gemini Key 1
        if self.gemini_clients:
            try:
                response = self.gemini_clients[0].generate_content(full_prompt)
                self.current_provider = "Gemini Key 1"
                return response.text
            except Exception as e:
                print(f"⚠️  Gemini Key 1 falhou: {e}")

        # Tentar Gemini Key 2
        if len(self.gemini_clients) > 1:
            try:
                genai.configure(api_key=self.gemini_clients[1]["api_key"])
                model = genai.GenerativeModel("gemini-pro")
                response = model.generate_content(full_prompt)
                self.current_provider = "Gemini Key 2"
                return response.text
            except Exception as e:
                print(f"⚠️  Gemini Key 2 falhou: {e}")

        # Tentar OpenAI
        if self.openai_client:
            try:
                response = self.openai_client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=2000,
                )
                self.current_provider = "OpenAI GPT-4"
                return response.choices[0].message.content
            except Exception as e:
                print(f"⚠️  OpenAI falhou: {e}")

        # Tentar Docker models (Ollama via API)
        if self.docker_client:
            try:
                # Verificar se containers Ollama estão rodando
                for model in Config.DOCKER_MODELS:
                    try:
                        # Chamar API local do Ollama
                        response = requests.post(
                            "http://localhost:11434/api/generate",
                            json={
                                "model": model.replace("ai/", ""),
                                "prompt": full_prompt,
                            },
                            timeout=30,
                        )
                        if response.status_code == 200:
                            self.current_provider = f"Docker ({model})"
                            return response.json().get("response")
                    except:
                        continue
            except Exception as e:
                print(f"⚠️  Docker models falharam: {e}")

        print("❌ Todos os LLMs falharam")
        return None


# ==========================================
# AGENTE DE EXTRAÇÃO TERRITORIAL
# ==========================================


class TerritorialExtractor:
    """Extrai dados territoriais usando browser automation + LLM"""

    def __init__(self):
        self.llm_manager = LLMAgentManager()
        self.cache = self._load_cache()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def _load_cache(self) -> Dict:
        """Carrega cache de extrações anteriores"""
        if Config.CACHE_FILE.exists():
            try:
                with open(Config.CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        """Salva cache"""
        with open(Config.CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    async def setup_browser(self):
        """Inicializa browser Playwright"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright não disponível")

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=Config.HEADLESS,
            args=["--disable-blink-features=AutomationControlled"],
        )

        context = await self.browser.new_context(
            user_agent=Config.USER_AGENT, viewport={"width": 1920, "height": 1080}
        )

        self.page = await context.new_page()
        print("✅ Browser Chromium inicializado")

    async def close_browser(self):
        """Fecha browser"""
        if self.browser:
            await self.browser.close()

    async def extract_from_website(
        self, cnpj: str, razao_social: str, sigla: str
    ) -> Dict:
        """
        Extrai dados territoriais do site oficial da distribuidora

        Args:
            cnpj: CNPJ da distribuidora
            razao_social: Razão social
            sigla: Sigla da distribuidora

        Returns:
            Dict com dados territoriais extraídos
        """
        # Verificar cache
        cache_key = f"{cnpj}_{sigla}"
        if cache_key in self.cache:
            print(f"📦 Cache hit: {sigla}")
            return self.cache[cache_key]

        print(f"\n🔍 Extraindo dados territoriais: {sigla} ({razao_social})")

        # 1. Buscar URL oficial via Google/LLM
        search_query = f"{razao_social} distribuidora energia elétrica site oficial"
        oficial_url = await self._find_official_website(search_query, sigla)

        if not oficial_url:
            print(f"⚠️  Não foi possível encontrar site oficial para {sigla}")
            return self._empty_result()

        # 2. Navegar até o site
        try:
            await self.page.goto(
                oficial_url, wait_until="domcontentloaded", timeout=Config.TIMEOUT
            )
            await asyncio.sleep(2)  # Aguardar carregamento dinâmico
        except Exception as e:
            print(f"❌ Erro ao acessar {oficial_url}: {e}")
            return self._empty_result()

        # 3. Extrair HTML
        html_content = await self.page.content()
        soup = BeautifulSoup(html_content, "html.parser")

        # Remover scripts, styles
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text_content = soup.get_text(separator="\n", strip=True)

        # 4. Usar LLM para extração semântica
        extraction_result = await self._llm_extract_territorial_data(
            text_content=text_content, sigla=sigla, razao_social=razao_social
        )

        # 5. Validar e enriquecer
        validated_result = self._validate_and_enrich(extraction_result, sigla)

        # 6. Salvar em cache
        self.cache[cache_key] = validated_result
        self._save_cache()

        return validated_result

    async def _find_official_website(
        self, search_query: str, sigla: str
    ) -> Optional[str]:
        """Encontra URL oficial da distribuidora"""
        # Lista de URLs conhecidas (fallback)
        known_urls = {
            "CEMIG": "https://www.cemig.com.br",
            "COPEL": "https://www.copel.com",
            "CELESC": "https://www.celesc.com.br",
            "ENEL": "https://www.enel.com.br",
            "ENERGISA": "https://www.energisa.com.br",
            "EQUATORIAL": "https://www.equatorialenergia.com.br",
            "LIGHT": "https://www.light.com.br",
            "EDP": "https://www.edp.com.br",
        }

        # Verificar URLs conhecidas
        for key, url in known_urls.items():
            if key in sigla.upper():
                return url

        # Usar LLM para buscar
        prompt = f"""
        Encontre a URL oficial da distribuidora de energia elétrica brasileira:
        
        Nome: {search_query}
        Sigla: {sigla}
        
        Retorne APENAS a URL no formato: https://www.exemplo.com.br
        Não inclua explicações.
        """

        url = await self.llm_manager.generate_content(prompt)

        if url and url.startswith("http"):
            return url.strip()

        return None

    async def _llm_extract_territorial_data(
        self, text_content: str, sigla: str, razao_social: str
    ) -> Dict:
        """Extrai dados territoriais usando LLM"""

        # Limitar texto a 8000 caracteres para evitar problemas de token
        text_content = text_content[:8000]

        prompt = f"""
        Você é um especialista em análise de dados de distribuidoras de energia elétrica no Brasil.
        
        Analise o conteúdo do site abaixo e extraia as seguintes informações sobre a distribuidora {sigla} ({razao_social}):
        
        1. Estados atendidos (siglas separadas por vírgula, ex: SP, RJ, MG)
        2. Lista de municípios atendidos (se disponível)
        3. Total de municípios atendidos (número)
        4. Área de concessão em km² (se disponível)
        5. População atendida (se disponível)
        6. Número de unidades consumidoras (se disponível)
        
        IMPORTANTE:
        - Retorne APENAS um JSON válido
        - Se algum dado não estiver disponível, use null
        - Para estados, use siglas oficiais (SP, RJ, MG, etc.)
        - Para municípios, retorne uma lista de nomes
        
        Formato esperado:
        {{
            "estados": ["SP", "MG"],
            "municipios": ["São Paulo", "Campinas", "..."],
            "total_municipios": 50,
            "area_concessao_km2": 12000,
            "populacao_atendida": 5000000,
            "unidades_consumidoras": 2000000,
            "confidence_score": 0.85
        }}
        
        Conteúdo do site:
        {text_content}
        """

        response = await self.llm_manager.generate_content(prompt)

        if not response:
            return self._empty_result()

        # Tentar parsear JSON
        try:
            # Extrair JSON da resposta (pode vir com markdown)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)

                # Adicionar metadados
                data["extraction_method"] = "LLM + Browser Automation"
                data["llm_provider"] = self.llm_manager.current_provider
                data["extraction_date"] = datetime.now().isoformat()

                return data
            else:
                print(f"⚠️  Resposta LLM não contém JSON válido")
                return self._empty_result()

        except json.JSONDecodeError as e:
            print(f"❌ Erro ao parsear JSON: {e}")
            print(f"Resposta LLM: {response[:500]}")
            return self._empty_result()

    def _validate_and_enrich(self, data: Dict, sigla: str) -> Dict:
        """Valida e enriquece dados extraídos"""

        # Validação básica
        if not data.get("estados") or not data.get("total_municipios"):
            data["quality_status"] = "INCOMPLETE"
        elif data.get("total_municipios", 0) < Config.MIN_MUNICIPIOS:
            data["quality_status"] = "INSUFFICIENT_DATA"
        elif data.get("confidence_score", 0) < Config.MIN_CONFIDENCE_SCORE:
            data["quality_status"] = "LOW_CONFIDENCE"
        else:
            data["quality_status"] = "VALID"

        # Calcular coordenadas estimadas (centro dos estados)
        if data.get("estados"):
            coords = self._estimate_coordinates(data["estados"])
            data.update(coords)

        return data

    def _estimate_coordinates(self, estados: List[str]) -> Dict:
        """Calcula coordenadas estimadas baseado nos estados"""
        # Coordenadas centrais dos estados (aproximadas)
        estado_coords = {
            "SP": (-23.5505, -46.6333),
            "RJ": (-22.9068, -43.1729),
            "MG": (-19.9167, -43.9345),
            "ES": (-20.3155, -40.3128),
            "PR": (-25.4296, -49.2713),
            "SC": (-27.5954, -48.5480),
            "RS": (-30.0346, -51.2177),
            "BA": (-12.9777, -38.5016),
            "SE": (-10.9472, -37.0731),
            "AL": (-9.6658, -35.7353),
            "PE": (-8.0476, -34.8770),
            "PB": (-7.1195, -34.8450),
            "RN": (-5.7945, -35.2110),
            "CE": (-3.7172, -38.5434),
            "PI": (-5.0892, -42.8016),
            "MA": (-2.5387, -44.2826),
            "PA": (-1.4554, -48.4898),
            "AP": (0.0349, -51.0694),
            "AM": (-3.1190, -60.0217),
            "RR": (2.8235, -60.6758),
            "RO": (-8.7619, -63.9039),
            "AC": (-8.7700, -70.5500),
            "TO": (-10.1753, -48.2982),
            "GO": (-16.6869, -49.2648),
            "MT": (-15.6014, -56.0979),
            "MS": (-20.4697, -54.6201),
            "DF": (-15.7801, -47.9292),
        }

        if not estados:
            return {}

        # Calcular centro geográfico médio
        lats = [estado_coords[e][0] for e in estados if e in estado_coords]
        lngs = [estado_coords[e][1] for e in estados if e in estado_coords]

        if not lats or not lngs:
            return {}

        return {
            "lat_centro": sum(lats) / len(lats),
            "lng_centro": sum(lngs) / len(lngs),
            "lat_minima": min(lats) - 1.5,
            "lat_maxima": max(lats) + 1.5,
            "lng_minima": min(lngs) - 1.5,
            "lng_maxima": max(lngs) + 1.5,
        }

    def _empty_result(self) -> Dict:
        """Retorna resultado vazio"""
        return {
            "estados": None,
            "municipios": None,
            "total_municipios": 0,
            "area_concessao_km2": None,
            "populacao_atendida": None,
            "unidades_consumidoras": None,
            "confidence_score": 0.0,
            "quality_status": "NO_DATA",
            "extraction_method": "Failed",
            "extraction_date": datetime.now().isoformat(),
        }


# ==========================================
# ORQUESTRADOR PRINCIPAL
# ==========================================


async def main():
    """Função principal"""

    print("=" * 70)
    print("ANEEL DISTRIBUIDORAS - EXTRAÇÃO TERRITORIAL 360°")
    print("=" * 70)
    print()

    # Setup
    Config.setup_dirs()

    # Carregar dados
    print("📂 Carregando dados...")
    df = pd.read_csv(Config.INPUT_CSV, sep=";", encoding="utf-8")
    print(f"✅ {len(df)} distribuidoras carregadas")
    print()

    # Filtrar apenas distribuidoras ativas e sem dados territoriais
    df_to_extract = df[
        (df["Ativo"] == "Sim")
        & (df["Distribuição"] == "Sim")
        & (df["Total Municípios"] == 0)
    ].copy()

    print(f"🎯 {len(df_to_extract)} distribuidoras precisam de dados territoriais")
    print()

    # Inicializar extrator
    extractor = TerritorialExtractor()

    if PLAYWRIGHT_AVAILABLE:
        await extractor.setup_browser()
    else:
        print("⚠️  Modo sem browser - usando apenas LLM")

    # Processar uma a uma
    results = []

    for idx, row in df_to_extract.iterrows():
        cnpj = row["CNPJ"]
        razao_social = row["Razão Social"]
        sigla = row["Sigla"]

        try:
            result = await extractor.extract_from_website(cnpj, razao_social, sigla)
            results.append(
                {"cnpj": cnpj, "sigla": sigla, "razao_social": razao_social, **result}
            )

            # Rate limiting
            await asyncio.sleep(1.0 / Config.MAX_REQUESTS)

        except Exception as e:
            print(f"❌ Erro ao processar {sigla}: {e}")
            results.append(
                {
                    "cnpj": cnpj,
                    "sigla": sigla,
                    "razao_social": razao_social,
                    **extractor._empty_result(),
                }
            )

    # Fechar browser
    if PLAYWRIGHT_AVAILABLE:
        await extractor.close_browser()

    # Salvar resultados
    print("\n💾 Salvando resultados...")

    df_results = pd.DataFrame(results)

    # Merge com dados originais
    df_final = df.merge(
        df_results,
        left_on="CNPJ",
        right_on="cnpj",
        how="left",
        suffixes=("", "_extracted"),
    )

    # Atualizar campos
    for col in [
        "estados",
        "total_municipios",
        "area_concessao_km2",
        "populacao_atendida",
    ]:
        if f"{col}_extracted" in df_final.columns:
            df_final[col] = df_final[f"{col}_extracted"].combine_first(df_final[col])

    # Salvar CSV
    df_final.to_csv(Config.OUTPUT_CSV, sep=";", index=False, encoding="utf-8")
    print(f"✅ CSV salvo: {Config.OUTPUT_CSV}")

    # Salvar JSON
    df_final.to_json(Config.OUTPUT_JSON, orient="records", force_ascii=False, indent=2)
    print(f"✅ JSON salvo: {Config.OUTPUT_JSON}")

    # Estatísticas
    print("\n📊 ESTATÍSTICAS:")
    print(f"Total processadas: {len(results)}")
    print(f"Válidas: {sum(1 for r in results if r.get('quality_status') == 'VALID')}")
    print(
        f"Incompletas: {sum(1 for r in results if r.get('quality_status') == 'INCOMPLETE')}"
    )
    print(
        f"Sem dados: {sum(1 for r in results if r.get('quality_status') == 'NO_DATA')}"
    )
    print()
    print("✅ PROCESSO CONCLUÍDO")


if __name__ == "__main__":
    asyncio.run(main())
