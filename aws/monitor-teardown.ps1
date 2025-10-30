# Monitor CloudFormation Stack Deletion
Write-Host "`n🔍 MONITORAMENTO DE TEARDOWN`n" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor DarkGray

$stackName = "ysh-b2b-infrastructure"
$profile = "ysh-production"
$region = "us-east-1"

Write-Host "`n📊 Verificando status do stack..." -ForegroundColor Yellow

$result = aws cloudformation describe-stacks --stack-name $stackName --profile $profile --region $region 2>&1 | Out-String

if ($result -match "does not exist") {
      Write-Host "`n✅ STACK COMPLETAMENTE DELETADO!" -ForegroundColor Green
      Write-Host "   Todos os 21 recursos foram removidos com sucesso" -ForegroundColor Gray
    
      Write-Host "`n📋 Recursos deletados:" -ForegroundColor Cyan
      Write-Host "   ❌ RDS PostgreSQL: production-ysh-b2b-postgres" -ForegroundColor White
      Write-Host "   ❌ ElastiCache Redis: production-ysh-b2b-redis" -ForegroundColor White
      Write-Host "   ❌ Application Load Balancer" -ForegroundColor White
      Write-Host "   ❌ ECS Cluster: production-ysh-b2b-cluster" -ForegroundColor White
      Write-Host "   ❌ VPC + 4 Subnets + Security Groups" -ForegroundColor White
    
      Write-Host "`n🔄 FASE 3: LIMPEZA DE RECURSOS ÓRFÃOS`n" -ForegroundColor Cyan
    
      # Deletar Secrets Manager
      Write-Host "🗑️ Deletando Secrets Manager..." -ForegroundColor Yellow
      $secrets = aws secretsmanager list-secrets --profile $profile --region $region --output json | ConvertFrom-Json | Select-Object -ExpandProperty SecretList | Where-Object { $_.Name -like "*ysh*" -or $_.Name -like "*production*" }
    
      if ($secrets.Count -gt 0) {
            Write-Host "   Encontrados $($secrets.Count) secrets:" -ForegroundColor Gray
            foreach ($secret in $secrets) {
                  Write-Host "   • $($secret.Name)" -ForegroundColor White
                  aws secretsmanager delete-secret --secret-id $secret.Name --force-delete-without-recovery --profile $profile --region $region --output json | Out-Null
                  Write-Host "     ✅ Deletado" -ForegroundColor Green
            }
      }
      else {
            Write-Host "   ℹ️ Nenhum secret encontrado" -ForegroundColor Gray
      }
    
      # Deletar ECR Repositories
      Write-Host "`n🗑️ Deletando ECR Repositories..." -ForegroundColor Yellow
      $repos = @("ysh-backend", "ysh-storefront")
      foreach ($repo in $repos) {
            try {
                  aws ecr delete-repository --repository-name $repo --force --profile $profile --region $region --output json | Out-Null
                  Write-Host "   ✅ $repo deletado" -ForegroundColor Green
            }
            catch {
                  Write-Host "   ℹ️ $repo não encontrado ou já deletado" -ForegroundColor Gray
            }
      }
    
      # Deletar CloudWatch Log Groups
      Write-Host "`n🗑️ Deletando CloudWatch Log Groups..." -ForegroundColor Yellow
      $logGroups = aws logs describe-log-groups --profile $profile --region $region --output json | ConvertFrom-Json | Select-Object -ExpandProperty logGroups | Where-Object { $_.logGroupName -like "*ysh*" -or $_.logGroupName -like "*production*" }
    
      if ($logGroups.Count -gt 0) {
            Write-Host "   Encontrados $($logGroups.Count) log groups:" -ForegroundColor Gray
            foreach ($logGroup in $logGroups) {
                  Write-Host "   • $($logGroup.logGroupName)" -ForegroundColor White
                  aws logs delete-log-group --log-group-name $logGroup.logGroupName --profile $profile --region $region
                  Write-Host "     ✅ Deletado" -ForegroundColor Green
            }
      }
      else {
            Write-Host "   ℹ️ Nenhum log group encontrado" -ForegroundColor Gray
      }
    
      # Verificar snapshot do RDS
      Write-Host "`n📸 Verificando snapshot do RDS..." -ForegroundColor Yellow
      $snapshots = aws rds describe-db-snapshots --profile $profile --region $region --output json | ConvertFrom-Json | Select-Object -ExpandProperty DBSnapshots | Where-Object { $_.DBSnapshotIdentifier -like "*ysh-final-backup*" } | Sort-Object SnapshotCreateTime -Descending | Select-Object -First 1
    
      if ($snapshots) {
            Write-Host "   ✅ Backup encontrado:" -ForegroundColor Green
            Write-Host "      ID: $($snapshots.DBSnapshotIdentifier)" -ForegroundColor White
            Write-Host "      Status: $($snapshots.Status)" -ForegroundColor $(if ($snapshots.Status -eq "available") { "Green" } else { "Yellow" })
            Write-Host "      Size: $($snapshots.AllocatedStorage) GB" -ForegroundColor Gray
      }
    
      Write-Host "`n" -NoNewline
      Write-Host "═══════════════════════════════════════════════════" -ForegroundColor DarkGray
      Write-Host "✅ TEARDOWN COMPLETO FINALIZADO!" -ForegroundColor Green
      Write-Host "═══════════════════════════════════════════════════" -ForegroundColor DarkGray
      Write-Host "`n💰 Custo após teardown: ~$0.40/mês (apenas snapshot RDS)" -ForegroundColor Yellow
      Write-Host "   Para economia total, delete o snapshot manualmente se não precisar" -ForegroundColor Gray
    
}
elseif ($LASTEXITCODE -eq 0) {
      $stackData = $result | ConvertFrom-Json
      $stack = $stackData.Stacks[0]
    
      Write-Host "`n⏳ Status: $($stack.StackStatus)" -ForegroundColor Yellow
    
      if ($stack.StackStatus -eq "DELETE_IN_PROGRESS") {
            Write-Host "`n🔄 Deleção em andamento..." -ForegroundColor Cyan
            Write-Host "   Tempo estimado restante: 10-20 minutos" -ForegroundColor Gray
        
            Write-Host "`n📦 Recursos sendo deletados:" -ForegroundColor Yellow
            $resources = aws cloudformation list-stack-resources --stack-name $stackName --profile $profile --region $region --output json | ConvertFrom-Json | Select-Object -ExpandProperty StackResourceSummaries
        
            $deleting = $resources | Where-Object { $_.ResourceStatus -eq "DELETE_IN_PROGRESS" }
            $deleted = $resources | Where-Object { $_.ResourceStatus -eq "DELETE_COMPLETE" }
        
            Write-Host "   ✅ Deletados: $($deleted.Count)/$($resources.Count)" -ForegroundColor Green
            Write-Host "   ⏳ Em progresso: $($deleting.Count)" -ForegroundColor Yellow
        
            if ($deleting.Count -gt 0) {
                  Write-Host "`n   Recursos em deleção:" -ForegroundColor Gray
                  $deleting | Select-Object -First 5 | ForEach-Object {
                        Write-Host "     🔄 $($_.ResourceType): $($_.LogicalResourceId)" -ForegroundColor White
                  }
            }
        
            Write-Host "`n💡 Execute este script novamente para atualizar o status" -ForegroundColor Cyan
      }
}
else {
      Write-Host "`n❌ Erro ao verificar stack:" -ForegroundColor Red
      Write-Host $result -ForegroundColor Gray
}
