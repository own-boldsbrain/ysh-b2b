# Script PowerShell para abrir Project Helios no WSL corretamente
# Remova a venv corrompida do Windows e abra no WSL
# Uso: .\scripts\open-wsl-project.ps1

Write-Host "🚀 Project Helios - Setup WSL" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se estamos no Windows
if ($PSVersionTable.Platform -eq "Unix") {
    Write-Host "⚠️  Este script é para Windows. Você está em Linux/Mac!" -ForegroundColor Yellow
    Write-Host "Execute no WSL: bash scripts/wsl-setup-venv.sh" -ForegroundColor Yellow
    exit 1
}

# 2. Encontrar o diretório do projeto
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
Write-Host "📁 Projeto: $projectRoot" -ForegroundColor Green
Write-Host ""

# 3. Perguntar se deseja remover venv local
Write-Host "A venv local do Windows será removida para evitar conflitos." -ForegroundColor Yellow
Write-Host "A nova venv será criada NO WSL (em ~/.venvs/helios)" -ForegroundColor Yellow
Write-Host ""

$venvPath = Join-Path $projectRoot ".venv"
if (Test-Path $venvPath) {
    Write-Host "🗑️  Removendo venv Windows corrompida em $venvPath..." -ForegroundColor Red
    Remove-Item -Recurse -Force $venvPath -ErrorAction SilentlyContinue
    Write-Host "✅ Removida!" -ForegroundColor Green
    Write-Host ""
}

# 4. Verificar se VS Code Insiders está instalado
Write-Host "🔍 Procurando VS Code Insiders..." -ForegroundColor Cyan
$vscodeInsiders = Get-Command "code-insiders" -ErrorAction SilentlyContinue

if (-not $vscodeInsiders) {
    Write-Host "❌ VS Code Insiders não encontrado no PATH!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Opções:" -ForegroundColor Yellow
    Write-Host "1. Instale VS Code Insiders: https://code.visualstudio.com/insiders/" -ForegroundColor Yellow
    Write-Host "2. Ou abra manualmente com:" -ForegroundColor Yellow
    Write-Host "   code-insiders project-helios-wsl.code-workspace" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ VS Code Insiders encontrado!" -ForegroundColor Green
Write-Host ""

# 5. Instruir para abrir no WSL
Write-Host "📖 Instruções:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Abra um terminal WSL (neste PowerShell ou em outro):" -ForegroundColor White
Write-Host "   wsl" -ForegroundColor Green
Write-Host ""
Write-Host "2️⃣  No WSL, execute o setup:" -ForegroundColor White
Write-Host "   bash scripts/wsl-setup-venv.sh" -ForegroundColor Green
Write-Host ""
Write-Host "3️⃣  Após o setup, abra no VS Code Insiders:" -ForegroundColor White
Write-Host "   code-insiders project-helios-wsl.code-workspace" -ForegroundColor Green
Write-Host ""
Write-Host "4️⃣  No VS Code Insiders:" -ForegroundColor White
Write-Host "   - Será solicitado para 'Reopen in WSL' → clique 'Reopen'" -ForegroundColor Green
Write-Host "   - Selecione o interpretador Python:" -ForegroundColor Green
Write-Host "     Ctrl+Shift+P → 'Python: Select Interpreter'" -ForegroundColor Green
Write-Host "     Escolha: ~/.venvs/helios/bin/python" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Pronto! Seu projeto estará totalmente sincronizado com WSL." -ForegroundColor Cyan
Write-Host ""

# 6. Oferecer abrir WSL agora
Write-Host "Deseja abrir um terminal WSL agora? (S/n)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq "S" -or $response -eq "s" -or $response -eq "") {
    Write-Host ""
    Write-Host "🚀 Abrindo WSL..." -ForegroundColor Cyan
    wsl
} else {
    Write-Host ""
    Write-Host "✅ Execute os passos acima no seu próprio terminal WSL." -ForegroundColor Green
}
