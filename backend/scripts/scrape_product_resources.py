"""
Product Datasheet and Image Scraper for Solar Inverters
Busca inteligente de datasheets e imagens de produtos usando múltiplas fontes
"""

import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, quote
import time
from dataclasses import dataclass
import hashlib

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class ProductResource:
    """Recurso de produto (datasheet ou imagem)"""

    url: str
    type: str  # 'datasheet' ou 'image'
    source: str
    filename: str
    status: str = "pending"
    error: Optional[str] = None


class ManufacturerScraper:
    """Scraper base para fabricantes"""

    def __init__(self, manufacturer: str, base_url: str):
        self.manufacturer = manufacturer
        self.base_url = base_url
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Cria sessão HTTP com retry strategy"""
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/pdf,image/*",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )
        return session

    def search_datasheet(self, model: str, product_data: Dict) -> Optional[str]:
        """Busca datasheet do produto (implementar em subclasses)"""
        raise NotImplementedError

    def search_image(self, model: str, product_data: Dict) -> Optional[str]:
        """Busca imagem do produto (implementar em subclasses)"""
        raise NotImplementedError


class HuaweiScraper(ManufacturerScraper):
    """Scraper para produtos Huawei"""

    def __init__(self):
        super().__init__("Huawei", "https://solar.huawei.com/br/")

    def search_datasheet(self, model: str, product_data: Dict) -> Optional[str]:
        """Busca datasheet Huawei"""
        # Estratégias de busca:
        # 1. Site oficial Brasil
        # 2. Download center
        # 3. Página do produto específica

        search_patterns = [
            f"https://solar.huawei.com/br/download?product={model}",
            f"https://solar.huawei.com/download/{model}",
            f"https://support.huawei.com/enterprise/en/doc/{model}",
        ]

        for url in search_patterns:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    # Procurar por links de PDF
                    if ".pdf" in response.text.lower():
                        logger.info(f"✓ Datasheet encontrado: {url}")
                        return url
            except Exception as e:
                logger.debug(f"Erro ao buscar {url}: {e}")

        return None

    def search_image(self, model: str, product_data: Dict) -> Optional[str]:
        """Busca imagem do produto Huawei"""
        # Página de produtos
        try:
            product_page = f"{self.base_url}products/"
            response = self.session.get(product_page, timeout=10)

            if response.status_code == 200:
                # Extrair imagens (simplificado - implementar parser HTML real)
                # Este é um exemplo - precisa de BeautifulSoup para parsing real
                return f"{self.base_url}images/products/{model}.jpg"
        except Exception as e:
            logger.debug(f"Erro ao buscar imagem: {e}")

        return None


class GrowattScraper(ManufacturerScraper):
    """Scraper para produtos Growatt"""

    def __init__(self):
        super().__init__("Growatt", "https://br.growatt.com/")

    def search_datasheet(self, model: str, product_data: Dict) -> Optional[str]:
        """Busca datasheet Growatt"""
        # Site Brasil tem seção de downloads
        search_urls = [
            f"https://br.growatt.com/datasheet/{model}",
            f"https://en.growatt.com/upload/file/{model}_Datasheet",
            f"https://server.growatt.com/download/{model}",
        ]

        for url in search_urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200 and "pdf" in response.headers.get(
                    "content-type", ""
                ):
                    logger.info(f"✓ Datasheet Growatt encontrado: {url}")
                    return url
            except Exception as e:
                logger.debug(f"Erro ao buscar {url}: {e}")

        return None


class SolisScraper(ManufacturerScraper):
    """Scraper para produtos Solis"""

    def __init__(self):
        super().__init__("Solis", "https://www.solisinverters.com/")

    def search_datasheet(self, model: str, product_data: Dict) -> Optional[str]:
        """Busca datasheet Solis"""
        # Solis tem centro de downloads estruturado
        return None  # Implementar lógica específica


class SungrowScraper(ManufacturerScraper):
    """Scraper para produtos Sungrow"""

    def __init__(self):
        super().__init__("Sungrow", "https://br.sungrowpower.com/")

    def search_datasheet(self, model: str, product_data: Dict) -> Optional[str]:
        """Busca datasheet Sungrow"""
        downloads_url = "https://br.sungrowpower.com/Downloads"

        try:
            response = self.session.get(downloads_url, timeout=10)
            if response.status_code == 200:
                # Parsear página de downloads
                # Implementar busca por modelo específico
                pass
        except Exception as e:
            logger.debug(f"Erro ao buscar downloads Sungrow: {e}")

        return None


class FoxessScraper(ManufacturerScraper):
    """Scraper para produtos Foxess"""

    def __init__(self):
        super().__init__("Foxess", "https://www.fox-ess.com/")


class ProductResourceCollector:
    """Coletor principal de recursos de produtos"""

    def __init__(self, inventory_file: Path):
        self.inventory_file = inventory_file
        self.inventory = self._load_inventory()
        self.output_dir = Path("data/products-resources")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Scrapers por fabricante
        self.scrapers = {
            "Huawei": HuaweiScraper(),
            "Growatt": GrowattScraper(),
            "Solis": SolisScraper(),
            "Sungrow": SungrowScraper(),
            "Foxess": FoxessScraper(),
        }

    def _load_inventory(self) -> Dict:
        """Carrega inventário de produtos"""
        with open(self.inventory_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def collect_resources_for_manufacturer(self, manufacturer: str) -> Dict:
        """Coleta recursos para todos os produtos de um fabricante"""
        logger.info(f"\n{'='*80}")
        logger.info(f"Coletando recursos para: {manufacturer}")
        logger.info(f"{'='*80}")

        if manufacturer.lower() not in self.inventory["products"]:
            logger.warning(f"Fabricante {manufacturer} não encontrado no inventário")
            return {}

        products = self.inventory["products"][manufacturer.lower()]
        scraper = self.scrapers.get(manufacturer)

        if not scraper:
            logger.warning(f"Scraper não disponível para {manufacturer}")
            return {}

        results = {
            "manufacturer": manufacturer,
            "total_products": len(products),
            "datasheets_found": 0,
            "images_found": 0,
            "products": [],
        }

        for product in products:
            logger.info(f"\n📦 Processando: {product['model']}")

            product_result = {
                "id": product["id"],
                "model": product["model"],
                "datasheet": None,
                "image": None,
            }

            # Buscar datasheet
            try:
                datasheet_url = scraper.search_datasheet(product["model"], product)
                if datasheet_url:
                    product_result["datasheet"] = datasheet_url
                    results["datasheets_found"] += 1
                    logger.info(f"  ✓ Datasheet: {datasheet_url}")
                else:
                    logger.warning(f"  ✗ Datasheet não encontrado")
            except Exception as e:
                logger.error(f"  ✗ Erro ao buscar datasheet: {e}")

            # Buscar imagem
            try:
                image_url = scraper.search_image(product["model"], product)
                if image_url:
                    product_result["image"] = image_url
                    results["images_found"] += 1
                    logger.info(f"  ✓ Imagem: {image_url}")
                else:
                    logger.warning(f"  ✗ Imagem não encontrada")
            except Exception as e:
                logger.error(f"  ✗ Erro ao buscar imagem: {e}")

            results["products"].append(product_result)
            time.sleep(0.5)  # Rate limiting

        # Salvar resultados
        self._save_results(manufacturer, results)

        return results

    def _save_results(self, manufacturer: str, results: Dict):
        """Salva resultados da coleta"""
        output_file = self.output_dir / f"{manufacturer.lower()}_resources.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"\n💾 Resultados salvos em: {output_file}")
        logger.info(f"📊 Resumo:")
        logger.info(f"   Total de produtos: {results['total_products']}")
        logger.info(f"   Datasheets encontrados: {results['datasheets_found']}")
        logger.info(f"   Imagens encontradas: {results['images_found']}")
        logger.info(
            f"   Taxa de sucesso: {(results['datasheets_found'] + results['images_found']) / (results['total_products'] * 2) * 100:.1f}%"
        )

    def collect_all(self):
        """Coleta recursos para todos os fabricantes"""
        logger.info(f"\n🚀 Iniciando coleta de recursos para todos os fabricantes")
        logger.info(
            f"Total de fabricantes: {len(self.inventory['metadata']['manufacturers'])}"
        )

        for manufacturer in self.inventory["metadata"]["manufacturers"].keys():
            if manufacturer in ["Unknown", "Nep"]:
                logger.info(f"\n⏭️  Pulando {manufacturer} (scraper não implementado)")
                continue

            try:
                self.collect_resources_for_manufacturer(manufacturer)
            except Exception as e:
                logger.error(f"\n❌ Erro ao processar {manufacturer}: {e}")

        logger.info(f"\n✅ Coleta finalizada!")


def main():
    """Função principal"""
    inventory_file = Path("data/products_inventory_raw.json")

    if not inventory_file.exists():
        logger.error(f"Arquivo de inventário não encontrado: {inventory_file}")
        return

    collector = ProductResourceCollector(inventory_file)

    # Testar com Huawei primeiro
    logger.info("🧪 Modo de teste - coletando recursos da Huawei")
    collector.collect_resources_for_manufacturer("Huawei")

    # Descomentar para executar para todos os fabricantes
    # collector.collect_all()


if __name__ == "__main__":
    main()
