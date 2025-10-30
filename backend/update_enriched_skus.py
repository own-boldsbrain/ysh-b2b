"""
Update enriched-skus-for-dynamodb.json with manufacturer URLs from manufacturers_urls_database.json
Focus on Huawei and Deye products
"""

import json
from pathlib import Path

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_manufacturer_urls(manufacturers_db):
    """Extract URLs for Huawei and Deye models"""
    urls = {}

    for manufacturer_key, manufacturer_data in manufacturers_db['manufacturers'].items():
        if manufacturer_key.lower() in ['huawei', 'deye']:
            manufacturer_name = manufacturer_key.upper()
            urls[manufacturer_name] = {}

            for line_key, line_data in manufacturer_data.get('product_lines', {}).items():
                if 'models' in line_data:
                    for model in line_data['models']:
                        model_name = model['name']
                        # Clean model name for matching
                        clean_name = model_name.replace('SUN2000-', '').replace('SUN-', '').replace('/', '').replace('.', '').upper()
                        urls[manufacturer_name][clean_name] = {
                            'product_page': model.get('product_page', ''),
                            'datasheet_url': model.get('datasheet_url', '')
                        }

    return urls

def update_product_urls(products, manufacturer_urls):
    """Update products with manufacturer URLs"""
    updated_count = 0
    huawei_count = 0
    deye_count = 0
    import re

    for product in products:
        manufacturer = product.get('manufacturer', '').upper()
        sku = product.get('sku', '').upper()

        if manufacturer == 'HUAWEI':
            huawei_count += 1
        elif manufacturer == 'DEYE':
            deye_count += 1

        if manufacturer in manufacturer_urls:
            model_in_sku = ''

            if manufacturer == 'HUAWEI':
                # Extract model from HUAWEI SKU like HUAWEISUN20003KTLL1AFCIIMAGEPRODUCT600382
                match = re.search(r'SUN2000(\w+)', sku)
                if match:
                    model_in_sku = match.group(1).upper()
            elif manufacturer == 'DEYE':
                # Extract model from DEYE SKU like DEYESUN75KG01P3LVIMAGE
                match = re.search(r'SUN(\w+)IMAGE', sku)
                if match:
                    model_in_sku = match.group(1).upper()

            if model_in_sku:
                # Find matching model
                for model_key, urls in manufacturer_urls[manufacturer].items():
                    if model_key in model_in_sku or model_in_sku in model_key:
                        product['product_page'] = urls['product_page']
                        if urls['datasheet_url']:
                            product['datasheet_url'] = urls['datasheet_url']
                        updated_count += 1
                        break

            # Fallback: add general manufacturer URLs
            if 'product_page' not in product:
                if manufacturer == 'HUAWEI':
                    product['manufacturer_website'] = 'https://solar.huawei.com/br/'
                    updated_count += 1
                elif manufacturer == 'DEYE':
                    product['manufacturer_website'] = 'https://pt.deyeinverter.com/'
                    updated_count += 1

    print(f"Huawei products: {huawei_count}")
    print(f"Deye products: {deye_count}")
    return updated_count

def main():
    base_path = Path(__file__).parent

    # Load data
    enriched_file = base_path / 'enriched-skus-for-dynamodb.json'
    manufacturers_file = base_path / 'data' / 'manufacturers_urls_database.json'

    print("Loading enriched SKUs...")
    enriched_data = load_json(enriched_file)

    print("Loading manufacturers database...")
    manufacturers_data = load_json(manufacturers_file)

    # Extract URLs
    manufacturer_urls = extract_manufacturer_urls(manufacturers_data)
    print(f"Extracted URLs for {len(manufacturer_urls)} manufacturers")

    # Update products
    updated_count = update_product_urls(enriched_data, manufacturer_urls)
    print(f"Updated {updated_count} products with URLs")

    # Save updated data
    output_file = base_path / 'enriched-skus-for-dynamodb-updated.json'
    save_json(enriched_data, output_file)
    print(f"Saved updated data to {output_file}")

if __name__ == "__main__":
    main()