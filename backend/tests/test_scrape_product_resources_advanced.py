"""
Testes unitários para scrape_product_resources_advanced
========================================================

Cobertura:
- CacheManager: carregamento, salvamento, get/set
- URLValidator: validação de URLs acessíveis/inacessíveis
- DuckDuckGoClient: buscas PDF e imagens (mockadas)
- GenericScraper: search_datasheet, search_image
- Funções utilitárias: normalise_category, filter_products, _confidence_score
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

# Importar módulo alvo
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scrape_product_resources_advanced import (
    CacheManager,
    CoverageSummary,
    DuckDuckGoClient,
    GenericScraper,
    ProductResource,
    ResourceInfo,
    ScraperConfig,
    URLValidator,
    _confidence_score,
    _safe_ratio,
    filter_products,
    normalise_category,
)


# ============================================================================
# Fixtures
# ============================================================================
@pytest.fixture
def temp_cache_file(tmp_path: Path) -> Path:
    """Retorna caminho temporário para cache."""
    return tmp_path / "test_cache.json"


@pytest.fixture
def sample_inventory() -> dict:
    """Inventário de exemplo para testes."""
    return {
        "products": {
            "huawei": [
                {
                    "id": "huawei-sun2000-5ktl",
                    "manufacturer": "Huawei",
                    "model": "SUN2000-5KTL",
                    "name": "SUN2000-5KTL Inverter",
                    "type": "Inverter",
                },
                {
                    "id": "huawei-sun2000-10ktl",
                    "manufacturer": "Huawei",
                    "model": "SUN2000-10KTL",
                    "name": "SUN2000-10KTL Hybrid Inverter",
                    "type": "Hybrid Inverter",
                },
            ],
            "enphase": [
                {
                    "id": "enphase-iq8plus",
                    "manufacturer": "Enphase",
                    "model": "IQ8PLUS",
                    "name": "IQ8+ Microinverter",
                    "type": "Microinverter",
                }
            ],
        }
    }


@pytest.fixture
def scraper_config() -> ScraperConfig:
    """Configuração de scraper de exemplo."""
    return ScraperConfig(
        manufacturer="Huawei",
        base_url="https://solar.huawei.com/",
        preferred_domains=("solar.huawei.com", "huawei.com"),
        datasheet_hints=("manual", "specification"),
        image_hints=("render",),
    )


# ============================================================================
# Testes de CacheManager
# ============================================================================
class TestCacheManager:
    def test_cache_empty_on_init(self, temp_cache_file: Path) -> None:
        """Cache vazio quando arquivo não existe."""
        cache = CacheManager(temp_cache_file)
        assert not cache.has("test_key")
        assert cache.get("test_key") is None

    def test_cache_set_and_get(self, temp_cache_file: Path) -> None:
        """Armazenar e recuperar valores."""
        cache = CacheManager(temp_cache_file)
        cache.set("key1", {"url": "http://example.com", "status": "found"})

        assert cache.has("key1")
        assert cache.get("key1") == {"url": "http://example.com", "status": "found"}

    def test_cache_persistence(self, temp_cache_file: Path) -> None:
        """Cache persiste após salvar e recarregar."""
        cache1 = CacheManager(temp_cache_file)
        cache1.set("persistent_key", {"data": "value"})
        cache1.save()

        # Criar nova instância apontando para mesmo arquivo
        cache2 = CacheManager(temp_cache_file)
        assert cache2.has("persistent_key")
        assert cache2.get("persistent_key") == {"data": "value"}

    def test_cache_clear(self, temp_cache_file: Path) -> None:
        """Limpar cache remove todas as entradas."""
        cache = CacheManager(temp_cache_file)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.save()

        cache.clear()
        assert not cache.has("key1")
        assert not cache.has("key2")
        assert not temp_cache_file.exists()


# ============================================================================
# Testes de URLValidator
# ============================================================================
class TestURLValidator:
    @patch("requests.Session.head")
    def test_validate_url_success(self, mock_head: Mock) -> None:
        """URL válida retorna True."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

        validator = URLValidator(timeout=5)
        assert validator.validate_url("http://example.com/file.pdf") is True

    @patch("requests.Session.head")
    def test_validate_url_not_found(self, mock_head: Mock) -> None:
        """URL 404 retorna False."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_head.return_value = mock_response

        validator = URLValidator(timeout=5)
        assert validator.validate_url("http://example.com/missing.pdf") is False

    @patch("requests.Session.head")
    @patch("requests.Session.get")
    def test_validate_url_fallback_to_get(
        self, mock_get: Mock, mock_head: Mock
    ) -> None:
        """Fallback para GET se HEAD falhar."""
        mock_head.side_effect = requests.RequestException("HEAD not supported")
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        validator = URLValidator(timeout=5)
        assert validator.validate_url("http://example.com/file.pdf") is True

    @patch("requests.Session.head")
    @patch("requests.Session.get")
    def test_validate_url_complete_failure(
        self, mock_get: Mock, mock_head: Mock
    ) -> None:
        """Retorna False se HEAD e GET falharem."""
        mock_head.side_effect = requests.RequestException("HEAD failed")
        mock_get.side_effect = requests.RequestException("GET failed")

        validator = URLValidator(timeout=5)
        assert validator.validate_url("http://invalid.example.com") is False


# ============================================================================
# Testes de DuckDuckGoClient (mockado)
# ============================================================================
class TestDuckDuckGoClient:
    @patch("requests.Session.get")
    def test_search_pdf_returns_links(self, mock_get: Mock) -> None:
        """Busca PDF retorna lista de links."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <a class="result__a" href="http://example.com/datasheet.pdf">Datasheet</a>
            <a class="result__a" href="http://example.com/manual.pdf">Manual</a>
        </html>
        """
        mock_get.return_value = mock_response

        client = DuckDuckGoClient()
        results = client.search_pdf("Huawei SUN2000", max_results=5)

        assert len(results) == 2
        assert "datasheet.pdf" in results[0]
        assert "manual.pdf" in results[1]

    @patch("requests.Session.get")
    def test_search_images_returns_urls(self, mock_get: Mock) -> None:
        """Busca de imagens retorna URLs."""
        # Mock inicial para obter vqd
        mock_vqd_response = Mock()
        mock_vqd_response.status_code = 200
        mock_vqd_response.text = 'vqd="test-token-123"'

        # Mock da busca de imagens
        mock_image_response = Mock()
        mock_image_response.status_code = 200
        mock_image_response.json.return_value = {
            "results": [
                {"image": "http://example.com/image1.jpg"},
                {"image": "http://example.com/image2.png"},
            ]
        }

        mock_get.side_effect = [mock_vqd_response, mock_image_response]

        client = DuckDuckGoClient()
        results = client.search_images("Huawei inverter", max_results=5)

        assert len(results) == 2
        assert "image1.jpg" in results[0]
        assert "image2.png" in results[1]


# ============================================================================
# Testes de GenericScraper
# ============================================================================
class TestGenericScraper:
    def test_scraper_config_adds_base_domain(self) -> None:
        """ScraperConfig adiciona domínio base aos preferred_domains."""
        config = ScraperConfig(
            manufacturer="Test",
            base_url="https://test.example.com/",
            preferred_domains=("example.com",),
        )

        assert "test.example.com" in config.preferred_domains
        assert "example.com" in config.preferred_domains

    def test_build_datasheet_queries(self, scraper_config: ScraperConfig) -> None:
        """Gera queries de datasheet corretas."""
        scraper = GenericScraper(scraper_config)
        queries = scraper._build_datasheet_queries("SUN2000-5KTL", "Inverter 5kW")

        assert any("SUN2000-5KTL datasheet" in q for q in queries)
        assert any("manual" in q for q in queries)
        assert any("specification" in q for q in queries)

    def test_build_image_queries(self, scraper_config: ScraperConfig) -> None:
        """Gera queries de imagem corretas."""
        scraper = GenericScraper(scraper_config)
        queries = scraper._build_image_queries("SUN2000-5KTL", "Inverter 5kW")

        assert any("SUN2000-5KTL product image" in q for q in queries)
        assert any("render" in q for q in queries)


# ============================================================================
# Testes de funções utilitárias
# ============================================================================
class TestUtilityFunctions:
    def test_normalise_category_inverter(self) -> None:
        assert normalise_category("Inverter") == "inverters"
        assert normalise_category("String Inverter") == "inverters"

    def test_normalise_category_microinverter(self) -> None:
        assert normalise_category("Microinverter") == "microinverters"
        assert normalise_category("Micro Inverter") == "microinverters"

    def test_normalise_category_hybrid(self) -> None:
        assert normalise_category("Hybrid Inverter") == "hybrid_inverters"
        assert normalise_category("Hybrid") == "hybrid_inverters"

    def test_filter_products_all_categories(self, sample_inventory: Dict) -> None:
        """Filtra produtos por categorias."""
        categories = {"inverters", "microinverters", "hybrid_inverters"}
        products = filter_products(sample_inventory, categories)

        assert len(products) == 3

    def test_filter_products_by_manufacturer(self, sample_inventory: Dict) -> None:
        """Filtra por fabricante específico."""
        categories = {"inverters", "microinverters", "hybrid_inverters"}
        products = filter_products(
            sample_inventory, categories, manufacturers={"huawei"}
        )

        assert len(products) == 2
        assert all(p["manufacturer"] == "Huawei" for p in products)

    def test_filter_products_with_limit(self, sample_inventory: Dict) -> None:
        """Respeita limite de produtos."""
        categories = {"inverters", "microinverters", "hybrid_inverters"}
        products = filter_products(sample_inventory, categories, limit=1)

        assert len(products) == 1

    def test_confidence_score_preferred_domain(self) -> None:
        """Score alto para domínio preferencial."""
        score = _confidence_score(
            "https://solar.huawei.com/datasheet.pdf", ("solar.huawei.com",)
        )
        assert score == 0.95

    def test_confidence_score_generic_domain(self) -> None:
        """Score médio para domínio genérico."""
        score = _confidence_score("https://example.com/datasheet.pdf", ("huawei.com",))
        assert score == 0.5

    def test_safe_ratio_normal(self) -> None:
        """Cálculo correto de ratio."""
        assert _safe_ratio(5, 10) == 0.5
        assert _safe_ratio(1, 3) == 0.3333

    def test_safe_ratio_zero_total(self) -> None:
        """Retorna 0 quando total é 0."""
        assert _safe_ratio(5, 0) == 0.0


# ============================================================================
# Testes de CoverageSummary
# ============================================================================
class TestCoverageSummary:
    def test_summary_initialization(self) -> None:
        """Inicia com contadores zerados."""
        summary = CoverageSummary()
        assert summary.total_products == 0
        assert summary.datasheets_found == 0
        assert summary.images_found == 0

    def test_summary_update_with_found_resources(self) -> None:
        """Atualiza contadores quando recursos encontrados."""
        summary = CoverageSummary()

        product = ProductResource(
            manufacturer="Huawei",
            product_id="test-1",
            model="SUN2000",
            name="Test",
            type="Inverter",
            category="inverters",
            datasheet=ResourceInfo(status="found", url="http://example.com/ds.pdf"),
            image=ResourceInfo(status="found", url="http://example.com/img.jpg"),
        )

        summary.update(product)

        assert summary.total_products == 1
        assert summary.datasheets_found == 1
        assert summary.images_found == 1
        assert summary.datasheet_coverage == 1.0
        assert summary.image_coverage == 1.0

    def test_summary_update_with_missing_resources(self) -> None:
        """Não incrementa contadores quando recursos faltantes."""
        summary = CoverageSummary()

        product = ProductResource(
            manufacturer="Huawei",
            product_id="test-1",
            model="SUN2000",
            name="Test",
            type="Inverter",
            category="inverters",
            datasheet=ResourceInfo(status="not_found"),
            image=ResourceInfo(status="not_found"),
        )

        summary.update(product)

        assert summary.total_products == 1
        assert summary.datasheets_found == 0
        assert summary.images_found == 0
        assert summary.datasheet_coverage == 0.0
        assert summary.image_coverage == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
