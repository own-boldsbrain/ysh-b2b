# 🚀 Upload ANEEL Datasets para Hugging Face

## Status Atual
- ✅ **210 arquivos CSV** prontos em `aneel_datasets/`
- ✅ Script `upload_to_huggingface.py` configurado
- ✅ `huggingface_hub[cli]` instalado
- ⚠️ **Login pendente** - Requer token de acesso

## Pré-requisitos

### 1. Obter Token Hugging Face
1. Acesse: https://huggingface.co/settings/tokens
2. Clique em **"New token"**
3. Nome: `aneel-datasets-upload`
4. Tipo: **Write**
5. Copie o token gerado (ex: `hf_xxxxxxxxxxxxx`)

### 2. Fazer Login

#### Opção A: Login Interativo (Recomendado)
```powershell
cd data/project-helios
C:/Python314/python.exe -m huggingface_hub.commands.huggingface_cli login
# Cole o token quando solicitado
```

#### Opção B: Login via Token Direto
```powershell
$env:HUGGING_FACE_HUB_TOKEN="hf_seu_token_aqui"
C:/Python314/python.exe -c "from huggingface_hub import HfApi; HfApi(token='$env:HUGGING_FACE_HUB_TOKEN').whoami()"
```

### 3. Executar Upload

```powershell
cd data/project-helios
C:/Python314/python.exe upload_to_huggingface.py
```

## Script de Upload

O script `upload_to_huggingface.py`:
1. Cria repositório: `fernando-bold/aneel-datasets`
2. Faz upload de todos os 210 CSVs
3. Dataset ficará público no Hugging Face Hub

## Estrutura do Dataset

```
fernando-bold/aneel-datasets/
├── indice-aneel-satisfacao-consumidor.csv
├── ouvidoria-aneel-2014~2025.csv (12 arquivos)
├── samp-2003~2025.csv (23 arquivos)
├── componentes-tarifarias-2012~2025.csv (14 arquivos)
├── banco-preco-referencia-*.csv (16 arquivos)
├── interrupcoes-energia-eletrica-2017~2025.csv (9 arquivos)
└── ... (145+ arquivos adicionais)
```

## Próximos Passos

1. **Login no Hugging Face** (ação manual necessária)
2. **Executar upload** (`python upload_to_huggingface.py`)
3. **Verificar no Hub**: https://huggingface.co/datasets/fernando-bold/aneel-datasets

## Integração com MCP

Após upload, o dataset estará disponível via:
- Hugging Face Datasets API
- MCP Hugging Face Server
- APIs REST do Hugging Face Hub

## Troubleshooting

### Erro: "Not logged in"
```powershell
C:/Python314/python.exe -m huggingface_hub.commands.huggingface_cli login
```

### Erro: "Repository already exists"
- Normal na segunda execução
- Script continua com upload dos arquivos

### Timeout durante upload
- Arquivos grandes podem demorar
- Script processa todos os 210 CSVs sequencialmente
- Estimativa: 5-10 minutos para upload completo

## Comandos Úteis

```powershell
# Verificar login
C:/Python314/python.exe -m huggingface_hub.commands.huggingface_cli whoami

# Listar datasets do usuário
C:/Python314/python.exe -c "from huggingface_hub import HfApi; print([d.id for d in HfApi().list_datasets(author='fernando-bold')])"

# Testar acesso ao dataset após upload
C:/Python314/python.exe -c "from datasets import load_dataset; ds = load_dataset('fernando-bold/aneel-datasets', data_files='indice-aneel-satisfacao-consumidor.csv'); print(ds)"
```

---

**Task**: C-06 - Upload ANEEL datasets para Hugging Face  
**Prioridade**: CRÍTICA (bloqueia integração MCP ANEEL)  
**Ação Requerida**: Login manual do usuário com token HF
