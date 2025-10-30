#!/usr/bin/env python3
"""Lista fabricantes de inversores com detalhes de cobertura de imagens"""

import json
from collections import defaultdict

# Carregar inventário
with open("data/products_inventory_raw.json", "r", encoding="utf-8") as f:
    inventory = json.load(f)

# Carregar mapa de imagens
with open("static/products/product_image_map.json", "r", encoding="utf-8") as f:
    image_map = json.load(f)

# Extrair inversores do inventário
inverters_by_mfg = defaultdict(list)

for manufacturer, products in inventory["products"].items():
    for product in products:
        if "inverter" in product.get("type", "").lower():
            inverters_by_mfg[manufacturer.upper()].append(
                {
                    "id": product.get("id"),
                    "model": product.get("model"),
                    "power": product.get("power"),
                    "voltage": product.get("voltage"),
                    "name": product.get("name"),
                }
            )

print("⚡ INVERSORES - FABRICANTES E MODELOS")
print("=" * 90)
print()

total_inverters = 0
for mfg in sorted(inverters_by_mfg.keys()):
    models = inverters_by_mfg[mfg]
    total_inverters += len(models)
    print(f"🏭 {mfg}")
    print(f'   {"ID":6} | {"Modelo":30} | {"Potência":12} | {"Tensão":10}')
    print(f'   {"-"*6}-+-{"-"*30}-+-{"-"*12}-+-{"-"*10}')

    for model in sorted(models, key=lambda x: x["model"]):
        print(
            f'   {model["id"]:6} | {model["model"][:30]:30} | {model["power"][:12]:12} | {model["voltage"][:10]:10}'
        )
    print()

print("=" * 90)
print(
    f"📊 RESUMO: {len(inverters_by_mfg)} fabricantes | {total_inverters} modelos de inversores"
)

# Verificar imagens disponíveis para cada fabricante
print("\n")
print("🖼️  VERIFICAÇÃO DE IMAGENS")
print("=" * 90)

for mfg in sorted(inverters_by_mfg.keys()):
    models = inverters_by_mfg[mfg]
    with_images = 0

    for model_info in models:
        model_clean = (
            model_info["model"]
            .upper()
            .replace("-", "")
            .replace("_", "")
            .replace(" ", "")
        )

        for img_sku in image_map["images"].keys():
            img_sku_clean = (
                img_sku.upper().replace("-", "").replace("_", "").replace(" ", "")
            )
            if model_clean in img_sku_clean or img_sku_clean in model_clean:
                with_images += 1
                break

    pct = 100 * with_images / len(models) if len(models) > 0 else 0
    status = "✅" if pct > 50 else "⚠️ " if pct > 0 else "❌"
    bar = "█" * int(pct / 5)

    print(
        f"{status} {mfg:15} | {with_images:2}/{len(models):2} ({pct:5.1f}%) | {bar:<20}"
    )
