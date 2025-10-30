#!/usr/bin/env python3
"""
Lista todas as categorias de produtos Fortlev existentes.
"""
import json
import os
from pathlib import Path

FORTLEV_DIR = r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\distributors\fortlev"


def list_categories():
    """Lista todas as categorias de produtos."""

    # Buscar arquivos fortlev-*.json
    json_files = list(Path(FORTLEV_DIR).glob("fortlev-*.json"))

    categories = {}

    for file in json_files:
        filename = file.name

        # Extrair categoria do nome do arquivo
        if filename.startswith("fortlev-") and filename.endswith(".json"):
            category = filename.replace("fortlev-", "").replace(".json", "")

            # Pular arquivos especiais
            if category in [
                "all-products",
                "kits-enhanced",
                "kits-normalized",
                "kits-synced",
                "kits-synced-fixed",
                "kits-vision-enriched",
                "kits-with-images",
                "kits-with-skus",
            ]:
                continue

            # Contar produtos
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    count = len(data) if isinstance(data, list) else 0

                    # Pegar amostra
                    sample = None
                    if isinstance(data, list) and len(data) > 0:
                        sample = data[0].get("name", "N/A")

                    categories[category] = {
                        "file": filename,
                        "count": count,
                        "sample": sample,
                    }
            except Exception as e:
                categories[category] = {"file": filename, "count": 0, "error": str(e)}

    return categories


def main():
    print("=" * 80)
    print("CATEGORIAS DE PRODUTOS FORTLEV")
    print("=" * 80)
    print()

    categories = list_categories()

    # Ordenar por nome
    sorted_categories = sorted(categories.items())

    # Exibir tabela
    print(f"{'#':<4} {'CATEGORIA':<25} {'ARQUIVO':<35} {'QTD':<6}")
    print("-" * 80)

    for i, (category, info) in enumerate(sorted_categories, 1):
        count = info.get("count", 0)
        filename = info.get("file", "")

        # Traduzir categoria para português
        category_pt = {
            "accessories": "Acessórios",
            "batteries": "Baterias",
            "boxes": "Caixas",
            "conduits": "Condutores/Eletrodutos",
            "ev_chargers": "Carregadores EV",
            "hybrid_inverters": "Inversores Híbridos",
            "inverters": "Inversores",
            "kits": "Kits Completos",
            "microinverters": "Microinversores",
            "miscellaneous": "Diversos",
            "panels": "Painéis Solares",
            "security": "Segurança",
            "stringboxes": "String Boxes",
            "structures": "Estruturas",
            "transformers": "Transformadores",
        }.get(category, category.title())

        print(f"{i:<4} {category_pt:<25} {filename:<35} {count:<6}")

    print("-" * 80)
    print(f"{'TOTAL:':<4} {len(categories)} categorias encontradas")
    print()

    # Estatísticas
    total_products = sum(cat.get("count", 0) for cat in categories.values())
    print(f"Total de produtos: {total_products}")
    print()

    # Top 5 categorias
    print("TOP 5 CATEGORIAS COM MAIS PRODUTOS:")
    top_5 = sorted(
        categories.items(), key=lambda x: x[1].get("count", 0), reverse=True
    )[:5]

    for i, (category, info) in enumerate(top_5, 1):
        count = info.get("count", 0)
        sample = info.get("sample", "N/A")

        category_pt = {
            "accessories": "Acessórios",
            "batteries": "Baterias",
            "boxes": "Caixas",
            "conduits": "Condutores/Eletrodutos",
            "ev_chargers": "Carregadores EV",
            "hybrid_inverters": "Inversores Híbridos",
            "inverters": "Inversores",
            "kits": "Kits Completos",
            "microinverters": "Microinversores",
            "miscellaneous": "Diversos",
            "panels": "Painéis Solares",
            "security": "Segurança",
            "stringboxes": "String Boxes",
            "structures": "Estruturas",
            "transformers": "Transformadores",
        }.get(category, category.title())

        print(f"{i}. {category_pt}: {count} produtos")
        if sample and sample != "N/A":
            print(f"   Exemplo: {sample[:80]}...")
        print()


if __name__ == "__main__":
    main()
