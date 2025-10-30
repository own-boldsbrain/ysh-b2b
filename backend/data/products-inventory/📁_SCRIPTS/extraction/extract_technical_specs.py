"""
Technical Specifications Extractor - YSH Unified Inventory
Extrai modelos, séries e especificações técnicas de todos os produtos
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any


class TechnicalSpecsExtractor:
    def __init__(self, json_file: Path):
        self.json_file = json_file
        self.products = []
        self.specs = {
            "panels": defaultdict(list),
            "inverters": defaultdict(list),
            "batteries": defaultdict(list),
            "kits": defaultdict(list),
        }

    def load_products(self):
        """Carrega produtos do JSON."""
        with open(self.json_file, "r", encoding="utf-8") as f:
            self.products = json.load(f)
        print(f"✅ {len(self.products)} produtos carregados")

    def extract_panel_specs(self, panel_data: Dict) -> Dict:
        """Extrai especificações de painéis."""
        description = panel_data.get("description", "")

        specs = {
            "manufacturer": panel_data.get("brand") or panel_data.get("manufacturer"),
            "power_w": panel_data.get("power_w"),
            "quantity": panel_data.get("quantity"),
            "description": description,
            "model": None,
            "technology": None,
            "efficiency": None,
            "bifacial": False,
        }

        # Extrair modelo
        model_patterns = [
            r"([A-Z0-9\-]+)\s*\|",  # Padrão: MODELO |
            r"([A-Z]{2,}\s*[0-9]{2,}[A-Z0-9\-]*)",  # Padrão: LR5-72HPH-550M
            r"(HN[0-9]{2}[A-Z]\-[0-9]{2}[A-Z]+)",  # Padrão: HN18N-72H
            r"(DHN\-[0-9]{2}[A-Z0-9\-/]+)",  # Padrão: DHN-72X16/DG
        ]

        for pattern in model_patterns:
            match = re.search(pattern, description)
            if match:
                specs["model"] = match.group(1).strip()
                break

        # Extrair tecnologia
        tech_keywords = {
            "MONO": "Monocrystalline",
            "POLY": "Polycrystalline",
            "N-TYPE": "N-Type",
            "P-TYPE": "P-Type",
            "PERC": "PERC",
            "TOPCON": "TOPCon",
            "HJT": "HJT",
            "IBC": "IBC",
        }

        for keyword, tech in tech_keywords.items():
            if keyword in description.upper():
                specs["technology"] = tech
                break

        # Bifacial
        if "BIFACIAL" in description.upper() or "BF" in description.upper():
            specs["bifacial"] = True

        # Eficiência
        eff_match = re.search(r"(\d{2}[,\.]\d+)%?\s*E[F\.]", description)
        if eff_match:
            specs["efficiency"] = float(eff_match.group(1).replace(",", "."))

        return specs

    def extract_inverter_specs(self, inverter_data: Dict) -> Dict:
        """Extrai especificações de inversores."""
        description = inverter_data.get("description", "")

        specs = {
            "manufacturer": inverter_data.get("brand")
            or inverter_data.get("manufacturer"),
            "power_kw": inverter_data.get("power_kw"),
            "rating": inverter_data.get("rating"),
            "type": inverter_data.get("type"),
            "quantity": inverter_data.get("quantity"),
            "description": description,
            "model": None,
            "voltage": None,
            "phases": None,
            "mppt": None,
            "hybrid": False,
        }

        # Extrair modelo
        model_patterns = [
            r"([A-Z0-9\-]+)\s+(?:MONOF|TRIF|HYBRID)",
            r"(NEO\s*\-?\s*[0-9]{4}[A-Z\-]*)",  # Growatt NEO
            r"(GW[0-9]{4,5}[A-Z\-]*)",  # GoodWe
            r"(SUN\-[A-Z0-9\-]+)",  # Deye SUN-
            r"(TSOL\-[A-Z0-9\-]+)",  # Tsuness
            r"(SG[0-9]{2,}[A-Z0-9]*)",  # Sungrow
        ]

        for pattern in model_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                specs["model"] = match.group(1).strip()
                break

        # Voltagem
        voltage_match = re.search(r"(\d{3})V", description)
        if voltage_match:
            specs["voltage"] = int(voltage_match.group(1))

        # Fases
        if "MONOF" in description.upper() or "MONOFÁSICO" in description.upper():
            specs["phases"] = 1
        elif "TRIF" in description.upper() or "TRIFÁSICO" in description.upper():
            specs["phases"] = 3

        # MPPT
        mppt_match = re.search(r"(\d+)\s*MPPT", description)
        if mppt_match:
            specs["mppt"] = int(mppt_match.group(1))

        # Híbrido
        if "HYBRID" in description.upper() or "HIBRIDO" in description.upper():
            specs["hybrid"] = True

        return specs

    def extract_battery_specs(self, battery_data: Dict) -> Dict:
        """Extrai especificações de baterias."""
        description = battery_data.get("description", "")

        specs = {
            "manufacturer": battery_data.get("brand"),
            "capacity_ah": battery_data.get("capacity_ah"),
            "voltage_v": battery_data.get("voltage_v"),
            "technology": battery_data.get("technology"),
            "quantity": battery_data.get("quantity"),
            "description": description,
            "model": None,
            "capacity_kwh": None,
            "chemistry": None,
        }

        # Capacidade em kWh
        if specs["capacity_ah"] and specs["voltage_v"]:
            specs["capacity_kwh"] = round(
                (specs["capacity_ah"] * specs["voltage_v"]) / 1000, 2
            )

        # Química da bateria
        tech = (specs["technology"] or "").upper()
        if "LITI" in tech or "LFP" in tech or "LIFEPO4" in tech:
            specs["chemistry"] = "Lithium LFP"
        elif "CHUMBO" in tech or "LEAD" in tech or "ÁCIDO" in tech:
            specs["chemistry"] = "Lead-Acid"
        elif "NMC" in tech:
            specs["chemistry"] = "Lithium NMC"

        # Extrair modelo do description
        model_match = re.search(r"([A-Z0-9\-]+Ah/\d+V)", description)
        if model_match:
            specs["model"] = model_match.group(1)

        return specs

    def extract_kit_specs(self, product: Dict) -> Dict:
        """Extrai especificações de kits completos."""
        name = product.get("name", "")

        specs = {
            "id": product.get("id"),
            "name": name,
            "distributor": product.get("distributor"),
            "type": product.get("type"),
            "power_kwp": product.get("power", {}).get("kwp"),
            "power_w": product.get("power", {}).get("watts"),
            "price_brl": product.get("pricing", {}).get("price_brl"),
            "price_per_wp": product.get("pricing", {}).get("price_per_wp"),
            "kit_type": None,
            "application": None,
            "grid_type": None,
            "roof_type": None,
        }

        # Tipo de kit
        name_upper = name.upper()
        if "OFF-GRID" in name_upper or "OFF GRID" in name_upper:
            specs["kit_type"] = "Off-Grid"
            specs["grid_type"] = "Standalone"
        elif (
            "HYBRID" in name_upper or "HIBRIDO" in name_upper or "HÍBRIDO" in name_upper
        ):
            specs["kit_type"] = "Hybrid"
            specs["grid_type"] = "Grid-Tie with Backup"
        elif "ON-GRID" in name_upper or "GRID-TIE" in name_upper:
            specs["kit_type"] = "On-Grid"
            specs["grid_type"] = "Grid-Tie"
        else:
            specs["kit_type"] = "Standard"
            specs["grid_type"] = "Grid-Tie"

        # Tipo de telhado
        metadata = product.get("metadata", {})
        roof = metadata.get("estrutura", "")
        if roof:
            roof_map = {
                "CERÂMICO": "Ceramic Tile",
                "CERAMICO": "Ceramic Tile",
                "FIBROCIMENTO": "Fiber Cement",
                "METÁLICO": "Metal Roof",
                "METALICO": "Metal Roof",
                "MINITRILHO": "Mini-Rail",
                "LAJE": "Concrete Slab",
                "SOLO": "Ground Mount",
            }
            specs["roof_type"] = roof_map.get(roof.upper(), roof)

        # Aplicação
        if specs["power_kwp"]:
            if specs["power_kwp"] < 5:
                specs["application"] = "Residential Small"
            elif specs["power_kwp"] < 10:
                specs["application"] = "Residential Medium"
            elif specs["power_kwp"] < 20:
                specs["application"] = "Residential Large"
            elif specs["power_kwp"] < 75:
                specs["application"] = "Commercial Small"
            elif specs["power_kwp"] < 150:
                specs["application"] = "Commercial Medium"
            else:
                specs["application"] = "Commercial Large"

        return specs

    def process_all_products(self):
        """Processa todos os produtos e extrai especificações."""
        print("\n🔍 Processando produtos...")

        for idx, product in enumerate(self.products):
            if idx % 500 == 0:
                print(f"  Processando produto {idx}/{len(self.products)}...")

            category = product.get("category")
            components = product.get("components", {})

            # Kits
            if category == "kits":
                kit_specs = self.extract_kit_specs(product)
                self.specs["kits"]["all"].append(kit_specs)

                # Armazenar por tipo
                kit_type = kit_specs["kit_type"]
                if kit_type:
                    self.specs["kits"][kit_type].append(kit_specs)

            # Painéis
            for panel in components.get("panels", []):
                panel_specs = self.extract_panel_specs(panel)
                manufacturer = panel_specs["manufacturer"]
                if manufacturer:
                    self.specs["panels"][manufacturer].append(panel_specs)

            # Inversores
            for inverter in components.get("inverters", []):
                inverter_specs = self.extract_inverter_specs(inverter)
                manufacturer = inverter_specs["manufacturer"]
                if manufacturer:
                    self.specs["inverters"][manufacturer].append(inverter_specs)

            # Baterias
            for battery in components.get("batteries", []):
                battery_specs = self.extract_battery_specs(battery)
                manufacturer = battery_specs["manufacturer"]
                if manufacturer:
                    self.specs["batteries"][manufacturer].append(battery_specs)

        print(f"✅ Todos os produtos processados!")

    def generate_summary(self) -> Dict:
        """Gera sumário das especificações extraídas."""
        summary = {
            "total_products": len(self.products),
            "kits": {
                "total": len(self.specs["kits"]["all"]),
                "by_type": {},
                "power_distribution": {},
                "price_distribution": {},
            },
            "panels": {
                "total": sum(len(specs) for specs in self.specs["panels"].values()),
                "manufacturers": len(self.specs["panels"]),
                "technologies": Counter(),
                "power_range": {},
            },
            "inverters": {
                "total": sum(len(specs) for specs in self.specs["inverters"].values()),
                "manufacturers": len(self.specs["inverters"]),
                "types": Counter(),
                "power_range": {},
            },
            "batteries": {
                "total": sum(len(specs) for specs in self.specs["batteries"].values()),
                "manufacturers": len(self.specs["batteries"]),
                "chemistries": Counter(),
                "capacity_range": {},
            },
        }

        # Kits por tipo
        for kit_type in ["Off-Grid", "On-Grid", "Hybrid", "Standard"]:
            count = len(self.specs["kits"].get(kit_type, []))
            if count > 0:
                summary["kits"]["by_type"][kit_type] = count

        # Painéis - tecnologias
        for manufacturer, panels in self.specs["panels"].items():
            for panel in panels:
                if panel["technology"]:
                    summary["panels"]["technologies"][panel["technology"]] += 1

        # Inversores - tipos
        for manufacturer, inverters in self.specs["inverters"].items():
            for inverter in inverters:
                inv_type = inverter.get("type") or "Standard"
                summary["inverters"]["types"][inv_type] += 1

        # Baterias - químicas
        for manufacturer, batteries in self.specs["batteries"].items():
            for battery in batteries:
                if battery["chemistry"]:
                    summary["batteries"]["chemistries"][battery["chemistry"]] += 1

        return summary

    def save_results(self, output_dir: Path):
        """Salva resultados em arquivos JSON."""
        output_dir.mkdir(exist_ok=True)

        # Salvar especificações completas
        specs_file = output_dir / "technical_specifications_complete.json"
        with open(specs_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "kits": dict(self.specs["kits"]),
                    "panels": {k: v for k, v in self.specs["panels"].items()},
                    "inverters": {k: v for k, v in self.specs["inverters"].items()},
                    "batteries": {k: v for k, v in self.specs["batteries"].items()},
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"✅ Especificações completas: {specs_file}")

        # Salvar sumário
        summary = self.generate_summary()
        summary_file = output_dir / "technical_specifications_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"✅ Sumário: {summary_file}")

        return summary

    def print_report(self, summary: Dict):
        """Imprime relatório formatado."""
        print("\n" + "=" * 80)
        print("ESPECIFICAÇÕES TÉCNICAS - YSH SOLAR INVENTORY")
        print("=" * 80)

        print(f"\n📦 PRODUTOS TOTAIS: {summary['total_products']}")

        # Kits
        print(f"\n🎁 KITS SOLARES: {summary['kits']['total']}")
        print("-" * 80)
        for kit_type, count in summary["kits"]["by_type"].items():
            percentage = (count / summary["kits"]["total"]) * 100
            print(f"  {kit_type:<20} {count:>6} ({percentage:.1f}%)")

        # Painéis
        print(f"\n☀️ PAINÉIS: {summary['panels']['total']}")
        print(f"  Fabricantes: {summary['panels']['manufacturers']}")
        print("-" * 80)
        print("  Tecnologias:")
        for tech, count in summary["panels"]["technologies"].most_common():
            percentage = (count / summary["panels"]["total"]) * 100
            print(f"    {tech:<20} {count:>6} ({percentage:.1f}%)")

        # Inversores
        print(f"\n⚡ INVERSORES: {summary['inverters']['total']}")
        print(f"  Fabricantes: {summary['inverters']['manufacturers']}")
        print("-" * 80)
        print("  Tipos:")
        for inv_type, count in summary["inverters"]["types"].most_common():
            percentage = (count / summary["inverters"]["total"]) * 100
            print(f"    {inv_type:<20} {count:>6} ({percentage:.1f}%)")

        # Baterias
        if summary["batteries"]["total"] > 0:
            print(f"\n🔋 BATERIAS: {summary['batteries']['total']}")
            print(f"  Fabricantes: {summary['batteries']['manufacturers']}")
            print("-" * 80)
            print("  Químicas:")
            for chem, count in summary["batteries"]["chemistries"].most_common():
                percentage = (count / summary["batteries"]["total"]) * 100
                print(f"    {chem:<20} {count:>6} ({percentage:.1f}%)")

        print("\n" + "=" * 80)


def main():
    base_path = Path(
        r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory"
    )
    json_file = base_path / "unified_products.json"
    output_dir = base_path / "technical_specs"

    extractor = TechnicalSpecsExtractor(json_file)
    extractor.load_products()
    extractor.process_all_products()
    summary = extractor.save_results(output_dir)
    extractor.print_report(summary)


if __name__ == "__main__":
    main()
