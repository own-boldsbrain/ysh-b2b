#!/usr/bin/env python3
"""
Unificador de Produtos Multi-Distribuidores
Varre todos os CSVs dos distribuidores e cria CSVs unificados por:
- Fabricantes
- Produtos
- Modelos
- Séries
- Múltiplos preços por distribuidor
"""
import json
import csv
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DistributorUnifier:
    """Unifica produtos de múltiplos distribuidores"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.distributors_path = base_path / "distributors"
        self.output_dir = base_path / "exports" / "unified"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Estruturas de dados para unificação
        self.products_by_manufacturer = defaultdict(list)
        self.products_by_model = defaultdict(list)
        self.products_by_category = defaultdict(list)
        self.all_products = []

    def normalize_manufacturer(self, name: str) -> str:
        """Normaliza nome de fabricante"""
        if not name:
            return "Unknown"

        # Mapeamento de fabricantes conhecidos
        mappings = {
            "growatt": "Growatt",
            "longi": "Longi",
            "canadian": "Canadian Solar",
            "jinko": "JinkoSolar",
            "ja solar": "JA Solar",
            "deye": "Deye",
            "saj": "SAJ",
            "sungrow": "Sungrow",
            "huawei": "Huawei",
            "fronius": "Fronius",
            "sma": "SMA",
            "weg": "WEG",
            "intelbras": "Intelbras",
        }

        name_lower = name.lower().strip()
        for key, value in mappings.items():
            if key in name_lower:
                return value

        return name.strip().title()

    def extract_power(self, text: str) -> float:
        """Extrai potência de strings variadas"""
        if not text:
            return 0.0

        # Padrões: 550W, 550wp, 5.5kW, 5.5kWp
        patterns = [
            r"(\d+\.?\d*)\s*kwp?",
            r"(\d+\.?\d*)\s*kw",
            r"(\d+)\s*wp?",
            r"(\d+)\s*w\b",
        ]

        text_lower = str(text).lower()

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = float(match.group(1))
                if "kw" in pattern:
                    return value * 1000
                return value

        return 0.0

    def parse_csv_file(self, csv_path: Path, distributor: str) -> List[Dict]:
        """Parse individual CSV file"""
        products = []

        try:
            with open(csv_path, "r", encoding="utf-8-sig") as f:
                # Tentar detectar delimiter
                sample = f.read(4096)
                f.seek(0)

                sniffer = csv.Sniffer()
                try:
                    dialect = sniffer.sniff(sample)
                    delimiter = dialect.delimiter
                except:
                    delimiter = ","

                reader = csv.DictReader(f, delimiter=delimiter)

                for row in reader:
                    # Normalizar chaves
                    normalized_row = {
                        k.strip().lower(): v.strip() if v else ""
                        for k, v in row.items()
                    }

                    # Extrair dados essenciais
                    product = self.extract_product_data(
                        normalized_row, distributor, csv_path.name
                    )

                    if product:
                        products.append(product)

        except Exception as e:
            logger.warning(f"Erro ao processar {csv_path.name}: {e}")

        return products

    def extract_product_data(
        self, row: Dict, distributor: str, source_file: str
    ) -> Dict:
        """Extrai dados do produto de uma linha CSV"""

        # Tentar encontrar campos comuns com variações
        name = (
            row.get("name")
            or row.get("nome")
            or row.get("produto")
            or row.get("description")
            or row.get("descrição")
            or row.get("title")
            or ""
        )

        if not name:
            return None

        # Preço
        price = (
            row.get("price")
            or row.get("preço")
            or row.get("preco")
            or row.get("valor")
            or row.get("price_brl")
            or "0"
        )

        # Limpar preço
        price_clean = re.sub(r"[^\d,.]", "", str(price))
        price_clean = price_clean.replace(",", ".")

        try:
            price_value = float(price_clean) if price_clean else 0.0
        except:
            price_value = 0.0

        # SKU/Código
        sku = (
            row.get("sku")
            or row.get("código")
            or row.get("codigo")
            or row.get("code")
            or row.get("id")
            or ""
        )

        # Categoria
        category = (
            row.get("category")
            or row.get("categoria")
            or row.get("type")
            or row.get("tipo")
            or self.infer_category(name)
        )

        # Fabricante
        manufacturer = (
            row.get("manufacturer")
            or row.get("fabricante")
            or row.get("marca")
            or row.get("brand")
            or self.extract_manufacturer_from_name(name)
        )

        # Potência
        power_field = (
            row.get("power")
            or row.get("potência")
            or row.get("potencia")
            or row.get("power_w")
            or row.get("watts")
            or ""
        )

        power = self.extract_power(power_field or name)

        # Modelo
        model = (
            row.get("model") or row.get("modelo") or self.extract_model_from_name(name)
        )

        return {
            "name": name,
            "sku": sku,
            "manufacturer": self.normalize_manufacturer(manufacturer),
            "model": model,
            "category": category,
            "power_w": power,
            "distributor": distributor,
            "price_brl": price_value,
            "source_file": source_file,
            # Campos originais para referência
            "original_data": row,
        }

    def infer_category(self, name: str) -> str:
        """Infere categoria baseado no nome"""
        name_lower = name.lower()

        if any(word in name_lower for word in ["kit", "sistema"]):
            return "kits"
        elif any(
            word in name_lower for word in ["painel", "panel", "módulo", "modulo"]
        ):
            return "panels"
        elif any(word in name_lower for word in ["inversor", "inverter"]):
            return "inverters"
        elif any(word in name_lower for word in ["bateria", "battery"]):
            return "batteries"
        elif any(word in name_lower for word in ["carregador", "charger"]):
            return "chargers"
        elif any(word in name_lower for word in ["estrutura", "structure", "suporte"]):
            return "structures"
        elif any(word in name_lower for word in ["cabo", "cable"]):
            return "cables"
        elif any(word in name_lower for word in ["string", "caixa"]):
            return "stringboxes"

        return "accessories"

    def extract_manufacturer_from_name(self, name: str) -> str:
        """Extrai fabricante do nome do produto"""
        manufacturers = [
            "Growatt",
            "Longi",
            "Canadian",
            "JinkoSolar",
            "JA Solar",
            "Deye",
            "SAJ",
            "Sungrow",
            "Huawei",
            "Fronius",
            "SMA",
            "WEG",
            "Intelbras",
            "Hoymiles",
            "Sofar",
            "GoodWe",
            "Risen",
            "Trina",
            "BYD",
            "Pylontech",
        ]

        name_lower = name.lower()
        for mfg in manufacturers:
            if mfg.lower() in name_lower:
                return mfg

        return "Unknown"

    def extract_model_from_name(self, name: str) -> str:
        """Extrai modelo do nome"""
        # Padrões comuns de modelos
        patterns = [
            r"([A-Z]{2,}-?\d+[A-Z]*)",
            r"(NEO-?\d+[A-Z]*)",
            r"(MIC-?\d+)",
            r"([A-Z]+-\d+[A-Z]*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, name)
            if match:
                return match.group(1)

        return ""

    def scan_all_distributors(self):
        """Varre todos os distribuidores"""
        logger.info("🔍 Varrendo distribuidores...")

        distributors = [
            "fortlev",
            "fotus",
            "meugerador",
            "neosolar",
            "odex",
            "solfacil",
        ]

        total_products = 0

        for distributor in distributors:
            dist_path = self.distributors_path / distributor
            if not dist_path.exists():
                logger.warning(f"⚠️  Distribuidor {distributor} não encontrado")
                continue

            logger.info(f"\n📂 Processando {distributor}...")

            # Encontrar todos os CSVs
            csv_files = list(dist_path.glob("*.csv"))
            csv_files += list(dist_path.glob("**/*.csv"))

            dist_count = 0
            for csv_file in csv_files:
                if "backup" in str(csv_file):
                    continue

                products = self.parse_csv_file(csv_file, distributor)
                dist_count += len(products)
                total_products += len(products)

                # Adicionar aos índices
                for product in products:
                    self.all_products.append(product)

                    mfg = product["manufacturer"]
                    self.products_by_manufacturer[mfg].append(product)

                    model = product["model"]
                    if model:
                        self.products_by_model[model].append(product)

                    category = product["category"]
                    self.products_by_category[category].append(product)

                logger.info(f"  ✓ {csv_file.name}: {len(products)} produtos")

            logger.info(f"  Total {distributor}: {dist_count} produtos")

        logger.info(f"\n✅ Total geral: {total_products} produtos")
        return total_products

    def create_unified_csvs(self):
        """Cria CSVs unificados"""
        logger.info("\n📊 Criando CSVs unificados...")

        # 1. Por fabricante
        self.create_manufacturer_csvs()

        # 2. Por categoria
        self.create_category_csvs()

        # 3. Por modelo (top modelos)
        self.create_model_csvs()

        # 4. Consolidado com preços múltiplos
        self.create_price_comparison_csv()

        # 5. CSV completo
        self.create_master_csv()

    def create_manufacturer_csvs(self):
        """CSV por fabricante"""
        logger.info("  Criando CSVs por fabricante...")

        for mfg, products in self.products_by_manufacturer.items():
            if mfg == "Unknown" or len(products) < 5:
                continue

            filename = f"manufacturer_{mfg.lower().replace(' ', '_')}.csv"
            filepath = self.output_dir / filename

            self.write_csv(filepath, products)
            logger.info(f"    ✓ {filename}: {len(products)} produtos")

    def create_category_csvs(self):
        """CSV por categoria"""
        logger.info("  Criando CSVs por categoria...")

        for category, products in self.products_by_category.items():
            filename = f"category_{category}.csv"
            filepath = self.output_dir / filename

            self.write_csv(filepath, products)
            logger.info(f"    ✓ {filename}: {len(products)} produtos")

    def create_model_csvs(self):
        """CSV dos principais modelos"""
        logger.info("  Criando CSVs de top modelos...")

        # Top 20 modelos mais presentes
        sorted_models = sorted(
            self.products_by_model.items(), key=lambda x: len(x[1]), reverse=True
        )[:20]

        for model, products in sorted_models:
            filename = f"model_{model.replace('/', '_')}.csv"
            filepath = self.output_dir / filename

            self.write_csv(filepath, products)
            logger.info(f"    ✓ {filename}: {len(products)} produtos")

    def create_price_comparison_csv(self):
        """CSV com comparação de preços entre distribuidores"""
        logger.info("  Criando comparação de preços...")

        # Agrupar por produto similar
        product_groups = defaultdict(list)

        for product in self.all_products:
            # Chave: fabricante + modelo + potência
            key = (product["manufacturer"], product["model"], product["power_w"])
            product_groups[key].append(product)

        # Criar CSV com múltiplos preços
        comparison_data = []

        for key, products in product_groups.items():
            if len(products) < 2:  # Só produtos em múltiplos distribuidores
                continue

            mfg, model, power = key

            row = {
                "manufacturer": mfg,
                "model": model,
                "power_w": power,
                "category": products[0]["category"],
                "distributors_count": len(set(p["distributor"] for p in products)),
            }

            # Adicionar preços por distribuidor
            for product in products:
                dist = product["distributor"]
                price = product["price_brl"]
                row[f"price_{dist}"] = price
                row[f"sku_{dist}"] = product["sku"]

            comparison_data.append(row)

        filepath = self.output_dir / "price_comparison.csv"

        if comparison_data:
            # Obter todos os campos
            all_fields = set()
            for row in comparison_data:
                all_fields.update(row.keys())

            fieldnames = sorted(all_fields)

            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(comparison_data)

            logger.info(f"    ✓ price_comparison.csv: {len(comparison_data)} produtos")

    def create_master_csv(self):
        """CSV mestre com todos os produtos"""
        logger.info("  Criando CSV mestre...")

        filepath = self.output_dir / "all_distributors_unified.csv"
        self.write_csv(filepath, self.all_products)

        logger.info(
            f"    ✓ all_distributors_unified.csv: {len(self.all_products)} produtos"
        )

    def write_csv(self, filepath: Path, products: List[Dict]):
        """Escreve produtos em CSV"""
        if not products:
            return

        # Campos para exportar
        fields = [
            "name",
            "sku",
            "manufacturer",
            "model",
            "category",
            "power_w",
            "distributor",
            "price_brl",
            "source_file",
        ]

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(products)

    def generate_summary(self):
        """Gera sumário da unificação"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 SUMÁRIO DA UNIFICAÇÃO")
        logger.info("=" * 80)

        logger.info(f"\n🏭 FABRICANTES ({len(self.products_by_manufacturer)}):")
        for mfg, products in sorted(
            self.products_by_manufacturer.items(), key=lambda x: len(x[1]), reverse=True
        )[:10]:
            logger.info(f"  {mfg:20s}: {len(products):5d} produtos")

        logger.info(f"\n📦 CATEGORIAS ({len(self.products_by_category)}):")
        for cat, products in sorted(
            self.products_by_category.items(), key=lambda x: len(x[1]), reverse=True
        ):
            logger.info(f"  {cat:20s}: {len(products):5d} produtos")

        logger.info(f"\n🎯 TOP MODELOS:")
        sorted_models = sorted(
            self.products_by_model.items(), key=lambda x: len(x[1]), reverse=True
        )[:10]
        for model, products in sorted_models:
            logger.info(f"  {model:20s}: {len(products):5d} produtos")

        logger.info("\n" + "=" * 80)
        logger.info(f"✅ Arquivos salvos em: {self.output_dir}")
        logger.info("=" * 80)


def main():
    """Função principal"""
    base_path = Path(__file__).parent

    unifier = DistributorUnifier(base_path)

    # Varrer todos os distribuidores
    total = unifier.scan_all_distributors()

    if total == 0:
        logger.error("❌ Nenhum produto encontrado!")
        return

    # Criar CSVs unificados
    unifier.create_unified_csvs()

    # Gerar sumário
    unifier.generate_summary()


if __name__ == "__main__":
    main()
