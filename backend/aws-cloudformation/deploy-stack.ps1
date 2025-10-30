# deploy-stack.ps1 - Deploy completo da stack AWS Free Tier (Windows)

$ErrorActionPreference = "Stop"

Write-Host "🚀 YSH B2B - AWS Free Tier Deployment" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Configurações
$STACK_NAME = "ysh-b2b-production"
$REGION = "us-east-1"

# Validar AWS CLI
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
      Write-Host "❌ AWS CLI não encontrado. Instalando..." -ForegroundColor Red
      pip install awscli
}

# Obter AWS Account ID
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)

$WORKSPACE = (Get-Location).Path
$env:AWS_PAGER = ""

function Get-FreeTcpPort {
      $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
      $listener.Start()
      $port = $listener.LocalEndpoint.Port
      $listener.Stop()
      return $port
}

function Start-SshTunnel {
      param(
            [string]$DbHost,
            [string]$JumpHost,
            [string]$SshKeyPath
      )

      $localPort = Get-FreeTcpPort
      $sshArgs = @(
            "-i", $SshKeyPath,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ExitOnForwardFailure=yes",
            "-N",
            "-L", "127.0.0.1:${localPort}:$DbHost:5432",
            "ec2-user@$JumpHost"
      )

      $sshProcess = Start-Process -FilePath "ssh" -ArgumentList $sshArgs -PassThru -WindowStyle Hidden

      $maxAttempts = 10
      $tunnelReady = $false
      for ($attempt = 0; $attempt -lt $maxAttempts; $attempt++) {
            Start-Sleep -Seconds 1
            if (Test-NetConnection -ComputerName '127.0.0.1' -Port $localPort -InformationLevel Quiet) {
                  $tunnelReady = $true
                  break
            }
      }

      if (-not $tunnelReady) {
            if ($sshProcess -and -not $sshProcess.HasExited) {
                  $sshProcess.Kill()
                  $sshProcess.WaitForExit()
            }
            throw "Não foi possível abrir túnel SSH para $DbHost via $JumpHost."
      }

      return @{ Port = $localPort; Process = $sshProcess }
}

function Stop-SshTunnel {
      param([System.Diagnostics.Process]$Process)

      if ($Process -and -not $Process.HasExited) {
            $Process.Kill()
            $Process.WaitForExit()
      }
}

function Invoke-PsqlFile {
      param(
            [string]$DbHost,
            [string]$DbName,
            [string]$DbUser,
            [string]$DbPassword,
            [string]$RelativePath,
            [string]$JumpHost,
            [string]$SshKeyPath
      )

      $fullPath = Join-Path $WORKSPACE $RelativePath
      if (-not (Test-Path $fullPath)) {
            throw "Arquivo SQL não encontrado: $RelativePath"
      }

      $mountPath = $WORKSPACE -replace '\\', '/'
      $relativeUnixPath = $RelativePath -replace '\\', '/'

      $tunnel = Start-SshTunnel -DbHost $DbHost -JumpHost $JumpHost -SshKeyPath $SshKeyPath

      try {
            docker run --rm `
                  -e PGPASSWORD=$DbPassword `
                  -v "${mountPath}:/workspace" `
                  postgres:15-alpine `
                  psql -h host.docker.internal -p $($tunnel.Port) -U $DbUser -d $DbName -f "/workspace/$relativeUnixPath"

            if ($LASTEXITCODE -ne 0) {
                  throw "psql execution failed for $RelativePath (exit code $LASTEXITCODE)"
            }
      }
      finally {
            Stop-SshTunnel -Process $tunnel.Process
      }
}

Write-Host "📋 Configurações:" -ForegroundColor Cyan
Write-Host "  • Stack Name: $STACK_NAME" -ForegroundColor White
Write-Host "  • Region: $REGION" -ForegroundColor White
Write-Host "  • AWS Account: $AWS_ACCOUNT_ID" -ForegroundColor White
Write-Host ""

