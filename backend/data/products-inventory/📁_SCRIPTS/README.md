# 📁 Scripts

Scripts organizados por funcionalidade.

## 📂 Estrutura

### 🔄 export/
Scripts de exportação de dados para CSV.

- `export_to_csv.py` - Exporta produtos para CSVs por categoria
- `create_unified_csvs.py` - Cria CSVs unificados por fabricante/preço

### 📤 upload/
Scripts de upload para Hugging Face.

- `upload_to_huggingface.py` - Upload inicial completo
- `update_huggingface_dataset.py` - Atualização incremental
- `check_upload_preparation.py` - Verificação pré-upload
- `fix_huggingface_readme.py` - Correção de metadata
- `upload_manual.ps1` - Script manual PowerShell

### 🔍 extraction/
Scripts de extração de dados dos distribuidores.

- `extract_datasheet_models.py` - Extrai modelos de datasheets
- `extract_manufacturers.py` - Extrai fabricantes
- `extract_technical_specs.py` - Extrai especificações técnicas
- `unified_product_extractor.py` - Extrator unificado

### 🔗 unification/
Scripts de unificação de catálogos.

- `unify_all_categories.py` - Unifica todas as categorias
- `unify_distributors.py` - Unifica dados de distribuidores

### 📊 analysis/
Scripts de análise e estatísticas.

- `generate_360_stats.py` - Gera estatísticas 360°

## 🚀 Uso

### Exportar CSVs
```bash
python export/export_to_csv.py
python export/create_unified_csvs.py
```

### Unificar Catálogos
```bash
python unification/unify_all_categories.py
```

### Upload HuggingFace
```bash
# Verificar
python upload/check_upload_preparation.py

# Upload
python upload/upload_to_huggingface.py

# Atualizar
python upload/update_huggingface_dataset.py
```

## 📝 Variáveis de Ambiente

Para scripts de upload:
```bash
export HF_TOKEN="seu_token_aqui"
```

Ou no PowerShell:
```powershell
$env:HF_TOKEN = "seu_token_aqui"
```
