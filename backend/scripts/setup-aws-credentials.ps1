# ╔════════════════════════════════════════════════════════════════════════════╗
# ║              SETUP AWS CREDENTIALS - YSH B2B PRODUCTION                    ║
# ╚════════════════════════════════════════════════════════════════════════════╝

Write-Host @"
╔════════════════════════════════════════════════════════════════════════════╗
║                  🔐 CONFIGURAÇÃO DE CREDENCIAIS AWS                        ║
╚════════════════════════════════════════════════════════════════════════════╝

Este script irá:
  1. Solicitar suas credenciais AWS
  2. Validar as credenciais
  3. Configurar a região padrão
  4. Testar a conexão

⚠️  Certifique-se de ter as credenciais AWS disponíveis:
    • Access Key ID
    • Secret Access Key

"@ -ForegroundColor Cyan

# Verificar se AWS CLI está instalado
$awsVersion = aws --version 2>&1
if ($LASTEXITCODE -ne 0) {
      Write-Host "❌ AWS CLI não encontrado! Instale em: https://aws.amazon.com/cli/" -ForegroundColor Red
      exit 1
}

Write-Host "✅ AWS CLI detectado: $awsVersion" -ForegroundColor Green
Write-Host ""

# Passo 1: Obter Access Key ID
Write-Host "┌─ Passo 1: Access Key ID" -ForegroundColor Cyan
Write-Host "│  Obtenha em: AWS Console → IAM → Users → Security Credentials" -ForegroundColor Gray
$accessKey = Read-Host "│  Access Key ID"
if ([string]::IsNullOrWhiteSpace($accessKey)) {
      Write-Host "│  ❌ Access Key ID não pode estar vazio!" -ForegroundColor Red
      exit 1
}
Write-Host "│  ✅ Recebido" -ForegroundColor Green
Write-Host "└─" -ForegroundColor Cyan
Write-Host ""

# Passo 2: Obter Secret Access Key
Write-Host "┌─ Passo 2: Secret Access Key" -ForegroundColor Cyan
Write-Host "│  ⚠️  Esta será a única vez que você verá este valor!" -ForegroundColor Yellow
$secretKey = Read-Host "│  Secret Access Key" -AsSecureString
$secretKeyPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
      [System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($secretKey)
)
if ([string]::IsNullOrWhiteSpace($secretKeyPlain)) {
      Write-Host "│  ❌ Secret Access Key não pode estar vazio!" -ForegroundColor Red
      exit 1
}
Write-Host "│  ✅ Recebido (guardado em memória)" -ForegroundColor Green
Write-Host "└─" -ForegroundColor Cyan
Write-Host ""

# Passo 3: Região
Write-Host "┌─ Passo 3: Região AWS" -ForegroundColor Cyan
Write-Host "│  Recomendado: us-east-1 (compatibilidade máxima)" -ForegroundColor Gray
Write-Host "│  Outras opções: us-west-1, eu-west-1, sa-east-1 (São Paulo)" -ForegroundColor Gray
$region = Read-Host "│  Região [us-east-1]"
if ([string]::IsNullOrWhiteSpace($region)) {
      $region = "us-east-1"
}
Write-Host "│  ✅ Definido: $region" -ForegroundColor Green
Write-Host "└─" -ForegroundColor Cyan
Write-Host ""

# Passo 4: Formato de output
Write-Host "┌─ Passo 4: Formato de saída" -ForegroundColor Cyan
Write-Host "│  Recomendado: json (melhor para scripts)" -ForegroundColor Gray
$format = Read-Host "│  Formato [json]"
if ([string]::IsNullOrWhiteSpace($format)) {
      $format = "json"
}
Write-Host "│  ✅ Definido: $format" -ForegroundColor Green
Write-Host "└─" -ForegroundColor Cyan
Write-Host ""

# Aplicar configuração
Write-Host "┌─ Aplicando configuração..." -ForegroundColor Cyan

# Criar arquivo ~/.aws/credentials
$awsHome = $env:USERPROFILE
$awsDir = Join-Path $awsHome ".aws"
if (!(Test-Path $awsDir)) {
      New-Item -ItemType Directory -Path $awsDir -Force | Out-Null
}

$credentialsFile = Join-Path $awsDir "credentials"
$configFile = Join-Path $awsDir "config"

# Backup de credenciais existentes
if (Test-Path $credentialsFile) {
      $backup = "$credentialsFile.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
      Copy-Item $credentialsFile $backup
      Write-Host "│  📦 Backup criado: $backup" -ForegroundColor Gray
}

# Escrever credenciais
$credentialsContent = @"
[default]
aws_access_key_id = $accessKey
aws_secret_access_key = $secretKeyPlain
"@

Set-Content -Path $credentialsFile -Value $credentialsContent -Force

# Configurar permissões (Windows)
icacls $credentialsFile /inheritance:r /grant:r "${env:USERDOMAIN}\${env:USERNAME}:(F)" | Out-Null

Write-Host "│  ✅ Credenciais salvas em: $credentialsFile" -ForegroundColor Green

# Configurar config
if (!(Test-Path $configFile)) {
      $configContent = @"
[default]
region = $region
output = $format
"@
      Set-Content -Path $configFile -Value $configContent -Force
      Write-Host "│  ✅ Config salva em: $configFile" -ForegroundColor Green
}
else {
      Write-Host "│  ℹ️  Config existente preservado" -ForegroundColor Gray
}

Write-Host "└─" -ForegroundColor Cyan
Write-Host ""

# Validar configuração
Write-Host "┌─ Validando configuração..." -ForegroundColor Cyan

$identity = aws sts get-caller-identity --output json 2>&1
if ($LASTEXITCODE -eq 0) {
      Write-Host "│  ✅ Credenciais validadas com sucesso!" -ForegroundColor Green
    
      $identityObj = $identity | ConvertFrom-Json
      Write-Host "│  AWS Account: $($identityObj.Account)" -ForegroundColor Gray
      Write-Host "│  User ARN: $($identityObj.Arn)" -ForegroundColor Gray
      Write-Host "└─" -ForegroundColor Cyan
      Write-Host ""
    
      Write-Host "✨ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO! ✨" -ForegroundColor Green
      Write-Host ""
      Write-Host "Próximos passos:" -ForegroundColor Cyan
      Write-Host "  1. node scripts/test-connectivity.js        # Testar conectividade" -ForegroundColor Gray
      Write-Host "  2. node scripts/verify-aws-setup.js         # Verificar setup" -ForegroundColor Gray
      Write-Host "  3. .\aws-cloudformation\deploy-stack.ps1    # Deploy stack" -ForegroundColor Gray
      Write-Host ""
}
else {
      Write-Host "│  ❌ Falha na validação!" -ForegroundColor Red
      Write-Host "│  Erro: $identity" -ForegroundColor Red
      Write-Host "└─" -ForegroundColor Cyan
      Write-Host ""
      Write-Host "Verifique se as credenciais estão corretas e tente novamente." -ForegroundColor Yellow
      exit 1
}
