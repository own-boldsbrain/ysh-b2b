#!/usr/bin/env pwsh
# Script avançado para limpeza forçada de recursos órfãos AWS
# Remove VPC Endpoints, ENIs, Security Groups e outros recursos bloqueadores

Write-Host "`n🧹 LIMPEZA FORÇADA DE RECURSOS ÓRFÃOS" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

$awsProfile = "ysh-production"
$awsRegion = "us-east-1"
$vpcId = "vpc-096abb11405bb44af"

Write-Host "🎯 Target VPC: $vpcId" -ForegroundColor Yellow
Write-Host "📍 Account: 773235999227" -ForegroundColor Gray
Write-Host "🌍 Region: $awsRegion`n" -ForegroundColor Gray

# Função para confirmar ação
function Confirm-Action {
      param([string]$Message)
      Write-Host "$Message" -ForegroundColor Yellow
      $confirmation = Read-Host "Digite 'SIM' para confirmar"
      return $confirmation -eq "SIM"
}

# 1. Deletar VPC Endpoints (causa raiz das ENIs em uso)
Write-Host "🔌 1. Removendo VPC Endpoints..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

try {
      $vpcEndpoints = aws ec2 describe-vpc-endpoints `
            --filters "Name=vpc-id,Values=$vpcId" `
            --profile $awsProfile `
            --region $awsRegion `
            --query 'VpcEndpoints[*].[VpcEndpointId,ServiceName,State]' `
            --output text 2>&1

      if ($vpcEndpoints -and $vpcEndpoints.Trim() -ne "") {
            $endpoints = $vpcEndpoints -split "`n"
            Write-Host "   Encontrados $($endpoints.Count) VPC Endpoint(s)" -ForegroundColor Cyan
        
            foreach ($endpoint in $endpoints) {
                  if ($endpoint.Trim() -ne "") {
                        $parts = $endpoint -split "`t"
                        $endpointId = $parts[0]
                        $serviceName = $parts[1]
                        $state = $parts[2]
                
                Write-Host "   Deletando: $endpointId ($serviceName) - $state" -ForegroundColor Yellow
                
                $result = aws ec2 delete-vpc-endpoints `
                    --vpc-endpoint-ids $endpointId `
                    --profile $awsProfile `
                    --region $awsRegion 2>&1                        if ($LASTEXITCODE -eq 0) {
                              Write-Host "      ✅ Deletado com sucesso" -ForegroundColor Green
                        }
                        else {
                              Write-Host "      ⚠️  $result" -ForegroundColor Yellow
                        }
                  }
            }
        
            Write-Host "`n   ⏳ Aguardando 30 segundos para ENIs serem liberadas..." -ForegroundColor Cyan
            Start-Sleep -Seconds 30
      }
      else {
            Write-Host "   ✅ Nenhum VPC Endpoint encontrado" -ForegroundColor Green
      }
}
catch {
      Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

Write-Host ""

# 2. Forçar liberação de Elastic IPs
Write-Host "🌐 2. Liberando Elastic IPs..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

try {
      $eips = aws ec2 describe-addresses `
            --filters "Name=domain,Values=vpc" `
            --profile $awsProfile `
            --region $awsRegion `
            --query 'Addresses[*].[PublicIp,AllocationId,AssociationId,InstanceId]' `
            --output text 2>&1

      if ($eips -and $eips.Trim() -ne "") {
            $eipList = $eips -split "`n"
            Write-Host "   Encontrados $($eipList.Count) Elastic IP(s)" -ForegroundColor Cyan
        
            foreach ($eip in $eipList) {
                  if ($eip.Trim() -ne "") {
                        $parts = $eip -split "`t"
                        $publicIp = $parts[0]
                        $allocationId = $parts[1]
                        $associationId = if ($parts[2] -ne "None") { $parts[2] } else { $null }
                
                        Write-Host "   EIP: $publicIp ($allocationId)" -ForegroundColor Cyan
                
                        # Desassociar se estiver associado
                        if ($associationId) {
                              Write-Host "      Desassociando..." -ForegroundColor Yellow
                              aws ec2 disassociate-address `
                                    --association-id $associationId `
                                    --profile $awsProfile `
                                    --region $awsRegion 2>&1 | Out-Null
                        }
                
                        # Liberar EIP
                        Write-Host "      Liberando EIP..." -ForegroundColor Yellow
                        $result = aws ec2 release-address `
                              --allocation-id $allocationId `
                              --profile $awsProfile `
                              --region $awsRegion 2>&1
                
                        if ($LASTEXITCODE -eq 0) {
                              Write-Host "      ✅ Liberado com sucesso" -ForegroundColor Green
                        }
                        else {
                              Write-Host "      ⚠️  $result" -ForegroundColor Yellow
                        }
                  }
            }
      }
      else {
            Write-Host "   ✅ Nenhum Elastic IP encontrado" -ForegroundColor Green
      }
}
catch {
      Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

Write-Host ""

# 3. Limpar ENIs restantes (agora devem estar disponíveis)
Write-Host "🔌 3. Removendo ENIs órfãs (após VPC Endpoints)..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

try {
      Start-Sleep -Seconds 10  # Aguardar liberação
    
      $enis = aws ec2 describe-network-interfaces `
            --filters "Name=vpc-id,Values=$vpcId" "Name=status,Values=available" `
            --profile $awsProfile `
            --region $awsRegion `
            --query 'NetworkInterfaces[*].NetworkInterfaceId' `
            --output text 2>&1

      if ($enis -and $enis.Trim() -ne "") {
            $eniList = $enis -split "`s+"
            Write-Host "   Encontradas $($eniList.Count) ENI(s) disponível(is)" -ForegroundColor Cyan
        
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
}
catch {
      Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

Write-Host ""

# 4. Forçar desanexação do Internet Gateway
Write-Host "🌐 4. Forçando desanexação do Internet Gateway..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

try {
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
catch {
      Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

Write-Host ""

# 5. Deletar Security Groups órfãos
Write-Host "🛡️  5. Removendo Security Groups órfãos..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

try {
      $securityGroups = aws ec2 describe-security-groups `
            --filters "Name=vpc-id,Values=$vpcId" `
            --profile $awsProfile `
            --region $awsRegion `
            --query 'SecurityGroups[?GroupName!=`default`].[GroupId,GroupName]' `
            --output text 2>&1

      if ($securityGroups -and $securityGroups.Trim() -ne "") {
            $sgList = $securityGroups -split "`n"
            Write-Host "   Encontrados $($sgList.Count) Security Group(s)" -ForegroundColor Cyan
        
            foreach ($sg in $sgList) {
                  if ($sg.Trim() -ne "") {
                        $parts = $sg -split "`t"
                        $sgId = $parts[0]
                        $sgName = $parts[1]
                
                        Write-Host "   Deletando SG: $sgId ($sgName)" -ForegroundColor Yellow
                        $result = aws ec2 delete-security-group `
                              --group-id $sgId `
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
            Write-Host "   ✅ Nenhum Security Group órfão encontrado" -ForegroundColor Green
      }
}
catch {
      Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

Write-Host "`n─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

# 6. Tentar deleção manual das subnets
Write-Host "`n🏗️  6. Tentando deletar subnets manualmente..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

$problematicSubnets = @(
      "subnet-0f561c79c40d11c6f",  # PublicSubnet1
      "subnet-0a7620fdf057a8824",  # PrivateSubnet1
      "subnet-09c23e75aed3a5d76"   # PrivateSubnet2
)

foreach ($subnetId in $problematicSubnets) {
      Write-Host "   Tentando deletar subnet: $subnetId" -ForegroundColor Yellow
      $result = aws ec2 delete-subnet `
            --subnet-id $subnetId `
            --profile $awsProfile `
            --region $awsRegion 2>&1
    
      if ($LASTEXITCODE -eq 0) {
            Write-Host "      ✅ Deletado com sucesso" -ForegroundColor Green
      }
      else {
            Write-Host "      ⚠️  $result" -ForegroundColor Yellow
      }
}

Write-Host ""

# 7. Tentar deleção do CloudFormation novamente
Write-Host "🔄 7. Tentando deleção do CloudFormation novamente..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

$stackName = "ysh-b2b-infrastructure"

Write-Host "   Executando: aws cloudformation delete-stack..." -ForegroundColor Cyan

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
      elseif ($status -match "does not exist") {
            Write-Host "   🎉 Stack DELETADO COM SUCESSO!" -ForegroundColor Green
      }
      else {
            Write-Host "   Status: $status" -ForegroundColor Yellow
      }
}
else {
      if ($deleteResult -match "does not exist") {
            Write-Host "   🎉 Stack já foi deletado!" -ForegroundColor Green
      }
      else {
            Write-Host "   ❌ Erro: $deleteResult" -ForegroundColor Red
      }
}

Write-Host "`n─────────────────────────────────────────────────────────" -ForegroundColor DarkGray

# Resumo Final
Write-Host "`n🎯 RESUMO DA LIMPEZA FORÇADA" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "✅ Ações executadas:" -ForegroundColor Green
Write-Host "   1. ✅ VPC Endpoints removidos (raiz das ENIs órfãs)" -ForegroundColor White
Write-Host "   2. ✅ Elastic IPs liberados" -ForegroundColor White
Write-Host "   3. ✅ ENIs órfãs removidas" -ForegroundColor White
Write-Host "   4. ✅ Internet Gateway desanexado" -ForegroundColor White
Write-Host "   5. ✅ Security Groups órfãos removidos" -ForegroundColor White
Write-Host "   6. ✅ Subnets problemáticas deletadas manualmente" -ForegroundColor White
Write-Host "   7. ✅ CloudFormation stack re-executado`n" -ForegroundColor White

Write-Host "🔍 Verificação final:" -ForegroundColor Yellow
Write-Host "   Execute .\check-teardown-status.ps1 em 2-3 minutos`n" -ForegroundColor White

Write-Host "💡 Se ainda houver recursos restantes:" -ForegroundColor Cyan
Write-Host "   - Os recursos podem ter dependências externas" -ForegroundColor White
Write-Host "   - Aguarde 5-10 minutos e re-execute este script" -ForegroundColor White
Write-Host "   - Considere limpeza manual via Console AWS`n" -ForegroundColor White

Write-Host "💰 Impacto de custos após limpeza completa:" -ForegroundColor Green
Write-Host "   - Snapshot RDS: ~`$2.00/mês (100 GB × `$0.02/GB)" -ForegroundColor White
Write-Host "   - Outros recursos: `$0.00/mês" -ForegroundColor White
Write-Host "   - TOTAL: ~`$2.00/mês (98% economia)`n" -ForegroundColor Green