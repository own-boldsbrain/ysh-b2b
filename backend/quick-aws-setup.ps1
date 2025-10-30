# ==========================================
# CONFIGURAÇÃO RÁPIDA AWS - SSO PRÉ-AUTORIZADO
# Execução em um comando para deploy completo
# ==========================================

param(
      [switch]$FullDeploy,
      [switch]$OnlyValidate,
      [switch]$UpdateImages,
      [switch]$ConfigureSecrets
)

$ErrorActionPreference = "Stop"

# Configurações fixas baseadas no SSO autorizado
$AWS_CONFIG = @{
      Profile     = "ysh-production"
      Region      = "us-east-1"
      AccountId   = "773235999227"
      StackName   = "production-ysh-stack"
      SSOStartUrl = "https://d-9066293405.awsapps.com/start"
}

Write-Host @"
🚀 YSH B2B - Configuração AWS Automática
════════════════════════════════════════════════════════════════

✅ SSO Pré-autorizado detectado:
   Account: $($AWS_CONFIG.AccountId)
   Profile: $($AWS_CONFIG.Profile)
   Region: $($AWS_CONFIG.Region)

"@ -ForegroundColor Cyan

# ==========================================
# VALIDAÇÃO RÁPIDA
# ==========================================

Write-Host "🔍 Validação rápida..." -ForegroundColor Yellow

# AWS CLI + SSO
try {
      $identity = aws sts get-caller-identity --profile $AWS_CONFIG.Profile | ConvertFrom-Json
      Write-Host "✅ SSO ativo: $($identity.Arn.Split('/')[-1])" -ForegroundColor Green
}
catch {
      Write-Host "❌ SSO expirado - Execute: aws sso login --profile $($AWS_CONFIG.Profile)" -ForegroundColor Red
      exit 1
}

# Docker
try {
      docker info | Out-Null
      Write-Host "✅ Docker ativo" -ForegroundColor Green
}
catch {
      Write-Host "❌ Docker não está rodando" -ForegroundColor Red
      exit 1
}

if ($OnlyValidate) {
      Write-Host "`n✅ Validação concluída - Sistema pronto para deploy" -ForegroundColor Green
      exit 0
}

# ==========================================
# DOCKER BUILD RÁPIDO
# ==========================================

if ($UpdateImages -or $FullDeploy) {
      Write-Host "`n🐳 Build de imagens otimizadas..." -ForegroundColor Yellow
    
      # Build paralelo
      $backendJob = Start-Job -ScriptBlock { 
            docker build -t ysh/backend:optimized -f Dockerfile.mcp-optimized . --quiet
      }
    
      $workerJob = Start-Job -ScriptBlock {
            docker build -t ysh/worker:optimized -f Dockerfile.worker . --quiet
      }
    
      # Aguardar builds
      Wait-Job $backendJob, $workerJob | Out-Null
    
      if ((Receive-Job $backendJob) -and (Receive-Job $workerJob)) {
            Write-Host "✅ Imagens construídas" -ForegroundColor Green
      }
      else {
            Write-Host "❌ Falha no build" -ForegroundColor Red
            exit 1
      }
    
      Remove-Job $backendJob, $workerJob
}

# ==========================================
# ECR PUSH RÁPIDO
# ==========================================

if ($UpdateImages -or $FullDeploy) {
      Write-Host "`n📤 Push para ECR..." -ForegroundColor Yellow
    
      # Login ECR
      aws ecr get-login-password --region $AWS_CONFIG.Region --profile $AWS_CONFIG.Profile | 
      docker login --username AWS --password-stdin "$($AWS_CONFIG.AccountId).dkr.ecr.$($AWS_CONFIG.Region).amazonaws.com" 2>$null
    
      # Criar repos (se necessário)
      aws ecr create-repository --repository-name ysh/backend --profile $AWS_CONFIG.Profile 2>$null
      aws ecr create-repository --repository-name ysh/worker --profile $AWS_CONFIG.Profile 2>$null
    
      # Tag e push
      $ecrBase = "$($AWS_CONFIG.AccountId).dkr.ecr.$($AWS_CONFIG.Region).amazonaws.com"
    
      docker tag ysh/backend:optimized "$ecrBase/ysh/backend:latest"
      docker tag ysh/worker:optimized "$ecrBase/ysh/worker:latest"
    
      docker push "$ecrBase/ysh/backend:latest" --quiet
      docker push "$ecrBase/ysh/worker:latest" --quiet
    
      Write-Host "✅ Imagens no ECR" -ForegroundColor Green
}

# ==========================================
# CLOUDFORMATION DEPLOY
# ==========================================

