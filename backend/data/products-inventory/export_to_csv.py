#!/usr/bin/env python3
"""
High-Performance CSV Export - YSH Solar Inventory
Converte unified_products.json em CSVs otimizados por categoria
"""
import json
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OptimizedCSVExporter:
    """Exportador otimizado com processamento em streaming e cache eficiente"""

    def __init__(self, json_file: Path, output_dir: Path):
        self.json_file = json_file
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Cache para evitar reprocessamento
        self.category_cache = defaultdict(list)

    def flatten_product(self, product: Dict) -> Dict:
        """Achata estrutura JSON para CSV com campos relevantes"""
        flat = {
            "id": product.get("id", ""),
            "name": product.get("name", ""),
            "distributor": product.get("distributor", ""),
            "category": product.get("category", ""),
            "type": product.get("type", ""),
            # Power
            "power_kwp": product.get("power", {}).get("kwp", ""),
            "power_watts": product.get("power", {}).get("watts", ""),
            # Pricing
            "price_brl": product.get("pricing", {}).get("price_brl", ""),
            "price_per_wp": product.get("pricing", {}).get("price_per_wp", ""),
            "currency": product.get("pricing", {}).get("currency", "BRL"),
            # Components summary
            "total_panels": product.get("totals", {}).get("total_panels", 0),
            "total_inverters": product.get("totals", {}).get("total_inverters", 0),
            "total_batteries": product.get("totals", {}).get("total_batteries", 0),
            "total_structures": product.get("totals", {}).get("total_structures", 0),
            # Metadata
            "source_csv": product.get("metadata", {}).get("source_csv", ""),
            "status": product.get("metadata", {}).get("status", ""),
            # Media
            "image_url": product.get("media", {}).get("image_url", ""),
            # Tags (convertido para string)
            "tags": "|".join(product.get("tags", [])),
        }

        # Adicionar informações de componentes específicos
        components = product.get("components", {})

        # Painéis
        panels = components.get("panels", [])
        if panels:
            panel = panels[0]  # Primeiro painel
            flat["panel_manufacturer"] = panel.get("manufacturer", "")
            flat["panel_power_w"] = panel.get("power_w", "")
            flat["panel_quantity"] = panel.get("quantity", "")
            flat["panel_image"] = panel.get("image", "")
        else:
            flat["panel_manufacturer"] = ""
            flat["panel_power_w"] = ""
            flat["panel_quantity"] = ""
            flat["panel_image"] = ""

        # Inversores
        inverters = components.get("inverters", [])
        if inverters:
            inverter = inverters[0]  # Primeiro inversor
            flat["inverter_manufacturer"] = inverter.get("manufacturer", "")
            flat["inverter_power_kw"] = inverter.get("power_kw", "")
            flat["inverter_quantity"] = inverter.get("quantity", "")
            flat["inverter_image"] = inverter.get("image", "")
        else:
            flat["inverter_manufacturer"] = ""
            flat["inverter_power_kw"] = ""
            flat["inverter_quantity"] = ""
            flat["inverter_image"] = ""

        # Baterias
        batteries = components.get("batteries", [])
        if batteries:
            battery = batteries[0]  # Primeira bateria
            flat["battery_manufacturer"] = battery.get("manufacturer", "")
            flat["battery_capacity_kwh"] = battery.get("capacity_kwh", "")
            flat["battery_voltage_v"] = battery.get("voltage_v", "")
            flat["battery_quantity"] = battery.get("quantity", "")
        else:
            flat["battery_manufacturer"] = ""
            flat["battery_capacity_kwh"] = ""
            flat["battery_voltage_v"] = ""
            flat["battery_quantity"] = ""

        return flat

    def process_products_streaming(self):
        """Processa produtos em streaming para otimizar memória"""
        logger.info(f"📖 Carregando produtos de {self.json_file}...")

        with open(self.json_file, "r", encoding="utf-8") as f:
            products = json.load(f)

        logger.info(f"✅ {len(products)} produtos carregados")

        # Agrupar por categoria E por tipos especiais
        for idx, product in enumerate(products, 1):
            if idx % 500 == 0:
                logger.info(f"   Processando produto {idx}/{len(products)}...")

            # Categoria padrão
            category = product.get("category", "unknown")
            flat_product = self.flatten_product(product)
            self.category_cache[category].append(flat_product)

            # Categorias adicionais baseadas em componentes/características
            components = product.get("components", {})
            name_lower = product.get("name", "").lower()

            # Produtos com baterias
            if components.get("batteries", []):
                self.category_cache["products_with_batteries"].append(flat_product)

            # Carregadores (EV ou outros)
            if any(
                word in name_lower for word in ["carregador", "charger", "charging"]
            ):
                self.category_cache["chargers"].append(flat_product)

            # Cabos
            if any(word in name_lower for word in ["cabo", "cable", "wire"]):
                self.category_cache["cables"].append(flat_product)

            # Acessórios
            if any(
                word in name_lower
                for word in [
                    "acessório",
                    "accessory",
                    "mounting",
                    "structure",
                    "conector",
                    "connector",
                ]
            ):
                self.category_cache["accessories"].append(flat_product)

        logger.info(f"✅ Produtos agrupados em {len(self.category_cache)} categorias")
        return self.category_cache

    def export_category_to_csv(self, category: str, products: List[Dict]):
        """Exporta uma categoria para CSV com encoding otimizado"""
        if not products:
            logger.warning(f"⚠️  Categoria '{category}' vazia, ignorando...")
            return

        csv_file = self.output_dir / f"{category}.csv"
        logger.info(f"📝 Exportando {len(products)} produtos para {csv_file.name}...")

        # Obter todos os campos únicos (união de todos os produtos)
        all_fields = set()
        for product in products:
            all_fields.update(product.keys())

        fieldnames = sorted(all_fields)

        # Escrever CSV
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(products)

        logger.info(f"✅ {csv_file.name} criado com {len(products)} linhas")

    def export_all_categories(self):
        """Exporta todas as categorias para CSVs separados"""
        logger.info("🚀 Iniciando exportação para CSV...")

        # Processar produtos
        categories = self.process_products_streaming()

        # Exportar cada categoria
        for category, products in categories.items():
            self.export_category_to_csv(category, products)

        # Criar CSV consolidado (todos os produtos)
        logger.info("📦 Criando CSV consolidado...")
        all_products = []
        for products in categories.values():
            all_products.extend(products)

        consolidated_file = self.output_dir / "all_products.csv"
        if all_products:
            fieldnames = sorted(set().union(*[set(p.keys()) for p in all_products]))
            with open(consolidated_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(all_products)
            logger.info(
                f"✅ {consolidated_file.name} criado com {len(all_products)} linhas"
            )

        # Sumário
        logger.info("\n" + "=" * 80)
        logger.info("📊 SUMÁRIO DA EXPORTAÇÃO")
        logger.info("=" * 80)
        for category, products in sorted(categories.items()):
            logger.info(f"  {category:20s}: {len(products):5d} produtos")
        logger.info(f"  {'TOTAL':20s}: {len(all_products):5d} produtos")
        logger.info("=" * 80)
        logger.info(f"✅ Exportação concluída! Arquivos salvos em: {self.output_dir}")


def main():
    """Função principal"""
    base_path = Path(__file__).parent
    json_file = base_path / "unified_products.json"
    output_dir = base_path / "exports" / "csv"

    if not json_file.exists():
        logger.error(f"❌ Arquivo {json_file} não encontrado!")
        return

    exporter = OptimizedCSVExporter(json_file, output_dir)
    exporter.export_all_categories()


if __name__ == "__main__":
    main()
