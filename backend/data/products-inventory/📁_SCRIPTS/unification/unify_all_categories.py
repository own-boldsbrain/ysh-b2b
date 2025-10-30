#!/usr/bin/env python3
"""
Unificador Completo de Produtos por Categoria
Processa todos os JSONs dos distribuidores e cria CSVs unificados
"""

import json
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
from datetime import datetime


class CompleteCatalogUnifier:
    """Unificador completo do catálogo por categorias"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.distributors_dir = base_dir / "distributors"
        self.output_dir = base_dir / "exports" / "unified_categories"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Mapeamento de categorias
        self.categories_map = {
            "inverters": {
                "files": [
                    "fortlev-inverters.json",
                    "solfacil-inverters.json",
                    "odex-inverters.json",
                ],
                "name": "Inversores",
            },
            "hybrid_inverters": {
                "files": ["fortlev-hybrid_inverters.json"],
                "name": "Inversores Híbridos",
            },
            "microinverters": {
                "files": ["fortlev-microinverters.json"],
                "name": "Microinversores",
            },
            "panels": {
                "files": [
                    "fortlev-panels.json",
                    "solfacil-panels.json",
                    "odex-panels.json",
                ],
                "name": "Painéis Solares",
            },
            "batteries": {
                "files": ["fortlev-batteries.json", "solfacil-batteries.json"],
                "name": "Baterias",
            },
            "structures": {
                "files": [
                    "fortlev-structures.json",
                    "solfacil-structures.json",
                    "odex-structures.json",
                ],
                "name": "Estruturas de Fixação",
            },
            "cables": {"files": ["solfacil-cables.json"], "name": "Cabos e Conectores"},
            "stringboxes": {
                "files": ["fortlev-stringboxes.json", "odex-stringboxes.json"],
                "name": "String Boxes",
            },
            "accessories": {
                "files": ["fortlev-accessories.json", "solfacil-accessories.json"],
                "name": "Acessórios",
            },
            "ev_chargers": {
                "files": ["fortlev-ev_chargers.json"],
                "name": "Carregadores EV",
            },
            "boxes": {"files": ["fortlev-boxes.json"], "name": "Caixas e Quadros"},
            "conduits": {"files": ["fortlev-conduits.json"], "name": "Eletrodutos"},
            "security": {"files": ["fortlev-security.json"], "name": "Segurança"},
            "transformers": {
                "files": ["fortlev-transformers.json"],
                "name": "Transformadores",
            },
            "miscellaneous": {
                "files": ["fortlev-miscellaneous.json"],
                "name": "Diversos",
            },
        }

        self.stats = defaultdict(int)

    def extract_distributor(self, file_path: Path) -> str:
        """Extrai nome do distribuidor do caminho do arquivo"""
        parts = file_path.parts
        if "fortlev" in parts:
            return "Fortlev"
        elif "solfacil" in parts:
            return "Solfacil"
        elif "odex" in parts:
            return "Odex"
        elif "fotus" in parts:
            return "Fotus"
        elif "neosolar" in parts:
            return "NeoSolar"
        return "Unknown"

    def flatten_product(
        self, product: Dict[str, Any], distributor: str
    ) -> Dict[str, Any]:
        """Achata estrutura do produto para CSV"""
        flat = {
            "distributor": distributor,
            "id": product.get("id", ""),
            "name": product.get("name", ""),
            "manufacturer": product.get("manufacturer", ""),
            "model": product.get("model", ""),
            "sku": product.get("sku", ""),
            "category": product.get("category", ""),
            "type": product.get("type", ""),
        }

        # Pricing
        pricing = product.get("pricing", {})
        flat["price_brl"] = pricing.get("price_brl", "")
        flat["currency"] = pricing.get("currency", "BRL")
        flat["price_per_unit"] = pricing.get("price_per_unit", "")

        # Specifications técnicas
        specs = product.get("specifications", {})

        # Power (para inversores, painéis)
        if "power" in product:
            power = product["power"]
            flat["power_kw"] = power.get(
                "kw", power.get("watts", 0) / 1000 if "watts" in power else ""
            )
            flat["power_w"] = power.get("watts", power.get("w", ""))
        else:
            flat["power_kw"] = specs.get("power_kw", specs.get("nominal_power_kw", ""))
            flat["power_w"] = specs.get("power_w", specs.get("nominal_power_w", ""))

        # Voltage
        flat["voltage_v"] = specs.get("voltage_v", specs.get("nominal_voltage", ""))
        flat["voltage_range"] = specs.get("voltage_range", "")

        # Current
        flat["current_a"] = specs.get("current_a", specs.get("max_current", ""))

        # Efficiency
        flat["efficiency_percent"] = specs.get(
            "efficiency_percent", specs.get("max_efficiency", "")
        )

        # Dimensions
        dimensions = specs.get("dimensions", {})
        if isinstance(dimensions, dict):
            flat["length_mm"] = dimensions.get("length_mm", "")
            flat["width_mm"] = dimensions.get("width_mm", "")
            flat["height_mm"] = dimensions.get("height_mm", "")
            flat["weight_kg"] = dimensions.get("weight_kg", "")
        else:
            flat["dimensions"] = str(dimensions)

        # Battery specific
        if "capacity_ah" in specs:
            flat["capacity_ah"] = specs["capacity_ah"]
        if "energy_kwh" in specs:
            flat["energy_kwh"] = specs["energy_kwh"]

        # Cable specific
        if "section_mm2" in specs:
            flat["section_mm2"] = specs["section_mm2"]
        if "length_m" in specs:
            flat["length_m"] = specs["length_m"]

        # Certifications
        certs = product.get("certifications", [])
        flat["certifications"] = (
            ", ".join(certs) if isinstance(certs, list) else str(certs)
        )

        # Stock
        stock = product.get("stock", {})
        flat["stock_available"] = stock.get("available", "")
        flat["stock_quantity"] = stock.get("quantity", "")

        # Warranty
        warranty = product.get("warranty", {})
        flat["warranty_years"] = warranty.get("years", "")

        # Tags
        tags = product.get("tags", [])
        flat["tags"] = ", ".join(tags) if isinstance(tags, list) else ""

        # Description
        flat["description"] = product.get("description", "")[
            :500
        ]  # Limitar a 500 chars

        # Image
        media = product.get("media", {})
        flat["image_url"] = media.get("image_url", product.get("image_url", ""))

        return flat

    def load_category_products(self, category: str, files: List[str]) -> List[Dict]:
        """Carrega produtos de uma categoria de múltiplos distribuidores"""
        products = []

        for filename in files:
            # Identificar distribuidor pelo nome do arquivo
            if filename.startswith("fortlev"):
                dist_dir = self.distributors_dir / "fortlev"
            elif filename.startswith("solfacil"):
                dist_dir = self.distributors_dir / "solfacil"
            elif filename.startswith("odex"):
                dist_dir = self.distributors_dir / "odex"
            else:
                continue

            file_path = dist_dir / filename

            if not file_path.exists():
                print(f"  ⚠️  Arquivo não encontrado: {file_path.name}")
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, list):
                    distributor = self.extract_distributor(file_path)
                    for item in data:
                        item["_source_file"] = filename
                        item["_distributor"] = distributor
                        products.append(item)

                    self.stats[f"{category}_products"] += len(data)
                    print(
                        f"  ✓ {distributor:10} | {len(data):4} produtos de {filename}"
                    )

            except Exception as e:
                print(f"  ❌ Erro ao ler {file_path.name}: {e}")

        return products

    def create_category_csv(self, category: str, config: Dict):
        """Cria CSV unificado para uma categoria"""
        print(f"\n{'='*80}")
        print(f"📦 CATEGORIA: {config['name']} ({category})")
        print(f"{'='*80}")

        # Carregar produtos
        products = self.load_category_products(category, config["files"])

        if not products:
            print(f"  ⚠️  Nenhum produto encontrado para {category}")
            return

        # Achatar produtos
        flattened = []
        for p in products:
            try:
                flat = self.flatten_product(p, p.get("_distributor", "Unknown"))
                flattened.append(flat)
            except Exception as e:
                print(f"  ⚠️  Erro ao processar produto {p.get('id', 'unknown')}: {e}")

        if not flattened:
            print(f"  ⚠️  Nenhum produto válido após processamento")
            return

        # Coletar todas as chaves
        all_keys = set()
        for item in flattened:
            all_keys.update(item.keys())

        # Ordenar chaves com prioridade
        priority_keys = [
            "distributor",
            "id",
            "name",
            "manufacturer",
            "model",
            "sku",
            "category",
            "type",
            "price_brl",
            "power_kw",
            "power_w",
            "voltage_v",
            "current_a",
            "efficiency_percent",
        ]

        other_keys = sorted(all_keys - set(priority_keys))
        fieldnames = [k for k in priority_keys if k in all_keys] + other_keys

        # Salvar CSV
        output_file = self.output_dir / f"category_{category}.csv"

        with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(flattened)

        file_size = output_file.stat().st_size / 1024
        self.stats["total_files"] += 1
        self.stats["total_products"] += len(flattened)

        print(f"\n  ✅ CSV criado: {output_file.name}")
        print(f"     • Produtos: {len(flattened)}")
        print(f"     • Colunas: {len(fieldnames)}")
        print(f"     • Tamanho: {file_size:.2f} KB")

    def create_master_comparison(self):
        """Cria CSV mestre com comparação de preços entre distribuidores"""
        print(f"\n{'='*80}")
        print(f"📊 CRIANDO CSV MESTRE DE COMPARAÇÃO")
        print(f"{'='*80}")

        # Carregar unified_products.json como base
        unified_file = self.base_dir / "unified_products.json"

        if not unified_file.exists():
            print("  ⚠️  unified_products.json não encontrado")
            return

        with open(unified_file, "r", encoding="utf-8") as f:
            unified_data = json.load(f)

        # Processar apenas produtos não-kits
        products_by_category = defaultdict(list)

        for product in unified_data:
            category = product.get("category", "unknown")
            if category != "kits":  # Pular kits (já foram processados)
                products_by_category[category].append(product)

        print(f"\n  📋 Categorias encontradas em unified_products.json:")
        for cat, prods in sorted(
            products_by_category.items(), key=lambda x: -len(x[1])
        ):
            print(f"     • {cat}: {len(prods)} produtos")

    def run(self):
        """Executa unificação completa"""
        print("\n" + "=" * 80)
        print("🚀 INICIANDO UNIFICAÇÃO COMPLETA DO CATÁLOGO")
        print("=" * 80)
        print(f"📁 Diretório base: {self.base_dir}")
        print(f"📁 Saída: {self.output_dir}")
        print(f"📊 Total de categorias: {len(self.categories_map)}")

        # Processar cada categoria
        for category, config in sorted(self.categories_map.items()):
            self.create_category_csv(category, config)

        # Criar comparação mestre
        self.create_master_comparison()

        # Sumário final
        print(f"\n{'='*80}")
        print("✅ UNIFICAÇÃO CONCLUÍDA!")
        print(f"{'='*80}")
        print(f"\n📊 ESTATÍSTICAS FINAIS:")
        print(f"  • Categorias processadas: {len(self.categories_map)}")
        print(f"  • CSVs criados: {self.stats['total_files']}")
        print(f"  • Total de produtos: {self.stats['total_products']}")
        print(f"\n📁 Arquivos salvos em: {self.output_dir}")

        # Listar arquivos criados
        csv_files = sorted(self.output_dir.glob("*.csv"))
        if csv_files:
            print(f"\n📄 ARQUIVOS CRIADOS:")
            for csv_file in csv_files:
                size_kb = csv_file.stat().st_size / 1024
                print(f"  • {csv_file.name:40} ({size_kb:8.2f} KB)")


def main():
    """Função principal"""
    base_dir = Path(__file__).parent
    unifier = CompleteCatalogUnifier(base_dir)
    unifier.run()


if __name__ == "__main__":
    main()
