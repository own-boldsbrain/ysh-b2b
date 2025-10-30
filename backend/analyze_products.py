import json
import collections
from pathlib import Path

# Caminho para o arquivo de dados unificado
file_path = Path("data/products-inventory/unified_products.json")

# Dicionário para armazenar a análise de saúde
health_analysis = {
    "total_products": 0,
    "readiness": {
        "medusa": {"ready": 0, "issues": 0},
        "facebook": {"ready": 0, "issues": 0},
    },
    "issues_by_product": {},
    "data_quality": {
        "missing_name": 0,
        "missing_category": 0,
        "missing_price": 0,
        "missing_distributor": 0,
        "missing_manufacturer": 0,
        "missing_image": 0,
        "missing_description": 0,
        "inconsistent_pricing": 0,
    },
}

# Carrega os dados
with file_path.open("r", encoding="utf-8") as f:
    data = json.load(f)

health_analysis["total_products"] = len(data)

# Entidades únicas
categories = set()
types = set()
distributors = set()
manufacturers = set()

for product in data:
    product_id = product.get("id", "unknown_id")
    issues = []

    # --- Análise de Qualidade dos Dados ---
    if not product.get("name"):
        health_analysis["data_quality"]["missing_name"] += 1
        issues.append("Missing 'name'")

    if not product.get("category"):
        health_analysis["data_quality"]["missing_category"] += 1
        issues.append("Missing 'category'")
    else:
        categories.add(product["category"])

    if not product.get("pricing", {}).get("price_brl"):
        health_analysis["data_quality"]["missing_price"] += 1
        issues.append("Missing 'price_brl'")

    if product.get("pricing", {}).get("price_brl", 0) <= 0:
        health_analysis["data_quality"]["inconsistent_pricing"] += 1
        issues.append("Invalid price (<= 0)")

    if not product.get("distributor"):
        health_analysis["data_quality"]["missing_distributor"] += 1
        issues.append("Missing 'distributor'")
    else:
        distributors.add(product["distributor"])

    if not product.get("description"):
        health_analysis["data_quality"]["missing_description"] += 1
        issues.append("Missing 'description'")

    # --- Análise de Componentes (Fabricantes) ---
    has_manufacturer = False
    components = product.get("components", {})
    for group in ["panels", "inverters", "batteries", "structures"]:
        for comp in components.get(group, []):
            if comp.get("manufacturer"):
                manufacturers.add(comp["manufacturer"].strip())
                has_manufacturer = True

    if not has_manufacturer:
        health_analysis["data_quality"]["missing_manufacturer"] += 1
        issues.append("No component has a 'manufacturer'")

    # --- Análise de Mídia ---
    if not product.get("media", {}).get("image_url") and not any(
        p.get("image_available") for p in components.get("panels", [])
    ):
        health_analysis["data_quality"]["missing_image"] += 1
        issues.append("Missing product or component image")

    # --- Avaliação de Prontidão (Readiness) ---
    # Medusa: requer nome, preço, categoria
    is_medusa_ready = (
        product.get("name")
        and product.get("pricing", {}).get("price_brl", 0) > 0
        and product.get("category")
    )
    if is_medusa_ready:
        health_analysis["readiness"]["medusa"]["ready"] += 1
    else:
        health_analysis["readiness"]["medusa"]["issues"] += 1

    # Facebook Commerce: requer nome, preço, descrição, imagem
    is_facebook_ready = (
        product.get("name")
        and product.get("pricing", {}).get("price_brl", 0) > 0
        and product.get("description")
        and (
            product.get("media", {}).get("image_url")
            or any(p.get("image_available") for p in components.get("panels", []))
        )
    )
    if is_facebook_ready:
        health_analysis["readiness"]["facebook"]["ready"] += 1
    else:
        health_analysis["readiness"]["facebook"]["issues"] += 1

    if issues:
        health_analysis["issues_by_product"][product_id] = issues

# --- Contagens para Top Lists ---
category_counts = collections.Counter(p["category"] for p in data if p.get("category"))
distributor_counts = collections.Counter(
    p["distributor"] for p in data if p.get("distributor")
)
manufacturer_counts = collections.Counter()
for p in data:
    comps = p.get("components", {})
    for group in ["panels", "inverters", "batteries", "structures"]:
        for comp in comps.get(group, []):
            if comp.get("manufacturer"):
                manufacturer_counts[comp["manufacturer"].strip()] += 1

# --- Impressão dos Resultados ---
print("--- Análise de Catálogo de Produtos ---")
print(f"\nTotal de Produtos Analisados: {health_analysis['total_products']}")

print("\n--- Entidades Únicas ---")
print(f"Categorias Únicas: {len(categories)}")
print(f"Tipos Únicos: Não analisado neste script")
print(f"Distribuidores Únicos: {len(distributors)}")
print(f"Fabricantes Únicos: {len(manufacturers)}")

print("\n--- Top 5 Entidades ---")
print("Top 5 Categorias:", category_counts.most_common(5))
print("Top 5 Distribuidores:", distributor_counts.most_common(5))
print("Top 5 Fabricantes (em componentes):", manufacturer_counts.most_common(5))

print("\n--- Saúde e Qualidade dos Dados ---")
for key, value in health_analysis["data_quality"].items():
    percentage = (
        (value / health_analysis["total_products"]) * 100
        if health_analysis["total_products"] > 0
        else 0
    )
    print(
        f"- {key.replace('_', ' ').title()}: {value} produtos afetados ({percentage:.2f}%)"
    )

print("\n--- Prontidão para Plataformas (Produção) ---")
medusa_ready_perc = (
    (
        health_analysis["readiness"]["medusa"]["ready"]
        / health_analysis["total_products"]
    )
    * 100
    if health_analysis["total_products"] > 0
    else 0
)
print(
    f"Medusa.js Marketplace: {health_analysis['readiness']['medusa']['ready']} produtos prontos ({medusa_ready_perc:.2f}%)"
)

facebook_ready_perc = (
    (
        health_analysis["readiness"]["facebook"]["ready"]
        / health_analysis["total_products"]
    )
    * 100
    if health_analysis["total_products"] > 0
    else 0
)
print(
    f"Facebook Commerce Platform: {health_analysis['readiness']['facebook']['ready']} produtos prontos ({facebook_ready_perc:.2f}%)"
)

# Salvar análise detalhada de problemas
with open("product_health_analysis.json", "w", encoding="utf-8") as f:
    json.dump(health_analysis, f, indent=2, ensure_ascii=False)

print("\nRelatório de saúde detalhado salvo em 'product_health_analysis.json'")
