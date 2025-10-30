"""Integra Database de URLs com Sistema de Fallback Inteligente.

Conecta manufacturers_urls_database.json ao intelligent_fallback_orchestrator
para fornecer URLs de referência durante buscas de produtos.

Workflow:
1. Carrega database de URLs por fabricante
2. Mapeia domínios base para cada marca
3. Fornece URLs candidatas ao fallback orchestrator
4. Enriquece resultados com contexto de produto
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ManufacturerURLContext:
    """Contexto de URLs de um fabricante."""

    name: str
    country: str
    base_domain: str
    official_brazil_url: str
    product_pages: Dict[str, List[str]]
    datasheet_urls: List[str]


class ManufacturerURLDatabase:
    """Database de URLs de fabricantes para fallback."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.manufacturers: Dict[str, ManufacturerURLContext] = {}
        self._load_database()

    def _load_database(self):
        """Carrega database de URLs."""
        with open(self.database_path, encoding="utf-8") as f:
            data = json.load(f)

        for name, manufacturer_data in data.get("manufacturers", {}).items():
            context = self._build_manufacturer_context(name, manufacturer_data)
            self.manufacturers[name.lower()] = context

        logger.info(f"✅ Carregados {len(self.manufacturers)} fabricantes")

    def _build_manufacturer_context(
        self, name: str, data: Dict[str, Any]
    ) -> ManufacturerURLContext:
        """Constrói contexto de URLs de um fabricante."""
        # Website principal Brasil
        websites = data.get("websites", {})
        official_brazil_url = websites.get(
            "official_brazil", websites.get("official_latam", "")
        )

        # Extrai domínio base
        base_domain = ""
        if official_brazil_url:
            from urllib.parse import urlparse

            parsed = urlparse(official_brazil_url)
            base_domain = f"{parsed.scheme}://{parsed.netloc}"

        # Agrupa páginas de produtos por tipo
        product_pages: Dict[str, List[str]] = {
            "string": [],
            "microinverter": [],
            "hybrid": [],
        }

        datasheet_urls: List[str] = []

        # Extrai URLs de product lines
        for line_name, line_data in data.get("product_lines", {}).items():
            # Classifica tipo de produto
            product_type = "string"
            if "micro" in line_name.lower():
                product_type = "microinverter"
            elif "hybrid" in line_name.lower():
                product_type = "hybrid"

            # Página da linha
            if "product_page" in line_data:
                product_pages[product_type].append(line_data["product_page"])

            # Modelos
            for model in line_data.get("models", []):
                if "product_page" in model:
                    product_pages[product_type].append(model["product_page"])
                if "datasheet_url" in model:
                    datasheet_urls.append(model["datasheet_url"])

        return ManufacturerURLContext(
            name=name,
            country=data.get("country", ""),
            base_domain=base_domain,
            official_brazil_url=official_brazil_url,
            product_pages=product_pages,
            datasheet_urls=datasheet_urls,
        )

    def get_manufacturer_context(self, manufacturer: str) -> ManufacturerURLContext | None:
        """Retorna contexto de URLs de um fabricante."""
        return self.manufacturers.get(manufacturer.lower())

    def get_base_domain(self, manufacturer: str) -> str:
        """Retorna domínio base de um fabricante."""
        context = self.get_manufacturer_context(manufacturer)
        return context.base_domain if context else ""

    def get_product_urls(
        self, manufacturer: str, product_type: str | None = None
    ) -> List[str]:
        """Retorna URLs de produtos de um fabricante.

        Args:
            manufacturer: Nome do fabricante
            product_type: Tipo de produto (string, microinverter, hybrid)
                         Se None, retorna todos
        """
        context = self.get_manufacturer_context(manufacturer)
        if not context:
            return []

        if product_type:
            return context.product_pages.get(product_type, [])

        # Retorna todas as URLs
        all_urls = []
        for urls in context.product_pages.values():
            all_urls.extend(urls)
        return all_urls

    def get_datasheet_urls(self, manufacturer: str) -> List[str]:
        """Retorna URLs de datasheets de um fabricante."""
        context = self.get_manufacturer_context(manufacturer)
        return context.datasheet_urls if context else []

    def infer_manufacturer_from_query(self, query: str) -> str | None:
        """Infere fabricante a partir de uma query.

        Args:
            query: Query de busca (e.g., "Growatt MIN 5000")

        Returns:
            Nome do fabricante ou None
        """
        query_lower = query.lower()

        for manufacturer in self.manufacturers.keys():
            if manufacturer in query_lower:
                return manufacturer

        # Tenta variações comuns
        aliases = {
            "growatt": ["growatt"],
            "sungrow": ["sungrow"],
            "deye": ["deye"],
            "goodwe": ["goodwe", "good we"],
            "fronius": ["fronius"],
            "huawei": ["huawei"],
            "enphase": ["enphase"],
            "hoymiles": ["hoymiles"],
            "apsystems": ["apsystems", "ap systems"],
        }

        for manufacturer, variations in aliases.items():
            if any(v in query_lower for v in variations):
                return manufacturer

        return None

    def get_all_manufacturers(self) -> List[str]:
        """Retorna lista de todos os fabricantes."""
        return list(self.manufacturers.keys())

    def export_domain_mapping(self) -> Dict[str, str]:
        """Exporta mapeamento fabricante → domínio base.

        Útil para integração com SearchAgent.
        """
        return {
            name: context.base_domain
            for name, context in self.manufacturers.items()
            if context.base_domain
        }


