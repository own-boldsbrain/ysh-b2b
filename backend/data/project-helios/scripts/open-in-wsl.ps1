# Script para abrir o Project Helios no VS Code Insiders via WSL
# Uso: .\scripts\open-in-wsl.ps1

param(
    [string]$VSCodePath = "code-insiders",
    [string]$WSLDistro = "Ubuntu"
)

Write-Host "🚀 Abrindo Project Helios no WSL..." -ForegroundColor Green

# Verificar se WSL está disponível
try {
    $wslCheck = wsl --list --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Error "WSL não está instalado ou não está funcionando. Por favor, instale o WSL primeiro."
        exit 1
    }
} catch {
    Write-Error "Erro ao verificar WSL: $_"
    exit 1
}

# Verificar se a distribuição especificada existe
if (!(wsl --list --quiet | Select-String $WSLDistro)) {
    Write-Warning "Distribuição '$WSLDistro' não encontrada. Usando a distribuição padrão."
    $WSLDistro = ""
}

# Obter o diretório atual do script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Tentar diferentes caminhos para o VS Code
$VSCodePaths = @(
    "code-insiders",
    "code",
    "${env:LOCALAPPDATA}\Programs\Microsoft VS Code Insiders\bin\code-insiders.cmd",
    "${env:PROGRAMFILES}\Microsoft VS Code Insiders\bin\code-insiders.cmd",
    "${env:LOCALAPPDATA}\Programs\Microsoft VS Code\bin\code.cmd",
    "${env:PROGRAMFILES}\Microsoft VS Code\bin\code.cmd"
)

$VSCodeFound = $false
foreach ($path in $VSCodePaths) {
    try {
        & $path --version 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $VSCodePath = $path
            $VSCodeFound = $true
            Write-Host "✅ VS Code encontrado em: $VSCodePath" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

if (!$VSCodeFound) {
    Write-Error "VS Code não encontrado. Por favor, instale o VS Code ou VS Code Insiders."
    exit 1
}

# Construir o comando para abrir no WSL
$WorkspaceFile = Join-Path $ProjectRoot "project-helios-wsl.code-workspace"

if (Test-Path $WorkspaceFile) {
    Write-Host "📁 Abrindo workspace: $WorkspaceFile" -ForegroundColor Yellow
    
    if ($WSLDistro) {
        & $VSCodePath $WorkspaceFile --remote "wsl+$WSLDistro"
    } else {
        & $VSCodePath $WorkspaceFile --remote wsl
    }
} else {
    Write-Host "📁 Workspace file não encontrado, abrindo diretório atual no WSL" -ForegroundColor Yellow
    
    if ($WSLDistro) {
        & $VSCodePath $ProjectRoot --remote "wsl+$WSLDistro"
    } else {
        & $VSCodePath $ProjectRoot --remote wsl
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Project Helios aberto no WSL com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Cyan
    Write-Host "1. Aguarde o VS Code carregar no WSL" -ForegroundColor White
    Write-Host "2. Abra o terminal integrado (Ctrl+`)" -ForegroundColor White
    Write-Host "3. Execute: python3 -m venv ~/.venvs/project-helios && source ~/.venvs/project-helios/bin/activate" -ForegroundColor White
    Write-Host "4. Execute: pip install -r haas/requirements.txt" -ForegroundColor White
    Write-Host "5. Configure o interpretador Python (Ctrl+Shift+P > Python: Select Interpreter)" -ForegroundColor White
} else {
    Write-Error "Erro ao abrir VS Code no WSL"
    exit 1
}