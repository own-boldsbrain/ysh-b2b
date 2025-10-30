#!/usr/bin/env pwsh
# Deploy ANEEL API para AWS
# Execute: .\deploy-aws-aneel-api.ps1

param(
      [switch]$SkipUpload,
      [switch]$DestroyOnly
)

Write-Host "`n🚀 AWS ANEEL API Deployment Script" -ForegroundColor Green
Write-Host "===================================`n" -ForegroundColor Gray

$backendPath = "c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend"
$awsProjectPath = Join-Path $backendPath "aws-aneel-api"
$aneelDataPath = Join-Path $backendPath "data\project-helios\aneel_datasets"

# Destroy mode
if ($DestroyOnly) {
      Write-Host "🗑️  Modo Destruição: Removendo recursos AWS..." -ForegroundColor Red
      Set-Location (Join-Path $awsProjectPath "terraform")
      terraform destroy -auto-approve
      exit 0
}

# 1. Criar estrutura do projeto
Write-Host "📁 Criando estrutura do projeto..." -ForegroundColor Cyan

if (-not (Test-Path $awsProjectPath)) {
      New-Item -Path $awsProjectPath -ItemType Directory -Force | Out-Null
      Write-Host "✅ Criado: aws-aneel-api/" -ForegroundColor Green
}

$dirs = @(
      "lambda\get-tariffs",
      "lambda\query-dataset",
      "lambda\get-concessionarias",
      "lambda\calculate-savings",
      "terraform",
      "scripts"
)

foreach ($dir in $dirs) {
      $fullPath = Join-Path $awsProjectPath $dir
      if (-not (Test-Path $fullPath)) {
            New-Item -Path $fullPath -ItemType Directory -Force | Out-Null
            Write-Host "  ✅ $dir" -ForegroundColor Gray
      }
}

# 2. Upload para S3 (se não skipado)
if (-not $SkipUpload) {
      Write-Host "`n📦 Fazendo upload dos datasets para S3..." -ForegroundColor Cyan
    
      $bucketName = "ysh-aneel-data-$(Get-Date -Format 'yyyyMMdd')"
    
      # Criar bucket
      Write-Host "  Criando bucket: $bucketName" -ForegroundColor Gray
      aws s3 mb "s3://$bucketName" --region us-east-1 2>&1 | Out-Null
    
      if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Bucket criado" -ForegroundColor Green
      }
      else {
            Write-Host "  ⚠️  Bucket pode já existir, continuando..." -ForegroundColor Yellow
      }
    
      # Upload CSVs
      Write-Host "  Sincronizando arquivos CSV..." -ForegroundColor Gray
      aws s3 sync $aneelDataPath "s3://$bucketName/" --exclude "*" --include "*.csv" --quiet
    
      if ($LASTEXITCODE -eq 0) {
            $fileCount = (Get-ChildItem $aneelDataPath -Filter "*.csv").Count
            Write-Host "  ✅ $fileCount arquivos enviados para S3" -ForegroundColor Green
      }
      else {
            Write-Host "  ❌ Erro no upload para S3" -ForegroundColor Red
            exit 1
      }
}
else {
      Write-Host "`n⏭️  Upload S3 ignorado (flag -SkipUpload)" -ForegroundColor Yellow
      $bucketName = Read-Host "  Digite o nome do bucket S3 existente"
}

# 3. Criar Lambda Handlers
Write-Host "`n📝 Criando Lambda handlers..." -ForegroundColor Cyan

# Handler: Get Tariffs
$getTariffsHandler = @"
import json
import boto3
import os

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', '$bucketName')

def lambda_handler(event, context):
    query_params = event.get('queryStringParameters', {}) or {}
    uf = query_params.get('uf', '').upper()
    grupo = query_params.get('grupo', 'B1').upper()
    
    if not uf:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Missing required parameter: uf'})
        }
    
    # Mock data (substituir por leitura real do S3)
    mock_tariffs = {
        'SP': {'B1': 0.72, 'B2': 0.68, 'B3': 0.75, 'A4': 0.65},
        'RJ': {'B1': 0.89, 'B2': 0.85, 'B3': 0.92, 'A4': 0.78},
        'MG': {'B1': 0.78, 'B2': 0.74, 'B3': 0.81, 'A4': 0.69}
    }
    
    tarifa = mock_tariffs.get(uf, {}).get(grupo, 0.85)
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
            'data': {
                'uf': uf,
                'grupo': grupo,
                'tarifa_kwh': tarifa,
                'updated_at': '2025-10-21'
            }
        })
    }
"@

$getTariffsHandler | Out-File -FilePath (Join-Path $awsProjectPath "lambda\get-tariffs\handler.py") -Encoding UTF8
Write-Host "  ✅ get-tariffs/handler.py" -ForegroundColor Gray

# Handler: Query Dataset
$queryDatasetHandler = @"
import json
import boto3
import os

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', '$bucketName')

