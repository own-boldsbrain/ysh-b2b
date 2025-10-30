"""
Unified Product Extractor - YSH Solar Inventory
Extrai e padroniza produtos de todos os distribuidores conforme o blueprint unificado.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any


class UnifiedProductExtractor:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.distributors = ["fortlev", "fotus", "neosolar", "odex", "solfacil"]
        self.unified_products = []

    def load_json_file(self, file_path: Path) -> List[Dict]:
        """Carrega um arquivo JSON e retorna a lista de produtos."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        except Exception as e:
            print(f"Erro ao carregar {file_path}: {e}")
            return []

    def standardize_fotus_product(self, product: Dict) -> Dict:
        """Padroniza produto do Fotus."""
        return {
            "id": product.get("id", ""),
            "name": product.get("name", ""),
            "distributor": "Fotus",
            "category": "kits",
            "type": product.get("type", ""),
            "power": {
                "kwp": product.get("potencia_kwp", 0),
                "watts": product.get("total_power_w", 0),
            },
            "pricing": {"price_brl": product.get("price_brl", 0), "currency": "BRL"},
            "components": {
                "panels": product.get("panels", []),
                "inverters": product.get("inverters", []),
                "batteries": product.get("batteries", []),
                "structures": product.get("structures", []),
            },
            "totals": {
                "total_panels": product.get("total_panels", 0),
                "total_inverters": product.get("total_inverters", 0),
                "total_batteries": len(product.get("batteries", [])),
                "total_structures": len(product.get("structures", [])),
                "total_power_w": product.get("total_power_w", 0),
            },
            "metadata": {
                "centro_distribuicao": product.get("centro_distribuicao", ""),
                "estrutura": product.get("estrutura", ""),
                "status": "published",
            },
            "media": {
                "image_url": product.get("image_url", ""),
                "processed_images": product.get("processed_images", {}),
                "image_quality_before": product.get("image_quality_before", 0),
                "image_quality_after": product.get("image_quality_after", 0),
            },
            "description": product.get("name", ""),
            "tags": ["Solar Kit", "Fotus"],
        }

    def standardize_fortlev_product(self, product: Dict) -> Dict:
        """Padroniza produto do Fortlev."""
        return {
            "id": product.get("id", ""),
            "name": product.get("name", ""),
            "distributor": "Fortlev",
            "category": product.get("category", "kits"),
            "type": product.get("type", ""),
            "power": {
                "kwp": product.get("system_power_kwp", 0),
                "watts": product.get("system_power_kwp", 0) * 1000,
            },
            "pricing": {
                "price_brl": product.get("pricing", {}).get("total", 0),
                "price_per_wp": product.get("price_per_wp", 0),
                "currency": "BRL",
            },
            "components": {
                "panels": (
                    [product.get("components", {}).get("panel", {})]
                    if product.get("components", {}).get("panel")
                    else []
                ),
                "inverters": (
                    [product.get("components", {}).get("inverter", {})]
                    if product.get("components", {}).get("inverter")
                    else []
                ),
                "batteries": [],
                "structures": [],
            },
            "totals": {
                "total_panels": 1 if product.get("components", {}).get("panel") else 0,
                "total_inverters": (
                    1 if product.get("components", {}).get("inverter") else 0
                ),
                "total_batteries": 0,
                "total_structures": 0,
                "total_power_w": product.get("system_power_kwp", 0) * 1000,
            },
            "metadata": {
                "source_csv": product.get("metadata", {}).get("source_csv", ""),
                "status": product.get("status", "draft"),
            },
            "media": {"image_url": "", "processed_images": {}},
            "description": product.get("description", ""),
            "tags": product.get("tags", []),
        }

    def standardize_neosolar_product(self, product: Dict) -> Dict:
        """Padroniza produto do Neosolar."""
        return {
            "id": product.get("id", ""),
            "name": product.get("name", ""),
            "distributor": "Neosolar",
            "category": "kits",
            "type": product.get("type", ""),
            "power": {
                "kwp": product.get("potencia_kwp", 0),
                "watts": product.get("total_power_w", 0),
            },
            "pricing": {"price_brl": product.get("price_brl", 0), "currency": "BRL"},
            "components": {
                "panels": product.get("panels", []),
                "inverters": product.get("inverters", []),
                "batteries": product.get("batteries", []),
                "structures": [],
            },
            "totals": {
                "total_panels": product.get("total_panels", 0),
                "total_inverters": product.get("total_inverters", 0),
                "total_batteries": product.get("total_batteries", 0),
                "total_structures": 0,
                "total_power_w": product.get("total_power_w", 0),
            },
            "metadata": {"status": product.get("status", "draft")},
            "media": {
                "image_url": product.get("image_url", ""),
                "processed_images": {},
            },
            "description": product.get("description_short", ""),
            "tags": ["Solar Kit", "Neosolar"],
        }

    def standardize_solfacil_product(self, product: Dict) -> Dict:
        """Padroniza produto do Solfacil (foco em painéis)."""
        return {
            "id": product.get("id", ""),
            "name": product.get("name", ""),
            "distributor": "Solfacil",
            "category": "panels",
            "type": "Solar Panel",
            "power": {"kwp": 0, "watts": 0},  # Não disponível nos dados
            "pricing": {
                "price_brl": 0,  # Preço não numérico nos dados
                "currency": "BRL",
            },
            "components": {
                "panels": [
                    {
                        "brand": product.get("manufacturer", ""),
                        "description": product.get("description", ""),
                        "quantity": 1,
                    }
                ],
                "inverters": [],
                "batteries": [],
                "structures": [],
            },
            "totals": {
                "total_panels": 1,
                "total_inverters": 0,
                "total_batteries": 0,
                "total_structures": 0,
                "total_power_w": 0,
            },
            "metadata": {
                "availability": product.get("availability", ""),
                "status": "published",
            },
            "media": {"image_url": product.get("image", ""), "processed_images": {}},
            "description": product.get("price", ""),  # Campo price contém descrição
            "tags": ["Solar Panel", "Solfacil"],
        }

    def extract_distributor_products(self, distributor: str) -> List[Dict]:
        """Extrai produtos de um distribuidor específico."""
        distributor_path = self.base_path / "distributors" / distributor
        products = []

        if not distributor_path.exists():
            return products

        # Mapeia arquivos principais por distribuidor
        file_map = {
            "fotus": ["fotus-kits.json", "fotus-kits-hibridos.json"],
            "fortlev": ["fortlev-kits.json"],
            "neosolar": ["neosolar-kits-normalized.json"],
            "solfacil": [
                "solfacil-panels.json",
                "solfacil-inverters.json",
                "solfacil-batteries.json",
            ],
            "odex": [],  # Nenhum JSON processado encontrado
        }

        for filename in file_map.get(distributor, []):
            file_path = distributor_path / filename
            if file_path.exists():
                raw_products = self.load_json_file(file_path)
                for product in raw_products:
                    if distributor == "fotus":
                        standardized = self.standardize_fotus_product(product)
                    elif distributor == "fortlev":
                        standardized = self.standardize_fortlev_product(product)
                    elif distributor == "neosolar":
                        standardized = self.standardize_neosolar_product(product)
                    elif distributor == "solfacil":
                        standardized = self.standardize_solfacil_product(product)
                    else:
                        continue

                    products.append(standardized)

        return products

    def extract_all_products(self) -> List[Dict]:
        """Extrai todos os produtos de todos os distribuidores."""
        all_products = []
        for distributor in self.distributors:
            print(f"Extraindo produtos de {distributor}...")
            products = self.extract_distributor_products(distributor)
            all_products.extend(products)
            print(f"  {len(products)} produtos extraídos de {distributor}")

        self.unified_products = all_products
        return all_products

    def save_unified_products(self, output_path: Path):
        """Salva os produtos unificados em um arquivo JSON."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.unified_products, f, ensure_ascii=False, indent=2)
        print(f"Produtos unificados salvos em {output_path}")


def main():
    base_path = Path(
        r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory"
    )

    extractor = UnifiedProductExtractor(str(base_path))
    products = extractor.extract_all_products()

    output_path = base_path / "unified_products.json"
    extractor.save_unified_products(output_path)

    print("\nResumo da Extração Unificada:")
    print(f"Total de produtos: {len(products)}")
    distributors_count = {}
    for p in products:
        dist = p["distributor"]
        distributors_count[dist] = distributors_count.get(dist, 0) + 1

    for dist, count in distributors_count.items():
        print(f"  {dist}: {count} produtos")


if __name__ == "__main__":
    main()
