#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_digital_twin_skus.py
=============================
Gera SKUs no formato Digital Twin consolidado, integrando:
- Dados de pricing existentes (enriched-skus-for-dynamodb-images-fixed.json)
- Imagens do S3 (validação e sincronização)
- Specs técnicas completas para PVLIB/NASA
- Estrutura pronta para KPIs e análises de ROI/Payback

Saída: digital-twin-skus.json com estrutura completa para análise técnico-estratégica
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError


# ==================== Configurações ====================

INPUT_FILE = Path(__file__).parent / "enriched-skus-for-dynamodb-images-fixed.json"
OUTPUT_FILE = Path(__file__).parent / "digital-twin-skus.json"
S3_BUCKET = "ysh-b2b-products"
S3_REGION = "us-east-1"

# Databases de specs técnicas (para equipamentos conhecidos)
INVERTER_SPECS_DB: Dict[str, Dict[str, Any]] = {
    "GOODWE": {
        "GW250K-HT": {
            "power_kw": 250.0,
            "voltage_v": 380,
            "efficiency_percent": 98.5,
            "mppt_count": 10,
            "mppt_voltage_range_v": "200-1000V",
            "dimensions_mm": "1050x780x350",
            "weight_kg": 85.5,
            "ip_rating": "IP66",
            "operating_temp_c": "-30°C a +60°C",
            "cell_technology": "String Inverter",
            "warranty_years": 10,
            "degradation_rate_percent_y": 0.45,
        },
        "GW100K-HT": {
            "power_kw": 100.0,
            "voltage_v": 380,
            "efficiency_percent": 98.75,
            "mppt_count": 6,
            "mppt_voltage_range_v": "200-1000V",
            "dimensions_mm": "850x650x300",
            "weight_kg": 58.0,
            "ip_rating": "IP66",
            "operating_temp_c": "-25°C a +60°C",
            "cell_technology": "String Inverter",
            "warranty_years": 10,
            "degradation_rate_percent_y": 0.45,
        },
    },
    "GROWATT": {
        "MAC-100KTL3-X": {
            "power_kw": 100.0,
            "voltage_v": 380,
            "efficiency_percent": 98.75,
            "mppt_count": 6,
            "mppt_voltage_range_v": "200-1000V",
            "dimensions_mm": "830x540x285",
            "weight_kg": 52.0,
            "ip_rating": "IP65",
            "operating_temp_c": "-25°C a +60°C",
            "cell_technology": "String Inverter",
            "warranty_years": 10,
            "degradation_rate_percent_y": 0.50,
        },
    },
    "SUNGROW": {
        "TSG110CX": {
            "power_kw": 110.0,
            "voltage_v": 380,
            "efficiency_percent": 98.6,
            "mppt_count": 9,
            "mppt_voltage_range_v": "200-1000V",
            "dimensions_mm": "900x600x310",
            "weight_kg": 65.0,
            "ip_rating": "IP65",
            "operating_temp_c": "-25°C a +60°C",
            "cell_technology": "String Inverter",
            "warranty_years": 10,
            "degradation_rate_percent_y": 0.50,
        },
    },
    "DEYE": {
        "SUN-8K-SG04LP3": {
            "power_kw": 8.0,
            "voltage_v": 220,
            "efficiency_percent": 97.6,
            "mppt_count": 2,
            "mppt_voltage_range_v": "90-550V",
            "dimensions_mm": "490x380x180",
            "weight_kg": 22.0,
            "ip_rating": "IP65",
            "operating_temp_c": "-25°C a +60°C",
            "cell_technology": "Hybrid Inverter",
            "warranty_years": 10,
            "degradation_rate_percent_y": 0.50,
        },
    },
    "HUAWEI": {
        "SUN2000-L-3KTL": {
            "power_kw": 3.0,
            "voltage_v": 220,
            "efficiency_percent": 98.4,
            "mppt_count": 2,
            "mppt_voltage_range_v": "90-560V",
            "dimensions_mm": "365x365x156",
            "weight_kg": 11.5,
            "ip_rating": "IP65",
            "operating_temp_c": "-25°C a +60°C",
            "cell_technology": "String Inverter",
            "warranty_years": 10,
            "degradation_rate_percent_y": 0.40,
        },
    },
}

