# =========================================
# YSH B2B - Instalação de Dependências
# =========================================
# Script PowerShell para configurar ambiente Python

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "YSH B2B - ANEEL Distribuidoras Extractor" -ForegroundColor Cyan
Write-Host "Instalando dependências..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "🔍 Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python não encontrado. Instale Python 3.10+ antes de continuar." -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green
Write-Host ""

# Criar ambiente virtual (opcional)
$createVenv = Read-Host "Deseja criar um ambiente virtual? (s/N)"
if ($createVenv -eq "s" -or $createVenv -eq "S") {
    Write-Host "📦 Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv .venv
    
    Write-Host "✅ Ambiente virtual criado" -ForegroundColor Green
    Write-Host "📌 Para ativar manualmente: .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "🔄 Ativando ambiente virtual..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

# Upgrade pip
Write-Host "⬆️  Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✅ pip atualizado" -ForegroundColor Green
Write-Host ""

# Instalar dependências
Write-Host "📥 Instalando dependências do requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao instalar dependências" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependências instaladas" -ForegroundColor Green
Write-Host ""

# Instalar Playwright browsers
Write-Host "🌐 Instalando navegadores Playwright..." -ForegroundColor Yellow
playwright install chromium
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Erro ao instalar navegadores Playwright" -ForegroundColor Yellow
    Write-Host "   Você pode executar manualmente: playwright install chromium" -ForegroundColor Yellow
} else {
    Write-Host "✅ Navegador Chromium instalado" -ForegroundColor Green
}
Write-Host ""

# Verificar Docker
Write-Host "🐳 Verificando Docker..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Docker não encontrado (opcional - apenas para fallback models)" -ForegroundColor Yellow
} else {
    Write-Host "✅ $dockerVersion" -ForegroundColor Green
}
Write-Host ""

# Verificar arquivo .env
Write-Host "🔑 Verificando arquivo .env..." -ForegroundColor Yellow
$envPath = "..\..\..\.env"
if (Test-Path $envPath) {
    Write-Host "✅ Arquivo .env encontrado" -ForegroundColor Green
    
    # Verificar se as chaves estão configuradas
    $envContent = Get-Content $envPath -Raw
    $hasGemini = $envContent -match "GEMINI_API_KEY_1=AIzaSy"
    $hasOpenAI = $envContent -match "OPENAI_API_KEY=sk-proj-"
    
    if ($hasGemini -and $hasOpenAI) {
        Write-Host "✅ API keys configuradas" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Algumas API keys podem estar faltando" -ForegroundColor Yellow
        Write-Host "   Verifique: $envPath" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Arquivo .env não encontrado" -ForegroundColor Yellow
    Write-Host "   Crie o arquivo com as API keys fornecidas" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ SETUP CONCLUÍDO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📌 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Verifique as API keys no arquivo .env" -ForegroundColor White
Write-Host "   2. Execute o extrator:" -ForegroundColor White
Write-Host "      python aneel_territorial_extractor.py" -ForegroundColor Yellow
Write-Host ""
