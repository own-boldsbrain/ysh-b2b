# Instruções para Upload do Dataset ANEEL para Hugging Face

## 📦 Contexto

Baixamos com sucesso **207 arquivos CSV** (totalizando ~500MB) da ANEEL. Agora precisamos fazer o upload para o Hugging Face para facilitar o acesso via MCP.

## 🔐 Passo 1: Autenticação

### Opção A: Via CLI (Recomendado)

```bash
# Instalar se necessário
pip install huggingface_hub

# Login interativo
huggingface-cli login
```

### Opção B: Token de Acesso

1. Acesse: https://huggingface.co/settings/tokens
2. Crie um novo token com permissão de **write**
3. Configure via variável de ambiente:

```bash
# Windows PowerShell
$env:HUGGING_FACE_HUB_TOKEN = "hf_..."

# Linux/Mac
export HUGGING_FACE_HUB_TOKEN="hf_..."
```

### Opção C: Via Script Python

```python
from huggingface_hub import login
login(token="hf_...")
```

## 🚀 Passo 2: Upload

### Método 1: Script Python (Mais Rápido)

```bash
# Já criado: upload_to_huggingface.py
# Após autenticação, execute:
python upload_to_huggingface.py
```

### Método 2: CLI (Alternativa)

```bash
# Upload de pasta completa
huggingface-cli upload fernando-bold/aneel-datasets ./aneel_datasets --repo-type=dataset
```

### Método 3: Upload em Lotes (Para Pastas Grandes)

```python
from huggingface_hub import HfApi
api = HfApi()

# Upload em lotes de 10 arquivos
import os
csv_files = [f for f in os.listdir('aneel_datasets') if f.endswith('.csv')]

for i in range(0, len(csv_files), 10):
    batch = csv_files[i:i+10]
    for file in batch:
        api.upload_file(
            path_or_fileobj=f'aneel_datasets/{file}',
            path_in_repo=file,
            repo_id='fernando-bold/aneel-datasets',
            repo_type='dataset'
        )
    print(f"Uploaded batch {i//10 + 1}")
```

## 📝 Passo 3: Criar README do Dataset

Após o upload, crie um `README.md` no repositório:

```markdown
---
language:
- pt
license: cc0-1.0
size_categories:
- 100K<n<1M
task_categories:
- tabular-classification
- tabular-regression
tags:
- energy
- solar
- brazil
- aneel
- utilities
pretty_name: ANEEL Open Data Brazil
---

# ANEEL Open Data - Dados Abertos da Agência Nacional de Energia Elétrica

## Dataset Description

Official open data from ANEEL (Brazilian National Electric Energy Agency) containing 207 CSV files with comprehensive information about:

- Distributed Generation (DG) projects
- Utilities and transmission companies
- Tariffs and regulatory data
- Inspection and compliance records
- R&D and energy efficiency projects

## Dataset Structure

See full documentation in ANEEL_DATASETS_SUMMARY.md

## Usage

```python
from datasets import load_dataset

# Load specific file
dataset = load_dataset("fernando-bold/aneel-datasets", data_files="empreendimento-geracao-distribuida.csv")

# Or load all files
dataset = load_dataset("fernando-bold/aneel-datasets")
```

## Citation

```tsx
@misc{aneel_opendata_2025,
  title={ANEEL Open Data Brazil},
  author={ANEEL},
  year={2025},
  url={https://dadosabertos.aneel.gov.br/}
}
```
```

## 🔍 Passo 4: Verificação

Após o upload, verifique:
1. https://huggingface.co/datasets/fernando-bold/aneel-datasets
2. Teste o download:

```python
from datasets import load_dataset
ds = load_dataset("fernando-bold/aneel-datasets", data_files="empreendimento-geracao-distribuida.csv")
print(ds)
```

## 🐛 Troubleshooting

### Erro 401 Unauthorized

- Verifique o token de autenticação
- Confirme permissões de write no token
- Re-execute o login

### Erro 413 Request Entity Too Large

- Use upload em lotes (Método 3)
- Considere comprimir arquivos maiores

### Timeout

- Aumente o timeout: `api.upload_folder(..., timeout=3600)`
- Use conexão mais estável

## 📊 Alternativa: GitHub

Se o Hugging Face não funcionar, podemos usar o GitHub:

```bash
cd aneel_datasets
git init
git add .
git commit -m "Add ANEEL datasets"
gh repo create aneel-datasets --public --source=. --push
```

---

**Status:** Aguardando autenticação no Hugging Face  
**Prioridade:** Alta  
**Impacto:** Essencial para consumo via MCP
