#!/usr/bin/env pwsh
# Upload ANEEL Datasets para Hugging Face
# Execute: .\upload-aneel-to-hf.ps1

Write-Host "`n🚀 ANEEL to Hugging Face Upload Script" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Gray

# 1. Verificar se está no diretório correto
$projectHeliosPath = "c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\project-helios"
if (-not (Test-Path $projectHeliosPath)) {
      Write-Host "❌ Erro: Diretório project-helios não encontrado" -ForegroundColor Red
      exit 1
}

Set-Location $projectHeliosPath

# 2. Verificar se os datasets existem
$aneelDataPath = Join-Path $projectHeliosPath "aneel_datasets"
if (-not (Test-Path $aneelDataPath)) {
      Write-Host "❌ Erro: Pasta aneel_datasets não encontrada" -ForegroundColor Red
      exit 1
}

$csvCount = (Get-ChildItem $aneelDataPath -Filter "*.csv").Count
Write-Host "✅ Encontrados $csvCount arquivos CSV" -ForegroundColor Green

# 3. Verificar autenticação Hugging Face
Write-Host "`n🔐 Verificando autenticação Hugging Face..." -ForegroundColor Cyan

try {
      $hfWhoami = huggingface-cli whoami 2>&1
      if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Autenticado no Hugging Face" -ForegroundColor Green
            Write-Host $hfWhoami
      }
      else {
            throw "Não autenticado"
      }
}
catch {
      Write-Host "❌ Você não está autenticado no Hugging Face" -ForegroundColor Red
      Write-Host "`nExecute o comando abaixo e cole seu token:" -ForegroundColor Yellow
      Write-Host "  huggingface-cli login" -ForegroundColor White
      Write-Host "`nToken disponível em: https://huggingface.co/settings/tokens" -ForegroundColor Gray
      exit 1
}

# 4. Confirmar upload
Write-Host "`n📦 Pronto para fazer upload de $csvCount arquivos (~500MB)" -ForegroundColor Cyan
Write-Host "Destino: fernando-bold/aneel-datasets`n" -ForegroundColor White

$confirmation = Read-Host "Deseja continuar? (S/N)"
if ($confirmation -ne 'S' -and $confirmation -ne 's') {
      Write-Host "Upload cancelado." -ForegroundColor Yellow
      exit 0
}

# 5. Executar upload
Write-Host "`n🚀 Iniciando upload..." -ForegroundColor Green
Write-Host "Isso pode levar vários minutos. Aguarde...`n" -ForegroundColor Yellow

try {
      python upload_to_huggingface.py
    
      if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Upload concluído com sucesso!" -ForegroundColor Green
            Write-Host "`n📊 Acesse seu dataset em:" -ForegroundColor Cyan
            Write-Host "   https://huggingface.co/datasets/fernando-bold/aneel-datasets" -ForegroundColor White
        
            Write-Host "`n🔍 Teste o acesso:" -ForegroundColor Cyan
            Write-Host @"
   from datasets import load_dataset
   ds = load_dataset("fernando-bold/aneel-datasets", 
                     data_files="empreendimento-geracao-distribuida.csv")
   print(ds)
"@ -ForegroundColor White
      }
      else {
            throw "Erro no upload"
      }
}
catch {
      Write-Host "`n❌ Erro durante upload:" -ForegroundColor Red
      Write-Host $_.Exception.Message -ForegroundColor Red
      exit 1
}

Write-Host "`n✨ Processo finalizado!" -ForegroundColor Green
