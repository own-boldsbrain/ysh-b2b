"""
Product Models & Series Extractor for Datasheets
Extrai modelos e séries de produtos para busca de datasheets e certificações
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set


class DatasheetSearchExtractor:
    def __init__(self, specs_file: Path):
        self.specs_file = specs_file
        self.specs_data = {}
        self.products_for_datasheets = {
            "panels": [],
            "inverters": [],
            "batteries": [],
            "controllers": [],
        }

    def load_specs(self):
        """Carrega especificações técnicas."""
        with open(self.specs_file, "r", encoding="utf-8") as f:
            self.specs_data = json.load(f)
        print(f"✅ Especificações carregadas")

    def extract_panel_models(self):
        """Extrai modelos de painéis para busca de datasheet."""
        panels_by_manufacturer = self.specs_data.get("panels", {})
        unique_models = defaultdict(set)

        for manufacturer, panels in panels_by_manufacturer.items():
            if manufacturer in ["None", "Unknown", None]:
                continue

            for panel in panels:
                model = panel.get("model")
                power_w = panel.get("power_w")
                description = panel.get("description", "")

                # Extrair modelo se não existir
                if not model and description:
                    # Tentar extrair modelo da descrição
                    patterns = [
                        r"([A-Z]{2,}[\-\s]*[0-9]{3,}[A-Z0-9\-]*)",  # LR5-72HPH-550M
                        r"([A-Z]+[0-9]{2,}[A-Z]\-[0-9]{2}[A-Z]+)",  # HN18N-72H
                        r"(DHN\-[0-9]{2}[A-Z0-9\-/]+)",  # DHN-72X16/DG
                    ]

                    for pattern in patterns:
                        match = re.search(pattern, description)
                        if match:
                            model = match.group(1).strip()
                            break

                if model:
                    model_clean = model.strip().upper()
                    unique_models[manufacturer].add(model_clean)

                    self.products_for_datasheets["panels"].append(
                        {
                            "manufacturer": manufacturer,
                            "model": model_clean,
                            "power_w": power_w,
                            "technology": panel.get("technology"),
                            "efficiency": panel.get("efficiency"),
                            "bifacial": panel.get("bifacial"),
                            "search_query": f"{manufacturer} {model_clean} solar panel datasheet",
                            "certification_query": f"{manufacturer} {model_clean} INMETRO certification",
                        }
                    )

        # Remover duplicatas
        seen = set()
        unique_panels = []
        for panel in self.products_for_datasheets["panels"]:
            key = (panel["manufacturer"], panel["model"])
            if key not in seen:
                seen.add(key)
                unique_panels.append(panel)

        self.products_for_datasheets["panels"] = unique_panels

        print(
            f"✅ Painéis: {len(unique_panels)} modelos únicos de {len(unique_models)} fabricantes"
        )
        return unique_panels

    def extract_inverter_models(self):
        """Extrai modelos de inversores para busca de datasheet."""
        inverters_by_manufacturer = self.specs_data.get("inverters", {})
        unique_models = defaultdict(set)

        for manufacturer, inverters in inverters_by_manufacturer.items():
            if manufacturer in ["None", "Unknown", None]:
                continue

            for inverter in inverters:
                model = inverter.get("model")
                power_kw = inverter.get("power_kw")
                description = inverter.get("description", "")
                inv_type = inverter.get("type")

                # Filtrar controladores PWM/MPPT para categoria separada
                if inv_type in ["PWM", "MPPT"]:
                    continue

                # Extrair modelo se não existir
                if not model and description:
                    patterns = [
                        r"(NEO[\-\s]*[0-9]{4}[A-Z0-9\-]*)",  # NEO-2000M
                        r"(GW[0-9]{4,5}[A-Z0-9\-]*)",  # GW6000
                        r"(SUN[\-\s][A-Z0-9\-]+)",  # SUN-M225G4
                        r"(TSOL[\-\s][A-Z0-9\-]+)",  # TSOL-MX3000D
                        r"(SG[0-9]{2,}[A-Z0-9]*)",  # SG110CX
                        r"([A-Z]{2,}[\-\s]*[0-9]{2,}[A-Z0-9\-]*)",  # Padrão genérico
                    ]

                    for pattern in patterns:
                        match = re.search(pattern, description, re.IGNORECASE)
                        if match:
                            model = match.group(1).strip()
                            break

                if model:
                    model_clean = model.strip().upper()
                    unique_models[manufacturer].add(model_clean)

                    self.products_for_datasheets["inverters"].append(
                        {
                            "manufacturer": manufacturer,
                            "model": model_clean,
                            "power_kw": power_kw,
                            "voltage": inverter.get("voltage"),
                            "phases": inverter.get("phases"),
                            "mppt": inverter.get("mppt"),
                            "hybrid": inverter.get("hybrid"),
                            "type": inv_type,
                            "search_query": f"{manufacturer} {model_clean} inverter datasheet",
                            "certification_query": f"{manufacturer} {model_clean} INMETRO certification",
                        }
                    )

        # Remover duplicatas
        seen = set()
        unique_inverters = []
        for inv in self.products_for_datasheets["inverters"]:
            key = (inv["manufacturer"], inv["model"])
            if key not in seen:
                seen.add(key)
                unique_inverters.append(inv)

        self.products_for_datasheets["inverters"] = unique_inverters

        print(
            f"✅ Inversores: {len(unique_inverters)} modelos únicos de {len(unique_models)} fabricantes"
        )
        return unique_inverters

    def extract_controller_models(self):
        """Extrai modelos de controladores PWM/MPPT."""
        inverters_by_manufacturer = self.specs_data.get("inverters", {})
        unique_models = defaultdict(set)

        for manufacturer, inverters in inverters_by_manufacturer.items():
            if manufacturer in ["None", "Unknown", None]:
                continue

            for inverter in inverters:
                inv_type = inverter.get("type")

                # Apenas controladores PWM/MPPT
                if inv_type not in ["PWM", "MPPT"]:
                    continue

                description = inverter.get("description", "")
                rating = inverter.get("rating", "")

                # Tentar extrair modelo
                model = None
                patterns = [
                    r"([A-Z]+[\-\s]*[0-9]{2,}[A-Z0-9]*)",  # Padrão genérico
                ]

                for pattern in patterns:
                    match = re.search(pattern, description)
                    if match:
                        model = match.group(1).strip()
                        break

                # Se não encontrou modelo, usar rating como modelo
                if not model and rating:
                    model = f"{inv_type}-{rating}"

                if model:
                    model_clean = model.strip().upper()
                    unique_models[manufacturer].add(model_clean)

                    self.products_for_datasheets["controllers"].append(
                        {
                            "manufacturer": manufacturer,
                            "model": model_clean,
                            "type": inv_type,
                            "rating": rating,
                            "search_query": f"{manufacturer} {model_clean} {inv_type} controller datasheet",
                            "certification_query": f"{manufacturer} {model_clean} certification",
                        }
                    )

        # Remover duplicatas
        seen = set()
        unique_controllers = []
        for ctrl in self.products_for_datasheets["controllers"]:
            key = (ctrl["manufacturer"], ctrl["model"])
            if key not in seen:
                seen.add(key)
                unique_controllers.append(ctrl)

        self.products_for_datasheets["controllers"] = unique_controllers

        print(
            f"✅ Controladores: {len(unique_controllers)} modelos únicos de {len(unique_models)} fabricantes"
        )
        return unique_controllers

    def extract_battery_models(self):
        """Extrai modelos de baterias para busca de datasheet."""
        batteries_by_manufacturer = self.specs_data.get("batteries", {})
        unique_models = defaultdict(set)

        for manufacturer, batteries in batteries_by_manufacturer.items():
            if manufacturer in ["None", "Unknown", None]:
                continue

            for battery in batteries:
                model = battery.get("model")
                description = battery.get("description", "")
                capacity_ah = battery.get("capacity_ah")
                voltage_v = battery.get("voltage_v")

                # Extrair modelo se não existir
                if not model and description:
                    # Padrão: 105Ah/12V
                    match = re.search(r"([0-9]+Ah/[0-9]+V)", description)
                    if match:
                        model = match.group(1)

                # Criar modelo genérico se não existir
                if not model and capacity_ah and voltage_v:
                    model = f"{capacity_ah}Ah/{voltage_v}V"

                if model:
                    model_clean = model.strip().upper()
                    unique_models[manufacturer].add(model_clean)

                    self.products_for_datasheets["batteries"].append(
                        {
                            "manufacturer": manufacturer,
                            "model": model_clean,
                            "capacity_ah": capacity_ah,
                            "voltage_v": voltage_v,
                            "capacity_kwh": battery.get("capacity_kwh"),
                            "chemistry": battery.get("chemistry"),
                            "search_query": f"{manufacturer} {model_clean} battery datasheet",
                            "certification_query": f"{manufacturer} {model_clean} INMETRO certification",
                        }
                    )

        # Remover duplicatas
        seen = set()
        unique_batteries = []
        for bat in self.products_for_datasheets["batteries"]:
            key = (bat["manufacturer"], bat["model"])
            if key not in seen:
                seen.add(key)
                unique_batteries.append(bat)

        self.products_for_datasheets["batteries"] = unique_batteries

        print(
            f"✅ Baterias: {len(unique_batteries)} modelos únicos de {len(unique_models)} fabricantes"
        )
        return unique_batteries

    def generate_datasheet_search_list(self, output_file: Path):
        """Gera lista de produtos para busca de datasheets."""
        print("\n🔍 Extraindo modelos de produtos...")

        self.extract_panel_models()
        self.extract_inverter_models()
        self.extract_controller_models()
        self.extract_battery_models()

        # Salvar resultado
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.products_for_datasheets, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Lista salva em: {output_file}")

        # Gerar CSV simplificado
        csv_file = output_file.with_suffix(".csv")
        self.generate_csv_list(csv_file)

        return self.products_for_datasheets

    def generate_csv_list(self, csv_file: Path):
        """Gera CSV simplificado para busca."""
        import csv

        with open(csv_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Category",
                    "Manufacturer",
                    "Model",
                    "Specs",
                    "Datasheet Query",
                    "Certification Query",
                ]
            )

            # Painéis
            for panel in self.products_for_datasheets["panels"]:
                specs = f"{panel['power_w']}W"
                if panel["technology"]:
                    specs += f" {panel['technology']}"
                if panel["bifacial"]:
                    specs += " Bifacial"

                writer.writerow(
                    [
                        "Panel",
                        panel["manufacturer"],
                        panel["model"],
                        specs,
                        panel["search_query"],
                        panel["certification_query"],
                    ]
                )

            # Inversores
            for inv in self.products_for_datasheets["inverters"]:
                specs = f"{inv['power_kw']}kW"
                if inv["phases"]:
                    specs += f" {inv['phases']}F"
                if inv["hybrid"]:
                    specs += " Hybrid"

                writer.writerow(
                    [
                        "Inverter",
                        inv["manufacturer"],
                        inv["model"],
                        specs,
                        inv["search_query"],
                        inv["certification_query"],
                    ]
                )

            # Controladores
            for ctrl in self.products_for_datasheets["controllers"]:
                specs = f"{ctrl['type']} {ctrl['rating']}"

                writer.writerow(
                    [
                        "Controller",
                        ctrl["manufacturer"],
                        ctrl["model"],
                        specs,
                        ctrl["search_query"],
                        ctrl["certification_query"],
                    ]
                )

            # Baterias
            for bat in self.products_for_datasheets["batteries"]:
                specs = f"{bat['capacity_ah']}Ah {bat['voltage_v']}V"
                if bat["chemistry"]:
                    specs += f" {bat['chemistry']}"

                writer.writerow(
                    [
                        "Battery",
                        bat["manufacturer"],
                        bat["model"],
                        specs,
                        bat["search_query"],
                        bat["certification_query"],
                    ]
                )

        print(f"✅ CSV salvo em: {csv_file}")

    def print_summary(self):
        """Imprime sumário da extração."""
        print("\n" + "=" * 80)
        print("LISTA DE PRODUTOS PARA BUSCA DE DATASHEETS E CERTIFICAÇÕES")
        print("=" * 80)

        total = (
            len(self.products_for_datasheets["panels"])
            + len(self.products_for_datasheets["inverters"])
            + len(self.products_for_datasheets["controllers"])
            + len(self.products_for_datasheets["batteries"])
        )

        print(f"\n📊 TOTAL: {total} modelos únicos\n")

        print(
            f"☀️  Painéis:       {len(self.products_for_datasheets['panels']):>4} modelos"
        )
        print(
            f"⚡ Inversores:    {len(self.products_for_datasheets['inverters']):>4} modelos"
        )
        print(
            f"🔌 Controladores: {len(self.products_for_datasheets['controllers']):>4} modelos"
        )
        print(
            f"🔋 Baterias:      {len(self.products_for_datasheets['batteries']):>4} modelos"
        )

        print("\n" + "-" * 80)
        print("Top 5 Painéis:")
        for i, panel in enumerate(self.products_for_datasheets["panels"][:5], 1):
            print(
                f"  {i}. {panel['manufacturer']} {panel['model']} ({panel['power_w']}W)"
            )

        print("\n" + "-" * 80)
        print("Top 5 Inversores:")
        for i, inv in enumerate(self.products_for_datasheets["inverters"][:5], 1):
            print(f"  {i}. {inv['manufacturer']} {inv['model']} ({inv['power_kw']}kW)")

        print("\n" + "=" * 80)


def main():
    base_path = Path(
        r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory"
    )
    specs_file = (
        base_path / "technical_specs" / "technical_specifications_complete.json"
    )
    output_file = base_path / "datasheet_search_list.json"

    extractor = DatasheetSearchExtractor(specs_file)
    extractor.load_specs()
    extractor.generate_datasheet_search_list(output_file)
    extractor.print_summary()


if __name__ == "__main__":
    main()
