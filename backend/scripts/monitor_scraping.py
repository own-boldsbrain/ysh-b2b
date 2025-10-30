#!/usr/bin/env python3
"""Monitoramento do progresso de scraping de recursos.

Este script resume, em uma execução rápida ou em modo watch, os principais
indicadores das etapas de scraping manual e dinâmico:

* Contagem de PDFs extraídos manualmente (`manual_scraped_resources.json`).
* Situação do inventário enriquecido manualmente (`products_inventory_enriched.json`).
* Situação do inventário enriquecido dinamicamente
  (`products_inventory_dynamic_enriched.json`).
* Quantidade de imagens baixadas em `data/products-resources/images`.

Uso:

```bash
python scripts/monitor_scraping.py          # execução única
python scripts/monitor_scraping.py --watch  # atualização contínua (5s)
python scripts/monitor_scraping.py --interval 10 --watch
```
"""

import argparse
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESOURCES_DIR = DATA_DIR / "products-resources"
IMAGES_DIR = RESOURCES_DIR / "images"


@dataclass
class InventoryStats:
    manufacturer: str
    total: int
    datasheet_found: int
    image_found: int

    @property
    def datasheet_ratio(self) -> float:
        return self.datasheet_found / self.total if self.total else 0.0

    @property
    def image_ratio(self) -> float:
        return self.image_found / self.total if self.total else 0.0


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    """Safely loads a JSON file if it exists."""

    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:  # pragma: no cover - IO
            return json.load(f)
    except (
        OSError,
        json.JSONDecodeError,
    ) as exc:  # pragma: no cover - defensive
        print(f"⚠️  Não foi possível ler {path.name}: {exc}")
        return None


def summarize_manual_resources() -> str:
    """Summarizes manual scraping resources."""

    manual_path = RESOURCES_DIR / "manual_scraped_resources.json"
    data = load_json(manual_path)
    if not data:
        return "Manual scraping: arquivo ausente"

    by_mfr = data.get("by_manufacturer", {})
    total_pdfs = sum(len(info.get("pdfs", [])) for info in by_mfr.values())
    total_images = sum(len(info.get("images", [])) for info in by_mfr.values())

    lines = [
        "📂 Recursos manuais",
        f"  Total PDFs: {total_pdfs}",
        f"  Total imagens: {total_images}",
        "  Por fabricante:",
    ]

    for manufacturer, info in sorted(by_mfr.items()):
        lines.append(
            "    - {:<10} PDFs: {:>3} | Imagens: {:>3}".format(
                manufacturer.upper(),
                len(info.get("pdfs", [])),
                len(info.get("images", [])),
            )
        )

    return "\n".join(lines)


def collect_inventory_stats(path: Path) -> list[InventoryStats]:
    data = load_json(path)
    if not data:
        return []

    products_section = data.get("products", {})
    stats: list[InventoryStats] = []

    for manufacturer, products in products_section.items():
        total = len(products)
        datasheet_found = sum(
            1 for product in products if product.get("datasheet_status") == "found"
        )
        image_found = sum(
            1 for product in products if product.get("image_status") == "found"
        )
        stats.append(
            InventoryStats(
                manufacturer=manufacturer,
                total=total,
                datasheet_found=datasheet_found,
                image_found=image_found,
            )
        )

    return stats


def summarize_inventory(path: Path, label: str) -> str:
    stats = collect_inventory_stats(path)
    if not stats:
        return f"{label}: arquivo ausente"

    total_products = sum(s.total for s in stats)
    total_datasheet = sum(s.datasheet_found for s in stats)
    total_images = sum(s.image_found for s in stats)

    lines = [
        f"📦 {label}",
        f"  Produtos: {total_products}",
        (
            "  Datasheets encontrados: "
            f"{total_datasheet} ({total_datasheet/total_products*100:.1f}%)"
        ),
        (
            "  Imagens encontradas: "
            f"{total_images} ({total_images/total_products*100:.1f}%)"
        ),
        "  Top 5 fabricantes:",
    ]

    top = sorted(stats, key=lambda s: s.image_ratio, reverse=True)[:5]
    for stat in top:
        lines.append(
            (
                "    - {:<10} datasheet {:>3}/{:<3} ({:>4.0%}) | "
                "imagens {:>3}/{:<3} ({:>4.0%})"
            ).format(
                stat.manufacturer.upper(),
                stat.datasheet_found,
                stat.total,
                stat.datasheet_ratio,
                stat.image_found,
                stat.total,
                stat.image_ratio,
            )
        )

    return "\n".join(lines)


def summarize_images_dir() -> str:
    if not IMAGES_DIR.exists():
        return "📁 Diretório de imagens: ausente"

    total_files = 0
    total_size = 0
    for entry in IMAGES_DIR.glob("**/*"):
        if entry.is_file():
            total_files += 1
            total_size += entry.stat().st_size

    return (
        "📁 Diretório de imagens\n"
        f"  Caminho: {IMAGES_DIR}\n"
        f"  Arquivos: {total_files}\n"
        f"  Tamanho total: {total_size / (1024 * 1024):.2f} MB"
    )


def print_report():
    os.system("cls" if os.name == "nt" else "clear")

    print(time.strftime("🕒 Monitoramento %Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    print(summarize_manual_resources())
    print(
        "\n"
        + summarize_inventory(
            DATA_DIR / "products_inventory_enriched.json",
            "Inventário manual",
        )
    )
    print(
        "\n"
        + summarize_inventory(
            DATA_DIR / "products_inventory_dynamic_enriched.json",
            "Inventário dinâmico",
        )
    )
    print("\n" + summarize_images_dir())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitorar status de scraping de produtos"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help=("Atualiza continuamente a cada intervalo " "(default: execução única)"),
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Intervalo entre atualizações em modo watch (segundos)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        while True:
            print_report()
            if not args.watch:
                break
            time.sleep(max(args.interval, 1.0))
    except KeyboardInterrupt:  # pragma: no cover - interação usuário
        print("\n👋 Encerrando monitoramento")


if __name__ == "__main__":
    main()
