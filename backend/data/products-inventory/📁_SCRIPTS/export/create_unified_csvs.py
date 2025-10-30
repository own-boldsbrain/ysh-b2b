#!/usr/bin/env python3
"""
Cria CSVs Unificados a partir do unified_products.json
Organiza por: Fabricantes, Modelos, Categorias, Comparação de Preços
"""
import json
import csv
import re
from pathlib import Path
from collections import defaultdict
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UnifiedCSVCreator:
    """Cria CSVs unificados a partir do JSON consolidado"""

    def __init__(self, json_path: Path, output_dir: Path):
        self.json_path = json_path
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.products = []
        self.by_manufacturer = defaultdict(list)
        self.by_category = defaultdict(list)
        self.by_model = defaultdict(list)

    def load_products(self):
        """Carrega produtos do JSON"""
        logger.info(f"📖 Carregando {self.json_path}...")

        with open(self.json_path, "r", encoding="utf-8") as f:
            self.products = json.load(f)

        logger.info(f"✅ {len(self.products)} produtos carregados")

    def index_products(self):
        """Indexa produtos por diferentes critérios"""
        logger.info("🔍 Indexando produtos...")

        for product in self.products:
            # Por distribuidor
            dist = product.get("distributor", "unknown")

            # Por fabricante
            components = product.get("components", {})

            # Painéis
            panels = components.get("panels", [])
            if panels and panels[0].get("manufacturer"):
                mfg = panels[0]["manufacturer"]
                self.by_manufacturer[mfg].append(product)

            # Inversores
            inverters = components.get("inverters", [])
            if inverters and inverters[0].get("manufacturer"):
                mfg = inverters[0]["manufacturer"]
                key = f"Inverter_{mfg}"
                self.by_manufacturer[key].append(product)

            # Baterias
            batteries = components.get("batteries", [])
            if batteries and batteries[0].get("manufacturer"):
                mfg = batteries[0]["manufacturer"]
                key = f"Battery_{mfg}"
                self.by_manufacturer[key].append(product)

            # Por categoria
            category = product.get("category", "unknown")
            self.by_category[category].append(product)

            # Por modelo (painel)
            if panels and panels[0].get("power_w"):
                power = panels[0]["power_w"]
                model_key = f"{power}W"
                self.by_model[model_key].append(product)

        logger.info(f"  {len(self.by_manufacturer)} fabricantes")
        logger.info(f"  {len(self.by_category)} categorias")
        logger.info(f"  {len(self.by_model)} modelos")

    def flatten_product(self, product):
        """Achata produto para CSV"""
        components = product.get("components", {})
        pricing = product.get("pricing", {})
        power = product.get("power", {})
        totals = product.get("totals", {})

        # Componentes
        panels = components.get("panels", [{}])
        panel = panels[0] if panels else {}

        inverters = components.get("inverters", [{}])
        inverter = inverters[0] if inverters else {}

        batteries = components.get("batteries", [{}])
        battery = batteries[0] if batteries else {}

        return {
            "id": product.get("id", ""),
            "name": product.get("name", ""),
            "distributor": product.get("distributor", ""),
            "category": product.get("category", ""),
            "type": product.get("type", ""),
            # Potência
            "power_kwp": power.get("kwp", ""),
            "power_watts": power.get("watts", ""),
            # Preços
            "price_brl": pricing.get("price_brl", ""),
            "price_per_wp": pricing.get("price_per_wp", ""),
            # Painéis
            "panel_manufacturer": panel.get("manufacturer", ""),
            "panel_power_w": panel.get("power_w", ""),
            "panel_quantity": panel.get("quantity", ""),
            # Inversores
            "inverter_manufacturer": inverter.get("manufacturer", ""),
            "inverter_power_kw": inverter.get("power_kw", ""),
            "inverter_quantity": inverter.get("quantity", ""),
            # Baterias
            "battery_manufacturer": battery.get("manufacturer", ""),
            "battery_capacity_kwh": battery.get("capacity_kwh", ""),
            "battery_voltage_v": battery.get("voltage_v", ""),
            "battery_quantity": battery.get("quantity", ""),
            # Totais
            "total_panels": totals.get("total_panels", 0),
            "total_inverters": totals.get("total_inverters", 0),
            "total_batteries": totals.get("total_batteries", 0),
        }

    def create_manufacturer_csvs(self):
        """CSVs por fabricante"""
        logger.info("\n📦 Criando CSVs por fabricante...")

        for mfg, products in self.by_manufacturer.items():
            if len(products) < 3:
                continue

            safe_name = mfg.replace(" ", "_").replace("/", "_")
            filename = f"manufacturer_{safe_name}.csv"
            filepath = self.output_dir / filename

            flat_products = [self.flatten_product(p) for p in products]
            self.write_csv(filepath, flat_products)

            logger.info(f"  ✓ {filename}: {len(products)} produtos")

    def create_category_csvs(self):
        """CSVs por categoria"""
        logger.info("\n📁 Criando CSVs por categoria...")

        for category, products in self.by_category.items():
            filename = f"category_{category}.csv"
            filepath = self.output_dir / filename

            flat_products = [self.flatten_product(p) for p in products]
            self.write_csv(filepath, flat_products)

            logger.info(f"  ✓ {filename}: {len(products)} produtos")

    def create_price_comparison_csv(self):
        """CSV com comparação de preços"""
        logger.info("\n💰 Criando comparação de preços...")

        # Agrupar por características similares
        groups = defaultdict(list)

        for product in self.products:
            components = product.get("components", {})
            panels = components.get("panels", [])
            inverters = components.get("inverters", [])

            if not panels or not inverters:
                continue

            panel = panels[0]
            inverter = inverters[0]

            # Chave: painel + inversor + potência
            key = (
                panel.get("manufacturer", ""),
                panel.get("power_w", 0),
                inverter.get("manufacturer", ""),
                product.get("power", {}).get("kwp", 0),
            )

            groups[key].append(product)

        # Criar comparação
        comparison = []

        for key, products in groups.items():
            if len(products) < 2:
                continue

            panel_mfg, panel_w, inv_mfg, kwp = key

            row = {
                "panel_manufacturer": panel_mfg,
                "panel_power_w": panel_w,
                "inverter_manufacturer": inv_mfg,
                "system_kwp": kwp,
                "distributors_count": len(products),
            }

            # Preços por distribuidor
            for p in products:
                dist = p["distributor"]
                price = p.get("pricing", {}).get("price_brl", 0)
                row[f"price_{dist}"] = price
                row[f"id_{dist}"] = p["id"]

            # Estatísticas
            prices = [
                p.get("pricing", {}).get("price_brl", 0)
                for p in products
                if p.get("pricing", {}).get("price_brl", 0) > 0
            ]

            if prices:
                row["min_price"] = min(prices)
                row["max_price"] = max(prices)
                row["avg_price"] = sum(prices) / len(prices)
                row["price_diff"] = max(prices) - min(prices)
                row["price_diff_pct"] = (
                    (max(prices) - min(prices)) / min(prices) * 100
                    if min(prices) > 0
                    else 0
                )

            comparison.append(row)

        # Ordenar por diferença de preço
        comparison.sort(key=lambda x: x.get("price_diff_pct", 0), reverse=True)

        filepath = self.output_dir / "price_comparison_multi_distributor.csv"

        if comparison:
            fields = set()
            for row in comparison:
                fields.update(row.keys())

            fieldnames = sorted(fields)

            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(comparison)

            logger.info(
                f"  ✓ price_comparison_multi_distributor.csv: "
                f"{len(comparison)} grupos"
            )

    def create_panel_models_csv(self):
        """CSV de modelos de painéis"""
        logger.info("\n☀️  Criando CSV de modelos de painéis...")

        panel_models = defaultdict(list)

        for product in self.products:
            panels = product.get("components", {}).get("panels", [])
            if not panels:
                continue

            for panel in panels:
                mfg = panel.get("manufacturer", "")
                power = panel.get("power_w", 0)

                if mfg and power:
                    key = (mfg, power)
                    panel_models[key].append(product)

        # Criar CSV
        rows = []
        for (mfg, power), products in panel_models.items():
            prices = [
                p.get("pricing", {}).get("price_brl", 0)
                / p.get("totals", {}).get("total_panels", 1)
                for p in products
                if p.get("pricing", {}).get("price_brl", 0) > 0
                and p.get("totals", {}).get("total_panels", 0) > 0
            ]

            if prices:
                row = {
                    "manufacturer": mfg,
                    "power_w": power,
                    "kits_count": len(products),
                    "distributors": "|".join(set(p["distributor"] for p in products)),
                    "avg_price_per_panel": sum(prices) / len(prices),
                    "min_price_per_panel": min(prices),
                    "max_price_per_panel": max(prices),
                }
                rows.append(row)

        # Ordenar por fabricante e potência
        rows.sort(key=lambda x: (x["manufacturer"], x["power_w"]))

        filepath = self.output_dir / "panel_models_pricing.csv"

        if rows:
            fields = [
                "manufacturer",
                "power_w",
                "kits_count",
                "distributors",
                "avg_price_per_panel",
                "min_price_per_panel",
                "max_price_per_panel",
            ]

            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)

            logger.info(f"  ✓ panel_models_pricing.csv: {len(rows)} modelos")

    def write_csv(self, filepath, products):
        """Escreve CSV"""
        if not products:
            return

        fields = set()
        for p in products:
            fields.update(p.keys())

        fieldnames = sorted(fields)

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)

    def create_all_csvs(self):
        """Cria todos os CSVs"""
        self.load_products()
        self.index_products()

        self.create_manufacturer_csvs()
        self.create_category_csvs()
        self.create_price_comparison_csv()
        self.create_panel_models_csv()

        # Master CSV
        logger.info("\n📊 Criando CSV mestre...")
        filepath = self.output_dir / "all_products_unified.csv"
        flat_products = [self.flatten_product(p) for p in self.products]
        self.write_csv(filepath, flat_products)
        logger.info(f"  ✓ all_products_unified.csv: {len(self.products)} produtos")

        logger.info(f"\n✅ CSVs salvos em: {self.output_dir}")


def main():
    base_path = Path(__file__).parent
    json_path = base_path / "unified_products.json"
    output_dir = base_path / "exports" / "unified"

    if not json_path.exists():
        logger.error(f"❌ {json_path} não encontrado!")
        return

    creator = UnifiedCSVCreator(json_path, output_dir)
    creator.create_all_csvs()


if __name__ == "__main__":
    main()
