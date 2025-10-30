/**
 * Automated CDN Deployment Pipeline
 * Waits for certificate validation then deploys complete infrastructure
 * 
 * Usage:
 *   node scripts/auto-deploy-cdn.js
 */

import AWS from 'aws-sdk';
import { existsSync, readFileSync } from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const acm = new AWS.ACM({ region: 'us-east-1' });

const CHECK_INTERVAL = 30000; // 30 seconds
const MAX_CHECKS = 60; // 30 minutes

async function waitForValidation() {
  if (!existsSync('acm-certificate-info.json')) {
    console.error('❌ Certificado não encontrado.');
    process.exit(1);
  }

  const certInfo = JSON.parse(readFileSync('acm-certificate-info.json', 'utf8'));
  const certificateArn = certInfo.certificateArn;

  console.log('🔄 Aguardando validação do certificado...\n');
  console.log(`   ARN: ${certificateArn}`);
  console.log(`   Domínio: ${certInfo.domain}\n`);

  let checks = 0;

  while (checks < MAX_CHECKS) {
    checks++;
    const timestamp = new Date().toLocaleTimeString('pt-BR');

    try {
      const result = await acm.describeCertificate({
        CertificateArn: certificateArn
      }).promise();

      const status = result.Certificate.Status;
      console.log(`[${timestamp}] Check ${checks}/${MAX_CHECKS} - Status: ${status}`);

      if (status === 'ISSUED') {
        console.log('\n✅ CERTIFICADO VALIDADO!\n');
        return true;
      } else if (status === 'FAILED' || status === 'VALIDATION_TIMED_OUT') {
        console.error(`\n❌ Validação falhou: ${status}\n`);
        return false;
      }

      await new Promise(resolve => setTimeout(resolve, CHECK_INTERVAL));

    } catch (error) {
      console.error(`\n❌ Erro: ${error.message}`);
      return false;
    }
  }

  console.warn('\n⚠️  Timeout atingido.\n');
  return false;
}

async function deployInfrastructure() {
  console.log('🚀 Iniciando deployment da infraestrutura...\n');
  console.log('='.repeat(70) + '\n');

  try {
    // Step 1: Setup complete infrastructure
    console.log('📋 PASSO 1: Criando CloudFront Distribution...\n');
    const { stdout: setupOutput } = await execAsync('node scripts/setup-complete-infrastructure.js');
    console.log(setupOutput);

    // Step 2: Wait for deployment
    console.log('\n📋 PASSO 2: Aguardando deployment (pode levar 15-30 minutos)...\n');
    
    let deployed = false;
    let deployChecks = 0;
    const maxDeployChecks = 90; // 45 minutes

    while (!deployed && deployChecks < maxDeployChecks) {
      deployChecks++;
      await new Promise(resolve => setTimeout(resolve, 30000));

      try {
        const { stdout } = await execAsync('node scripts/check-cloudfront-status.js');
        console.log(`[${new Date().toLocaleTimeString('pt-BR')}] Check ${deployChecks}/${maxDeployChecks}`);
        
        if (stdout.includes('DISTRIBUTION IMPLANTADA') || stdout.includes('Deployed')) {
          deployed = true;
          console.log('\n✅ CloudFront deployment concluído!\n');
        }
      } catch (error) {
        // Continue checking
      }
    }

    if (!deployed) {
      console.log('\n⚠️  Deployment ainda em progresso. Verifique manualmente:\n');
      console.log('   node scripts/check-cloudfront-status.js\n');
    }

    // Step 3: Update URLs
    console.log('📋 PASSO 3: Atualizando URLs para CloudFront...\n');
    const { stdout: urlsOutput } = await execAsync('node scripts/update-image-urls-to-cloudfront.js');
    console.log(urlsOutput);

    console.log('\n' + '='.repeat(70));
    console.log('\n🎉 DEPLOYMENT COMPLETO!\n');
    console.log('📋 Próximos passos:\n');
    console.log('1. Adicione o registro CNAME no GoDaddy (veja cloudfront-distribution-info.json)');
    console.log('2. Aguarde propagação DNS (5-30 minutos)');
    console.log('3. Teste: https://cdn.yellosolarhub.com/products/inversores/286844.png\n');
    console.log('='.repeat(70) + '\n');

  } catch (error) {
    console.error('\n❌ Erro no deployment:', error.message);
    process.exit(1);
  }
}

async function main() {
  console.log('🚀 YSH B2B - Automated CDN Deployment\n');
  console.log('='.repeat(70) + '\n');

  const validated = await waitForValidation();

  if (validated) {
    await deployInfrastructure();
  } else {
    console.error('❌ Não foi possível validar o certificado.\n');
    process.exit(1);
  }
}

main();
