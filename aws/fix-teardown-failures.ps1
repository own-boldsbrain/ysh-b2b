#!/usr/bin/env pwsh
# Script para corrigir falhas do teardown CloudFormation
# Resolve problemas de proteção RDS e dependências de rede

Write-Host "`n🔧 CORRIGINDO FALHAS DO TEARDOWN" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

$awsProfile = "ysh-production"
$awsRegion = "us-east-1"
$stackName = "ysh-b2b-infrastructure"

# 1. Desabilitar proteção de deleção do RDS
Write-Host "💾 1. Desabilitando proteção de deleção do RDS..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

$dbIdentifier = "production-ysh-b2b-postgres"

try {
      Write-Host "   Verificando instância RDS: $dbIdentifier" -ForegroundColor Cyan
    
      $dbInfo = aws rds describe-db-instances `
            --db-instance-identifier $dbIdentifier `
            --profile $awsProfile `
            --region $awsRegion `
            --query 'DBInstances[0].DeletionProtection' `
            --output text 2>&1
    
      if ($LASTEXITCODE -eq 0) {
            if ($dbInfo -eq "True") {
                  Write-Host "   ⚠️  Proteção de deleção ATIVADA - Desabilitando..." -ForegroundColor Yellow
            
                  $result = aws rds modify-db-instance `
                        --db-instance-identifier $dbIdentifier `
                        --no-deletion-protection `
                        --apply-immediately `
                        --profile $awsProfile `
                        --region $awsRegion 2>&1
            
                  if ($LASTEXITCODE -eq 0) {
                        Write-Host "   ✅ Proteção de deleção DESABILITADA com sucesso" -ForegroundColor Green
                        Write-Host "   ⏳ Aguardando 30 segundos para aplicar mudança..." -ForegroundColor Cyan
                        Start-Sleep -Seconds 30
                  }
                  else {
                        Write-Host "   ❌ Erro ao desabilitar proteção: $result" -ForegroundColor Red
                  }
            }
            else {
                  Write-Host "   ✅ Proteção de deleção já está DESABILITADA" -ForegroundColor Green
            }
      }
      else {
            if ($dbInfo -match "DBInstanceNotFound") {
                  Write-Host "   ✅ Instância RDS não encontrada (já deletada)" -ForegroundColor Green
            }
            else {
                  Write-Host "   ❌ Erro ao verificar RDS: $dbInfo" -ForegroundColor Red
            }
      }
}
catch {
      Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

Write-Host ""

# 2. Limpar ENIs (Elastic Network Interfaces) órfãs
Write-Host "🔌 2. Limpando ENIs (Elastic Network Interfaces) órfãs..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

try {
      # Obter VPC do stack
      $vpcId = aws cloudformation describe-stack-resources `
            --stack-name $stackName `
            --profile $awsProfile `
            --region $awsRegion `
            --query "StackResources[?ResourceType=='AWS::EC2::VPC'].PhysicalResourceId" `
            --output text 2>&1
    
      if ($LASTEXITCODE -eq 0 -and $vpcId) {
            Write-Host "   VPC ID: $vpcId" -ForegroundColor Cyan
        
            # Listar ENIs disponíveis na VPC
            $enis = aws ec2 describe-network-interfaces `
                  --filters "Name=vpc-id,Values=$vpcId" "Name=status,Values=available" `
                  --profile $awsProfile `
                  --region $awsRegion `
                  --query 'NetworkInterfaces[*].NetworkInterfaceId' `
                  --output text 2>&1
        
            if ($enis -and $enis.Trim() -ne "") {
                  $eniList = $enis -split "`s+"
                  Write-Host "   Encontradas $($eniList.Count) ENI(s) disponível(is)" -ForegroundColor Yellow
            
                  foreach ($eni in $eniList) {
                        if ($eni.Trim() -ne "") {
                              Write-Host "   Deletando ENI: $eni" -ForegroundColor Yellow
                              $result = aws ec2 delete-network-interface `
                                    --network-interface-id $eni `
                                    --profile $awsProfile `
                                    --region $awsRegion 2>&1
                    
                              if ($LASTEXITCODE -eq 0) {
                                    Write-Host "      ✅ Deletado com sucesso" -ForegroundColor Green
                              }
                              else {
                                    Write-Host "      ⚠️  $result" -ForegroundColor Yellow
                              }
                        }
                  }
            }
            else {
                  Write-Host "   ✅ Nenhuma ENI órfã encontrada" -ForegroundColor Green
            }
        
            # Listar ENIs ainda em uso
            $enisInUse = aws ec2 describe-network-interfaces `
                  --filters "Name=vpc-id,Values=$vpcId" "Name=status,Values=in-use" `
                  --profile $awsProfile `
                  --region $awsRegion `
                  --query 'NetworkInterfaces[*].[NetworkInterfaceId,Attachment.InstanceOwnerId,Description]' `
                  --output table 2>&1
        
            if ($enisInUse -and $enisInUse.Trim() -ne "" -and $enisInUse -notmatch "None") {
                  Write-Host "`n   ⚠️  ENIs ainda em uso:" -ForegroundColor Yellow
                  Write-Host $enisInUse
                  Write-Host "`n   💡 Aguarde alguns minutos e execute novamente" -ForegroundColor Cyan
            }
      }
      else {
            Write-Host "   ℹ️  VPC não encontrada ou já deletada" -ForegroundColor Gray
      }
}
catch {
      Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

Write-Host ""

# 3. Forçar desanexação do Internet Gateway
Write-Host "🌐 3. Forçando desanexação do Internet Gateway..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

try {
      if ($vpcId) {
            # Listar Internet Gateways anexados à VPC
            $igws = aws ec2 describe-internet-gateways `
                  --filters "Name=attachment.vpc-id,Values=$vpcId" `
                  --profile $awsProfile `
                  --region $awsRegion `
                  --query 'InternetGateways[*].InternetGatewayId' `
                  --output text 2>&1
        
            if ($igws -and $igws.Trim() -ne "") {
                  $igwList = $igws -split "`s+"
                  foreach ($igw in $igwList) {
                        if ($igw.Trim() -ne "") {
                              Write-Host "   Desanexando IGW: $igw da VPC: $vpcId" -ForegroundColor Yellow
                              $result = aws ec2 detach-internet-gateway `
                                    --internet-gateway-id $igw `
                                    --vpc-id $vpcId `
                                    --profile $awsProfile `
                                    --region $awsRegion 2>&1
                    
                              if ($LASTEXITCODE -eq 0) {
                                    Write-Host "      ✅ Desanexado com sucesso" -ForegroundColor Green
                              }
                              else {
                                    if ($result -match "not attached") {
                                          Write-Host "      ✅ IGW já estava desanexado" -ForegroundColor Green
                                    }
                                    else {
                                          Write-Host "      ⚠️  $result" -ForegroundColor Yellow
                                    }
                              }
                        }
                  }
            }
            else {
                  Write-Host "   ✅ Nenhum Internet Gateway anexado" -ForegroundColor Green
            }
      }
}
catch {
      Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

Write-Host "`n─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

# 4. Tentar novamente a deleção do stack
Write-Host "`n🔄 4. Tentando novamente a deleção do stack..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

Write-Host "`n   Executando: aws cloudformation delete-stack..." -ForegroundColor Cyan

$deleteResult = aws cloudformation delete-stack `
      --stack-name $stackName `
      --profile $awsProfile `
      --region $awsRegion 2>&1

if ($LASTEXITCODE -eq 0) {
      Write-Host "   ✅ Comando de deleção executado com sucesso" -ForegroundColor Green
      Write-Host "`n   ⏳ Stack entrando em DELETE_IN_PROGRESS..." -ForegroundColor Yellow
      Write-Host "   ⏱️  Aguardando 15 segundos..." -ForegroundColor Cyan
      Start-Sleep -Seconds 15
    
      # Verificar status
      Write-Host "`n   📊 Status atual:" -ForegroundColor Cyan
      $status = aws cloudformation describe-stacks `
            --stack-name $stackName `
            --profile $awsProfile `
            --region $awsRegion `
            --query 'Stacks[0].StackStatus' `
            --output text 2>&1
    
      if ($status -eq "DELETE_IN_PROGRESS") {
            Write-Host "   ✅ Stack em DELETE_IN_PROGRESS" -ForegroundColor Green
      }
      else {
            Write-Host "   Status: $status" -ForegroundColor Yellow
      }
}
else {
      if ($deleteResult -match "does not exist") {
            Write-Host "   ✅ Stack já foi deletado!" -ForegroundColor Green
      }
      else {
            Write-Host "   ❌ Erro: $deleteResult" -ForegroundColor Red
      }
}

Write-Host "`n─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

# Resumo Final
Write-Host "`n📋 RESUMO" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "✅ Correções aplicadas:" -ForegroundColor Green
Write-Host "   - Proteção de deleção RDS desabilitada" -ForegroundColor White
Write-Host "   - ENIs órfãs removidas" -ForegroundColor White
Write-Host "   - Internet Gateway desanexado" -ForegroundColor White
Write-Host "   - Deleção do stack reiniciada`n" -ForegroundColor White

Write-Host "🔍 Próximo passo:" -ForegroundColor Yellow
Write-Host "   Execute .\check-teardown-status.ps1 em 2-3 minutos para verificar progresso`n" -ForegroundColor White

Write-Host "💡 Se ainda houver erros:" -ForegroundColor Cyan
Write-Host "   1. Aguarde 5 minutos e execute este script novamente" -ForegroundColor White
Write-Host "   2. Verifique o Console AWS CloudFormation para detalhes" -ForegroundColor White
Write-Host "   3. https://console.aws.amazon.com/cloudformation`n" -ForegroundColor Gray
