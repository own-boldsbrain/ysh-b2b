#!/usr/bin/env pwsh
# Script para limpar recursos órfãos após teardown do CloudFormation
# Execute APENAS após confirmar que o stack foi completamente deletado

Write-Host "`n🧹 LIMPEZA DE RECURSOS ÓRFÃOS - YSH B2B" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

$awsProfile = "ysh-production"
$awsRegion = "us-east-1"

# Confirmação
Write-Host "⚠️  ATENÇÃO: Este script irá deletar recursos órfãos!" -ForegroundColor Yellow
Write-Host "   - Secrets Manager" -ForegroundColor Yellow
Write-Host "   - ECR Repositories (vazios)" -ForegroundColor Yellow
Write-Host "   - CloudWatch Log Groups`n" -ForegroundColor Yellow

$confirmation = Read-Host "Deseja continuar? (digite 'SIM' para confirmar)"

if ($confirmation -ne "SIM") {
      Write-Host "`n❌ Operação cancelada pelo usuário.`n" -ForegroundColor Red
      exit 0
}

Write-Host "`n🚀 Iniciando limpeza...`n" -ForegroundColor Green

# 1. Limpar Secrets Manager
Write-Host "📜 1. Limpando Secrets Manager..." -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

$secrets = aws secretsmanager list-secrets `
      --profile $awsProfile `
      --region $awsRegion `
      --query "SecretList[?contains(Name, 'ysh') || contains(Name, 'production')].Name" `
      --output text 2>&1

if ($secrets -and $secrets.Trim() -ne "") {
      $secretList = $secrets -split "`s+"
      foreach ($secret in $secretList) {
            if ($secret.Trim() -ne "") {
                  Write-Host "   Deletando: $secret" -ForegroundColor Yellow
                  $result = aws secretsmanager delete-secret `
                        --secret-id $secret `
                        --force-delete-without-recovery `
                        --profile $awsProfile `
                        --region $awsRegion 2>&1
            
                  if ($LASTEXITCODE -eq 0) {
                        Write-Host "      ✅ Deletado com sucesso" -ForegroundColor Green
                  }
                  else {
                        Write-Host "      ❌ Erro: $result" -ForegroundColor Red
                  }
            }
      }
}
else {
      Write-Host "   ✅ Nenhum secret encontrado" -ForegroundColor Green
}

Write-Host ""

# 2. Limpar ECR Repositories
Write-Host "📦 2. Limpando ECR Repositories..." -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

$repos = aws ecr describe-repositories `
      --profile $awsProfile `
      --region $awsRegion `
      --query "repositories[?contains(repositoryName, 'ysh')].repositoryName" `
      --output text 2>&1

if ($repos -and $repos.Trim() -ne "") {
      $repoList = $repos -split "`s+"
      foreach ($repo in $repoList) {
            if ($repo.Trim() -ne "" -and $repo -notmatch "cdk-hnb659fds") {
                  Write-Host "   Deletando: $repo" -ForegroundColor Yellow
            
                  # Verificar se está vazio
                  $images = aws ecr list-images `
                        --repository-name $repo `
                        --profile $awsProfile `
                        --region $awsRegion `
                        --query 'imageIds[*]' `
                        --output text 2>&1
            
                  if ($images -and $images.Trim() -ne "") {
                        Write-Host "      ⚠️  Repositório não está vazio, pulando..." -ForegroundColor Yellow
                        continue
                  }
            
                  $result = aws ecr delete-repository `
                        --repository-name $repo `
                        --profile $awsProfile `
                        --region $awsRegion 2>&1
            
                  if ($LASTEXITCODE -eq 0) {
                        Write-Host "      ✅ Deletado com sucesso" -ForegroundColor Green
                  }
                  else {
                        Write-Host "      ❌ Erro: $result" -ForegroundColor Red
                  }
            }
      }
}
else {
      Write-Host "   ✅ Nenhum repositório encontrado" -ForegroundColor Green
}

Write-Host ""

# 3. Limpar CloudWatch Log Groups
Write-Host "📝 3. Limpando CloudWatch Log Groups..." -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

$logGroups = aws logs describe-log-groups `
      --profile $awsProfile `
      --region $awsRegion `
      --query "logGroups[?contains(logGroupName, 'ysh') || contains(logGroupName, 'production') || contains(logGroupName, 'ecs')].logGroupName" `
      --output text 2>&1

if ($logGroups -and $logGroups.Trim() -ne "") {
      $logGroupList = $logGroups -split "`n"
      foreach ($logGroup in $logGroupList) {
            if ($logGroup.Trim() -ne "") {
                  Write-Host "   Deletando: $logGroup" -ForegroundColor Yellow
                  $result = aws logs delete-log-group `
                        --log-group-name $logGroup.Trim() `
                        --profile $awsProfile `
                        --region $awsRegion 2>&1
            
                  if ($LASTEXITCODE -eq 0) {
                        Write-Host "      ✅ Deletado com sucesso" -ForegroundColor Green
                  }
                  else {
                        Write-Host "      ❌ Erro: $result" -ForegroundColor Red
                  }
            }
      }
}
else {
      Write-Host "   ✅ Nenhum log group encontrado" -ForegroundColor Green
}

Write-Host "`n─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

# Resumo Final
Write-Host "`n✅ LIMPEZA CONCLUÍDA!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "💰 Custo mensal estimado após limpeza:" -ForegroundColor Yellow
Write-Host "   - Snapshot RDS: ~`$0.40/mês" -ForegroundColor White
Write-Host "   - Outros recursos: `$0.00/mês" -ForegroundColor White
Write-Host "   - TOTAL: ~`$0.40/mês`n" -ForegroundColor Green

Write-Host "💡 Para deletar o snapshot e zerar custos:" -ForegroundColor Cyan
Write-Host "   aws rds delete-db-snapshot --db-snapshot-identifier ysh-final-backup-20251019-180524 --profile $awsProfile --region $awsRegion`n" -ForegroundColor Gray
