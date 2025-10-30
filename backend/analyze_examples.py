import json

with open('digital-twin-skus-enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filtrar SKUs com specs extraídas
enriched = [s for s in data if s['specs_technical_sheet']['electrical_ref']['p_mp_ref_w'] is not None]

print(f'\n🎯 EXEMPLOS DE EXTRAÇÃO BEM-SUCEDIDA\n{\"=\"*50}\n')

# Inversores
inversores = [s for s in enriched if s['product_type'] == 'inversor'][:5]
print(f'📌 INVERSORES ({len([s for s in enriched if s[\"product_type\"] == \"inversor\"])} total):')
for inv in inversores:
    specs = inv['specs_technical_sheet']['electrical_ref']
    print(f'\n  SKU: {inv[\"sku\"][:40]}...')
    print(f'  ├─ Potência: {specs[\"p_mp_ref_w\"]/1000:.1f} kW')
    print(f'  ├─ Eficiência: {specs[\"efficiency_percent\"]}%')
    print(f'  └─ MPPTs: {specs[\"mppt_count\"]}')

# Kits
kits = [s for s in enriched if s['product_type'] == 'kit_completo'][:5]
print(f'\n\n📌 KITS ({len([s for s in enriched if s[\"product_type\"] == \"kit_completo\"])} total):')
for kit in kits:
    specs = kit['specs_technical_sheet']['electrical_ref']
    print(f'\n  SKU: {kit[\"sku\"][:40]}...')
    print(f'  ├─ Potência: {specs[\"p_mp_ref_w\"]/1000:.2f} kWp')
    print(f'  └─ MPPTs: {specs[\"mppt_count\"]}')
