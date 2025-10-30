#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analisa padrões de SKUs para extração de specs técnicas."""

import json
from collections import defaultdict

# Carrega digital-twin-skus.json
with open("digital-twin-skus.json", "r", encoding="utf-8") as f:
    skus = json.load(f)

# Separa por tipo
by_type = defaultdict(list)
for sku in skus:
    by_type[sku["product_type"]].append(sku)

# Exemplos de cada tipo
print("=" * 70)
print("📊 ANÁLISE DE PADRÕES DE SKUs")
print("=" * 70)

print("\n🔌 INVERSORES (Total: {})".format(len(by_type["inversor"])))
print("-" * 70)
for inv in by_type["inversor"][:10]:
    print(f"SKU: {inv['sku']}")
    print(f"  Manufacturer: {inv['manufacturer']}")
    print(f"  Model: {inv['model']}")
    print(f"  Pricing: R$ {inv['pricing']['cost_price_brl']:.2f} → R$ {inv['pricing']['final_price_brl']:.2f}")
    print()

print("\n📦 KITS COMPLETOS (Total: {})".format(len(by_type["kit_completo"])))
print("-" * 70)
for kit in by_type["kit_completo"][:5]:
    print(f"SKU: {kit['sku']}")
    print(f"  Pricing: R$ {kit['pricing']['cost_price_brl']:.2f}")
    print()

print("\n🔧 COMPONENTES (Total: {})".format(len(by_type["componente"])))
print("-" * 70)
for comp in by_type["componente"][:10]:
    print(f"SKU: {comp['sku']}")
    print(f"  Manufacturer: {comp['manufacturer']}")
    print(f"  Category: {comp['category']}")
    print()

# Análise de padrões de nomenclatura
print("\n" + "=" * 70)
print("🔍 PADRÕES DE NOMENCLATURA")
print("=" * 70)

# Padrões de potência em inversores
print("\nPotência em Inversores:")
for inv in by_type["inversor"][:15]:
    sku = inv["sku"]
    # Regex patterns para potência
    import re
    
    patterns = [
        r"(\d+)K",  # Ex: 250K, 100K
        r"(\d+)KW", # Ex: 8KW, 3KW
        r"(\d+\.\d+)K",  # Ex: 2.5K
    ]
    
    for pattern in patterns:
        match = re.search(pattern, sku, re.IGNORECASE)
        if match:
            power = match.group(1)
            print(f"  {sku[:40]:<40} → {power}kW")
            break
