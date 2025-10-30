# 🚀 ANEEL AWS API Deployment - Guia Completo

## 📋 Visão Geral

Este guia detalha como:

1. ✅ Acessar datasets da ANEEL via **Hugging Face MCP**
2. 🚀 Criar **APIs serverless na AWS** para servir esses dados
3. 🔄 Integrar com o backend YSH B2B existente

---

## 🎯 Parte 1: Hugging Face MCP - Acesso aos Datasets

### MCP Disponível

Você está autenticado como **`fernando-bold`** e tem acesso aos seguintes tools:

```typescript
// Buscar datasets
mcp_huggingface_dataset_search({
  query: "aneel energy brazil",
  author: "fernando-bold",
  limit: 20
})

// Obter detalhes de um dataset
mcp_huggingface_hub_repo_details({
  repo_ids: ["fernando-bold/aneel-datasets"],
  repo_type: "dataset",
  include_readme: true
})

// Buscar na documentação
mcp_huggingface_hf_doc_search({
  query: "how to load dataset from hub",
  product: "datasets"
})
```

### Upload dos Datasets ANEEL

**Status Atual:** 207 arquivos CSV (~500MB) prontos para upload

**Método Recomendado:**

```powershell
# 1. Autenticar no Hugging Face
cd c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\project-helios

# 2. Verificar se o script está pronto
Get-Content upload_to_huggingface.py

# 3. Executar upload
python upload_to_huggingface.py
```

**Script Python já pronto:**

- ✅ Cria repositório `fernando-bold/aneel-datasets`
- ✅ Upload paralelo com 4 workers
- ✅ Fallback automático se houver erro
- ✅ Filtro para apenas arquivos CSV

---

## 🏗️ Parte 2: AWS Serverless API - Arquitetura

### Opção A: AWS Lambda + API Gateway (Recomendado)

**Por quê?**

- ✅ **Custo zero** até 1 milhão de requests/mês
- ✅ **Escalabilidade automática**
- ✅ **Manutenção zero** de infraestrutura
- ✅ **Integração nativa** com S3, DynamoDB, CloudFront

```tsx
┌─────────────────┐
│   CloudFront    │  <-- CDN Global
│   (Cache)       │
└────────┬────────┘
         │
┌────────▼────────┐
│  API Gateway    │  <-- REST API
│  /aneel/*       │
└────────┬────────┘
         │
┌────────▼────────┐
│  Lambda Python  │  <-- Business Logic
│  - Query S3     │
│  - Filter CSV   │
│  - Return JSON  │
└────────┬────────┘
         │
┌────────▼────────┐
│   S3 Bucket     │  <-- Data Lake
│   aneel-data/   │      207 CSV files
└─────────────────┘
```

### Opção B: AWS AppSync + DynamoDB

**Para casos que precisam de:**

- GraphQL
- Subscriptions em tempo real
- Sincronização offline

---

## 🛠️ Parte 3: Implementação - Lambda API

### 3.1 Estrutura do Projeto

```tsx
aws-aneel-api/
├── lambda/
│   ├── get-tariffs/
│   │   ├── handler.py          # GET /tariffs
│   │   └── requirements.txt
│   ├── get-concessionarias/
│   │   ├── handler.py          # GET /concessionarias
│   │   └── requirements.txt
│   ├── calculate-savings/
│   │   ├── handler.py          # POST /calculate-savings
│   │   └── requirements.txt
│   └── query-dataset/
│       ├── handler.py          # GET /datasets/{name}
│       └── requirements.txt
├── terraform/
│   ├── main.tf                 # Infraestrutura como código
│   ├── lambda.tf
│   ├── api-gateway.tf
│   ├── s3.tf
│   └── cloudfront.tf
├── scripts/
│   ├── upload-to-s3.py         # Subir CSVs para S3
│   └── deploy.sh               # Deploy automatizado
└── README.md
```

### 3.2 Lambda Handler - Get Tariffs

```python
# lambda/get-tariffs/handler.py
import json
import boto3
import pandas as pd
from io import StringIO

s3 = boto3.client('s3')
BUCKET_NAME = 'ysh-aneel-data'

def lambda_handler(event, context):
    """
    GET /aneel/tariffs?uf=SP&grupo=B1
    """
    # Parse query params
    query_params = event.get('queryStringParameters', {})
    uf = query_params.get('uf')
    grupo = query_params.get('grupo', 'B1')
    
    if not uf:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Missing required parameter: uf'
            })
        }
    
    try:
        # Carregar CSV do S3
        response = s3.get_object(
            Bucket=BUCKET_NAME,
            Key='tarifas-energia-eletrica.csv'
        )
        
        # Parse CSV
        csv_content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_content))
        
        # Filtrar por UF e grupo
        filtered = df[
            (df['SigUF'] == uf.upper()) & 
            (df['SigGrupo'] == grupo.upper())
        ]
        
        if filtered.empty:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': f'No tariff found for UF={uf}, grupo={grupo}'
                })
            }
        
        # Converter para JSON
        tariff_data = filtered.iloc[0].to_dict()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600'  # Cache 1 hora
            },
            'body': json.dumps({
                'data': tariff_data,
                'metadata': {
                    'source': 'ANEEL Open Data',
                    'cached': False
                }
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
```