Write-Host "🔐 Verificando KeyPair padrão..." -ForegroundColor Yellow
$keyPairCheck = aws ec2 describe-key-pairs `
      --key-names ysh-keypair `
      --region $REGION `
      --no-cli-pager 2>$null

if ($LASTEXITCODE -ne 0) {
      Write-Host "🔑 KeyPair 'ysh-keypair' não encontrado. Criando novo..." -ForegroundColor Yellow
      $keyMaterial = aws ec2 create-key-pair `
            --key-name ysh-keypair `
            --region $REGION `
            --query 'KeyMaterial' `
            --output text `
            --no-cli-pager

      $keyPath = Join-Path $WORKSPACE "ysh-keypair.pem"
      Set-Content -Path $keyPath -Value $keyMaterial -Encoding ascii

      try {
            icacls $keyPath /inheritance:r /grant:r "$env:USERNAME:R" | Out-Null
      }
      catch {
            Write-Host "⚠️  Ajuste manualmente as permissões do arquivo $keyPath" -ForegroundColor Yellow
      }

      Write-Host "✅ KeyPair criado e salvo em $keyPath" -ForegroundColor Green
}
else {
      Write-Host "✅ KeyPair 'ysh-keypair' encontrado." -ForegroundColor Green
}

Write-Host ""

$keyPath = Join-Path $WORKSPACE "ysh-keypair.pem"
if (-not (Test-Path $keyPath)) {
      throw "Arquivo $keyPath não encontrado. Necessário para criar túnel SSH até o backend."
}

if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
      throw "Ferramenta SSH não encontrada no PATH. Instale o cliente OpenSSH para continuar."
}

