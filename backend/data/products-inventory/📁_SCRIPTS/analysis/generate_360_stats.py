#!/usr/bin/env python3
"""
Script para gerar estatísticas 360º dos fabricantes, modelos e séries
a partir do datasheet_search_list.json
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any


def load_datasheet_list() -> Dict:
    """Carrega o arquivo datasheet_search_list.json"""
    file_path = Path(__file__).parent / "datasheet_search_list.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_manufacturers(data: Dict) -> Dict:
    """Analisa fabricantes por categoria"""
    manufacturers = defaultdict(
        lambda: {
            "models": [],
            "total_models": 0,
            "categories": set(),
            "technologies": set(),
            "power_range": {"min": None, "max": None},
            "has_datasheet_query": 0,
            "has_certification_query": 0,
        }
    )

    for category, items in data.items():
        for item in items:
            manufacturer = item.get("manufacturer", "Unknown")
            model = item.get("model", "Unknown")

            manufacturers[manufacturer]["models"].append(
                {"model": model, "category": category, "data": item}
            )
            manufacturers[manufacturer]["total_models"] += 1
            manufacturers[manufacturer]["categories"].add(category)

            # Tecnologia
            if "technology" in item and item["technology"]:
                manufacturers[manufacturer]["technologies"].add(item["technology"])

            # Range de potência
            power = item.get("power_w") or item.get("power_kw")
            if power:
                current_min = manufacturers[manufacturer]["power_range"]["min"]
                current_max = manufacturers[manufacturer]["power_range"]["max"]
                manufacturers[manufacturer]["power_range"]["min"] = (
                    min(power, current_min) if current_min else power
                )
                manufacturers[manufacturer]["power_range"]["max"] = (
                    max(power, current_max) if current_max else power
                )

            # Queries
            if "search_query" in item:
                manufacturers[manufacturer]["has_datasheet_query"] += 1
            if "certification_query" in item:
                manufacturers[manufacturer]["has_certification_query"] += 1

    # Converter sets para listas
    for mfr in manufacturers.values():
        mfr["categories"] = sorted(list(mfr["categories"]))
        mfr["technologies"] = sorted(list(mfr["technologies"]))

    return dict(manufacturers)


def generate_manufacturer_report(manufacturers: Dict) -> str:
    """Gera relatório detalhado de fabricantes"""
    report = []
    report.append("=" * 80)
    report.append("RELATÓRIO 360º - FABRICANTES, MODELOS E SÉRIES")
    report.append("=" * 80)
    report.append("")

    # Ordenar por quantidade de modelos
    sorted_manufacturers = sorted(
        manufacturers.items(), key=lambda x: x[1]["total_models"], reverse=True
    )

    for rank, (manufacturer, info) in enumerate(sorted_manufacturers, 1):
        report.append(f"\n{rank}. {manufacturer}")
        report.append("-" * 80)
        report.append(f"   Total de Modelos: {info['total_models']}")
        report.append(f"   Categorias: {', '.join(info['categories'])}")

        if info["technologies"]:
            report.append(f"   Tecnologias: {', '.join(info['technologies'])}")

        if info["power_range"]["min"] or info["power_range"]["max"]:
            pmin = info["power_range"]["min"] or "N/A"
            pmax = info["power_range"]["max"] or "N/A"
            report.append(f"   Faixa de Potência: {pmin} - {pmax}")

        report.append(
            f"   Datasheets: {info['has_datasheet_query']}/{info['total_models']} "
            + f"({info['has_datasheet_query']/info['total_models']*100:.1f}%)"
        )
        report.append(
            f"   Certificações: {info['has_certification_query']}/{info['total_models']} "
            + f"({info['has_certification_query']/info['total_models']*100:.1f}%)"
        )

        # Lista de modelos
        report.append(f"\n   Modelos ({info['total_models']}):")
        for model_info in info["models"][:10]:  # Primeiros 10
            report.append(f"      - {model_info['model']} ({model_info['category']})")

        if info["total_models"] > 10:
            report.append(f"      ... e mais {info['total_models'] - 10} modelos")

    return "\n".join(report)


def generate_series_analysis(manufacturers: Dict) -> Dict:
    """Analisa séries de produtos por fabricante"""
    series_analysis = {}

    for manufacturer, info in manufacturers.items():
        series = defaultdict(list)

        for model_info in info["models"]:
            model = model_info["model"]
            category = model_info["category"]

            # Tentar identificar série pelo prefixo do modelo
            parts = model.split("-")
            if len(parts) > 1:
                serie_name = parts[0]
                series[serie_name].append({"model": model, "category": category})
            else:
                # Sem série identificável
                series["OTHER"].append({"model": model, "category": category})

        if len(series) > 1:  # Só incluir se tiver múltiplas séries
            series_analysis[manufacturer] = dict(series)

    return series_analysis


def generate_technology_matrix(data: Dict) -> Dict:
    """Gera matriz de tecnologias por categoria"""
    matrix = defaultdict(lambda: defaultdict(int))

    for category, items in data.items():
        for item in items:
            tech = item.get("technology", "Unspecified")
            matrix[category][tech] += 1

    return dict(matrix)


def main():
    print("Carregando dados...")
    data = load_datasheet_list()

    print("Analisando fabricantes...")
    manufacturers = analyze_manufacturers(data)

    print("Gerando relatório de fabricantes...")
    report = generate_manufacturer_report(manufacturers)

    # Salvar relatório em arquivo
    output_file = Path(__file__).parent / "MANUFACTURERS_360_REPORT.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ Relatório salvo em: {output_file}")

    print("\nAnalisando séries de produtos...")
    series = generate_series_analysis(manufacturers)

    # Salvar análise de séries
    series_file = Path(__file__).parent / "product_series_analysis.json"
    with open(series_file, "w", encoding="utf-8") as f:
        json.dump(series, f, indent=2, ensure_ascii=False)
    print(f"✅ Análise de séries salva em: {series_file}")

    print("\nGerando matriz de tecnologias...")
    tech_matrix = generate_technology_matrix(data)

    # Salvar matriz de tecnologias
    tech_file = Path(__file__).parent / "technology_matrix.json"
    with open(tech_file, "w", encoding="utf-8") as f:
        json.dump(tech_matrix, f, indent=2, ensure_ascii=False)
    print(f"✅ Matriz de tecnologias salva em: {tech_file}")

    # Estatísticas resumidas
    print("\n" + "=" * 80)
    print("ESTATÍSTICAS RESUMIDAS")
    print("=" * 80)
    print(f"Total de Fabricantes: {len(manufacturers)}")
    print(f"Total de Modelos: {sum(m['total_models'] for m in manufacturers.values())}")
    print(f"Categorias: {', '.join(data.keys())}")
    print(f"Fabricantes com múltiplas séries: {len(series)}")

    # Top 10 fabricantes
    print("\nTop 10 Fabricantes por Número de Modelos:")
    sorted_mfrs = sorted(
        manufacturers.items(), key=lambda x: x[1]["total_models"], reverse=True
    )
    for rank, (mfr, info) in enumerate(sorted_mfrs[:10], 1):
        print(f"  {rank}. {mfr}: {info['total_models']} modelos")

    print("\n✅ Análise completa finalizada!")
    print(f"\nArquivos gerados:")
    print(f"  1. {output_file.name}")
    print(f"  2. {series_file.name}")
    print(f"  3. {tech_file.name}")
    print(f"  4. MANUFACTURERS_360_COMPLETE.md")


if __name__ == "__main__":
    main()
