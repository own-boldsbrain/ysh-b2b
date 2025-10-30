#!/usr/bin/env python3
"""
Script de Análise de Sincronização SKU ⟷ Imagens
Compara produtos do inventário com o mapeamento de imagens
"""

import json
from collections import defaultdict
from pathlib import Path

# Carregar inventário
with open("data/products_inventory_raw.json", "r", encoding="utf-8") as f:
    inventory = json.load(f)

# Carregar mapa de imagens
with open("static/products/product_image_map.json", "r", encoding="utf-8") as f:
    image_map = json.load(f)

# Extrair produtos com seus identificadores
products_by_model = {}
for manufacturer, products in inventory["products"].items():
    for product in products:
        model = product.get("model", "").upper()
        products_by_model[model] = {
            "id": product.get("id"),
            "manufacturer": manufacturer.upper(),
            "model": model,
            "full_name": product.get("name"),
        }

# Extrair SKUs do mapa (normalizados)
image_skus = list(image_map["images"].keys())

# Análise
total_products = len(products_by_model)
synced = 0
missing_images = []

print("📊 ANÁLISE DE SINCRONIZAÇÃO SKU ⟷ IMAGENS")
print("=" * 80)
print(f"\n📦 Total de Produtos no Inventário: {total_products}")
print(f"🖼️  Total de SKUs com Imagens Mapeadas: {len(image_skus)}")

# Verificar sincronização por modelo
for model_key, product_info in products_by_model.items():
    model_clean = model_key.replace("-", "").replace("_", "").replace(" ", "")

    # Procurar correspondência
    found = False
    for img_sku in image_skus:
        img_sku_clean = (
            img_sku.upper().replace("-", "").replace("_", "").replace(" ", "")
        )
        if model_clean in img_sku_clean or img_sku_clean in model_clean:
            synced += 1
            found = True
            break

    if not found:
        missing_images.append(
            {
                "id": product_info["id"],
                "model": product_info["model"],
                "manufacturer": product_info["manufacturer"],
                "name": product_info["full_name"],
            }
        )

print(f"\n✅ Produtos COM Imagens: {synced} ({100*synced/total_products:.1f}%)")
print(
    f"❌ Produtos SEM Imagens: {len(missing_images)} ({100*len(missing_images)/total_products:.1f}%)"
)

print(f"\n❌ PRIMEIROS 15 PRODUTOS SEM IMAGENS:")
print("-" * 80)
for i, prod in enumerate(missing_images[:15], 1):
    print(
        f'{i:2}. [{prod["id"]}] {prod["manufacturer"]:15} | {prod["model"]:25} | {prod["name"][:40]}'
    )

# Estatísticas por fabricante
print(f"\n\n📈 COBERTURA POR FABRICANTE:")
print("-" * 80)
by_mfg = defaultdict(lambda: {"total": 0, "with_images": 0})

for model_key, product_info in products_by_model.items():
    mfg = product_info["manufacturer"]
    by_mfg[mfg]["total"] += 1

    model_clean = model_key.replace("-", "").replace("_", "").replace(" ", "")
    for img_sku in image_skus:
        img_sku_clean = (
            img_sku.upper().replace("-", "").replace("_", "").replace(" ", "")
        )
        if model_clean in img_sku_clean or img_sku_clean in model_clean:
            by_mfg[mfg]["with_images"] += 1
            break

for mfg in sorted(by_mfg.keys()):
    stats = by_mfg[mfg]
    pct = 100 * stats["with_images"] / stats["total"] if stats["total"] > 0 else 0
    bar = "█" * int(pct / 5)
    print(
        f'{mfg:15} | {stats["with_images"]:3}/{stats["total"]:3} ({pct:5.1f}%) | {bar:<20}'
    )

# Estatísticas de categorias
print(f"\n\n📂 IMAGENS POR CATEGORIA:")
print("-" * 80)
categories = defaultdict(int)
for sku, images_list in image_map["images"].items():
    for img in images_list:
        cat = img.get("category", "Unknown")
        categories[cat] += 1

for cat in sorted(categories.keys()):
    count = categories[cat]
    print(f"{cat:40} | {count:4} imagens")

print(f'\n{"TOTAL":40} | {len(image_skus):4} SKUs mapeados')