# Configurar credenciais se necessário
try {
      aws sts get-caller-identity | Out-Null
}
catch {
      Write-Host "⚙️  Configurando AWS CLI..." -ForegroundColor Yellow
      aws configure
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📦 Etapa 1/4: Build de Imagens Docker" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Build imagens otimizadas
Write-Host "🐳 Building backend image..." -ForegroundColor Yellow
docker build -t ysh/backend:latest -f Dockerfile.mcp-optimized .

Write-Host ""
Write-Host "🐳 Building worker image..." -ForegroundColor Yellow
docker build -t ysh/worker:latest -f Dockerfile.worker .

Write-Host "✅ Imagens construídas" -ForegroundColor Green

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📤 Etapa 2/4: Push para ECR" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Criar repositórios ECR
Write-Host "📦 Criando repositórios ECR..." -ForegroundColor Yellow
aws ecr create-repository --repository-name ysh/backend --region $REGION 2>$null
aws ecr create-repository --repository-name ysh/worker --region $REGION 2>$null

# Login ECR
Write-Host "🔐 Login no ECR..." -ForegroundColor Yellow
$ecrPassword = aws ecr get-login-password --region $REGION
$ecrPassword | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

# Tag imagens
Write-Host "🏷️  Tagging images..." -ForegroundColor Yellow
docker tag ysh/backend:latest "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/ysh/backend:latest"
docker tag ysh/worker:latest "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/ysh/worker:latest"

# Push imagens
Write-Host "📤 Pushing backend image..." -ForegroundColor Yellow
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/ysh/backend:latest"

Write-Host "📤 Pushing worker image..." -ForegroundColor Yellow
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/ysh/worker:latest"

Write-Host "✅ Imagens no ECR" -ForegroundColor Green

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "☁️  Etapa 3/4: Deploy CloudFormation Stack" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Gerar senha ou reaproveitar existente
function New-RandomPassword {
      param(
            [int]$Length = 32
      )

      if ($Length -lt 12) {
            throw "Password length must be at least 12 characters."
      }

      $lower = 'abcdefghijklmnopqrstuvwxyz'
      $upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
      $digits = '0123456789'
      $symbols = '_-'
      $allChars = $lower + $upper + $digits + $symbols

      function Get-RandomChar {
            param([string]$Charset)

            $buffer = New-Object byte[] 1
            [System.Security.Cryptography.RandomNumberGenerator]::Fill($buffer)
            return $Charset[$buffer[0] % $Charset.Length]
      }

      $passwordList = [System.Collections.Generic.List[char]]::new()
      $passwordList.Add((Get-RandomChar $lower)) | Out-Null
      $passwordList.Add((Get-RandomChar $upper)) | Out-Null
      $passwordList.Add((Get-RandomChar $digits)) | Out-Null
      $passwordList.Add((Get-RandomChar $symbols)) | Out-Null

      for ($i = $passwordList.Count; $i -lt $Length; $i++) {
            $passwordList.Add((Get-RandomChar $allChars)) | Out-Null
      }

      $passwordArray = $passwordList.ToArray()
      for ($i = $passwordArray.Length - 1; $i -gt 0; $i--) {
            $shuffleBuffer = New-Object byte[] 1
            [System.Security.Cryptography.RandomNumberGenerator]::Fill($shuffleBuffer)
            $j = $shuffleBuffer[0] % ($i + 1)
            $temp = $passwordArray[$i]
            $passwordArray[$i] = $passwordArray[$j]
            $passwordArray[$j] = $temp
      }

      return -join $passwordArray
}

# Validar template
Write-Host "✅ Validando template CloudFormation..." -ForegroundColor Yellow
aws cloudformation validate-template `
      --template-body file://aws-cloudformation/main-stack.yml `
      --region $REGION

Write-Host ""

$stackExists = $false
$stackStatus = ""
$describeOutput = aws cloudformation describe-stacks `
      --stack-name $STACK_NAME `
      --region $REGION `
      --query 'Stacks[0].StackStatus' `
      --output text `
      --no-cli-pager 2>$null

if ($LASTEXITCODE -eq 0 -and $describeOutput) {
      $stackExists = $true
      $stackStatus = $describeOutput.Trim()
}

if ($stackExists -and ($stackStatus -eq "ROLLBACK_COMPLETE" -or $stackStatus -eq "ROLLBACK_FAILED")) {
      Write-Host "♻️  Removendo stack em estado de rollback para recriação..." -ForegroundColor Yellow
      aws cloudformation delete-stack `
            --stack-name $STACK_NAME `
            --region $REGION | Out-Null

      $waitDeleteOutput = aws cloudformation wait stack-delete-complete `
            --stack-name $STACK_NAME `
            --region $REGION 2>&1

      if ($LASTEXITCODE -ne 0) {
            Write-Error "Falha ao remover stack anterior: $waitDeleteOutput"
            throw
      }

      $stackExists = $false
      $stackStatus = ""
}

$existingDbPassword = $null
if (Test-Path ".env.aws") {
      $envContent = Get-Content ".env.aws" -Raw
      if ($envContent -match 'DB_PASSWORD=(.+)') {
            $existingDbPassword = $matches[1].Trim()
      }
}

$generatedNewPassword = $false

if ($stackExists) {
      if (-not $existingDbPassword) {
            throw "Stack já existe, porém não foi possível ler DB_PASSWORD em .env.aws."
      }
      $DB_PASSWORD = $existingDbPassword
      Write-Host "🔑 Reutilizando senha do banco de dados existente." -ForegroundColor Yellow
}
else {
      if (-not $existingDbPassword) {
            $DB_PASSWORD = New-RandomPassword 32
            $generatedNewPassword = $true
      }
      else {
            $DB_PASSWORD = $existingDbPassword
      }
}

if ($generatedNewPassword) {
      Write-Host "🔑 Gerando senha do banco de dados..." -ForegroundColor Yellow
      Set-Content -Path ".env.aws" -Value "DB_PASSWORD=$DB_PASSWORD"
      Write-Host "✅ Senha salva em .env.aws (mantenha seguro!)" -ForegroundColor Green
}

if ($stackExists) {
      Write-Host "♻️  Atualizando CloudFormation stack..." -ForegroundColor Yellow
      $updateOutput = aws cloudformation update-stack `
            --stack-name $STACK_NAME `
            --template-body file://aws-cloudformation/main-stack.yml `
            --parameters `
            'ParameterKey=KeyPairName,ParameterValue=ysh-keypair' `
            "ParameterKey=DBPassword,ParameterValue=$DB_PASSWORD" `
            --capabilities CAPABILITY_IAM `
            --region $REGION 2>&1

      if ($LASTEXITCODE -ne 0) {
            if ($updateOutput -match "No updates are to be performed") {
                  Write-Host "ℹ️  Nenhuma atualização necessária para a stack." -ForegroundColor Yellow
            }
            else {
                  Write-Error "Falha ao atualizar stack: $updateOutput"
                  throw
            }
      }
      else {
            Write-Host "⏳ Aguardando atualização da stack..." -ForegroundColor Yellow
            $waitUpdateOutput = aws cloudformation wait stack-update-complete `
                  --stack-name $STACK_NAME `
                  --region $REGION 2>&1

            if ($LASTEXITCODE -ne 0) {
                  Write-Error "Falha ao aguardar atualização da stack: $waitUpdateOutput"
                  throw
            }
      }
}
else {
      Write-Host "🚀 Criando CloudFormation stack..." -ForegroundColor Yellow
      $createOutput = aws cloudformation create-stack `
            --stack-name $STACK_NAME `
            --template-body file://aws-cloudformation/main-stack.yml `
            --parameters `
            'ParameterKey=KeyPairName,ParameterValue=ysh-keypair' `
            "ParameterKey=DBPassword,ParameterValue=$DB_PASSWORD" `
            --capabilities CAPABILITY_IAM `
            --region $REGION 2>&1

      if ($LASTEXITCODE -ne 0) {
            Write-Error "Falha ao criar stack: $createOutput"
            throw
      }

      Write-Host ""
      Write-Host "⏳ Aguardando criação da stack (isso pode levar 15-20 minutos)..." -ForegroundColor Yellow
      $waitCreateOutput = aws cloudformation wait stack-create-complete `
            --stack-name $STACK_NAME `
            --region $REGION 2>&1

      if ($LASTEXITCODE -ne 0) {
            Write-Error "Falha ao aguardar criação da stack: $waitCreateOutput"
            throw
      }
}