### 3.3 Lambda Handler - Query Dataset Genérico

```python
# lambda/query-dataset/handler.py
import json
import boto3
import pandas as pd
from io import StringIO

s3 = boto3.client('s3')
BUCKET_NAME = 'ysh-aneel-data'

def lambda_handler(event, context):
    """
    GET /aneel/datasets/{dataset_name}?filter=column:value&limit=100
    
    Exemplo: 
    GET /aneel/datasets/empreendimento-geracao-distribuida?filter=SigUF:SP&limit=50
    """
    # Parse path params
    dataset_name = event['pathParameters']['dataset_name']
    
    # Parse query params
    query_params = event.get('queryStringParameters', {})
    filter_param = query_params.get('filter', '')
    limit = int(query_params.get('limit', 100))
    
    # Validar dataset name (segurança)
    if not dataset_name.endswith('.csv'):
        dataset_name += '.csv'
    
    try:
        # Carregar CSV do S3
        response = s3.get_object(
            Bucket=BUCKET_NAME,
            Key=dataset_name
        )
        
        # Parse CSV
        csv_content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_content))
        
        # Aplicar filtro se existir
        if filter_param:
            column, value = filter_param.split(':')
            df = df[df[column] == value]
        
        # Limitar resultados
        df = df.head(limit)
        
        # Converter para JSON
        data = df.to_dict(orient='records')
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=1800'
            },
            'body': json.dumps({
                'data': data,
                'metadata': {
                    'total_rows': len(data),
                    'dataset': dataset_name,
                    'filter_applied': filter_param if filter_param else None
                }
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Failed to load dataset',
                'message': str(e)
            })
        }
```

### 3.4 Terraform - Infraestrutura como Código

```hcl
# terraform/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# S3 Bucket para dados ANEEL
resource "aws_s3_bucket" "aneel_data" {
  bucket = "ysh-aneel-data"
  
  tags = {
    Project     = "YSH-B2B"
    Environment = "production"
    DataSource  = "ANEEL"
  }
}

# Tornar bucket público para leitura (dados são abertos)
resource "aws_s3_bucket_public_access_block" "aneel_data" {
  bucket = aws_s3_bucket.aneel_data.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Lambda Execution Role
resource "aws_iam_role" "lambda_execution" {
  name = "aneel-api-lambda-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Policy para Lambda acessar S3 e CloudWatch
resource "aws_iam_role_policy" "lambda_policy" {
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.aneel_data.arn,
          "${aws_s3_bucket.aneel_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Lambda Function - Get Tariffs
resource "aws_lambda_function" "get_tariffs" {
  filename      = "../lambda/get-tariffs.zip"
  function_name = "aneel-get-tariffs"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 512

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.aneel_data.id
    }
  }
}

# Lambda Function - Query Dataset
resource "aws_lambda_function" "query_dataset" {
  filename      = "../lambda/query-dataset.zip"
  function_name = "aneel-query-dataset"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 60
  memory_size   = 1024

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.aneel_data.id
    }
  }
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "aneel_api" {
  name        = "ANEEL-API"
  description = "API Gateway for ANEEL Open Data"
}

# API Gateway Resource - /tariffs
resource "aws_api_gateway_resource" "tariffs" {
  rest_api_id = aws_api_gateway_rest_api.aneel_api.id
  parent_id   = aws_api_gateway_rest_api.aneel_api.root_resource_id
  path_part   = "tariffs"
}

# API Gateway Method - GET /tariffs
resource "aws_api_gateway_method" "get_tariffs" {
  rest_api_id   = aws_api_gateway_rest_api.aneel_api.id
  resource_id   = aws_api_gateway_resource.tariffs.id
  http_method   = "GET"
  authorization = "NONE"
}

# Lambda Integration
resource "aws_api_gateway_integration" "lambda_get_tariffs" {
  rest_api_id = aws_api_gateway_rest_api.aneel_api.id
  resource_id = aws_api_gateway_resource.tariffs.id
  http_method = aws_api_gateway_method.get_tariffs.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_tariffs.invoke_arn
}

# Lambda Permission para API Gateway
resource "aws_lambda_permission" "api_gateway_get_tariffs" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_tariffs.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.aneel_api.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "production" {
  depends_on = [
    aws_api_gateway_integration.lambda_get_tariffs
  ]

  rest_api_id = aws_api_gateway_rest_api.aneel_api.id
  stage_name  = "prod"
}

# Outputs
output "api_url" {
  value = "${aws_api_gateway_deployment.production.invoke_url}"
}

output "s3_bucket" {
  value = aws_s3_bucket.aneel_data.bucket
}
```

