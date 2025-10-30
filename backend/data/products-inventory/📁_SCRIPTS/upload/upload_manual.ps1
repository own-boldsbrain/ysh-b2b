# Upload para Hugging Face - PowerShell
# Configure seu token primeiro: $env:HF_TOKEN = 'seu_token'

$REPO_ID = "fernando-bold/ysh-solar-products-brazil"

# Verificar token
if (-not $env:HF_TOKEN) {
    Write-Host "❌ Token não configurado!" -ForegroundColor Red
    Write-Host "Configure com: `$env:HF_TOKEN = 'seu_token'" -ForegroundColor Yellow
    exit 1
}

# Instalar huggingface-cli se necessário
pip install -q huggingface_hub


# Lote 1: JSON Principal
Write-Host 'Uploading lote 1: JSON Principal' -ForegroundColor Cyan
huggingface-cli upload $REPO_ID 'unified_products.json' 'data/unified_products.json' --repo-type dataset
Start-Sleep -Seconds 1

# Lote 2: CSVs por Categoria
Write-Host 'Uploading lote 2: CSVs por Categoria' -ForegroundColor Cyan
huggingface-cli upload $REPO_ID 'exports\csv\all_products.csv' 'data/csv/categories/all_products.csv' --repo-type dataset
huggingface-cli upload $REPO_ID 'exports\csv\chargers.csv' 'data/csv/categories/chargers.csv' --repo-type dataset
huggingface-cli upload $REPO_ID 'exports\csv\kits.csv' 'data/csv/categories/kits.csv' --repo-type dataset
huggingface-cli upload $REPO_ID 'exports\csv\panels.csv' 'data/csv/categories/panels.csv' --repo-type dataset
huggingface-cli upload $REPO_ID 'exports\csv\products_with_batteries.csv' 'data/csv/categories/products_with_batteries.csv' --repo-type dataset
Start-Sleep -Seconds 1

# Lote 3: CSVs de Fabricantes
Write-Host 'Uploading lote 3: CSVs de Fabricantes' -ForegroundColor Cyan
huggingface-cli upload $REPO_ID 'exports\unified\manufacturer_BYD.csv' 'data/csv/manufacturers/manufacturer_BYD.csv' --repo-type dataset
huggingface-cli upload $REPO_ID 'exports\unified\manufacturer_Inverter_Enphase.csv' 'data/csv/manufacturers/manufacturer_Inverter_Enphase.csv' --repo-type dataset
huggingface-cli upload $REPO_ID 'exports\unified\manufacturer_Inverter_Growatt.csv' 'data/csv/manufacturers/manufacturer_Inverter_Growatt.csv' --repo-type dataset
huggingface-cli upload $REPO_ID 'exports\unified\manufacturer_Inverter_Sungrow.csv' 'data/csv/manufacturers/manufacturer_Inverter_Sungrow.csv' --repo-type dataset
huggingface-cli upload $REPO_ID 'exports\unified\manufacturer_Longi.csv' 'data/csv/manufacturers/manufacturer_Longi.csv' --repo-type dataset
huggingface-cli upload $REPO_ID 'exports\unified\manufacturer_Risen.csv' 'data/csv/manufacturers/manufacturer_Risen.csv' --repo-type dataset
Start-Sleep -Seconds 1

# Lote 4: CSVs de Categorias Unificadas
Write-Host 'Uploading lote 4: CSVs de Categorias Unificadas' -ForegroundColor Cyan
huggingface-cli upload $REPO_ID 'exports\unified\category_kits.csv' 'data/csv/unified_categories/category_kits.csv' --repo-type dataset
huggingface-cli upload $REPO_ID 'exports\unified\category_panels.csv' 'data/csv/unified_categories/category_panels.csv' --repo-type dataset
Start-Sleep -Seconds 1

# Lote 5: CSVs de Análise de Preços
Write-Host 'Uploading lote 5: CSVs de Análise de Preços' -ForegroundColor Cyan
huggingface-cli upload $REPO_ID 'exports\unified\price_comparison_multi_distributor.csv' 'data/csv/price_analysis/price_comparison_multi_distributor.csv' --repo-type dataset
huggingface-cli upload $REPO_ID 'exports\unified\panel_models_pricing.csv' 'data/csv/price_analysis/panel_models_pricing.csv' --repo-type dataset
Start-Sleep -Seconds 1

# Lote 6: CSV Mestre Unificado
Write-Host 'Uploading lote 6: CSV Mestre Unificado' -ForegroundColor Cyan
huggingface-cli upload $REPO_ID 'exports\unified\all_products_unified.csv' 'data/csv/all_products_unified.csv' --repo-type dataset
Start-Sleep -Seconds 1

Write-Host '✅ Upload concluído!' -ForegroundColor Green