def integrate_with_fallback_orchestrator():
    """Exemplo de integração com fallback orchestrator."""
    from intelligent_fallback_orchestrator import IntelligentFallbackOrchestrator

    # Carrega database
    workspace = Path(__file__).parent.parent
    database_path = workspace / "data" / "manufacturers_urls_database.json"

    url_db = ManufacturerURLDatabase(database_path)

    # Cria orchestrator
    orchestrator = IntelligentFallbackOrchestrator()

    # Query de teste
    query = "Growatt MIN 5000TL-XH datasheet"

    # Infere fabricante
    manufacturer = url_db.infer_manufacturer_from_query(query)
    print(f"🔍 Query: {query}")
    print(f"🏭 Fabricante detectado: {manufacturer}")

    if manufacturer:
        # Pega domínio base
        base_domain = url_db.get_base_domain(manufacturer)
        print(f"🌐 Domínio base: {base_domain}")

        # Busca com fallback orchestrator
        result = orchestrator.search(
            base_domain=base_domain,
            product_name=query,
            manufacturer=manufacturer,
        )

        if result:
            print(f"✅ URL encontrada: {result.url}")
            print(f"📊 Score: {result.score:.3f}")
            print(f"🔧 Layer: {result.layer.value}")
        else:
            print("❌ Nenhuma URL encontrada")


def generate_domain_mapping_for_search_agent():
    """Gera mapeamento de domínios para SearchAgent."""
    workspace = Path(__file__).parent.parent
    database_path = workspace / "data" / "manufacturers_urls_database.json"

    url_db = ManufacturerURLDatabase(database_path)
    mapping = url_db.export_domain_mapping()

    print("\n# Domain mapping para SearchAgent._infer_domain()\n")
    print("MANUFACTURER_DOMAINS = {")
    for manufacturer, domain in sorted(mapping.items()):
        print(f'    "{manufacturer.upper()}": "{domain}",')
    print("}")


if __name__ == "__main__":
    # Testa integração
    print("=" * 80)
    print("🧪 Teste de Integração: URL Database + Fallback Orchestrator")
    print("=" * 80 + "\n")

    try:
        integrate_with_fallback_orchestrator()
    except Exception as e:
        print(f"⚠️  Erro na integração: {e}")

    print("\n" + "=" * 80)
    print("📋 Gerando mapeamento de domínios para SearchAgent")
    print("=" * 80)

    generate_domain_mapping_for_search_agent()