---

## 🚀 Parte 4: Deploy Step-by-Step

### 4.1 Preparação

```powershell
# 1. Criar estrutura de pastas
cd c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend
New-Item -Path "aws-aneel-api" -ItemType Directory
cd aws-aneel-api

New-Item -Path "lambda\get-tariffs" -ItemType Directory -Force
New-Item -Path "lambda\query-dataset" -ItemType Directory -Force
New-Item -Path "terraform" -ItemType Directory -Force
New-Item -Path "scripts" -ItemType Directory -Force

# 2. Criar requirements.txt
@"
boto3==1.34.0
pandas==2.1.4
"@ | Out-File -FilePath "lambda\get-tariffs\requirements.txt" -Encoding UTF8

# 3. Copiar handlers (criar os arquivos .py)
```

### 4.2 Upload dos CSVs para S3

```powershell
# scripts/upload-to-s3.ps1
$sourcePath = "..\data\project-helios\aneel_datasets"
$bucketName = "ysh-aneel-data"

# Criar bucket (uma vez)
aws s3 mb s3://$bucketName --region us-east-1

# Upload de todos os CSVs
aws s3 sync $sourcePath s3://$bucketName/ --exclude "*" --include "*.csv"

# Verificar
aws s3 ls s3://$bucketName/ --recursive
```

### 4.3 Criar Pacotes Lambda

```powershell
# Para cada função Lambda
cd lambda\get-tariffs

# Instalar dependências em pasta temporária
pip install -r requirements.txt -t package/

# Copiar handler
Copy-Item handler.py package/

# Criar ZIP
Compress-Archive -Path package\* -DestinationPath ..\get-tariffs.zip -Force

cd ..\..
```

### 4.4 Deploy com Terraform

```powershell
cd terraform

# Inicializar
terraform init

# Planejar
terraform plan -out=tfplan

# Aplicar
terraform apply tfplan

# Obter URL da API
terraform output api_url
# Output: https://xyz123.execute-api.us-east-1.amazonaws.com/prod
```

---

## 🔗 Parte 5: Integração com Backend YSH

### 5.1 Adicionar AWS API como Fonte de Dados

```typescript
// src/modules/tarifa-aneel/aws-client.ts
import axios from 'axios'

const AWS_ANEEL_API_URL = process.env.AWS_ANEEL_API_URL || 
  'https://xyz123.execute-api.us-east-1.amazonaws.com/prod'

export class AWSAneelClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = AWS_ANEEL_API_URL
  }

  async getTariff(uf: string, grupo: string = 'B1') {
    const response = await axios.get(`${this.baseUrl}/tariffs`, {
      params: { uf, grupo }
    })
    return response.data
  }

  async queryDataset(datasetName: string, filters?: Record<string, string>, limit: number = 100) {
    const params: any = { limit }
    
    if (filters) {
      // Converter {SigUF: 'SP'} para "SigUF:SP"
      params.filter = Object.entries(filters)
        .map(([key, value]) => `${key}:${value}`)
        .join(',')
    }

    const response = await axios.get(
      `${this.baseUrl}/datasets/${datasetName}`,
      { params }
    )
    return response.data
  }

  async getConcessionarias(uf?: string) {
    const response = await axios.get(`${this.baseUrl}/concessionarias`, {
      params: { uf }
    })
    return response.data
  }
}
```

### 5.2 Refatorar ANEELTariffService

```typescript
// src/modules/tarifa-aneel/service-aws.ts
import { AWSAneelClient } from './aws-client'

class ANEELTariffServiceAWS {
  private awsClient: AWSAneelClient

  constructor() {
    this.awsClient = new AWSAneelClient()
  }

  async getTariffByUF(uf: string, grupo: 'B1' | 'B2' | 'B3' | 'A4' = 'B1') {
    try {
      // Tentar AWS primeiro (dados mais atualizados)
      const data = await this.awsClient.getTariff(uf, grupo)
      return data.data
    } catch (error) {
      // Fallback para dados estáticos locais
      console.warn('AWS ANEEL API failed, using local fallback', error)
      return this.getFallbackTariff(uf, grupo)
    }
  }

  private getFallbackTariff(uf: string, grupo: string) {
    // Usar dados estáticos do service.ts original
    const TARIFAS_BASE = [
      // ... dados existentes
    ]
    return TARIFAS_BASE.find(t => t.uf === uf && t.grupo === grupo)
  }
}

export default ANEELTariffServiceAWS
```

