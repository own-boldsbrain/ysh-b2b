# ==========================================
# INICIALIZAÇÃO AUTOMATIZADA AWS SSO
# YSH B2B - Deploy Automático
# ==========================================

param(
      [string]$Environment = "production",
      [string]$Profile = "ysh-production",
      [string]$Region = "us-east-1",
      [switch]$DeployStack,
      [switch]$SkipValidation,
      [switch]$UpdateSecrets,
      [switch]$Verbose
)

$ErrorActionPreference = "Stop"

if ($Verbose) { $VerbosePreference = "Continue" }

# ==========================================
# CONFIGURAÇÕES
# ==========================================

$CONFIG = @{
      Profile     = $Profile
      Region      = $Region
      Environment = $Environment
      AccountId   = "773235999227"
      SSOStartUrl = "https://d-9066293405.awsapps.com/start"
      SSORegion   = "us-east-1"
      StackName   = "$Environment-ysh-stack"
      Domain      = "yellosolarhub.store"
}

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

function Write-Title {
      param([string]$Title)
      Write-Host "`n" + "="*80 -ForegroundColor Cyan
      Write-Host "  $Title" -ForegroundColor White
      Write-Host "="*80 -ForegroundColor Cyan
}

function Write-Step {
      param([string]$Message)
      Write-Host "`n🔄 $Message" -ForegroundColor Yellow
}