Write-Host "✅ Stack criada com sucesso!" -ForegroundColor Green

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "💾 Etapa 4/4: Inicialização de Databases" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Aguardar RDS ficar disponível antes de rodar scripts
Write-Host "⏳ Aguardando instâncias RDS ficarem disponíveis..." -ForegroundColor Yellow
aws rds wait db-instance-available `
      --db-instance-identifier "$STACK_NAME-supabase-db" `
      --region $REGION

aws rds wait db-instance-available `
      --db-instance-identifier "$STACK_NAME-temporal-db" `
      --region $REGION
Write-Host "✅ RDS disponível." -ForegroundColor Green

# Obter outputs
Write-Host "📊 Obtendo endpoints..." -ForegroundColor Yellow
$SUPABASE_DB = aws cloudformation describe-stacks `
      --stack-name $STACK_NAME `
      --region $REGION `
      --query 'Stacks[0].Outputs[?OutputKey==`SupabaseDBEndpoint`].OutputValue' `
      --output text

$TEMPORAL_DB = aws cloudformation describe-stacks `
      --stack-name $STACK_NAME `
      --region $REGION `
      --query 'Stacks[0].Outputs[?OutputKey==`TemporalDBEndpoint`].OutputValue' `
      --output text

$REDIS_ENDPOINT = aws cloudformation describe-stacks `
      --stack-name $STACK_NAME `
      --region $REGION `
      --query 'Stacks[0].Outputs[?OutputKey==`RedisEndpoint`].OutputValue' `
      --output text