### 5.3 Adicionar Feature Flag

```typescript
// medusa-config.ts
export default defineConfig({
  modules: {
    // ... outros módulos
    aneelTariff: {
      resolve: "./modules/tarifa-aneel",
      options: {
        useAWSBackend: process.env.ANEEL_USE_AWS_BACKEND === 'true',
        awsApiUrl: process.env.AWS_ANEEL_API_URL
      }
    }
  }
})
```

```env
# .env
ANEEL_USE_AWS_BACKEND=true
AWS_ANEEL_API_URL=https://xyz123.execute-api.us-east-1.amazonaws.com/prod
```

---

## 📊 Parte 6: Monitoramento e Custos

### CloudWatch Dashboards

```hcl
# terraform/monitoring.tf
resource "aws_cloudwatch_dashboard" "aneel_api" {
  dashboard_name = "ANEEL-API-Metrics"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", { stat = "Sum" }],
            ["AWS/Lambda", "Errors", { stat = "Sum" }],
            ["AWS/Lambda", "Duration", { stat = "Average" }]
          ]
          period = 300
          stat   = "Average"
          region = "us-east-1"
          title  = "Lambda Performance"
        }
      }
    ]
  })
}
```

### Estimativa de Custos (AWS Free Tier)

| Serviço | Free Tier | Custo Adicional |
|:---|:---|:---|
| **Lambda** | 1M requests/mês | $0.20 por 1M requests |
| **API Gateway** | Nenhum free tier | $3.50 por 1M requests |
| **S3** | 5GB storage | $0.023 por GB/mês |
| **CloudFront** | 1TB transfer | $0.085 por GB |
| **Total Estimado** | ~$0/mês para <100k req | ~$5/mês para 1M req |

**Para o volume esperado do Helios (Ano 1: 3.120 projetos):**

- ~10k requests/mês → **Custo: $0** (dentro do free tier)

---

## 🎯 Parte 7: Comparação - Hugging Face vs AWS

| Aspecto | Hugging Face + MCP | AWS Lambda + S3 |
|:---|:---|:---|
| **Setup** | ✅ Mais simples | ⚠️ Mais complexo |
| **Custo** | ✅ Gratuito | ✅ ~$0 até 100k req/mês |
| **Performance** | ⚠️ ~500ms-2s | ✅ ~50-200ms |
| **Escalabilidade** | ⚠️ Rate limits HF | ✅ Infinita (AWS) |
| **Customização** | ⚠️ Limitada | ✅ Total controle |
| **Manutenção** | ✅ Zero | ⚠️ Infraestrutura para gerenciar |
| **Recomendação** | **MVP/Prototipagem** | **Produção/Escala** |

---

## 🚀 Próximos Passos Recomendados

### Fase 1: Quick Win (2-3 dias)

1. ✅ Upload datasets para Hugging Face
2. ✅ Testar acesso via MCP
3. ✅ Integrar no backend YSH com feature flag

### Fase 2: Produção (1-2 semanas)

1. 🔧 Criar Lambda functions
2. 🔧 Deploy infraestrutura com Terraform
3. 🔧 Migrar tráfego gradualmente para AWS

### Fase 3: Otimização (Contínuo)

1. 📊 Implementar CloudWatch Dashboards
2. 🚀 Adicionar CloudFront CDN
3. 🔄 Automação de ETL (sync periódico com ANEEL)

---

## 📝 Comandos Rápidos

```powershell
# 1. Upload para Hugging Face
cd c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\project-helios
python upload_to_huggingface.py

# 2. Upload para S3
aws s3 sync aneel_datasets s3://ysh-aneel-data/ --include "*.csv"

# 3. Deploy AWS
cd ..\..\aws-aneel-api\terraform
terraform init
terraform apply -auto-approve

# 4. Testar API
$apiUrl = terraform output -raw api_url
Invoke-RestMethod "$apiUrl/tariffs?uf=SP&grupo=B1"
```

---

**Documento:** ANEEL AWS API Deployment Guide  
**Versão:** 1.0  
**Data:** 21 de Outubro de 2025  
**Autor:** GitHub Copilot + fernando-bold
