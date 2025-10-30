#!/usr/bin/env python3
"""
Sincroniza consolidated-products.json para formatos legados:
- digital-twin-skus.json
- enriched-skus-for-dynamodb.json
"""
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

def backup_files():
    """Cria backup dos arquivos antigos"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(__file__).parent / "backups" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_backup = [
        "digital-twin-skus.json",
        "digital-twin-skus-enriched.json",
        "enriched-skus-for-dynamodb.json",
        "image-url-validation-report.json",
        "IMAGES_SYNC_REPORT.json",
        "FACEBOOK_IMAGES_VALIDATION.json"
    ]
    
    print(f"📦 Criando backup em: {backup_dir}\n")
    
    for filename in files_to_backup:
        source = Path(__file__).parent / filename
        if source.exists():
            dest = backup_dir / filename
            shutil.copy2(source, dest)
            print(f"  ✅ {filename}")
    
    return backup_dir

def parse_price_brl(price_value) -> float:
    """Converte preço brasileiro para float"""
    if not price_value:
        return 0.0
    
    if isinstance(price_value, (int, float)):
        return float(price_value)
    
    # Remover R$, espaços e converter vírgula/ponto
    price_str = str(price_value).replace('R$', '').strip()
    price_str = price_str.replace('.', '').replace(',', '.')
    
    try:
        return float(price_str)
    except ValueError:
        return 0.0

def calculate_dynamic_pricing(product: dict) -> dict:
    """Calcula pricing dinâmico baseado em custo"""
    cost_price = parse_price_brl(product['price_brl'])
    
    # Validar preço
    if not cost_price or cost_price <= 0:
        cost_price = 1000.0  # Preço padrão para produtos sem valor
    
    # Markup baseado em potência
    power = product['specs']['power_kwp']
    if power and power > 10:
        base_markup = 35
    elif power and power > 5:
        base_markup = 30
    else:
        base_markup = 28
    
    adjustment = -3  # Ajuste neutro
    final_markup = base_markup + adjustment
    
    selling_price = cost_price * (1 + final_markup / 100)
    gross_margin = (selling_price - cost_price) / selling_price * 100
    net_margin = gross_margin - 9  # Custos operacionais estimados
    
    # Psychological pricing
    final_price = round(selling_price - 0.01, 2)
    
    return {
        "cost_price_brl": cost_price,
        "final_price_brl": final_price,
        "strategy": "dynamic_v2_consolidated",
        "kpis": {
            "gross_margin_percent": round(gross_margin, 1),
            "net_margin_percent": round(net_margin, 1),
            "selling_price": final_price,
            "markup_applied": final_markup,
            "adjustments_applied": adjustment,
            "confidence": "high"
        }
    }

def convert_to_digital_twin_format(product: dict) -> dict:
    """Converte para formato digital-twin-skus.json"""
    pricing = calculate_dynamic_pricing(product)
    
    return {
        "sku": product['sku'],
        "manufacturer": product['manufacturer'],
        "model": "UNKNOWN",
        "category": product['equipment_type'],
        "product_type": product['equipment_type'],
        "image_url": product['image_url'],
        "image_validated": False,
        "pricing": pricing,
        "legal_strategic": {
            "aneel_inmetro_registry": None,
            "warranty_years": 10,
            "degradation_rate_percent_y": 0.5,
            "maintenance_schedule": {
                "cleaning_interval_months": 6,
                "inspection_interval_months": 12
            }
        },
        "specs_technical_sheet": {
            "power_kwp": product['specs']['power_kwp'],
            "voltage_v": product['specs']['voltage_v'],
            "panels": product['components']['panels'],
            "inverters": product['components']['inverters'],
            "batteries": product['components']['batteries']
        },
        "location_analysis": {
            "location": {"lat": None, "lng": None},
            "source_pvgis": None,
            "source_nasa_power": None
        },
        "operational_anomalies": {
            "last_inspection_id": None,
            "status": "NO_DATA",
            "active_anomalies": []
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_version": "2.0.0",
        "source_file": "consolidated-products.json",
        "original_id": product['original_id'],
        "distributor": product['distributor']
    }

def convert_to_dynamodb_format(product: dict) -> dict:
    """Converte para formato enriched-skus-for-dynamodb.json"""
    cost_price = parse_price_brl(product['price_brl'])
    
    # Validar preço
    if not cost_price or cost_price <= 0:
        cost_price = 1000.0
    
    # Cálculo de markup
    power = product['specs']['power_kwp']
    base_markup = 28 if not power or power <= 5 else 30 if power <= 10 else 35
    adjustment = -3
    final_markup = base_markup + adjustment
    
    selling_price = cost_price * (1 + final_markup / 100)
    final_price = round(selling_price - 0.01, 2)
    
    gross_margin = (selling_price - cost_price) / selling_price * 100
    net_margin = gross_margin - 9
    
    # Splits regionais
    total_value = final_price
    equipments_value = total_value * 0.60
    labor_value = total_value * 0.13
    freight_value = total_value * 0.05
    project_value = total_value * 0.11
    commissioning_value = total_value * 0.11
    
    return {
        "sku": product['sku'],
        "cost_price": cost_price,
        "price_score": {
            "category": "average",
            "delta": 0,
            "bestPrice": cost_price,
            "explanation": "Preço consolidado de distribuidor"
        },
        "dynamic_markup": {
            "costPrice": cost_price,
            "baseMarkup": base_markup,
            "adjustment": adjustment,
            "finalMarkup": final_markup,
            "sellingPrice": selling_price,
            "grossMargin": round(gross_margin, 1),
            "netMargin": round(net_margin, 1),
            "scenario": "neutro"
        },
        "dynamic_adjustments": {
            "time_adjustment": 0,
            "inventory_adjustment": 0,
            "competition_adjustment": 0,
            "segment_adjustment": 0,
            "urgency_adjustment": 0,
            "total_adjustment": adjustment
        },
        "channel_pricing": {
            "basePrice": selling_price,
            "channel": "b2c",
            "discount": 0,
            "channelPrice": final_price,
            "commission": 0
        },
        "final_price": final_price,
        "psychological_pricing": {
            "charm_applied": True
        },
        "project_splits": {
            "scenario": "neutro",
            "region": "sudeste",
            "total_value": total_value,
            "equipments": {
                "percentage": 60,
                "value": round(equipments_value, 2)
            },
            "labor": {
                "percentage": 13,
                "value": round(labor_value, 2)
            },
            "freight": {
                "percentage": 5,
                "value": round(freight_value, 2)
            },
            "project": {
                "percentage": 11,
                "value": round(project_value, 2)
            },
            "commissioning": {
                "percentage": 11,
                "value": round(commissioning_value, 2)
            }
        },
        "distributor": product['distributor'],
        "original_id": product['original_id'],
        "name": product['name'],
        "equipment_type": product['equipment_type'],
        "manufacturer": product['manufacturer'],
        "specs": product['specs'],
        "components": product['components'],
        "image_url": product['image_url'],
        "source_file": product['source_file'],
        "consolidated_at": product['consolidated_at']
    }

def main():
    """Função principal"""
    
    print("=" * 80)
    print("🔄 Sincronização de Dados Consolidados para Formatos Legados")
    print("=" * 80)
    
    # Backup
    backup_dir = backup_files()
    print(f"\n✅ Backup completo: {backup_dir}\n")
    
    # Carregar dados consolidados
    consolidated_file = Path(__file__).parent / "consolidated-products.json"
    print(f"📖 Lendo: {consolidated_file.name}")
    
    with open(consolidated_file, encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"   Total de produtos: {len(products)}\n")
    
    # Converter para digital-twin-skus.json
    print("🔄 Gerando digital-twin-skus.json...")
    digital_twin_products = [convert_to_digital_twin_format(p) for p in products]
    
    digital_twin_file = Path(__file__).parent / "digital-twin-skus.json"
    with open(digital_twin_file, 'w', encoding='utf-8') as f:
        json.dump(digital_twin_products, f, indent=2, ensure_ascii=False)
    
    size_mb = digital_twin_file.stat().st_size / 1024 / 1024
    print(f"   ✅ {len(digital_twin_products)} produtos | {size_mb:.1f} MB\n")
    
    # Converter para enriched-skus-for-dynamodb.json
    print("🔄 Gerando enriched-skus-for-dynamodb.json...")
    dynamodb_products = [convert_to_dynamodb_format(p) for p in products]
    
    dynamodb_file = Path(__file__).parent / "enriched-skus-for-dynamodb.json"
    with open(dynamodb_file, 'w', encoding='utf-8') as f:
        json.dump(dynamodb_products, f, indent=2, ensure_ascii=False)
    
    size_mb = dynamodb_file.stat().st_size / 1024 / 1024
    print(f"   ✅ {len(dynamodb_products)} produtos | {size_mb:.1f} MB\n")
    
    # Estatísticas
    print("=" * 80)
    print("📊 ESTATÍSTICAS DE SINCRONIZAÇÃO")
    print("=" * 80)
    
    with_power = sum(1 for p in products if p['specs']['power_kwp'])
    with_voltage = sum(1 for p in products if p['specs']['voltage_v'])
    with_image = sum(1 for p in products if p['image_url'])
    
    total = len(products)
    
    print(f"\nCobertura de Dados:")
    print(f"  Power (kWp):     {with_power:5d}/{total} ({with_power/total*100:5.1f}%)")
    print(f"  Voltage (V):     {with_voltage:5d}/{total} ({with_voltage/total*100:5.1f}%)")
    print(f"  Image URL:       {with_image:5d}/{total} ({with_image/total*100:5.1f}%)")
    
    # Pricing ranges
    prices = [parse_price_brl(p['price_brl']) for p in products if parse_price_brl(p['price_brl']) > 0]
    if prices:
        print(f"\nFaixa de Preços (Cost):")
        print(f"  Mínimo:  R$ {min(prices):,.2f}")
        print(f"  Médio:   R$ {sum(prices)/len(prices):,.2f}")
        print(f"  Máximo:  R$ {max(prices):,.2f}")
    
    # Power ranges
    powers = [p['specs']['power_kwp'] for p in products if p['specs']['power_kwp']]
    if powers:
        print(f"\nFaixa de Potências:")
        print(f"  Mínimo:  {min(powers):.2f} kWp")
        print(f"  Médio:   {sum(powers)/len(powers):.2f} kWp")
        print(f"  Máximo:  {max(powers):.2f} kWp")
    
    print(f"\n{'='*80}")
    print("✅ Sincronização concluída com sucesso!")
    print("=" * 80)

if __name__ == "__main__":
    main()