$BACKEND_URL = aws cloudformation describe-stacks `
      --stack-name $STACK_NAME `
      --region $REGION `
      --query 'Stacks[0].Outputs[?OutputKey==`BackendURL`].OutputValue' `
      --output text

if ($BACKEND_URL -match 'http://([^/:]+)') {
      $BACKEND_IP = $matches[1]
}
else {
      throw "Não foi possível extrair o IP público do backend a partir de $BACKEND_URL."
}

# Inicializar Supabase DB
Write-Host "💾 Inicializando Supabase DB..." -ForegroundColor Yellow
Invoke-PsqlFile -DbHost $SUPABASE_DB -DbName "postgres" -DbUser "supabase_admin" -DbPassword $DB_PASSWORD -RelativePath "init-scripts/supabase-init.sql" -JumpHost $BACKEND_IP -SshKeyPath $keyPath

Write-Host "✅ Supabase DB inicializado" -ForegroundColor Green

Write-Host ""
Write-Host "🚚 Etapa 4.1/4: Migrando e Populando Catálogo de Produtos..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Migrar a tabela do catálogo
Write-Host "🔧 Migrando a tabela do catálogo de produtos..." -ForegroundColor Yellow
Invoke-PsqlFile -DbHost $SUPABASE_DB -DbName "postgres" -DbUser "supabase_admin" -DbPassword $DB_PASSWORD -RelativePath "database/migrations/003-create-catalog-table.sql" -JumpHost $BACKEND_IP -SshKeyPath $keyPath
Write-Host "✅ Tabela do catálogo migrada." -ForegroundColor Green

# Instalar dependências do script de importação
Write-Host "📦 Instalando dependências para o script de importação..." -ForegroundColor Yellow
npm install --omit=dev --legacy-peer-deps
Write-Host "✅ Dependências instaladas." -ForegroundColor Green

# Popular a tabela do catálogo
Write-Host "🚚 Populando a tabela do catálogo com produtos..." -ForegroundColor Yellow
$catalogTunnel = Start-SshTunnel -DbHost $SUPABASE_DB -JumpHost $BACKEND_IP -SshKeyPath $keyPath
try {
      $env:DATABASE_URL = "postgresql://supabase_admin:$DB_PASSWORD@127.0.0.1:$($catalogTunnel.Port)/postgres"
      node scripts/import-catalog-to-db.js
      if ($LASTEXITCODE -ne 0) {
            throw "Importação do catálogo falhou (exit code $LASTEXITCODE)"
      }
      Write-Host "✅ Tabela do catálogo populada." -ForegroundColor Green
}
finally {
      Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
      Stop-SshTunnel -Process $catalogTunnel.Process
}


Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎉 DEPLOYMENT CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Informações da Stack:" -ForegroundColor Cyan
Write-Host "" 
Write-Host "Backend API:" -ForegroundColor Yellow
Write-Host "  $BACKEND_URL" -ForegroundColor White
Write-Host "" 
Write-Host "Databases:" -ForegroundColor Yellow
Write-Host "  • Supabase DB: $SUPABASE_DB`:5432" -ForegroundColor White
Write-Host "  • Temporal DB: $TEMPORAL_DB`:5432" -ForegroundColor White
Write-Host "" 
Write-Host "Cache:" -ForegroundColor Yellow
Write-Host "  • Redis: $REDIS_ENDPOINT`:6379" -ForegroundColor White
Write-Host ""

Write-Host "💡 Próximos passos:" -ForegroundColor Cyan
Write-Host "  1. Testar health: Invoke-WebRequest $BACKEND_URL/health" -ForegroundColor Gray
Write-Host "  2. Ver logs: aws logs tail /aws/ec2/ysh-backend --follow" -ForegroundColor Gray
Write-Host "  3. Monitorar custos: aws ce get-cost-and-usage" -ForegroundColor Gray
Write-Host ""

Write-Host "⚠️  Lembrete: Stack está no Free Tier por 12 meses" -ForegroundColor Yellow
Write-Host ""