def lambda_handler(event, context):
    dataset_name = event.get('pathParameters', {}).get('dataset_name', '')
    
    if not dataset_name:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Missing dataset_name'})
        }
    
    # Lista datasets disponíveis
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, MaxKeys=100)
        files = [obj['Key'] for obj in response.get('Contents', [])]
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'dataset': dataset_name,
                'available_datasets': files[:10],
                'total': len(files)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
"@

$queryDatasetHandler | Out-File -FilePath (Join-Path $awsProjectPath "lambda\query-dataset\handler.py") -Encoding UTF8
Write-Host "  ✅ query-dataset/handler.py" -ForegroundColor Gray

# 4. Criar Terraform config
Write-Host "`n🏗️  Criando configuração Terraform..." -ForegroundColor Cyan

$terraformMain = @"
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

# Lambda Execution Role
resource "aws_iam_role" "lambda_execution" {
  name = "aneel-api-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda: Get Tariffs
data "archive_file" "get_tariffs" {
  type        = "zip"
  source_dir  = "../lambda/get-tariffs"
  output_path = "../lambda/get-tariffs.zip"
}

resource "aws_lambda_function" "get_tariffs" {
  filename         = data.archive_file.get_tariffs.output_path
  function_name    = "aneel-get-tariffs"
  role            = aws_iam_role.lambda_execution.arn
  handler         = "handler.lambda_handler"
  runtime         = "python3.11"
  source_code_hash = data.archive_file.get_tariffs.output_base64sha256
  timeout         = 30

  environment {
    variables = {
      BUCKET_NAME = "$bucketName"
    }
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "aneel_api" {
  name = "ANEEL-OpenData-API"
}

resource "aws_api_gateway_resource" "tariffs" {
  rest_api_id = aws_api_gateway_rest_api.aneel_api.id
  parent_id   = aws_api_gateway_rest_api.aneel_api.root_resource_id
  path_part   = "tariffs"
}

resource "aws_api_gateway_method" "get_tariffs" {
  rest_api_id   = aws_api_gateway_rest_api.aneel_api.id
  resource_id   = aws_api_gateway_resource.tariffs.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.aneel_api.id
  resource_id = aws_api_gateway_resource.tariffs.id
  http_method = aws_api_gateway_method.get_tariffs.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_tariffs.invoke_arn
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_tariffs.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "$${aws_api_gateway_rest_api.aneel_api.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "prod" {
  depends_on  = [aws_api_gateway_integration.lambda]
  rest_api_id = aws_api_gateway_rest_api.aneel_api.id
  stage_name  = "prod"
}

output "api_url" {
  value = "$${aws_api_gateway_deployment.prod.invoke_url}"
}
"@

$terraformMain | Out-File -FilePath (Join-Path $awsProjectPath "terraform\main.tf") -Encoding UTF8
Write-Host "  ✅ terraform/main.tf" -ForegroundColor Green

# 5. Deploy Terraform
Write-Host "`n🚀 Executando Terraform Deploy..." -ForegroundColor Cyan
Set-Location (Join-Path $awsProjectPath "terraform")

Write-Host "  terraform init..." -ForegroundColor Gray
terraform init -upgrade

if ($LASTEXITCODE -ne 0) {
      Write-Host "❌ Erro no terraform init" -ForegroundColor Red
      exit 1
}

Write-Host "  terraform plan..." -ForegroundColor Gray
terraform plan -out=tfplan

if ($LASTEXITCODE -ne 0) {
      Write-Host "❌ Erro no terraform plan" -ForegroundColor Red
      exit 1
}

Write-Host "`n📋 Plano criado. Deseja aplicar? (S/N)" -ForegroundColor Yellow
$apply = Read-Host
if ($apply -eq 'S' -or $apply -eq 's') {
      Write-Host "  terraform apply..." -ForegroundColor Gray
      terraform apply tfplan
    
      if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Deploy concluído com sucesso!" -ForegroundColor Green
        
            $apiUrl = terraform output -raw api_url
            Write-Host "`n🌐 API URL: $apiUrl" -ForegroundColor Cyan
        
            Write-Host "`n🧪 Teste a API:" -ForegroundColor Cyan
            Write-Host "  Invoke-RestMethod `"$apiUrl/tariffs?uf=SP&grupo=B1`"" -ForegroundColor White
        
            # Salvar URL no .env
            $envPath = Join-Path $backendPath ".env"
            if (Test-Path $envPath) {
                  Add-Content -Path $envPath -Value "`nAWS_ANEEL_API_URL=$apiUrl"
                  Write-Host "`n✅ URL salva em .env" -ForegroundColor Green
            }
      }
      else {
            Write-Host "`n❌ Erro no deploy" -ForegroundColor Red
            exit 1
      }
}
else {
      Write-Host "Deploy cancelado." -ForegroundColor Yellow
}

Write-Host "`n✨ Script finalizado!" -ForegroundColor Green