PANEL_SPECS_DB: Dict[str, Dict[str, Any]] = {
    "CANADIAN_SOLAR": {
        "CS5P-220M": {
            "power_w": 220,
            "voltage_v_oc": 59.4,
            "current_a_sc": 5.1,
            "voltage_v_mp": 46.9,
            "current_a_mp": 4.69,
            "efficiency_percent": 16.5,
            "dimensions_mm": "1650x992x40",
            "weight_kg": 18.6,
            "cell_technology": "Mono-c-Si",
            "warranty_years": 25,
            "degradation_rate_percent_y": 0.55,
            "t_noct_c": 42.4,
            "alpha_sc_percent_c": 0.004539,
            "beta_oc_percent_c": -0.22216,
        },
    },
}


# ==================== Funções Auxiliares ====================


def extract_manufacturer_model(sku: str) -> tuple[Optional[str], Optional[str]]:
    """
    Extrai fabricante e modelo do SKU.
    Ex: GOODWEGW250KHTIMAGEPRODUCT600142 -> (GOODWE, GW250K-HT)
    """
    # Padrões comuns
    patterns = [
        r"^(GOODWE)(GW\d+K[-\w]*)",
        r"^(GROWATT)(MAC[-\d\w]+)",
        r"^(SUNGROW)(TSG\d+[-\w]*)",
        r"^(DEYE)(SUN[-\d\w]+)",
        r"^(HUAWEI)(SUN\d+[-\w]+)",
        r"^(FRONIUS)([\w-]+)",
        r"^(SMA)([\w-]+)",
        r"^(ABB)([\w-]+)",
    ]
    
    for pattern in patterns:
        match = re.match(pattern, sku, re.IGNORECASE)
        if match:
            manufacturer = match.group(1).upper()
            model = match.group(2).upper()
            # Ajuste de formatação
            if manufacturer == "GOODWE":
                model = model.replace("GW", "GW").replace("K", "K-")
                model = re.sub(r"(-\w{2,})", lambda m: m.group(1).replace("-", "-"), model)
            return manufacturer, model
    
    return None, None


def get_technical_specs(
    manufacturer: Optional[str], model: Optional[str], category: str
) -> Optional[Dict[str, Any]]:
    """Busca specs técnicas nos databases conhecidos."""
    if not manufacturer or not model:
        return None
    
    if category == "inversores" and manufacturer in INVERTER_SPECS_DB:
        # Busca fuzzy por modelo
        for known_model, specs in INVERTER_SPECS_DB[manufacturer].items():
            if known_model.replace("-", "").upper() in model.replace("-", "").upper():
                return specs
    
    if category == "paineis_solares" and manufacturer in PANEL_SPECS_DB:
        for known_model, specs in PANEL_SPECS_DB[manufacturer].items():
            if known_model.replace("-", "").upper() in model.replace("-", "").upper():
                return specs
    
    return None


def validate_s3_image(s3_client, bucket: str, image_url: str) -> bool:
    """Valida se a imagem existe no S3."""
    if not image_url or not image_url.startswith("https://"):
        return False
    
    try:
        # Extrai o caminho do S3 da URL
        # https://cdn.yellosolarhub.com/products/inversores/GOODWE-GW250K-HT.png
        # -> images/products/inversores/GOODWE-GW250K-HT.png
        path_parts = image_url.split("/products/")
        if len(path_parts) < 2:
            return False
        
        s3_key = f"images/products/{path_parts[1]}"
        s3_client.head_object(Bucket=bucket, Key=s3_key)
        return True
    except ClientError:
        return False


def determine_product_type(category: str, sku: str) -> str:
    """Determina o tipo de produto baseado na categoria e SKU."""
    category_lower = category.lower()
    sku_lower = sku.lower()
    
    if "inversor" in category_lower or any(x in sku_lower for x in ["gw", "mac", "tsg", "sun"]):
        return "inversor"
    if "painel" in category_lower or "panel" in category_lower:
        return "painel_solar"
    if "estrutura" in category_lower:
        return "estrutura"
    if "bateria" in category_lower:
        return "bateria"
    if "kit" in category_lower:
        return "kit_completo"
    
    return "componente"


