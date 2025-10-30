import json

# Carregar dados
with open(
    r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\products-inventory-backup-20251017-134630\distributors\fortlev\fortlev-inverters.json",
    "r",
    encoding="utf-8",
) as f:
    data = json.load(f)

# Códigos não encontrados
missing_codes = [
    "IIN00126",
    "IIN00224",
    "IIN00225",
    "IIN00232",
    "IIN00301",
    "IIN00316",
    "IIN00342",
    "IIN00349",
    "IIN00352",
    "IIN00364",
    "IIN00365",
    "IIN00366",
    "IIN00367",
    "IIN00368",
    "IIN00370",
    "IIN00376",
    "IIN00377",
    "IIN00379",
    "IIN00386",
]

print("Procurando códigos não mapeados no JSON...\n")
found = []
for product in data:
    image_url = product.get("image", "")
    for code in missing_codes:
        if code in image_url:
            found.append(code)
            print(f"✓ {code} ENCONTRADO:")
            print(f"  ID: {product['id']}")
            print(f"  Nome: {product['name']}")
            print(f"  Imagem: {image_url}")
            print()

not_in_json = [c for c in missing_codes if c not in found]
print(f"\n{len(not_in_json)} códigos NÃO estão no JSON:")
for code in not_in_json:
    print(f"  - {code}")
