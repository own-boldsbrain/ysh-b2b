#!/usr/bin/env pwsh
# Script para verificar status do teardown AWS - YSH B2B
# Execute no terminal onde AWS CLI funciona

Write-Host "`n🔍 VERIFICANDO STATUS DO TEARDOWN..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

$stackName = "ysh-b2b-infrastructure"
$profile = "ysh-production"
$region = "us-east-1"

# 1. Verificar Stack CloudFormation
Write-Host "📦 1. CloudFormation Stack Status" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

try {
      $stackStatus = aws cloudformation describe-stacks `
            --stack-name $stackName `
            --profile $profile `
            --region $region `
            --query 'Stacks[0].StackStatus' `
            --output text 2>&1

      if ($LASTEXITCODE -eq 0) {
            Write-Host "   Status: " -NoNewline
            switch ($stackStatus) {
                  "DELETE_IN_PROGRESS" { 
                        Write-Host "⏳ $stackStatus" -ForegroundColor Yellow
                
                        # Mostrar progresso
                        Write-Host "`n   📊 Progresso da Deleção:" -ForegroundColor Cyan
                        $events = aws cloudformation describe-stack-events `
                              --stack-name $stackName `
                              --profile $profile `
                              --region $region `
                              --query 'StackEvents[?ResourceStatus==`DELETE_IN_PROGRESS` || ResourceStatus==`DELETE_COMPLETE`].[Timestamp,LogicalResourceId,ResourceStatus]' `
                              --output table 2>&1
                
                        Write-Host $events
                
                        # Calcular tempo decorrido
                        $stackInfo = aws cloudformation describe-stacks `
                              --stack-name $stackName `
                              --profile $profile `
                              --region $region `
                              --query 'Stacks[0].DeletionTime' `
                              --output text 2>&1
                
                        if ($stackInfo -ne $null -and $stackInfo -ne "") {
                              $deletionTime = [DateTime]::Parse($stackInfo)
                              $elapsed = (Get-Date).ToUniversalTime() - $deletionTime
                              Write-Host "`n   ⏱️  Tempo decorrido: $($elapsed.Minutes) minutos $($elapsed.Seconds) segundos" -ForegroundColor Cyan
                              Write-Host "   ⏱️  Tempo restante estimado: 15-25 minutos (total)" -ForegroundColor Cyan
                        }
                  }
                  "DELETE_COMPLETE" {
                        Write-Host "✅ $stackStatus - Stack deletado com sucesso!" -ForegroundColor Green
                  }
                  "DELETE_FAILED" {
                        Write-Host "❌ $stackStatus - Falha na deleção!" -ForegroundColor Red
                        Write-Host "`n   Últimos eventos de erro:" -ForegroundColor Yellow
                        $errors = aws cloudformation describe-stack-events `
                              --stack-name $stackName `
                              --profile $profile `
                              --region $region `
                              --query 'StackEvents[?ResourceStatus==`DELETE_FAILED`].[LogicalResourceId,ResourceStatusReason]' `
                              --output table 2>&1
                        Write-Host $errors
                  }
                  default {
                        Write-Host "⚠️  $stackStatus" -ForegroundColor Yellow
                  }
            }
      }
      else {
            if ($stackStatus -match "does not exist") {
                  Write-Host "   Status: " -NoNewline
                  Write-Host "✅ DELETADO - Stack não existe mais!" -ForegroundColor Green
                  $stackDeleted = $true
            }
            else {
                  Write-Host "   ❌ Erro ao verificar stack:" -ForegroundColor Red
                  Write-Host "   $stackStatus" -ForegroundColor Red
            }
      }
}
catch {
      Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

Write-Host "`n─────────────────────────────────────────────────────────`n" -ForegroundColor DarkGray

# 2. Verificar Snapshot RDS
Write-Host "💾 2. RDS Snapshot Status" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

$snapshotId = "ysh-final-backup-20251019-180524"

try {
      $snapshotStatus = aws rds describe-db-snapshots `
            --db-snapshot-identifier $snapshotId `
            --profile $profile `
            --region $region `
            --query 'DBSnapshots[0].[Status,AllocatedStorage,SnapshotCreateTime]' `
            --output text 2>&1

      if ($LASTEXITCODE -eq 0) {
            $statusData = $snapshotStatus -split "`t"
            $status = $statusData[0]
            $size = $statusData[1]
            $createTime = $statusData[2]
        
            Write-Host "   Snapshot ID: " -NoNewline
            Write-Host "$snapshotId" -ForegroundColor Cyan
            Write-Host "   Status: " -NoNewline
        
            switch ($status) {
                  "available" { 
                        Write-Host "✅ $status" -ForegroundColor Green 
                        Write-Host "   Tamanho: $size GB" -ForegroundColor Gray
                        Write-Host "   Criado em: $createTime" -ForegroundColor Gray
                        Write-Host "   💰 Custo estimado: $([math]::Round($size * 0.02, 2))/mês" -ForegroundColor Yellow
                  }
                  "creating" { 
                        Write-Host "⏳ $status" -ForegroundColor Yellow 
                        Write-Host "   Tamanho: $size GB (estimado)" -ForegroundColor Gray
                  }
                  default { 
                        Write-Host "⚠️  $status" -ForegroundColor Yellow 
                  }
            }
      }
      else {
            Write-Host "   ⚠️  Snapshot não encontrado ou erro ao verificar" -ForegroundColor Yellow
      }
}
catch {
      Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

Write-Host "`n─────────────────────────────────────────────────────────`n" -ForegroundColor DarkGray

# 3. Recursos Órfãos (só verificar se stack foi deletado)
if ($stackDeleted) {
      Write-Host "🧹 3. Recursos Órfãos a Limpar" -ForegroundColor Yellow
      Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

      # Secrets Manager
      Write-Host "`n   📜 Secrets Manager:" -ForegroundColor Cyan
      $secrets = aws secretsmanager list-secrets `
            --profile $profile `
            --region $region `
            --query "SecretList[?contains(Name, 'ysh') || contains(Name, 'production')].Name" `
            --output text 2>&1
    
      if ($secrets -and $secrets.Trim() -ne "") {
            $secretCount = ($secrets -split "`n").Count
            Write-Host "      ⚠️  $secretCount secret(s) encontrado(s)" -ForegroundColor Yellow
            Write-Host "      Secrets: $secrets" -ForegroundColor Gray
      }
      else {
            Write-Host "      ✅ Nenhum secret órfão" -ForegroundColor Green
      }

      # ECR Repositories
      Write-Host "`n   📦 ECR Repositories:" -ForegroundColor Cyan
      $repos = aws ecr describe-repositories `
            --profile $profile `
            --region $region `
            --query "repositories[?contains(repositoryName, 'ysh')].repositoryName" `
            --output text 2>&1
    
      if ($repos -and $repos.Trim() -ne "") {
            $repoCount = ($repos -split "`n").Count
            Write-Host "      ⚠️  $repoCount repositório(s) encontrado(s)" -ForegroundColor Yellow
            Write-Host "      Repos: $repos" -ForegroundColor Gray
      }
      else {
            Write-Host "      ✅ Nenhum repositório órfão" -ForegroundColor Green
      }

      # CloudWatch Log Groups
      Write-Host "`n   📝 CloudWatch Log Groups:" -ForegroundColor Cyan
      $logGroups = aws logs describe-log-groups `
            --profile $profile `
            --region $region `
            --query "logGroups[?contains(logGroupName, 'ysh') || contains(logGroupName, 'production') || contains(logGroupName, 'ecs')].logGroupName" `
            --output text 2>&1
    
      if ($logGroups -and $logGroups.Trim() -ne "") {
            $logCount = ($logGroups -split "`n").Count
            Write-Host "      ⚠️  $logCount log group(s) encontrado(s)" -ForegroundColor Yellow
            Write-Host "      Grupos: $logGroups" -ForegroundColor Gray
      }
      else {
            Write-Host "      ✅ Nenhum log group órfão" -ForegroundColor Green
      }

      Write-Host "`n─────────────────────────────────────────────────────────" -ForegroundColor DarkGray
      Write-Host "`n💡 Para limpar recursos órfãos, execute:" -ForegroundColor Cyan
      Write-Host "   .\cleanup-orphan-resources.ps1`n" -ForegroundColor White
}

# 4. Resumo Final
Write-Host "`n📋 RESUMO FINAL" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($stackDeleted) {
      Write-Host "✅ Teardown COMPLETO!" -ForegroundColor Green
      Write-Host "`n   Próximos passos:" -ForegroundColor Yellow
      Write-Host "   1. Execute .\cleanup-orphan-resources.ps1 para limpar recursos órfãos" -ForegroundColor White
      Write-Host "   2. (Opcional) Delete snapshot RDS para economia total:" -ForegroundColor White
      Write-Host "      aws rds delete-db-snapshot --db-snapshot-identifier $snapshotId --profile $profile --region $region" -ForegroundColor Gray
}
elseif ($stackStatus -eq "DELETE_IN_PROGRESS") {
      Write-Host "⏳ Teardown EM ANDAMENTO" -ForegroundColor Yellow
      Write-Host "`n   Execute este script novamente em alguns minutos para verificar progresso." -ForegroundColor White
}
else {
      Write-Host "⚠️  Status indefinido - verificar manualmente" -ForegroundColor Yellow
}

Write-Host "`n═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