def generate_digital_twin_sku(
    source_sku: Dict[str, Any], s3_client, s3_bucket: str, validate_images: bool = True
) -> Dict[str, Any]:
    """Gera um SKU no formato Digital Twin consolidado."""
    
    sku = source_sku.get("sku", "")
    manufacturer_raw = source_sku.get("manufacturer", "")
    category = source_sku.get("category", "componentes")
    
    # Extrai manufacturer e model
    manufacturer, model = extract_manufacturer_model(sku)
    if not manufacturer and manufacturer_raw:
        manufacturer = manufacturer_raw.upper()
    
    # Determina product_type
    product_type = determine_product_type(category, sku)
    
    # Busca specs técnicas
    tech_specs = get_technical_specs(manufacturer, model, category)
    
    # Valida imagem no S3
    image_url = source_sku.get("image_url", "")
    image_valid = validate_s3_image(s3_client, s3_bucket, image_url) if validate_images else True
    
    # Monta o Digital Twin
    digital_twin = {
        # ===== Identificação =====
        "sku": sku,
        "manufacturer": manufacturer or "UNKNOWN",
        "model": model or "UNKNOWN",
        "category": category,
        "product_type": product_type,
        "image_url": image_url if image_valid else None,
        "image_validated": image_valid,
        
        # ===== Pricing (do source) =====
        "pricing": {
            "cost_price_brl": source_sku.get("cost_price", 0.0),
            "final_price_brl": source_sku.get("final_price", 0.0),
            "strategy": "dynamic_v1",
            "kpis": source_sku.get("kpis", {}),
        },
        
        # ===== Legal & Strategic (placeholders + specs conhecidas) =====
        "legal_strategic": {
            "aneel_inmetro_registry": None,  # A ser preenchido
            "warranty_years": tech_specs.get("warranty_years", 10) if tech_specs else 10,
            "degradation_rate_percent_y": (
                tech_specs.get("degradation_rate_percent_y", 0.50) if tech_specs else 0.50
            ),
            "maintenance_schedule": {
                "cleaning_interval_months": 6,
                "inspection_interval_months": 12,
            },
        },
        
        # ===== Specs Technical Sheet =====
        "specs_technical_sheet": {},
        
        # ===== Location Analysis (placeholder - a ser preenchido por lat/lng) =====
        "location_analysis": {
            "location": {"lat": None, "lng": None},
            "source_pvgis": None,
            "source_nasa_power": None,
        },
        
        # ===== Operational Anomalies (placeholder) =====
        "operational_anomalies": {
            "last_inspection_id": None,
            "status": "NO_DATA",
            "active_anomalies": [],
        },
        
        # ===== Metadados =====
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "data_version": "1.0.0",
        "source_file": "enriched-skus-for-dynamodb-images-fixed.json",
    }
    
    # Preenche specs técnicas se disponíveis
    if tech_specs:
        digital_twin["specs_technical_sheet"] = {
            "physical": {
                "dimensions_mm": tech_specs.get("dimensions_mm"),
                "weight_kg": tech_specs.get("weight_kg"),
                "area_m2": None,  # Calcular se necessário
                "ip_rating": tech_specs.get("ip_rating"),
                "operating_temp_c": tech_specs.get("operating_temp_c"),
            },
            "electrical_ref": {
                "p_mp_ref_w": tech_specs.get("power_kw", 0) * 1000 if "power_kw" in tech_specs else tech_specs.get("power_w"),
                "v_oc_ref_v": tech_specs.get("voltage_v") or tech_specs.get("voltage_v_oc"),
                "i_sc_ref_a": tech_specs.get("current_a_sc"),
                "v_mp_ref_v": tech_specs.get("voltage_v_mp"),
                "i_mp_ref_a": tech_specs.get("current_a_mp"),
                "efficiency_percent": tech_specs.get("efficiency_percent"),
                "mppt_count": tech_specs.get("mppt_count"),
                "mppt_voltage_range_v": tech_specs.get("mppt_voltage_range_v"),
                "cell_technology": tech_specs.get("cell_technology"),
            },
            "thermal": {
                "t_noct_c": tech_specs.get("t_noct_c"),
                "alpha_sc_percent_c": tech_specs.get("alpha_sc_percent_c"),
                "beta_oc_percent_c": tech_specs.get("beta_oc_percent_c"),
                "gamma_r_percent_c": tech_specs.get("gamma_r_percent_c"),
            },
            "pvlib_desoto_model": {
                "a_ref": None,  # Calcular ou importar
                "i_l_ref_a": None,
                "i_o_ref_a": None,
                "r_s_ohms": None,
                "r_sh_ref_ohms": None,
            },
        }
    
    return digital_twin


