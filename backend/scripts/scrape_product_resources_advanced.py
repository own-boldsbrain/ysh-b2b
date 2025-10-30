"""
Advanced Product Resource Scraper
=================================

Pipeline responsável por garantir cobertura de datasheets e imagens para
inversores, microinversores e híbridos listados no inventário cru.

Principais funcionalidades
--------------------------
- Carregamento do inventário ``data/products_inventory_raw.json``;
- Filtro por categorias de interesse (inverters, microinverters, hybrid_inverters);
- Busca inteligente de datasheets (PDF) e imagens utilizando preferências por domínio
  oficial dos fabricantes e fallback via DuckDuckGo;
- Cálculo de métricas de cobertura por fabricante e consolidado;
- Persistência dos resultados em ``data/products-resources/product_resources.json``.

Uso:
  python scripts/scrape_product_resources_advanced.py --full
  python scripts/scrape_product_resources_advanced.py --manufacturers Huawei,Growatt --limit 5
"""

from __future__ import annotations

import argparse
import functools
import json
import logging
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
)

import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type variables
# ---------------------------------------------------------------------------
T = TypeVar("T")

# ---------------------------------------------------------------------------
# Configurações globais
# ---------------------------------------------------------------------------
INVENTORY_PATH = Path("data/products_inventory_raw.json")
OUTPUT_PATH = Path("data/products-resources/product_resources.json")
CACHE_PATH = Path("data/products-resources/.scraper_cache.json")
DOWNLOADS_PATH = Path("data/products-resources/downloads")
DEFAULT_CATEGORIES = {"inverters", "microinverters", "hybrid_inverters"}
NETWORK_TIMEOUT = 15
NETWORK_SLEEP = 1.0
RETRY_MAX_ATTEMPTS = 3
RETRY_BASE_DELAY = 1.0
RETRY_MAX_DELAY = 10.0