function Write-Success {
      param([string]$Message)
      Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
      param([string]$Message)
      Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
      param([string]$Message)
      Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
      param([string]$Message)
      Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

# ==========================================
# VALIDAÇÃO PRÉ-DEPLOYMENT
# ==========================================

function Test-Prerequisites {
      Write-Step "Validando pré-requisitos..."
    
      # 1. AWS CLI
      try {
            $awsVersion = aws --version
            Write-Success "AWS CLI: $awsVersion"
      }
      catch {
            Write-Error "AWS CLI não encontrado. Instale: winget install Amazon.AWSCLI"
            exit 1
      }
    
      # 2. Docker
      try {
            $dockerVersion = docker --version
            Write-Success "Docker: $dockerVersion"
      }
      catch {
            Write-Error "Docker não encontrado. Instale Docker Desktop"
            exit 1
      }
    
      # 3. Profile AWS
      $profiles = aws configure list-profiles
      if ($profiles -notcontains $CONFIG.Profile) {
            Write-Error "Profile '$($CONFIG.Profile)' não encontrado"
            Write-Info "Configure com: aws configure sso --profile $($CONFIG.Profile)"
            exit 1
      }
      Write-Success "Profile AWS: $($CONFIG.Profile)"
    
      # 4. SSO Session
      try {
            $identity = aws sts get-caller-identity --profile $CONFIG.Profile | ConvertFrom-Json
            Write-Success "SSO Autenticado: $($identity.Arn)"
            Write-Info "Account: $($identity.Account)"
            Write-Info "User: $($identity.UserId.Split(':')[-1])"
        
            if ($identity.Account -ne $CONFIG.AccountId) {
                  Write-Warning "Account ID diferente do esperado"
                  Write-Info "Esperado: $($CONFIG.AccountId)"
                  Write-Info "Atual: $($identity.Account)"
            }
      }
      catch {
            Write-Error "SSO não autenticado ou expirado"
            Write-Info "Execute: aws sso login --profile $($CONFIG.Profile)"
            exit 1
      }
    
      # 5. Arquivos necessários
      $requiredFiles = @(
            "aws-cloudformation\main-stack.yml",
            "Dockerfile.mcp-optimized",
            "Dockerfile.worker"
      )
    
      foreach ($file in $requiredFiles) {
            if (Test-Path $file) {
                  Write-Success "Arquivo encontrado: $file"
            }
            else {
                  Write-Error "Arquivo não encontrado: $file"
                  exit 1
            }
      }
}

# ==========================================
# DOCKER BUILD & PUSH
# ==========================================

function Build-OptimizedImages {
      Write-Step "Construindo imagens Docker otimizadas..."
    
      # Backend
      Write-Info "Building ysh/backend:optimized..."
      docker build -t ysh/backend:optimized -f Dockerfile.mcp-optimized . --quiet
      if ($LASTEXITCODE -ne 0) {
            Write-Error "Falha no build do backend"
            exit 1
      }
    
      # Worker
      Write-Info "Building ysh/worker:optimized..."
      docker build -t ysh/worker:optimized -f Dockerfile.worker . --quiet
      if ($LASTEXITCODE -ne 0) {
            Write-Error "Falha no build do worker"
            exit 1
      }
    
      # Verificar tamanhos
      $backendSize = docker images ysh/backend:optimized --format "{{.Size}}"
      $workerSize = docker images ysh/worker:optimized --format "{{.Size}}"
    
      Write-Success "Imagens construídas:"
      Write-Info "  Backend: $backendSize"
      Write-Info "  Worker: $workerSize"
}

function Push-ToECR {
      Write-Step "Fazendo push para AWS ECR..."
    
      # Login ECR
      $ecrLogin = aws ecr get-login-password --region $CONFIG.Region --profile $CONFIG.Profile
      $ecrLogin | docker login --username AWS --password-stdin "$($CONFIG.AccountId).dkr.ecr.$($CONFIG.Region).amazonaws.com"
    
      if ($LASTEXITCODE -ne 0) {
            Write-Error "Falha no login ECR"
            exit 1
      }
      Write-Success "Login ECR realizado"
    
      # Criar repositórios se não existirem
      $repositories = @("ysh/backend", "ysh/worker")
      foreach ($repo in $repositories) {
            try {
                  aws ecr create-repository --repository-name $repo --region $CONFIG.Region --profile $CONFIG.Profile 2>$null
                  Write-Info "Repositório criado: $repo"
            }
            catch {
                  Write-Info "Repositório já existe: $repo"
            }
      }
    
      # Tag e push
      $ecrUri = "$($CONFIG.AccountId).dkr.ecr.$($CONFIG.Region).amazonaws.com"
    
      # Backend
      docker tag ysh/backend:optimized "$ecrUri/ysh/backend:latest"
      docker push "$ecrUri/ysh/backend:latest" --quiet
      if ($LASTEXITCODE -ne 0) {
            Write-Error "Falha no push do backend"
            exit 1
      }
    
      # Worker  
      docker tag ysh/worker:optimized "$ecrUri/ysh/worker:latest"
      docker push "$ecrUri/ysh/worker:latest" --quiet
      if ($LASTEXITCODE -ne 0) {
            Write-Error "Falha no push do worker"
            exit 1
      }
    
      Write-Success "Push para ECR concluído"
}

# ==========================================
# CLOUDFORMATION DEPLOYMENT
# ==========================================

function Deploy-Infrastructure {
      Write-Step "Fazendo deploy da infraestrutura AWS..."
    
      # Gerar senhas seguras
      function New-SecurePassword {
            param([int]$Length = 20)
            $chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz123456789!@#$%^&*"
            -join ((1..$Length) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
      }
    
      $dbPassword = New-SecurePassword -Length 20
      $jwtSecret = New-SecurePassword -Length 32
      $cookieSecret = New-SecurePassword -Length 32      # Parâmetros CloudFormation
      $parameters = @(
            "ParameterKey=KeyPairName,ParameterValue=ysh-keypair",
            "ParameterKey=DBPassword,ParameterValue=$dbPassword"
      )
    
      # Verificar se stack já existe
      try {
            $existingStack = aws cloudformation describe-stacks --stack-name $CONFIG.StackName --profile $CONFIG.Profile --region $CONFIG.Region 2>&1 | ConvertFrom-Json
            Write-Warning "Stack '$($CONFIG.StackName)' já existe com status: $($existingStack.Stacks[0].StackStatus)"
        
            $choice = Read-Host "Deseja atualizar a stack? (y/N)"
            if ($choice -eq "y" -or $choice -eq "Y") {
                  Write-Info "Atualizando stack existente..."
                  aws cloudformation update-stack `
                        --stack-name $CONFIG.StackName `
                        --template-body fileb://aws-cloudformation/main-stack.yml `
                        --parameters $parameters `
                        --capabilities CAPABILITY_NAMED_IAM `
                        --profile $CONFIG.Profile `
                        --region $CONFIG.Region                  if ($LASTEXITCODE -eq 0) {
                        Write-Info "Aguardando atualização da stack..."
                        aws cloudformation wait stack-update-complete --stack-name $CONFIG.StackName --profile $CONFIG.Profile --region $CONFIG.Region
                        Write-Success "Stack atualizada com sucesso"
                  }
            }
            else {
                  Write-Info "Pulando atualização da stack"
                  return
            }
      }
      catch {
            Write-Info "Stack não existe, criando nova..."
        
            # Criar nova stack
            aws cloudformation create-stack `
                  --stack-name $CONFIG.StackName `
                  --template-body fileb://aws-cloudformation/main-stack-simple.yml `
                  --parameters $parameters `
                  --capabilities CAPABILITY_NAMED_IAM `
                  --profile $CONFIG.Profile `
                  --region $CONFIG.Region            if ($LASTEXITCODE -ne 0) {
                  Write-Error "Falha na criação da stack"
                  exit 1
            }
        
            Write-Info "Aguardando criação da stack (15-20 minutos)..."
            aws cloudformation wait stack-create-complete --stack-name $CONFIG.StackName --profile $CONFIG.Profile --region $CONFIG.Region
        
            if ($LASTEXITCODE -ne 0) {
                  Write-Error "Timeout ou falha na criação da stack"
                  Write-Info "Verifique o AWS Console para detalhes"
                  exit 1
            }
        
            Write-Success "Stack criada com sucesso"
      }
    
      # Salvar credenciais
      @"
# AWS Stack Credentials - Generated $(Get-Date)
DB_PASSWORD=$dbPassword
JWT_SECRET=$jwtSecret
COOKIE_SECRET=$cookieSecret
STACK_NAME=$($CONFIG.StackName)
ACCOUNT_ID=$($CONFIG.AccountId)
REGION=$($CONFIG.Region)
"@ | Out-File -FilePath ".env.aws" -Encoding UTF8
    
      Write-Success "Credenciais salvas em .env.aws"
}

# ==========================================
# OBTER OUTPUTS DA STACK
# ==========================================

function Get-StackOutputs {
      Write-Step "Obtendo outputs da stack..."
    
      try {
            $stack = aws cloudformation describe-stacks --stack-name $CONFIG.StackName --profile $CONFIG.Profile --region $CONFIG.Region | ConvertFrom-Json
            $outputs = @{}
        
            foreach ($output in $stack.Stacks[0].Outputs) {
                  $outputs[$output.OutputKey] = $output.OutputValue
            }
        
            Write-Success "Outputs obtidos:"
            Write-Info "  Backend URL: $($outputs.BackendURL)"
            Write-Info "  Database Endpoint: $($outputs.SupabaseDBEndpoint)"
            Write-Info "  Redis Endpoint: $($outputs.RedisEndpoint)"
            Write-Info "  S3 Bucket: $($outputs.LogsBucketName)"
        
            return $outputs
      }
      catch {
            Write-Warning "Não foi possível obter outputs da stack"
            return $null
      }
}

# ==========================================
# TESTES DE VALIDAÇÃO
# ==========================================

function Test-Deployment {
      param($Outputs)
    
      Write-Step "Testando deployment..."
    
      if ($Outputs -and $Outputs.BackendURL) {
            Write-Info "Testando health check do backend..."
            try {
                  $response = Invoke-WebRequest -Uri "$($Outputs.BackendURL)/health" -TimeoutSec 30 -ErrorAction Stop
                  if ($response.StatusCode -eq 200) {
                        Write-Success "Backend está respondendo (HTTP 200)"
                  }
                  else {
                        Write-Warning "Backend respondeu com status: $($response.StatusCode)"
                  }
            }
            catch {
                  Write-Warning "Backend ainda não está disponível"
                  Write-Info "Pode levar alguns minutos para inicializar"
            }
      }
}

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================

Write-Title "INICIALIZAÇÃO AUTOMATIZADA AWS SSO - YSH B2B"

Write-Info "Configuração:"
Write-Info "  Environment: $($CONFIG.Environment)"
Write-Info "  Profile: $($CONFIG.Profile)"
Write-Info "  Region: $($CONFIG.Region)"
Write-Info "  Account: $($CONFIG.AccountId)"
Write-Info "  Stack Name: $($CONFIG.StackName)"

if (-not $SkipValidation) {
      Test-Prerequisites
}

Build-OptimizedImages
Push-ToECR

if ($DeployStack) {
      Deploy-Infrastructure
      $outputs = Get-StackOutputs
      Test-Deployment -Outputs $outputs
}
else {
      Write-Warning "Deploy da stack pulado (use -DeployStack para executar)"
      Write-Info "Para fazer deploy: .\auto-init-aws.ps1 -DeployStack"
}

Write-Title "INICIALIZAÇÃO CONCLUÍDA"

Write-Success "✅ Imagens Docker construídas e enviadas para ECR"
if ($DeployStack) {
      Write-Success "✅ Infraestrutura AWS deployada"
      Write-Success "✅ Stack '$($CONFIG.StackName)' está operacional"
}

Write-Info "`nPróximos passos:"
if (-not $DeployStack) {
      Write-Info "  1. Execute: .\auto-init-aws.ps1 -DeployStack"
}
Write-Info "  2. Configure secrets: .\scripts\update-aws-secrets.ps1"
Write-Info "  3. Configure domínio: .\aws\deploy-with-domain.ps1"

Write-Info "`nMonitoramento:"
Write-Info "  • AWS Console: https://console.aws.amazon.com"
Write-Info "  • CloudFormation: https://console.aws.amazon.com/cloudformation"
Write-Info "  • ECS: https://console.aws.amazon.com/ecs"
Write-Info "  • ECR: https://console.aws.amazon.com/ecr"