# ==================== Main ====================


def main():
    print("🚀 Gerando Digital Twin SKUs...")
    print(f"📂 Input: {INPUT_FILE}")
    print(f"📤 Output: {OUTPUT_FILE}")
    print(f"☁️  S3 Bucket: {S3_BUCKET} ({S3_REGION})")
    
    # Inicializa S3 client
    try:
        s3_client = boto3.client("s3", region_name=S3_REGION)
        print("✅ Conectado ao S3")
    except Exception as e:
        print(f"⚠️  Erro ao conectar S3: {e}")
        print("   Continuando sem validação de imagens...")
        s3_client = None
    
    # Carrega dados de entrada
    print(f"\n📖 Carregando SKUs de {INPUT_FILE.name}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        source_skus = json.load(f)
    
    print(f"   Total de SKUs: {len(source_skus)}")
    
    # Gera Digital Twins
    print("\n🔄 Gerando Digital Twin SKUs...")
    digital_twins: List[Dict[str, Any]] = []
    
    stats = {
        "total": len(source_skus),
        "processed": 0,
        "with_specs": 0,
        "with_valid_images": 0,
        "inversores": 0,
        "paineis": 0,
        "kits": 0,
        "outros": 0,
    }
    
    for idx, source_sku in enumerate(source_skus):
        if (idx + 1) % 100 == 0:
            print(f"   Processando: {idx + 1}/{stats['total']}...")
        
        try:
            dt_sku = generate_digital_twin_sku(
                source_sku,
                s3_client,
                S3_BUCKET,
                validate_images=(s3_client is not None),
            )
            
            digital_twins.append(dt_sku)
            stats["processed"] += 1
            
            if dt_sku.get("specs_technical_sheet"):
                stats["with_specs"] += 1
            
            if dt_sku.get("image_validated"):
                stats["with_valid_images"] += 1
            
            # Contadores por tipo
            product_type = dt_sku.get("product_type", "")
            if "inversor" in product_type:
                stats["inversores"] += 1
            elif "painel" in product_type:
                stats["paineis"] += 1
            elif "kit" in product_type:
                stats["kits"] += 1
            else:
                stats["outros"] += 1
        
        except Exception as e:
            print(f"   ⚠️  Erro no SKU {source_sku.get('sku')}: {e}")
    
    # Salva resultado
    print(f"\n💾 Salvando {len(digital_twins)} Digital Twin SKUs em {OUTPUT_FILE.name}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(digital_twins, f, ensure_ascii=False, indent=2)
    
    # Estatísticas finais
    print("\n" + "=" * 60)
    print("📊 ESTATÍSTICAS FINAIS")
    print("=" * 60)
    print(f"Total de SKUs de entrada:      {stats['total']:>8}")
    print(f"SKUs processados:              {stats['processed']:>8}")
    print(f"SKUs com specs técnicas:       {stats['with_specs']:>8}")
    print(f"SKUs com imagens válidas (S3): {stats['with_valid_images']:>8}")
    print()
    print("Por tipo de produto:")
    print(f"  Inversores:                  {stats['inversores']:>8}")
    print(f"  Painéis Solares:             {stats['paineis']:>8}")
    print(f"  Kits Completos:              {stats['kits']:>8}")
    print(f"  Outros componentes:          {stats['outros']:>8}")
    print("=" * 60)
    print()
    print(f"✅ Arquivo gerado: {OUTPUT_FILE}")
    print("\n🎯 Próximos passos:")
    print("   1. Enriquecer com dados PVLIB (location_analysis.source_pvgis)")
    print("   2. Enriquecer com dados NASA POWER (location_analysis.source_nasa_power)")
    print("   3. Subir para DynamoDB/RDS com estrutura completa")


if __name__ == "__main__":
    main()