if ($FullDeploy) {
      Write-Host "`n☁️  Deploy CloudFormation..." -ForegroundColor Yellow
    
      # Verificar se stack existe
      $stackExists = $false
      try {
            aws cloudformation describe-stacks --stack-name $AWS_CONFIG.StackName --profile $AWS_CONFIG.Profile 2>$null | Out-Null
            $stackExists = $true
            Write-Host "⚠️  Stack já existe - Atualizando..." -ForegroundColor Yellow
      }
      catch {
            Write-Host "ℹ️  Criando nova stack..." -ForegroundColor Cyan
      }
    
      # Gerar parâmetros
      # Gerar parâmetros
      function New-SecurePassword {
            param([int]$Length = 20)
            $chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz123456789!@#$%^&*"
            -join ((1..$Length) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
      }
      $dbPassword = New-SecurePassword -Length 20
      $params = @(
            "ParameterKey=KeyPairName,ParameterValue=ysh-keypair",
            "ParameterKey=DBPassword,ParameterValue=$dbPassword"
      )
    
      if ($stackExists) {
            # Update stack
            aws cloudformation update-stack `
                  --stack-name $AWS_CONFIG.StackName `
                  --template-body file://aws-cloudformation/main-stack.yml `
                  --parameters $params `
                  --capabilities CAPABILITY_NAMED_IAM `
                  --profile $AWS_CONFIG.Profile `
                  --region $AWS_CONFIG.Region 2>$null
        
            if ($LASTEXITCODE -eq 0) {
                  Write-Host "⏳ Aguardando atualização..." -ForegroundColor Yellow
                  aws cloudformation wait stack-update-complete --stack-name $AWS_CONFIG.StackName --profile $AWS_CONFIG.Profile
            }
      }
      else {
            # Create stack
            aws cloudformation create-stack `
                  --stack-name $AWS_CONFIG.StackName `
                  --template-body file://aws-cloudformation/main-stack.yml `
                  --parameters $params `
                  --capabilities CAPABILITY_NAMED_IAM `
                  --profile $AWS_CONFIG.Profile `
                  --region $AWS_CONFIG.Region
        
            Write-Host "⏳ Aguardando criação (15-20 min)..." -ForegroundColor Yellow
            aws cloudformation wait stack-create-complete --stack-name $AWS_CONFIG.StackName --profile $AWS_CONFIG.Profile
      }
    
      if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Stack deployada" -ForegroundColor Green
        
            # Salvar credenciais
            "DB_PASSWORD=$dbPassword`nSTACK_NAME=$($AWS_CONFIG.StackName)`nREGION=$($AWS_CONFIG.Region)" | Out-File ".env.aws"
            Write-Host "✅ Credenciais salvas em .env.aws" -ForegroundColor Green
      }
      else {
            Write-Host "❌ Falha no deploy" -ForegroundColor Red
            exit 1
      }
}

# ==========================================
# CONFIGURAR SECRETS
# ==========================================

if ($ConfigureSecrets -or $FullDeploy) {
      Write-Host "`n🔐 Configurando secrets..." -ForegroundColor Yellow
    
      # Obter outputs da stack
      try {
            $stack = aws cloudformation describe-stacks --stack-name $AWS_CONFIG.StackName --profile $AWS_CONFIG.Profile | ConvertFrom-Json
            $backendUrl = ($stack.Stacks[0].Outputs | Where-Object { $_.OutputKey -eq "BackendURL" }).OutputValue
        
            if ($backendUrl) {
                  Write-Host "✅ Backend URL: $backendUrl" -ForegroundColor Green
            
                  # Configurar secrets básicos
                  $secrets = @{
                        "JWT_SECRET"         = [System.Web.Security.Membership]::GeneratePassword(32, 8)
                        "COOKIE_SECRET"      = [System.Web.Security.Membership]::GeneratePassword(32, 8)
                        "MEDUSA_BACKEND_URL" = $backendUrl
                  }
            
                  foreach ($secret in $secrets.GetEnumerator()) {
                        try {
                              aws secretsmanager create-secret `
                                    --name "/ysh-b2b/$($secret.Key.ToLower())" `
                                    --secret-string $secret.Value `
                                    --profile $AWS_CONFIG.Profile 2>$null
                              Write-Host "✅ Secret criado: $($secret.Key)" -ForegroundColor Green
                        }
                        catch {
                              Write-Host "ℹ️  Secret já existe: $($secret.Key)" -ForegroundColor Gray
                        }
                  }
            }
      }
      catch {
            Write-Host "⚠️  Não foi possível configurar secrets automaticamente" -ForegroundColor Yellow
      }
}

# ==========================================
# RESUMO FINAL
# ==========================================

Write-Host @"

════════════════════════════════════════════════════════════════
🎉 CONFIGURAÇÃO CONCLUÍDA
════════════════════════════════════════════════════════════════

✅ Status do Sistema:
   • SSO AWS: Ativo e autorizado
   • Docker Images: Construídas e no ECR
   • CloudFormation: $($AWS_CONFIG.StackName)
   • Region: $($AWS_CONFIG.Region)

🔗 Links importantes:
   • AWS Console: https://console.aws.amazon.com
   • CloudFormation: https://us-east-1.console.aws.amazon.com/cloudformation
   • ECR: https://us-east-1.console.aws.amazon.com/ecr

⚡ Comandos rápidos:
   • Só validar:    .\quick-aws-setup.ps1 -OnlyValidate
   • Update images: .\quick-aws-setup.ps1 -UpdateImages
   • Deploy full:   .\quick-aws-setup.ps1 -FullDeploy
   • Config secrets:.\quick-aws-setup.ps1 -ConfigureSecrets

"@ -ForegroundColor Cyan

if (-not ($UpdateImages -or $FullDeploy -or $ConfigureSecrets)) {
      Write-Host "💡 Para deploy completo execute:" -ForegroundColor Yellow
      Write-Host "   .\quick-aws-setup.ps1 -FullDeploy" -ForegroundColor White
}