# ---------------------------------------------------------------------------
# Retry decorator com backoff exponencial
# ---------------------------------------------------------------------------
def retry_with_backoff(
    max_attempts: int = RETRY_MAX_ATTEMPTS,
    base_delay: float = RETRY_BASE_DELAY,
    max_delay: float = RETRY_MAX_DELAY,
    exceptions: Tuple[type[Exception], ...] = (requests.RequestException,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator para retry automático com backoff exponencial."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == max_attempts:
                        raise
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.debug(
                        "[Retry %d/%d] %s falhou: %s. Aguardando %.2fs...",
                        attempt,
                        max_attempts,
                        func.__name__,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
            raise RuntimeError(f"{func.__name__} esgotou tentativas")

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Cache Manager
# ---------------------------------------------------------------------------
class CacheManager:
    """Gerencia cache persistente de resultados de busca."""

    def __init__(self, cache_path: Path = CACHE_PATH) -> None:
        self.cache_path = cache_path
        self._cache: Dict[str, Any] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Carrega cache do disco se existir."""
        if self.cache_path.exists():
            try:
                with self.cache_path.open("r", encoding="utf-8") as f:
                    self._cache = json.load(f)
                logger.info(
                    "Cache carregado: %d entradas de %s",
                    len(self._cache),
                    self.cache_path,
                )
            except Exception as exc:
                logger.warning("Erro ao carregar cache: %s", exc)
                self._cache = {}

    def save(self) -> None:
        """Salva cache no disco."""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with self.cache_path.open("w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
            logger.debug("Cache salvo: %d entradas", len(self._cache))
        except Exception as exc:
            logger.warning("Erro ao salvar cache: %s", exc)

    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache."""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Armazena valor no cache."""
        self._cache[key] = value

    def has(self, key: str) -> bool:
        """Verifica se chave existe no cache."""
        return key in self._cache

    def clear(self) -> None:
        """Limpa todo o cache."""
        self._cache = {}
        if self.cache_path.exists():
            self.cache_path.unlink()


@dataclass(slots=True)
class ResourceInfo:
    """Informações sobre o recurso coletado."""

    status: str
    url: Optional[str] = None
    source: Optional[str] = None
    confidence: float = 0.0
    error: Optional[str] = None
    attempts: List[str] = field(default_factory=list)
    cached: bool = False


@dataclass(slots=True)
class ProductResource:
    """Resultado consolidado de um produto."""

    manufacturer: str
    product_id: str
    model: str
    name: str
    type: str
    category: str
    datasheet: ResourceInfo
    image: ResourceInfo


@dataclass(slots=True)
class CoverageSummary:
    """Métricas de cobertura."""

    total_products: int = 0
    datasheets_found: int = 0
    images_found: int = 0

    def update(self, product: ProductResource) -> None:
        self.total_products += 1
        if product.datasheet.status == "found":
            self.datasheets_found += 1
        if product.image.status == "found":
            self.images_found += 1

    @property
    def datasheet_coverage(self) -> float:
        return _safe_ratio(self.datasheets_found, self.total_products)

    @property
    def image_coverage(self) -> float:
        return _safe_ratio(self.images_found, self.total_products)


# ---------------------------------------------------------------------------
# URL Validator
# ---------------------------------------------------------------------------
class URLValidator:
    """Valida URLs usando HEAD requests para verificar disponibilidade."""

    def __init__(self, timeout: int = 5) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36"
                ),
            }
        )

    @retry_with_backoff(max_attempts=2, exceptions=(requests.RequestException,))
    def validate_url(self, url: str) -> bool:
        """Verifica se URL está acessível via HEAD request."""
        try:
            response = self.session.head(
                url, timeout=self.timeout, allow_redirects=True
            )
            return response.status_code < 400
        except requests.RequestException:
            # Fallback para GET se HEAD não for suportado
            try:
                response = self.session.get(url, timeout=self.timeout, stream=True)
                return response.status_code < 400
            except requests.RequestException:
                return False

    def validate_urls(self, urls: List[str], max_valid: int = 1) -> List[str]:
        """Valida lista de URLs e retorna as válidas."""
        valid_urls: List[str] = []
        for url in urls:
            if self.validate_url(url):
                valid_urls.append(url)
                if len(valid_urls) >= max_valid:
                    break
        return valid_urls


# ---------------------------------------------------------------------------
# DuckDuckGo helper
# ---------------------------------------------------------------------------
class DuckDuckGoClient:
    """Cliente leve para buscas web e de imagens via DuckDuckGo."""

    _SEARCH_ENDPOINT = "https://duckduckgo.com/html/"
    _HOMEPAGE = "https://duckduckgo.com/"
    _IMAGE_ENDPOINT = "https://duckduckgo.com/i.js"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            }
        )
        self._vqd_cache: Dict[str, str] = {}
        self._cache: Dict[Tuple[str, str], List[str]] = {}

    def search_pdf(self, query: str, max_results: int = 5) -> List[str]:
        cache_key = ("pdf", query)
        if cache_key in self._cache:
            return self._cache[cache_key]

        logger.debug("[DDG] Buscando PDFs: %s", query)
        try:
            response = self.session.get(
                self._SEARCH_ENDPOINT,
                params={"q": query + " filetype:pdf"},
                timeout=NETWORK_TIMEOUT,
            )
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            logger.debug("[DDG] Erro na busca PDF (%s): %s", query, exc)
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        links: List[str] = []
        for anchor in soup.select("a.result__a"):
            href = anchor.get("href")
            if not href:
                continue

            # Links via redirecionamento ?uddg=
            if "duckduckgo.com/l/?uddg=" in href:
                href = unquote(href.split("uddg=")[-1])

            if href.lower().endswith(".pdf") or "pdf" in href.lower():
                links.append(href)
            if len(links) >= max_results:
                break

        self._cache[cache_key] = links
        return links

    def search_images(self, query: str, max_results: int = 5) -> List[str]:
        cache_key = ("image", query)
        if cache_key in self._cache:
            return self._cache[cache_key]

        logger.debug("[DDG] Buscando imagens: %s", query)
        token = self._ensure_vqd(query)
        if not token:
            return []

        try:
            response = self.session.get(
                self._IMAGE_ENDPOINT,
                params={
                    "l": "pt-br",
                    "o": "json",
                    "q": query,
                    "vqd": token,
                    "f": "",
                    "p": "1",
                },
                timeout=NETWORK_TIMEOUT,
            )
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            logger.debug("[DDG] Erro na busca de imagem (%s): %s", query, exc)
            return []

        data = response.json()
        results = [
            item.get("image") for item in data.get("results", []) if item.get("image")
        ]
        self._cache[cache_key] = results[:max_results]
        return self._cache[cache_key]

    def _ensure_vqd(self, query: str) -> Optional[str]:
        if query in self._vqd_cache:
            return self._vqd_cache[query]

        try:
            response = self.session.get(
                self._HOMEPAGE, params={"q": query}, timeout=NETWORK_TIMEOUT
            )
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            logger.debug("[DDG] Erro ao obter vqd (%s): %s", query, exc)
            return None

        match = re.search(r'vqd="([\w-]+)"', response.text)
        if not match:
            match = re.search(r"vqd='([\\w-]+)'", response.text)
        if match:
            token = match.group(1)
            self._vqd_cache[query] = token
            return token

        logger.debug("[DDG] Token vqd não encontrado para %s", query)
        return None


# ---------------------------------------------------------------------------
# Resource Downloader
# ---------------------------------------------------------------------------
class ResourceDownloader:
    """Gerencia download de PDFs e imagens para armazenamento local."""

    def __init__(self, base_path: Path = DOWNLOADS_PATH) -> None:
        self.base_path = base_path
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def download_file(
        self, url: str, manufacturer: str, model: str, resource_type: str
    ) -> Optional[Path]:
        """
        Baixa arquivo e salva em estrutura organizada.

        Args:
            url: URL do recurso
            manufacturer: Nome do fabricante
            model: Modelo do produto
            resource_type: 'datasheet' ou 'image'

        Returns:
            Path do arquivo baixado ou None em caso de erro
        """
        # Criar estrutura de diretórios
        safe_manufacturer = self._sanitize_filename(manufacturer)
        safe_model = self._sanitize_filename(model)
        target_dir = self.base_path / safe_manufacturer / safe_model
        target_dir.mkdir(parents=True, exist_ok=True)

        # Determinar extensão do arquivo
        parsed = urlparse(url)
        path_parts = Path(parsed.path)
        extension = path_parts.suffix or self._guess_extension(url, resource_type)

        # Nome do arquivo
        filename = f"{safe_model}_{resource_type}{extension}"
        target_file = target_dir / filename

        # Verificar se já existe
        if target_file.exists():
            logger.debug("  [DOWNLOAD] Arquivo já existe: %s", target_file)
            return target_file

        # Download
        try:
            logger.debug("  [DOWNLOAD] Baixando %s...", url)
            response = self.session.get(url, timeout=NETWORK_TIMEOUT, stream=True)
            response.raise_for_status()

            with target_file.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = target_file.stat().st_size
            logger.info(
                "  [DOWNLOAD] Salvo: %s (%.2f KB)", target_file.name, file_size / 1024
            )
            return target_file

        except Exception as exc:
            logger.warning("  [DOWNLOAD] Falha ao baixar %s: %s", url, exc)
            if target_file.exists():
                target_file.unlink()
            return None

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Remove caracteres inválidos de nomes de arquivo."""
        # Substituir caracteres problemáticos
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", name)
        sanitized = sanitized.replace(" ", "_")
        return sanitized[:100]  # Limitar tamanho

    @staticmethod
    def _guess_extension(url: str, resource_type: str) -> str:
        """Adivinha extensão baseada no tipo de recurso."""
        if resource_type == "datasheet":
            return ".pdf"
        elif resource_type == "image":
            # Tentar extrair do URL
            if "jpg" in url.lower() or "jpeg" in url.lower():
                return ".jpg"
            elif "png" in url.lower():
                return ".png"
            elif "webp" in url.lower():
                return ".webp"
            return ".jpg"  # Default
        return ""


# ---------------------------------------------------------------------------
# Scraper genérico orientado por configuração
# ---------------------------------------------------------------------------
@dataclass(slots=True)
class ScraperConfig:
    manufacturer: str
    base_url: Optional[str]
    preferred_domains: Sequence[str]
    keywords: Sequence[str] = ()
    datasheet_hints: Sequence[str] = ()
    image_hints: Sequence[str] = ()

    def __post_init__(self) -> None:
        if self.base_url:
            domain = urlparse(self.base_url).netloc
            if domain and domain not in self.preferred_domains:
                self.preferred_domains = tuple({domain, *self.preferred_domains})


class GenericScraper:
    """Scraper flexível baseado em buscas externas com suporte a fallback."""

    def __init__(
        self,
        config: ScraperConfig,
        search_client: Optional[DuckDuckGoClient] = None,
        enable_fallback: bool = False,
    ) -> None:
        self.config = config
        self.client = search_client or DuckDuckGoClient()
        self.enable_fallback = enable_fallback

    # ------------------------------------------------------------------
    # Datasheet
    # ------------------------------------------------------------------
    def search_datasheet(self, model: str, product_name: str) -> ResourceInfo:
        attempts: List[str] = []
        queries = self._build_datasheet_queries(model, product_name)

        for query in queries:
            attempts.append(query)
            links = self.client.search_pdf(query)
            filtered = self._filter_by_domain(links)
            candidate = filtered or links
            if candidate:
                return ResourceInfo(
                    status="found",
                    url=candidate[0],
                    source="duckduckgo",
                    confidence=_confidence_score(
                        candidate[0], self.config.preferred_domains
                    ),
                    attempts=attempts,
                )

            time.sleep(0.3)

        return ResourceInfo(status="not_found", attempts=attempts)

    # ------------------------------------------------------------------
    # Imagem
    # ------------------------------------------------------------------
    def search_image(self, model: str, product_name: str) -> ResourceInfo:
        attempts: List[str] = []
        queries = self._build_image_queries(model, product_name)

        for query in queries:
            attempts.append(query)
            images = self.client.search_images(query)
            filtered = self._filter_by_domain(
                images, extensions={".png", ".jpg", ".jpeg", ".webp"}
            )
            candidate = filtered or images
            if candidate:
                return ResourceInfo(
                    status="found",
                    url=candidate[0],
                    source="duckduckgo",
                    confidence=_confidence_score(
                        candidate[0], self.config.preferred_domains
                    ),
                    attempts=attempts,
                )
            time.sleep(0.3)

        return ResourceInfo(status="not_found", attempts=attempts)

    # ------------------------------------------------------------------
    # Query builders
    # ------------------------------------------------------------------
    def _build_datasheet_queries(self, model: str, product_name: str) -> List[str]:
        manufacturer = self.config.manufacturer
        clean_model = model.replace("(", " ").replace(")", " ")
        base_queries = [
            f"{manufacturer} {clean_model} datasheet pdf",
            f"{manufacturer} {product_name} datasheet",
            f"{clean_model} inverter datasheet pdf",
        ]

        for hint in self.config.datasheet_hints:
            base_queries.append(f"{manufacturer} {clean_model} {hint}")

        return base_queries

    def _build_image_queries(self, model: str, product_name: str) -> List[str]:
        manufacturer = self.config.manufacturer
        clean_model = model.replace("(", " ").replace(")", " ")
        base_queries = [
            f"{manufacturer} {clean_model} product image",
            f"{manufacturer} {product_name} inverter image",
            f"{clean_model} inverter photo",
        ]
        for hint in self.config.image_hints:
            base_queries.append(f"{manufacturer} {clean_model} {hint}")
        return base_queries

    # ------------------------------------------------------------------
    @staticmethod
    def _filter_by_domain(
        urls: Iterable[str], extensions: Optional[Set[str]] = None
    ) -> List[str]:
        matched: List[str] = []
        allowed_ext = extensions or set()
        for url in urls:
            domain = urlparse(url).netloc.lower()
            if not domain:
                continue
            if extensions:
                ext = Path(urlparse(url).path).suffix.lower()
                if ext and ext not in allowed_ext:
                    continue
            matched.append(url)
        return matched


# ---------------------------------------------------------------------------
# Configuração por fabricante
# ---------------------------------------------------------------------------
SCRAPER_CATALOG: Dict[str, ScraperConfig] = {
    "huawei": ScraperConfig(
        manufacturer="Huawei",
        base_url="https://solar.huawei.com/",
        preferred_domains=("solar.huawei.com", "support.huawei.com", "huawei.com"),
        datasheet_hints=("manual pdf", "specification"),
        image_hints=("render", "product"),
    ),
    "growatt": ScraperConfig(
        manufacturer="Growatt",
        base_url="https://www.growatt.com/",
        preferred_domains=("growatt.com", "us.growatt.com", "br.growatt.com"),
        datasheet_hints=("datasheet pdf", "specification"),
    ),
    "solis": ScraperConfig(
        manufacturer="Solis",
        base_url="https://www.solisinverters.com/",
        preferred_domains=("solisinverters.com", "solis.com"),
        datasheet_hints=("datasheet pdf", "brochure"),
    ),
    "sungrow": ScraperConfig(
        manufacturer="Sungrow",
        base_url="https://www.sungrowpower.com/",
        preferred_domains=("sungrowpower.com", "br.sungrowpower.com"),
        datasheet_hints=("downloads", "specification"),
    ),
    "foxess": ScraperConfig(
        manufacturer="FoxESS",
        base_url="https://www.fox-ess.com/",
        preferred_domains=("fox-ess.com", "fox-ess.de"),
        datasheet_hints=("datasheet", "specification"),
    ),
    "enphase": ScraperConfig(
        manufacturer="Enphase",
        base_url="https://enphase.com/",
        preferred_domains=("enphase.com",),
        datasheet_hints=("data sheet",),
        image_hints=("microinverter",),
    ),
    "goodwe": ScraperConfig(
        manufacturer="GoodWe",
        base_url="https://www.goodwe.com/",
        preferred_domains=("goodwe.com", "br.goodwe.com"),
        datasheet_hints=("datasheet",),
    ),
    "fronius": ScraperConfig(
        manufacturer="Fronius",
        base_url="https://www.fronius.com/",
        preferred_domains=("fronius.com",),
        datasheet_hints=("data sheet", "downloads"),
    ),
    "deye": ScraperConfig(
        manufacturer="Deye",
        base_url="https://www.deyeinverter.com/",
        preferred_domains=("deyeinverter.com", "pt.deyeinverter.com"),
        datasheet_hints=("pdf", "specification"),
        image_hints=("inverter",),
    ),
    "apsystems": ScraperConfig(
        manufacturer="APsystems",
        base_url="https://apsystems.com/",
        preferred_domains=("apsystems.com", "latam.apsystems.com"),
        datasheet_hints=("datasheet",),
        image_hints=("microinverter",),
    ),
    "nep": ScraperConfig(
        manufacturer="NEP",
        base_url="https://www.nepess.com/",
        preferred_domains=("nepess.com",),
        datasheet_hints=("datasheet", "rsd"),
    ),
    "canadian_solar": ScraperConfig(
        manufacturer="Canadian Solar",
        base_url="https://www.canadiansolar.com/",
        preferred_domains=("canadiansolar.com",),
        datasheet_hints=("datasheet", "specification"),
    ),
    "jinko": ScraperConfig(
        manufacturer="JinkoSolar",
        base_url="https://www.jinkosolar.com/",
        preferred_domains=("jinkosolar.com",),
        datasheet_hints=("datasheet", "specification"),
    ),
    "trina": ScraperConfig(
        manufacturer="Trina Solar",
        base_url="https://www.trinasolar.com/",
        preferred_domains=("trinasolar.com",),
        datasheet_hints=("datasheet", "specification"),
    ),
    "longi": ScraperConfig(
        manufacturer="LONGi",
        base_url="https://www.longi.com/",
        preferred_domains=("longi.com", "longi-solar.com"),
        datasheet_hints=("datasheet", "specification"),
    ),
    "ja_solar": ScraperConfig(
        manufacturer="JA Solar",
        base_url="https://www.jasolar.com/",
        preferred_domains=("jasolar.com",),
        datasheet_hints=("datasheet", "specification"),
    ),
}


# ---------------------------------------------------------------------------
# Funções utilitárias
# ---------------------------------------------------------------------------
def load_inventory(path: Path = INVENTORY_PATH) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Inventário não encontrado: {path}")
    with path.open("r", encoding="utf-8") as handler:
        return json.load(handler)


def normalise_category(product_type: str) -> str:
    text = product_type.lower()
    if "micro" in text:
        return "microinverters"
    if "hybrid" in text:
        return "hybrid_inverters"
    return "inverters"


def filter_products(
    inventory: Dict,
    categories: Set[str],
    manufacturers: Optional[Set[str]] = None,
    limit: Optional[int] = None,
) -> List[Dict]:
    selected: List[Dict] = []
    manufacturers = {m.lower() for m in manufacturers} if manufacturers else None

    for mfr_key, products in inventory.get("products", {}).items():
        if manufacturers and mfr_key.lower() not in manufacturers:
            continue

        for product in products:
            category = normalise_category(product.get("type", ""))
            if category not in categories:
                continue
            product_copy = dict(product)
            product_copy["inventory_category"] = category
            selected.append(product_copy)
            if limit and len(selected) >= limit:
                return selected

    return selected


def build_scraper(
    manufacturer: str, client: DuckDuckGoClient, enable_fallback: bool = False
) -> GenericScraper:
    config = SCRAPER_CATALOG.get(manufacturer.lower())
    if not config:
        config = ScraperConfig(
            manufacturer=manufacturer,
            base_url=None,
            preferred_domains=(manufacturer.lower() + ".com",),
        )
        SCRAPER_CATALOG[manufacturer.lower()] = config
    return GenericScraper(config, client, enable_fallback)


# ---------------------------------------------------------------------------
# Execução principal
# ---------------------------------------------------------------------------
def collect_resources(
    inventory: Dict,
    categories: Set[str],
    manufacturers: Optional[Set[str]] = None,
    limit: Optional[int] = None,
    use_cache: bool = True,
    validate_urls: bool = False,
    download_resources: bool = False,
) -> Tuple[List[ProductResource], Dict[str, CoverageSummary]]:
    products = filter_products(inventory, categories, manufacturers, limit)
    ddg_client = DuckDuckGoClient()
    cache = CacheManager() if use_cache else None
    validator = URLValidator() if validate_urls else None
    downloader = ResourceDownloader() if download_resources else None
    results: List[ProductResource] = []
    summaries: Dict[str, CoverageSummary] = {}

    for idx, product in enumerate(products, start=1):
        manufacturer = product.get("manufacturer", "Unknown")
        model = product.get("model", "")
        name = product.get("name", model)
        product_id = product.get("id", f"{manufacturer}-{model}")
        category = product.get(
            "inventory_category", normalise_category(product.get("type", ""))
        )

        # Calcular progresso em tempo real
        progress_pct = (idx / len(products)) * 100
        current_summary = summaries.get(manufacturer, CoverageSummary())

        logger.info(
            "[%d/%d | %.1f%%] %s | %s | %s | DS:%d/%d IMG:%d/%d",
            idx,
            len(products),
            progress_pct,
            manufacturer,
            model,
            category,
            current_summary.datasheets_found,
            current_summary.total_products,
            current_summary.images_found,
            current_summary.total_products,
        )

        # Verificar cache primeiro
        cache_key = f"{manufacturer}:{model}"
        search_start = time.time()

        if cache and cache.has(cache_key):
            cached_data = cache.get(cache_key)
            if cached_data:
                ds_data = dict(cached_data["datasheet"])
                ds_data["cached"] = True
                datasheet_info = ResourceInfo(**ds_data)

                img_data = dict(cached_data["image"])
                img_data["cached"] = True
                image_info = ResourceInfo(**img_data)
            else:
                datasheet_info = ResourceInfo(status="not_found")
                image_info = ResourceInfo(status="not_found")
            search_elapsed = time.time() - search_start
            logger.debug("  [CACHE] Resultado recuperado em %.3fs", search_elapsed)
        else:
            scraper = build_scraper(manufacturer, ddg_client)

            logger.debug("  [BUSCA] Iniciando coleta de recursos...")
            datasheet_info = scraper.search_datasheet(model, name)
            logger.debug(
                "    → Datasheet: %s (%d tentativas)",
                datasheet_info.status,
                len(datasheet_info.attempts),
            )

            image_info = scraper.search_image(model, name)
            logger.debug(
                "    → Imagem: %s (%d tentativas)",
                image_info.status,
                len(image_info.attempts),
            )

            # Validar URLs se habilitado
            if validator:
                if datasheet_info.url and not validator.validate_url(
                    datasheet_info.url
                ):
                    logger.warning(
                        "  [VALIDATION] Datasheet URL inválida: %s", datasheet_info.url
                    )
                    datasheet_info.status = "invalid_url"
                if image_info.url and not validator.validate_url(image_info.url):
                    logger.warning(
                        "  [VALIDATION] Image URL inválida: %s", image_info.url
                    )
                    image_info.status = "invalid_url"

            search_elapsed = time.time() - search_start
            logger.debug("  [BUSCA] Concluída em %.3fs", search_elapsed)

            # Salvar no cache
            if cache:
                cache.set(
                    cache_key,
                    {
                        "datasheet": asdict(datasheet_info),
                        "image": asdict(image_info),
                    },
                )

        product_result = ProductResource(
            manufacturer=manufacturer,
            product_id=product_id,
            model=model,
            name=name,
            type=product.get("type", ""),
            category=category,
            datasheet=datasheet_info,
            image=image_info,
        )
        results.append(product_result)

        summary = summaries.setdefault(manufacturer, CoverageSummary())
        summary.update(product_result)

        time.sleep(NETWORK_SLEEP)

    # Persistir cache ao final
    if cache:
        cache.save()

    return results, summaries


def persist_results(
    products: Sequence[ProductResource],
    summaries: Dict[str, CoverageSummary],
    metadata: Dict,
    output_path: Path = OUTPUT_PATH,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "metadata": {
            **metadata,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_products": len(products),
            "datasheets_found": sum(p.datasheet.status == "found" for p in products),
            "images_found": sum(p.image.status == "found" for p in products),
        },
        "by_manufacturer": {
            manufacturer: {
                "total_products": summary.total_products,
                "datasheets_found": summary.datasheets_found,
                "images_found": summary.images_found,
                "datasheet_coverage": round(summary.datasheet_coverage, 4),
                "image_coverage": round(summary.image_coverage, 4),
            }
            for manufacturer, summary in summaries.items()
        },
        "products": [
            {
                "manufacturer": product.manufacturer,
                "product_id": product.product_id,
                "model": product.model,
                "name": product.name,
                "type": product.type,
                "category": product.category,
                "datasheet": asdict(product.datasheet),
                "image": asdict(product.image),
            }
            for product in products
        ],
    }

    with output_path.open("w", encoding="utf-8") as handler:
        json.dump(payload, handler, indent=2, ensure_ascii=False)

    logger.info("Resultados salvos em %s", output_path)


# ---------------------------------------------------------------------------
# Utilitários auxiliares
# ---------------------------------------------------------------------------
def _safe_ratio(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(part / total, 4)


def _confidence_score(url: str, preferred_domains: Sequence[str]) -> float:
    domain = urlparse(url).netloc.lower()
    if not domain:
        return 0.1
    preferred = {d.lower() for d in preferred_domains}
    if domain in preferred:
        return 0.95
    if any(domain.endswith(p.lstrip("*")) for p in preferred):
        return 0.75
    return 0.5


def generate_markdown_report(
    products: Sequence[ProductResource],
    summaries: Dict[str, CoverageSummary],
    metadata: Dict,
    output_path: Path = OUTPUT_PATH.parent / "scraping_report.md",
) -> None:
    """Gera relatório markdown detalhado com estatísticas."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append("# Relatório de Coleta de Recursos de Produtos\n")
    lines.append(
        f"**Gerado em:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
    )
    lines.append(f"**Total de produtos:** {len(products)}\n")

    # Estatísticas gerais
    total_datasheets = sum(1 for p in products if p.datasheet.status == "found")
    total_images = sum(1 for p in products if p.image.status == "found")
    datasheet_pct = (total_datasheets / len(products) * 100) if products else 0
    image_pct = (total_images / len(products) * 100) if products else 0

    lines.append("\n## 📊 Estatísticas Gerais\n")
    lines.append(
        f"- **Datasheets encontrados:** {total_datasheets} ({datasheet_pct:.1f}%)\n"
    )
    lines.append(f"- **Imagens encontradas:** {total_images} ({image_pct:.1f}%)\n")
    lines.append(
        f"- **Taxa de sucesso combinada:** {((total_datasheets + total_images) / (len(products) * 2) * 100):.1f}%\n"
    )

    # Por fabricante
    lines.append("\n## 🏭 Cobertura por Fabricante\n")
    lines.append(
        "| Fabricante | Produtos | Datasheets | Imagens | Cobertura DS | Cobertura IMG |\n"
    )
    lines.append(
        "|------------|----------|------------|---------|--------------|---------------|\n"
    )

    for manufacturer in sorted(summaries.keys()):
        summary = summaries[manufacturer]
        lines.append(
            f"| {manufacturer} | {summary.total_products} | "
            f"{summary.datasheets_found} | {summary.images_found} | "
            f"{summary.datasheet_coverage * 100:.1f}% | "
            f"{summary.image_coverage * 100:.1f}% |\n"
        )

    # Top produtos com recursos completos
    complete_products = [
        p
        for p in products
        if p.datasheet.status == "found" and p.image.status == "found"
    ]
    lines.append(
        f"\n## ✅ Produtos com Recursos Completos ({len(complete_products)})\n"
    )
    for product in complete_products[:20]:  # Primeiros 20
        lines.append(f"- **{product.manufacturer}** - {product.model}\n")

    # Produtos com falhas
    failed_products = [
        p
        for p in products
        if p.datasheet.status != "found" or p.image.status != "found"
    ]
    lines.append(f"\n## ⚠️ Produtos com Recursos Faltantes ({len(failed_products)})\n")
    for product in failed_products[:20]:  # Primeiros 20
        missing = []
        if product.datasheet.status != "found":
            missing.append("datasheet")
        if product.image.status != "found":
            missing.append("imagem")
        lines.append(
            f"- **{product.manufacturer}** - {product.model} "
            f"(faltando: {', '.join(missing)})\n"
        )

    # Metadados de execução
    lines.append("\n## 🔧 Metadados de Execução\n")
    if "filters" in metadata:
        filters = metadata["filters"]
        lines.append(f"- **Categorias:** {', '.join(filters.get('categories', []))}\n")
        mfrs = filters.get("manufacturers", "all")
        if isinstance(mfrs, list):
            lines.append(f"- **Fabricantes:** {', '.join(mfrs)}\n")
        else:
            lines.append(f"- **Fabricantes:** {mfrs}\n")
        if filters.get("limit"):
            lines.append(f"- **Limite:** {filters['limit']}\n")

    with output_path.open("w", encoding="utf-8") as f:
        f.writelines(lines)

    logger.info("Relatório markdown salvo em %s", output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scraper avançado de recursos de produtos"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Processa todo o inventário para inversores, microinversores e híbridos",
    )
    parser.add_argument(
        "--manufacturers",
        type=str,
        default="",
        help="Lista separada por vírgula de fabricantes a processar",
    )
    parser.add_argument(
        "--categories",
        type=str,
        default="",
        help="Categorias (inverters,microinverters,hybrid_inverters). Default: todas",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limita o número total de produtos processados (útil para debug)",
    )
    parser.add_argument(
        "--skip-cache",
        action="store_true",
        help="Desabilita uso de cache persistente (refaz todas as buscas)",
    )
    parser.add_argument(
        "--validate-urls",
        action="store_true",
        help="Valida acessibilidade das URLs encontradas via HEAD request",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=str(OUTPUT_PATH),
        help=f"Caminho do arquivo JSON de saída (default: {OUTPUT_PATH})",
    )
    parser.add_argument(
        "--output-report",
        type=str,
        default=str(OUTPUT_PATH.parent / "scraping_report.md"),
        help="Caminho do relatório Markdown (default: scraping_report.md)",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Desabilita geração do relatório Markdown",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Ativa logs detalhados (DEBUG level)",
    )
    parser.add_argument(
        "--download-resources",
        action="store_true",
        help="Baixa PDFs e imagens para armazenamento local",
    )
    parser.add_argument(
        "--downloads-path",
        type=str,
        default=str(DOWNLOADS_PATH),
        help=f"Diretório base para downloads (default: {DOWNLOADS_PATH})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Configurar nível de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    inventory = load_inventory()
    categories = (
        DEFAULT_CATEGORIES
        if not args.categories
        else {cat.strip().lower() for cat in args.categories.split(",") if cat.strip()}
    )
    manufacturers = {m.strip() for m in args.manufacturers.split(",") if m.strip()}
    if not args.full and not manufacturers and not args.limit:
        logger.info(
            "Nenhum parâmetro especificado. Execute com --full para cobertura completa ou informe --manufacturers."
        )
        return

    logger.info("Categorias alvo: %s", ", ".join(sorted(categories)))
    if manufacturers:
        logger.info("Fabricantes filtrados: %s", ", ".join(sorted(manufacturers)))

    logger.info("Cache: %s", "desabilitado" if args.skip_cache else "habilitado")
    logger.info(
        "Validação de URLs: %s", "habilitada" if args.validate_urls else "desabilitada"
    )
    logger.info(
        "Download de recursos: %s",
        "habilitado" if args.download_resources else "desabilitado",
    )

    start_time = time.time()
    products, summaries = collect_resources(
        inventory,
        categories,
        manufacturers=manufacturers if manufacturers else None,
        limit=args.limit,
        use_cache=not args.skip_cache,
        validate_urls=args.validate_urls,
        download_resources=args.download_resources,
    )
    elapsed = time.time() - start_time

    metadata = {
        "inventory_file": str(INVENTORY_PATH),
        "execution_time_seconds": round(elapsed, 2),
        "cache_enabled": not args.skip_cache,
        "url_validation_enabled": args.validate_urls,
        "filters": {
            "categories": sorted(categories),
            "manufacturers": sorted(list(manufacturers)) if manufacturers else "all",
            "limit": args.limit,
        },
    }

    output_json = Path(args.output_json)
    persist_results(products, summaries, metadata, output_json)

    # Gerar relatório Markdown se não desabilitado
    if not args.no_report:
        output_report = Path(args.output_report)
        generate_markdown_report(products, summaries, metadata, output_report)

    logger.info("\n" + "=" * 70)
    logger.info("Cobertura consolidada:")
    for manufacturer, summary in summaries.items():
        logger.info(
            "  - %s | produtos=%d | datasheets=%d (%.1f%%) | imagens=%d (%.1f%%)",
            manufacturer,
            summary.total_products,
            summary.datasheets_found,
            summary.datasheet_coverage * 100,
            summary.images_found,
            summary.image_coverage * 100,
        )
    logger.info("=" * 70)
    logger.info("Tempo total de execução: %.2fs", elapsed)


if __name__ == "__main__":
    main()
